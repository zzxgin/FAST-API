"""
Review CRUD operations and business logic.

This module provides functions for creating, updating, and retrieving review records,
including idempotency checks and automatic notification push for assignment review events.

Attributes:
    None
"""
from sqlalchemy.orm import Session
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.crud.assignment import update_assignment, get_assignment
from app.schemas.assignment import AssignmentUpdate
from app.models.assignment import AssignmentStatus
from app.crud.notification import create_notification
from app.schemas.notification import NotificationCreate
from app.models.task import Task
from app.core.notification_templates import NOTIFICATION_TEMPLATES

def create_review(db: Session, review: ReviewCreate, reviewer_id: int):
    """
    Create a review for a task assignment with idempotency and notification push.

    Args:
        db (Session): SQLAlchemy database session.
        review (ReviewCreate): Review creation schema.
        reviewer_id (int): ID of the reviewer (admin or user).

    Returns:
        Review: The created review object, or None if duplicate submission.
    """
    # Idempotency: Only one pending/appealing review per assignment_id
    existing = db.query(Review).filter(
        Review.assignment_id == review.assignment_id,
        Review.review_result.in_(["pending", "appealing"])
    ).first()
    if existing:
        return None
    # Prevent duplicate submission: Same assignment_id + reviewer_id + review_result
    duplicate = db.query(Review).filter(
        Review.assignment_id == review.assignment_id,
        Review.reviewer_id == reviewer_id,
        Review.review_result == review.review_result
    ).first()
    if duplicate:
        return None
    db_review = Review(
        assignment_id=review.assignment_id,
        reviewer_id=reviewer_id,
        review_result=review.review_result,
        review_comment=review.review_comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    # Auto state flow: Update assignment status and review_time, push notification
    assignment = get_assignment(db, review.assignment_id)
    if assignment:
        # Get task title for notification
        task_title = None
        if hasattr(assignment, "task") and assignment.task:
            task_title = assignment.task.title
        else:
            # Fallback: query task if not loaded
            task = db.query(Task).filter(Task.id == assignment.task_id).first()
            if task:
                task_title = task.title
        if review.review_result == "approved":
            update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.approved, review_time=db_review.review_time))
            content = NOTIFICATION_TEMPLATES["review_approved"].format(task_title=task_title or "")
            create_notification(db, NotificationCreate(user_id=assignment.user_id, content=content))
        elif review.review_result == "rejected":
            update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.rejected, review_time=db_review.review_time))
            reason = review.review_comment or ""
            content = NOTIFICATION_TEMPLATES["review_rejected"].format(task_title=task_title or "", reason=reason)
            create_notification(db, NotificationCreate(user_id=assignment.user_id, content=content))
        elif review.review_result == "appealing":
            update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.appealing, review_time=db_review.review_time))
            content = NOTIFICATION_TEMPLATES["appeal_submitted"].format(task_title=task_title or "")
            create_notification(db, NotificationCreate(user_id=assignment.user_id, content=content))
    return db_review

def get_review(db: Session, review_id: int):
    return db.query(Review).filter(Review.id == review_id).first()

def get_reviews_by_assignment(db: Session, assignment_id: int):
    return db.query(Review).filter(Review.assignment_id == assignment_id).all()

def update_review(db: Session, review_id: int, review_update: ReviewUpdate):
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    for field, value in review_update.dict(exclude_unset=True).items():
        setattr(db_review, field, value)
    db.commit()
    db.refresh(db_review)
    return db_review
