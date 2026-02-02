from sqlalchemy.orm import Session
from app.models.extras import Notification
from app.models.user import User


def create_notification(db: Session, user_id: int, title: str, message: str):
    notification = Notification(user_id=user_id, title=title, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def notify_assignee(db: Session, task, user_id: int):
    create_notification(
        db,
        user_id,
        title="New Task Assignment",
        message=f"You have been assigned to task: {task.title}",
    )


def notify_status_change(db: Session, task):
    if task.assignee_id:
        create_notification(
            db,
            task.assignee_id,
            title="Task Status Updated",
            message=f"Task '{task.title}' status changed to {task.status.value}",
        )
