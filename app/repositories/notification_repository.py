from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import false

from app.models.extras import Notification, Comment, Attachment
from app.repositories.base import BaseRepository


def get_by_user(
        db: Session,
    user_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False
) -> List[Notification]:
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == false())
    return query.order_by(Notification.id.desc()).offset(skip).limit(limit).all()


def create_notification(
        db: Session, *, user_id: int, title: str, message: str
) -> Notification:
    notification = Notification(user_id=user_id, title=title, message=message)
    db.add(notification)
    db.flush()
    db.refresh(notification)
    return notification


def mark_as_read(db: Session, notification: Notification) -> Notification:
    notification.is_read = True
    db.add(notification)
    db.flush()
    db.refresh(notification)
    return notification


class NotificationRepository(BaseRepository[Notification, None, None]):

    def __init__(self):
        super().__init__(Notification)


def create_comment(
        db: Session, *, content: str, task_id: int, user_id: int
) -> Comment:
    comment = Comment(content=content, task_id=task_id, user_id=user_id)
    db.add(comment)
    db.flush()
    return comment


class CommentRepository(BaseRepository[Comment, None, None]):

    def __init__(self):
        super().__init__(Comment)

    def get_by_task(
        self, db: Session, task_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        return (
            db.query(Comment)
            .filter(Comment.task_id == task_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


def count_by_task(db: Session, task_id: int) -> int:
    return db.query(Attachment).filter(Attachment.task_id == task_id).count()

def create_attachment(
        db: Session, *, filename: str, file_path: str, task_id: int
) -> Attachment:
    attachment = Attachment(filename=filename, file_path=file_path, task_id=task_id)
    db.add(attachment)
    db.flush()
    return attachment


def get_by_task(db: Session, task_id: int) -> List[Attachment]:
    return db.query(Attachment).filter(Attachment.task_id == task_id).all()


class AttachmentRepository(BaseRepository[Attachment, None, None]):

    def __init__(self):
        super().__init__(Attachment)


notification_repository = NotificationRepository()
comment_repository = CommentRepository()
attachment_repository = AttachmentRepository()
