"""
Repository Layer - Database Operations

This package contains all repositories that handle database CRUD operations.
Repositories should not contain business logic, only data access logic.
"""

from app.repositories.base import BaseRepository
from app.repositories.task_repository import task_repository, TaskRepository
from app.repositories.project_repository import (
    project_repository,
    project_member_repository,
    ProjectRepository,
    ProjectMemberRepository,
)
from app.repositories.user_repository import user_repository, UserRepository
from app.repositories.organization_repository import (
    organization_repository,
    OrganizationRepository,
)
from app.repositories.notification_repository import (
    notification_repository,
    comment_repository,
    attachment_repository,
    NotificationRepository,
    CommentRepository,
    AttachmentRepository,
)

__all__ = [
    # Base
    "BaseRepository",
    # Task
    "task_repository",
    "TaskRepository",
    # Project
    "project_repository",
    "project_member_repository",
    "ProjectRepository",
    "ProjectMemberRepository",
    # User
    "user_repository",
    "UserRepository",
    # Organization
    "organization_repository",
    "OrganizationRepository",
    # Notification/Comment/Attachment
    "notification_repository",
    "comment_repository",
    "attachment_repository",
    "NotificationRepository",
    "CommentRepository",
    "AttachmentRepository",
]
