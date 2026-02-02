from typing import Optional, Any
from datetime import datetime, timedelta

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.core.rag import search_tasks
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.project import Project
from app.models.user import User


class ToolContext:
    db: Optional[Session] = None
    current_user: Optional[User] = None

    @classmethod
    def set_context(cls, db: Session, user: User):
        cls.db = db
        cls.current_user = user

    @classmethod
    def clear_context(cls):
        cls.db = None
        cls.current_user = None


@tool
def search_tasks_tool(query: str) -> str:
    """Use this tool to search for information about existing tasks, their status, assignees, or details. Input should be a natural language search query."""
    return search_tasks(query, top_k=5)


@tool
def list_tasks_tool(filter_type: str = "all") -> str:
    """Use this tool to list tasks with optional filtering. filter_type: One of 'all', 'overdue', 'high-priority', 'my-tasks'"""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    user = ToolContext.current_user

    tasks_query = (
        db.query(Task)
        .join(Project)
        .filter(Project.organization_id == user.organization_id)
    )

    if filter_type == "overdue":
        tasks_query = tasks_query.filter(
            Task.due_date < datetime.now(), Task.status != TaskStatus.DONE
        )
    elif filter_type == "high-priority":
        tasks_query = tasks_query.filter(Task.priority == TaskPriority.HIGH)
    elif filter_type == "my-tasks":
        tasks_query = tasks_query.filter(Task.assignee_id == user.id)

    tasks = tasks_query.limit(10).all()

    if not tasks:
        return "No tasks found matching the criteria."

    result_lines = []
    for t in tasks:
        assignee_name = t.assignee.full_name if t.assignee else "Unassigned"
        due_str = t.due_date.strftime("%Y-%m-%d") if t.due_date else "No due date"
        result_lines.append(
            f"• {t.title} [{t.status.value}] - Priority: {t.priority.value}, "
            f"Assigned to: {assignee_name}, Due: {due_str}"
        )

    return f"Found {len(tasks)} tasks:\n" + "\n".join(result_lines)


@tool
def create_task_tool(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: str = "",
    project_name: str = "",
    assignee_name: str = "",
) -> str:
    """Use this tool to create a new task. title: Title of the task (required), description: Description, priority: 'high', 'medium', or 'low', due_date: YYYY-MM-DD format, project_name: Name of the project, assignee_name: Name of the person to assign"""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    user = ToolContext.current_user

    project = None
    if project_name:
        project = (
            db.query(Project)
            .filter(
                Project.organization_id == user.organization_id,
                Project.name.ilike(f"%{project_name}%"),
            )
            .first()
        )

    if not project:
        project = (
            db.query(Project)
            .filter(Project.organization_id == user.organization_id)
            .first()
        )

    if not project:
        return "Error: No project found. Please create a project first."

    assignee = None
    if assignee_name:
        assignee = (
            db.query(User)
            .filter(
                User.organization_id == user.organization_id,
                User.full_name.ilike(f"%{assignee_name}%"),
            )
            .first()
        )
    priority_map = {
        "high": TaskPriority.HIGH,
        "medium": TaskPriority.MEDIUM,
        "low": TaskPriority.LOW,
    }
    task_priority = priority_map.get(priority.lower(), TaskPriority.MEDIUM)
    task_due_date = None
    if due_date:
        try:
            task_due_date = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            pass

    new_task = Task(
        title=title,
        description=description or "Created by AI Assistant",
        status=TaskStatus.TODO,
        priority=task_priority,
        due_date=task_due_date,
        project_id=project.id,
        assignee_id=assignee.id if assignee else user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    assignee_name_final = assignee.full_name if assignee else user.full_name
    due_str = task_due_date.strftime("%Y-%m-%d") if task_due_date else "No due date"

    return (
        f"✅ Created task '{new_task.title}' (ID: {new_task.id}) "
        f"with {task_priority.value} priority, assigned to {assignee_name_final}, "
        f"in project '{project.name}', due: {due_str}"
    )


@tool
def update_task_tool(task_title: str, new_status: str) -> str:
    """Use this tool to update the status of an existing task. task_title: Title or partial title, new_status: 'todo', 'in-progress', or 'done'"""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    user = ToolContext.current_user
    task = (
        db.query(Task)
        .join(Project)
        .filter(
            Project.organization_id == user.organization_id,
            Task.title.ilike(f"%{task_title}%"),
        )
        .first()
    )

    if not task:
        return f"❌ Task containing '{task_title}' not found."
    status_map = {
        "todo": TaskStatus.TODO,
        "in-progress": TaskStatus.IN_PROGRESS,
        "in_progress": TaskStatus.IN_PROGRESS,
        "done": TaskStatus.DONE,
    }

    new_status_lower = new_status.lower()
    if new_status_lower not in status_map:
        return f"❌ Invalid status: {new_status}. Use: todo, in-progress, or done"

    task.status = status_map[new_status_lower]
    db.commit()

    return f"✅ Task '{task.title}' status updated to {new_status_lower}"


@tool
def project_stats_tool(project_name: str = "") -> str:
    """Use this tool to get statistics about projects and their tasks. project_name: Optional project name to get stats for. Leave empty for all projects."""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    user = ToolContext.current_user

    projects_query = db.query(Project).filter(
        Project.organization_id == user.organization_id
    )

    if project_name:
        projects_query = projects_query.filter(Project.name.ilike(f"%{project_name}%"))

    projects = projects_query.limit(5).all()

    if not projects:
        return "No projects found."

    stats_lines = []
    for p in projects:
        todo_count = (
            db.query(Task)
            .filter(Task.project_id == p.id, Task.status == TaskStatus.TODO)
            .count()
        )
        in_progress_count = (
            db.query(Task)
            .filter(Task.project_id == p.id, Task.status == TaskStatus.IN_PROGRESS)
            .count()
        )
        done_count = (
            db.query(Task)
            .filter(Task.project_id == p.id, Task.status == TaskStatus.DONE)
            .count()
        )

        total = todo_count + in_progress_count + done_count
        stats_lines.append(
            f"📁 {p.name}: Todo={todo_count}, In Progress={in_progress_count}, "
            f"Done={done_count}, Total={total}"
        )

    return "📊 Project Statistics:\n" + "\n".join(stats_lines)


tools = [
    search_tasks_tool,
    list_tasks_tool,
    create_task_tool,
    update_task_tool,
    project_stats_tool,
]
