"""
Service Layer - Business Logic

This package contains all services that handle business logic.
Services orchestrate repository calls and implement business rules.
"""

from app.services.task_service import task_service, TaskService
from app.services.project_service import project_service, ProjectService
from app.services.user_service import user_service, UserService
from app.services.organization_service import organization_service, OrganizationService
from app.services.notification_service import (
    notification_service,
    NotificationService,
    # Backward compatible functions
    create_notification,
    notify_assignee,
    notify_status_change,
)

__all__ = [
    # Task
    "task_service",
    "TaskService",
    # Project
    "project_service",
    "ProjectService",
    # User
    "user_service",
    "UserService",
    # Organization
    "organization_service",
    "OrganizationService",
    # Notification
    "notification_service",
    "NotificationService",
    "create_notification",
    "notify_assignee",
    "notify_status_change",
]
