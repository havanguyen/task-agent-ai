import json
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from google import genai
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.models.project import Project
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User

router = APIRouter()

client = (
    genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None
)


class ChatRequest(BaseModel):
    message: str


class ActionResult(BaseModel):
    action: str
    success: bool
    details: str


class ChatResponse(BaseModel):
    response: str
    actions: List[ActionResult] = []


SYSTEM_PROMPT = """You are a Task Management AI Assistant. Parse user requests and respond with JSON.

AVAILABLE ACTIONS:

1. CREATE a task:
{"action": "create_task", "title": "task title", "priority": "high/medium/low", "due_date": "YYYY-MM-DD or null", "assignee_name": "person name or null", "project_name": "project name or null"}

2. LIST tasks:
{"action": "list_tasks", "filter": "all/overdue/high-priority/my-tasks"}

3. UPDATE task status:
{"action": "update_task", "task_title": "task title to search", "new_status": "todo/in-progress/done"}

4. Show PROJECT stats:
{"action": "project_stats", "project_name": "project name or null for all"}

5. Show HELP or general chat:
{"action": "chat", "message": "your helpful response"}

Examples:
User: "Create urgent task for John, due tomorrow"
Response: {"action": "create_task", "title": "Urgent task", "priority": "high", "due_date": "2026-01-22", "assignee_name": "John", "project_name": null}

User: "Show me overdue tasks"
Response: {"action": "list_tasks", "filter": "overdue"}

User: "Mark the review task as done"
Response: {"action": "update_task", "task_title": "review", "new_status": "done"}

User: "Show project statistics"
Response: {"action": "project_stats", "project_name": null}

User: "What can you do?" or "Help"
Response: {"action": "chat", "message": "I can help you with: 1) Create tasks, 2) List/filter tasks, 3) Update task status, 4) View project stats. Just tell me what you need!"}

User: "Hello"
Response: {"action": "chat", "message": "Hello! I'm your AI Assistant. I can help you create tasks, list tasks, update status, and view project statistics. What would you like to do?"}

IMPORTANT: Always respond with valid JSON only, no extra text.
"""


def parse_ai_response(text: str) -> dict:
    if text is None:
        return {
            "action": "chat",
            "message": "I'm sorry, I couldn't process that request.",
        }
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        return json.loads(text.strip())
    except:
        return {"action": "chat", "message": text}


def find_user_by_name(db: Session, name: str, org_id: int) -> Optional[User]:
    if not name:
        return None
    return (
        db.query(User)
        .filter(User.organization_id == org_id, User.full_name.ilike(f"%{name}%"))
        .first()
    )


def find_project_by_name(db: Session, name: str, org_id: int) -> Optional[Project]:
    if not name:
        return None
    return (
        db.query(Project)
        .filter(Project.organization_id == org_id, Project.name.ilike(f"%{name}%"))
        .first()
    )


def parse_due_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None


@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(
    request: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    prompt = SYSTEM_PROMPT + f"\nToday is: {today}\n\nUser: {request.message}"

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt
        )
        # Try different ways to get the text from response
        response_text = None
        if hasattr(response, "text") and response.text:
            response_text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                if hasattr(candidate.content, "parts") and candidate.content.parts:
                    response_text = candidate.content.parts[0].text

        parsed = parse_ai_response(response_text)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return ChatResponse(
                response="⏳ API quota exceeded. Please wait 1 minute and try again.",
                actions=[],
            )
        return ChatResponse(response=f"AI Error: {error_msg}", actions=[])

    actions = []
    final_response = ""

    if parsed.get("action") == "create_task":
        project = find_project_by_name(
            db, parsed.get("project_name"), current_user.organization_id
        )
        if not project:
            project = (
                db.query(Project)
                .filter(Project.organization_id == current_user.organization_id)
                .first()
            )

        if not project:
            final_response = "No project found. Please create a project first."
        else:
            assignee = find_user_by_name(
                db, parsed.get("assignee_name"), current_user.organization_id
            )

            priority_map = {
                "high": TaskPriority.HIGH,
                "medium": TaskPriority.MEDIUM,
                "low": TaskPriority.LOW,
            }
            priority = priority_map.get(
                parsed.get("priority", "medium"), TaskPriority.MEDIUM
            )

            due_date = parse_due_date(parsed.get("due_date"))
            if parsed.get("due_date") and "tomorrow" in request.message.lower():
                due_date = datetime.now() + timedelta(days=1)

            new_task = Task(
                title=parsed.get("title", "New Task"),
                description="Created by AI Assistant",
                status=TaskStatus.TODO,
                priority=priority,
                due_date=due_date,
                project_id=project.id,
                assignee_id=assignee.id if assignee else current_user.id,
            )
            db.add(new_task)
            db.commit()
            db.refresh(new_task)

            actions.append(
                ActionResult(
                    action="create_task",
                    success=True,
                    details=f"Created task: {new_task.title} (ID: {new_task.id})",
                )
            )

            assignee_name = assignee.full_name if assignee else current_user.full_name
            final_response = f"✅ Created task '{new_task.title}' with {priority.value} priority, assigned to {assignee_name}"
            if due_date:
                final_response += f", due {due_date.strftime('%Y-%m-%d')}"

    elif parsed.get("action") == "list_tasks":
        tasks_query = (
            db.query(Task)
            .join(Project)
            .filter(Project.organization_id == current_user.organization_id)
        )

        filter_type = parsed.get("filter", "all")
        if filter_type == "overdue":
            tasks_query = tasks_query.filter(
                Task.due_date < datetime.now(), Task.status != TaskStatus.DONE
            )
        elif filter_type == "high-priority":
            tasks_query = tasks_query.filter(Task.priority == TaskPriority.HIGH)
        elif filter_type == "my-tasks":
            tasks_query = tasks_query.filter(Task.assignee_id == current_user.id)

        tasks = tasks_query.limit(10).all()

        if tasks:
            task_list = "\n".join(
                [f"• {t.title} [{t.status.value}] - {t.priority.value}" for t in tasks]
            )
            final_response = f"📋 Task list:\n{task_list}"
        else:
            final_response = "No tasks found."

    elif parsed.get("action") == "update_task":
        task_title = parsed.get("task_title", "")
        new_status = parsed.get("new_status", "")

        task = (
            db.query(Task)
            .join(Project)
            .filter(
                Project.organization_id == current_user.organization_id,
                Task.title.ilike(f"%{task_title}%"),
            )
            .first()
        )

        if not task:
            final_response = f"❌ Task containing '{task_title}' not found."
        else:
            status_map = {
                "todo": TaskStatus.TODO,
                "in-progress": TaskStatus.IN_PROGRESS,
                "done": TaskStatus.DONE,
            }
            if new_status in status_map:
                task.status = status_map[new_status]
                db.commit()
                actions.append(
                    ActionResult(
                        action="update_task",
                        success=True,
                        details=f"Updated: {task.title} → {new_status}",
                    )
                )
                final_response = (
                    f"✅ Task '{task.title}' status updated to {new_status}"
                )
            else:
                final_response = (
                    f"❌ Invalid status: {new_status}. Use: todo, in-progress, done"
                )

    elif parsed.get("action") == "project_stats":
        projects = (
            db.query(Project)
            .filter(Project.organization_id == current_user.organization_id)
            .all()
        )

        if not projects:
            final_response = "No projects found."
        else:
            stats_list = []
            for p in projects[:5]:
                todo = (
                    db.query(Task)
                    .filter(Task.project_id == p.id, Task.status == TaskStatus.TODO)
                    .count()
                )
                in_progress = (
                    db.query(Task)
                    .filter(
                        Task.project_id == p.id, Task.status == TaskStatus.IN_PROGRESS
                    )
                    .count()
                )
                done = (
                    db.query(Task)
                    .filter(Task.project_id == p.id, Task.status == TaskStatus.DONE)
                    .count()
                )
                stats_list.append(
                    f"📁 {p.name}: Todo={todo}, In Progress={in_progress}, Done={done}"
                )
            final_response = "📊 Project Statistics:\n" + "\n".join(stats_list)

    else:
        final_response = parsed.get("message", response.text)

    return ChatResponse(response=final_response, actions=actions)
