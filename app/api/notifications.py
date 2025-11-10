"""
Notification API routes for sending, listing, and marking notifications.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate
from app.crud.notification import create_notification, get_notification, get_notifications_by_user, update_notification
from app.core.database import get_db
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.post("/send", response_model=NotificationRead)
def send_notification(notification: NotificationCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Send a notification to a user.
    - Only admin can send notifications.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can send notifications")
    created = create_notification(db, notification)
    return NotificationRead.from_orm(created)

@router.get("/user/{user_id}", response_model=List[NotificationRead])
def list_notifications_by_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    List all notifications for a user.
    - Only the user himself or admin can view.
    """
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="No permission to view notifications")
    notifications = get_notifications_by_user(db, user_id)
    return [NotificationRead.from_orm(n) for n in notifications]

@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Mark a notification as read.
    """
    notification = get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="No permission to update notification")
    updated = update_notification(db, notification_id, NotificationUpdate(is_read=True))
    return NotificationRead.from_orm(updated)
