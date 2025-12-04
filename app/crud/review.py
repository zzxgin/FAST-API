"""Thin CRUD helpers for Review.

This module intentionally keeps only simple data operations on the Review model.
All business rules (assignment/task/reward/notifications) are handled at the API layer.
"""
from typing import  Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.models.review import Review, ReviewType, ReviewResult
from app.models.assignment import TaskAssignment
from app.models.task import Task
from app.models.user import User
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
    task_title: Optional[str] = None,
    publisher_id: Optional[int] = None,
    submitter_username: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    """Query reviews with pagination and optional filters.

    Supported filters:
    - review_type
    - review_result
    - assignment_id
    - task_id (via join on TaskAssignment)
    - task_title (via join on TaskAssignment and Task)
    - publisher_id (via join on TaskAssignment and Task)
    - submitter_username (via join on TaskAssignment and User)
    - review_time between start_time and end_time
    """
    query = db.query(Review).options(joinedload(Review.assignment).joinedload("task"))

    if review_type is not None:
        query = query.filter(Review.review_type == review_type)
    if review_result is not None:
        query = query.filter(Review.review_result == review_result)
    if assignment_id is not None:
        query = query.filter(Review.assignment_id == assignment_id)
    
    if task_id is not None or task_title is not None or publisher_id is not None or submitter_username is not None:

        query = query.join(TaskAssignment, TaskAssignment.id == Review.assignment_id)
        
        if task_id is not None:
            query = query.filter(TaskAssignment.task_id == task_id)
        
        if submitter_username is not None:
            query = query.join(User, TaskAssignment.user_id == User.id)
            query = query.filter(User.username.ilike(f"%{submitter_username}%"))

        if task_title is not None or publisher_id is not None:
            query = query.join(Task, TaskAssignment.task_id == Task.id)
            if task_title is not None:
                query = query.filter(Task.title.ilike(f"%{task_title}%"))
            if publisher_id is not None:
                query = query.filter(Task.publisher_id == publisher_id)

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

def reject_other_pending_reviews(db: Session, task_id: int, accepted_assignment_id: int):
    """Reject all other pending acceptance reviews for a task once one is accepted."""
    db.query(Review).filter(
        Review.review_type == ReviewType.acceptance_review,
        Review.review_result == ReviewResult.pending,
        Review.assignment_id.in_(
            db.query(TaskAssignment.id).filter(
                TaskAssignment.task_id == task_id,
                TaskAssignment.id != accepted_assignment_id
            )
        )
    ).update({
        Review.review_result: ReviewResult.rejected,
        Review.review_comment: "自动拒绝：该任务已被其他申请通过",
        Review.review_time: datetime.utcnow()
    }, synchronize_session=False)
    db.commit()
