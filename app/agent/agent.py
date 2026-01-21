"""
Task AI Agent with Google Gemini Integration

This agent interacts with the Task Management System through the MCP server
and uses Google Gemini for natural language understanding.
"""

import os
import asyncio
import json
from typing import Any, Dict, List, Optional
import httpx
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAbMArGWvPXSE1wiDNlbAGbXueNNlCFNcg")
genai.configure(api_key=GEMINI_API_KEY)

# API Base URL
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Store auth token
auth_token: Optional[str] = None


class TaskAgent:
    """AI Agent for Task Management System"""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None

        # Define available tools/functions
        self.tools = {
            "login": self.login,
            "register_org": self.register_organization,
            "list_projects": self.list_projects,
            "create_project": self.create_project,
            "list_tasks": self.list_tasks,
            "create_task": self.create_task,
            "update_task": self.update_task,
            "get_overdue_tasks": self.get_overdue_tasks,
            "get_project_stats": self.get_project_stats,
        }

        self.tool_descriptions = """
Available Tools:
1. login(email, password) - Login to get access token
2. register_org(org_name, email, password, full_name) - Register new organization with admin user
3. list_projects() - List all projects in organization
4. create_project(name, description) - Create a new project
5. list_tasks(project_id, status, priority) - List tasks with optional filters
6. create_task(title, project_id, description, priority, due_date, assignee_id) - Create a new task
7. update_task(task_id, status, priority, due_date) - Update an existing task
8. get_overdue_tasks(project_id) - Get overdue tasks in a project
9. get_project_stats(project_id) - Get task count by status in a project
"""

    def _headers(self):
        """Get request headers with auth token"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get access token"""
        try:
            resp = await self.client.post(
                f"{BASE_URL}/api/v1/auth/login",
                data={"username": email, "password": password},
            )
            if resp.status_code == 200:
                data = resp.json()
                self.auth_token = data.get("access_token")
                return {"success": True, "message": "Logged in successfully"}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def register_organization(
        self, org_name: str, email: str, password: str, full_name: str
    ) -> Dict[str, Any]:
        """Register a new organization with admin user"""
        try:
            resp = await self.client.post(
                f"{BASE_URL}/api/v1/organizations/register",
                params={
                    "org_name": org_name,
                    "email": email,
                    "password": password,
                    "full_name": full_name,
                },
            )
            return resp.json() if resp.status_code == 200 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def list_projects(self) -> Dict[str, Any]:
        """List all projects"""
        try:
            resp = await self.client.get(
                f"{BASE_URL}/api/v1/projects/", headers=self._headers()
            )
            return resp.json() if resp.status_code == 200 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new project"""
        try:
            resp = await self.client.post(
                f"{BASE_URL}/api/v1/projects/",
                headers=self._headers(),
                json={
                    "name": name,
                    "description": description,
                    "organization_id": 1,
                },  # org_id from context
            )
            return resp.json() if resp.status_code == 200 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def list_tasks(
        self, project_id: int = None, status: str = None, priority: str = None
    ) -> Dict[str, Any]:
        """List tasks with filters"""
        try:
            params = {}
            if project_id:
                params["project_id"] = project_id
            if status:
                params["status"] = status
            if priority:
                params["priority"] = priority

            resp = await self.client.get(
                f"{BASE_URL}/api/v1/tasks/", headers=self._headers(), params=params
            )
            return resp.json() if resp.status_code == 200 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def create_task(
        self,
        title: str,
        project_id: int,
        description: str = "",
        priority: str = "medium",
        due_date: str = None,
        assignee_id: int = None,
    ) -> Dict[str, Any]:
        """Create a new task"""
        try:
            payload = {
                "title": title,
                "project_id": project_id,
                "description": description,
                "priority": priority,
            }
            if due_date:
                payload["due_date"] = due_date
            if assignee_id:
                payload["assignee_id"] = assignee_id

            resp = await self.client.post(
                f"{BASE_URL}/api/v1/tasks/", headers=self._headers(), json=payload
            )
            return resp.json() if resp.status_code == 200 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def update_task(
        self,
        task_id: int,
        status: str = None,
        priority: str = None,
        due_date: str = None,
    ) -> Dict[str, Any]:
        """Update a task"""
        try:
            payload = {}
            if status:
                payload["status"] = status
            if priority:
                payload["priority"] = priority
            if due_date:
                payload["due_date"] = due_date

            resp = await self.client.put(
                f"{BASE_URL}/api/v1/tasks/{task_id}",
                headers=self._headers(),
                json=payload,
            )
            return resp.json() if resp.status_code == 200 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def get_overdue_tasks(self, project_id: int) -> Dict[str, Any]:
        """Get overdue tasks"""
        try:
            resp = await self.client.get(
                f"{BASE_URL}/api/v1/projects/{project_id}/overdue",
                headers=self._headers(),
            )
            return resp.json() if resp.status_code == 200 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def get_project_stats(self, project_id: int) -> Dict[str, Any]:
        """Get project task statistics"""
        try:
            resp = await self.client.get(
                f"{BASE_URL}/api/v1/projects/{project_id}/stats",
                headers=self._headers(),
            )
            return resp.json() if resp.status_code == 200 else {"error": resp.text}
        except Exception as e:
            return {"error": str(e)}

    async def process_user_request(self, user_input: str) -> str:
        """Process natural language request using Gemini"""

        system_prompt = f"""You are a Task Management Assistant. You help users manage tasks, projects, and organizations.

{self.tool_descriptions}

Based on the user's request, determine which tool(s) to call and with what parameters.
Respond in JSON format with the following structure:
{{
    "thought": "Your reasoning about what the user wants",
    "action": "tool_name",
    "action_input": {{"param1": "value1", "param2": "value2"}}
}}

If no tool is needed, respond with:
{{
    "thought": "Your reasoning",
    "action": "respond",
    "action_input": {{"message": "Your response to the user"}}
}}

User request: {user_input}
"""

        try:
            response = self.model.generate_content(system_prompt)
            response_text = response.text.strip()

            # Parse JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            try:
                action_data = json.loads(response_text)
            except json.JSONDecodeError:
                return f"I understood your request but couldn't process it properly. Raw response: {response_text}"

            action = action_data.get("action")
            action_input = action_data.get("action_input", {})
            thought = action_data.get("thought", "")

            if action == "respond":
                return action_input.get(
                    "message", "I'm not sure how to help with that."
                )

            if action in self.tools:
                # Execute the tool
                result = await self.tools[action](**action_input)

                # Generate a natural language response based on the result
                summary_prompt = f"""Based on the following tool execution result, provide a helpful summary for the user.

Tool: {action}
Parameters: {json.dumps(action_input)}
Result: {json.dumps(result)}

Provide a concise, friendly response:"""

                summary_response = self.model.generate_content(summary_prompt)
                return summary_response.text.strip()
            else:
                return f"Unknown action: {action}"

        except Exception as e:
            return f"Error processing request: {str(e)}"

    async def chat(self):
        """Interactive chat loop"""
        print("\n=== Task Management AI Agent ===")
        print("Type 'quit' to exit, 'help' for available commands\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print("Goodbye!")
                    break

                if user_input.lower() == "help":
                    print(self.tool_descriptions)
                    continue

                print("Agent: Thinking...")
                response = await self.process_user_request(user_input)
                print(f"Agent: {response}\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def test_mcp_tools():
    """Test MCP tools via the agent"""
    print("\n=== Testing MCP Tools ===\n")
    agent = TaskAgent()

    try:
        # Test 1: Register organization
        print("Test 1: Register Organization")
        result = await agent.register_organization(
            org_name="Test Org",
            email="admin@test.com",
            password="password123",
            full_name="Admin User",
        )
        print(f"Result: {result}\n")

        # Test 2: Login
        print("Test 2: Login")
        result = await agent.login("admin@test.com", "password123")
        print(f"Result: {result}\n")

        # Test 3: Create Project
        print("Test 3: Create Project")
        result = await agent.create_project(
            "Website Redesign", "Redesign company website"
        )
        print(f"Result: {result}\n")

        # Test 4: Create Task
        print("Test 4: Create Task")
        result = await agent.create_task(
            title="Design mockups",
            project_id=1,
            description="Create initial design mockups",
            priority="high",
        )
        print(f"Result: {result}\n")

        # Test 5: List Tasks
        print("Test 5: List Tasks")
        result = await agent.list_tasks()
        print(f"Result: {result}\n")

        # Test 6: Natural Language Query
        print("Test 6: Natural Language Query")
        response = await agent.process_user_request("Show me all high priority tasks")
        print(f"Response: {response}\n")

    finally:
        await agent.close()


async def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        await test_mcp_tools()
    else:
        agent = TaskAgent()
        try:
            await agent.chat()
        finally:
            await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
