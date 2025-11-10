"""
CRUD operations for Notification model.
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate
from datetime import datetime

def create_notification(db: Session, notification: NotificationCreate):
    db_notification = Notification(
        user_id=notification.user_id,
        content=notification.content,
        created_at=datetime.utcnow()
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notification(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_notifications_by_user(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def update_notification(db: Session, notification_id: int, notification_update: NotificationUpdate):
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return None
    for field, value in notification_update.dict(exclude_unset=True).items():
        setattr(db_notification, field, value)
    db.commit()
    db.refresh(db_notification)
    return db_notification
