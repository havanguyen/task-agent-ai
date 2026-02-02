from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.extras import Notification as NotificationModel
from app.models.user import User
from app.schemas.notification import Notification
from app.schemas.api_response import ApiResponse

router = APIRouter()


@router.get("/")
def read_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
):
    notifications = (
        db.query(NotificationModel)
        .filter(NotificationModel.user_id == current_user.id)
        .order_by(NotificationModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return ApiResponse.success_response(
        data=notifications, message="Notifications retrieved successfully"
    )


@router.put("/{notification_id}/read")
def mark_notification_read(
    *,
    db: Session = Depends(deps.get_db),
    notification_id: int,
    current_user: User = Depends(deps.get_current_active_user),
):
    notification = (
        db.query(NotificationModel)
        .filter(
            NotificationModel.id == notification_id,
            NotificationModel.user_id == current_user.id,
        )
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return ApiResponse.success_response(
        data=notification, message="Notification marked as read"
    )
