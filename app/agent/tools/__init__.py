"""Agent tools package - exports all tools for the AI assistant."""

from app.agent.tools.base import ToolContext

from app.agent.tools.task_tools import (
    search_tasks_tool,
    list_tasks_tool,
    create_task_tool,
    update_task_tool,
    get_task_tool,
    task_tools,
)

from app.agent.tools.project_tools import (
    get_project_tool,
    create_project_tool,
    update_project_tool,
    project_stats_tool,
    project_tools,
)

from app.agent.tools.user_tools import (
    get_user_tool,
    list_users_tool,
    create_user_tool,
    update_user_tool,
    user_tools,
)

# Combined list of all tools
tools = task_tools + project_tools + user_tools

__all__ = [
    # Base
    "ToolContext",
    # Task tools
    "search_tasks_tool",
    "list_tasks_tool",
    "create_task_tool",
    "update_task_tool",
    "get_task_tool",
    "task_tools",
    # Project tools
    "get_project_tool",
    "create_project_tool",
    "update_project_tool",
    "project_stats_tool",
    "project_tools",
    # User tools
    "get_user_tool",
    "list_users_tool",
    "create_user_tool",
    "update_user_tool",
    "user_tools",
    # All tools
    "tools",
]
