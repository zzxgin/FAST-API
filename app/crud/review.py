"""Thin CRUD helpers for Review.

This module intentionally keeps only simple data operations on the Review model.
All business rules (assignment/task/reward/notifications) are handled at the API layer.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.review import Review, ReviewType, ReviewResult
from app.schemas.review import ReviewCreate, ReviewUpdate

def create_review(db: Session, review: ReviewCreate, reviewer_id: int):
    """Create a review row only (no business side effects)."""
    db_review = Review(
        assignment_id=review.assignment_id,
        reviewer_id=reviewer_id,
        review_result=review.review_result,
        review_type=review.review_type,
        review_comment=review.review_comment,
        review_time=datetime.utcnow(),
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_review(db: Session, review_id: int):
    return db.query(Review).filter(Review.id == review_id).first()

def get_pending_review(db: Session, assignment_id: int, review_type: ReviewType):
    """Get the pending review for a specific assignment and type."""
    return db.query(Review).filter(
        Review.assignment_id == assignment_id,
        Review.review_type == review_type,
        Review.review_result == ReviewResult.pending
    ).first()

def get_reviews_by_assignment(db: Session, assignment_id: int):
    return db.query(Review).filter(Review.assignment_id == assignment_id).all()


def list_reviews(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    review_type: Optional[ReviewType] = None,
    review_result: Optional[ReviewResult] = None,
    assignment_id: Optional[int] = None,
    task_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """Query reviews with pagination and optional filters.

    Supported filters:
    - review_type
    - review_result
    - assignment_id
    - task_id (via join on TaskAssignment)
    - review_time between start_time and end_time
    """
    query = db.query(Review)

    if review_type is not None:
        query = query.filter(Review.review_type == review_type)
    if review_result is not None:
        query = query.filter(Review.review_result == review_result)
    if assignment_id is not None:
        query = query.filter(Review.assignment_id == assignment_id)
    if task_id is not None:
        from app.models.assignment import TaskAssignment

        query = query.join(TaskAssignment, TaskAssignment.id == Review.assignment_id).filter(
            TaskAssignment.task_id == task_id
        )
    if start_time is not None:
        query = query.filter(Review.review_time >= start_time)
    if end_time is not None:
        query = query.filter(Review.review_time <= end_time)

    query = query.order_by(Review.id.desc()).offset(skip).limit(limit)
    return query.all()

def update_review(db: Session, review_id: int, review_update: ReviewUpdate):
    """Update Review columns only (no business side effects)."""
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    for field, value in review_update.dict(exclude_unset=True).items():
        setattr(db_review, field, value)
    db.commit()
    db.refresh(db_review)
    return db_review
