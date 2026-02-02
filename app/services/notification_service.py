from sqlalchemy.orm import Session

from app.models.extras import Notification
from app.repositories.notification_repository import (
    create_notification as repo_create_notification,
)


class NotificationService:

    def create_notification(
        self, db: Session, user_id: int, title: str, message: str
    ) -> Notification:
        notification = repo_create_notification(
            db, user_id=user_id, title=title, message=message
        )
        db.commit()
        db.refresh(notification)
        return notification

    def notify_assignee(self, db: Session, task, user_id: int) -> None:
        self.create_notification(
            db,
            user_id,
            title="New Task Assignment",
            message=f"You have been assigned to task: {task.title}",
        )

    def notify_status_change(self, db: Session, task) -> None:
        if task.assignee_id:
            self.create_notification(
                db,
                task.assignee_id,
                title="Task Status Updated",
                message=f"Task '{task.title}' status changed to {task.status.value}",
            )


notification_service = NotificationService()


def create_notification(db: Session, user_id: int, title: str, message: str):
    return notification_service.create_notification(db, user_id, title, message)


def notify_assignee(db: Session, task, user_id: int):
    return notification_service.notify_assignee(db, task, user_id)


def notify_status_change(db: Session, task):
    return notification_service.notify_status_change(db, task)
