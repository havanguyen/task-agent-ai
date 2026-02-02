from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from sqlalchemy.orm import Session

from app.config import settings
from app.agent.tools import tools, ToolContext
from app.models.user import User


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0,
        convert_system_message_to_human=True,
    )


def get_agent_executor():
    llm = get_llm()
    return create_react_agent(llm, tools)


SYSTEM_MESSAGE = """You are a helpful Task Management AI Assistant. You help users manage their tasks and projects.

You have access to the following capabilities:
1. **Search Tasks**: Search for information about existing tasks, their status, assignees, and details.
2. **List Tasks**: List tasks with filters (all, overdue, high-priority, my-tasks).
3. **Create Task**: Create new tasks with title, description, priority, due date, project, and assignee.
4. **Update Task**: Update the status of existing tasks (todo, in-progress, done).
5. **Project Stats**: View statistics about projects and their task counts.

Guidelines:
- Always use the search_tasks_tool first when the user asks about specific tasks or wants to know the status of something.
- Be helpful and provide clear, concise responses.
- When creating tasks, confirm the details with the user.
- If information is missing, ask for clarification or use reasonable defaults.
- Respond in the same language as the user's message.
"""


def run_agent(
    user_message: str, db: Optional[Session] = None, current_user: Optional[User] = None
) -> str:
    if db and current_user:
        ToolContext.set_context(db, current_user)

    try:
        agent_executor = get_agent_executor()

        inputs = {"messages": [("system", SYSTEM_MESSAGE), ("user", user_message)]}

        result = agent_executor.invoke(inputs)
        messages = result.get("messages", [])
        if messages:
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.content:
                    content = msg.content
                    if isinstance(content, str):
                        return content
                    elif isinstance(content, list):
                        text_parts = []
                        for part in content:
                            if isinstance(part, str):
                                text_parts.append(part)
                            elif isinstance(part, dict) and "text" in part:
                                text_parts.append(part["text"])
                        if text_parts:
                            return "\n".join(text_parts)

        return "I apologize, but I couldn't process your request. Please try again."

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "⏳ API quota exceeded. Please wait a moment and try again."
        return f"An error occurred: {error_msg}"

    finally:
        ToolContext.clear_context()
