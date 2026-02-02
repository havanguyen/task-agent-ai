"""Project-related agent tools."""

from langchain_core.tools import tool

from app.models.task import Task, TaskStatus
from app.models.project import Project
from app.agent.tools.base import ToolContext


@tool
def get_project_tool(project_name: str) -> str:
    """Use this tool to get detailed information about a specific project. project_name: Name or partial name of the project."""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    user = ToolContext.current_user

    project = (
        db.query(Project)
        .filter(
            Project.organization_id == user.organization_id,
            Project.name.ilike(f"%{project_name}%"),
        )
        .first()
    )

    if not project:
        return f"❌ Project containing '{project_name}' not found."

    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    member_count = len(project.members) if project.members else 0

    return (
        f"📁 **{project.name}** (ID: {project.id})\n"
        f"Description: {project.description or 'No description'}\n"
        f"Tasks: {task_count}\n"
        f"Members: {member_count}"
    )


@tool
def create_project_tool(name: str, description: str = "") -> str:
    """Use this tool to create a new project. Requires Admin or Manager role. name: Name of the project (required), description: Project description."""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    user = ToolContext.current_user

    from app.models.user import UserRole

    if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        return "❌ You don't have permission to create projects. Admin or Manager role required."

    existing = (
        db.query(Project)
        .filter(
            Project.organization_id == user.organization_id,
            Project.name == name,
        )
        .first()
    )

    if existing:
        return f"❌ Project '{name}' already exists."

    new_project = Project(
        name=name,
        description=description or "Created by AI Assistant",
        organization_id=user.organization_id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return f"✅ Created project '{new_project.name}' (ID: {new_project.id})"


@tool
def update_project_tool(
    project_name: str, new_name: str = "", new_description: str = ""
) -> str:
    """Use this tool to update an existing project. project_name: Current name of the project, new_name: New name (optional), new_description: New description (optional)."""
    if not ToolContext.db or not ToolContext.current_user:
        return "Error: Database context not available."

    db = ToolContext.db
    user = ToolContext.current_user

    from app.models.user import UserRole

    if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        return "❌ You don't have permission to update projects."

    project = (
        db.query(Project)
        .filter(
            Project.organization_id == user.organization_id,
            Project.name.ilike(f"%{project_name}%"),
        )
        .first()
    )

    if not project:
        return f"❌ Project containing '{project_name}' not found."

    updates = []
    if new_name:
        project.name = new_name
        updates.append(f"name → '{new_name}'")
    if new_description:
        project.description = new_description
        updates.append("description updated")

    if not updates:
        return "❌ No updates provided. Specify new_name or new_description."

    db.commit()
    return f"✅ Updated project '{project.name}': {', '.join(updates)}"


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


project_tools = [
    get_project_tool,
    create_project_tool,
    update_project_tool,
    project_stats_tool,
]
