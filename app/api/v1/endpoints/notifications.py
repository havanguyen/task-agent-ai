from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.extras import Notification
from app.models.user import User
from pydantic import BaseModel


class NotificationSchema(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool

    model_config = {"from_attributes": True}


router = APIRouter()


@router.get("/", response_model=List[NotificationSchema])
def read_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's notifications.
    """
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return notifications


@router.put("/{notification_id}/read", response_model=NotificationSchema)
def mark_notification_read(
    *,
    db: Session = Depends(deps.get_db),
    notification_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark notification as read.
    """
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id, Notification.user_id == current_user.id
        )
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
