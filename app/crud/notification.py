"""
CRUD operations for Notification model.
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate
from datetime import datetime
from app.models.assignment import TaskAssignment, AssignmentStatus

def create_notification(db: Session, notification: NotificationCreate):
    try:
        db_notification = Notification(
            user_id=notification.user_id,
            content=notification.content,
            created_at=datetime.utcnow()
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except Exception:
        db.rollback()
        raise

def get_notification(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_notifications_by_user(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def update_notification(db: Session, notification_id: int, notification_update: NotificationUpdate):
    try:
        db_notification = db.query(Notification).filter(Notification.id == notification_id).with_for_update().first()
        if not db_notification:
            return None
        for field, value in notification_update.dict(exclude_unset=True).items():
            setattr(db_notification, field, value)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except Exception:
        db.rollback()
        raise

def notify_rejected_applicants(db: Session, task_id: int, accepted_assignment_id: int, task_title: str):
    """Notify other applicants that the task has been assigned to someone else."""
    try:
        rejected_assignments = db.query(TaskAssignment).filter(
            TaskAssignment.task_id == task_id,
            TaskAssignment.id != accepted_assignment_id,
            TaskAssignment.status == AssignmentStatus.task_pending
        ).all()

        notifications = []
        for assignment in rejected_assignments:
            notifications.append(Notification(
                user_id=assignment.user_id,
                content=f"您申请的任务《{task_title}》已被其他人接取，您的申请已被拒绝。",
                created_at=datetime.utcnow()
            ))
        
        if notifications:
            db.add_all(notifications)
            db.commit()
    except Exception:
        db.rollback()
        raise
