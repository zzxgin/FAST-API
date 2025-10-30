"""
CRUD operations for Review model.
"""
from sqlalchemy.orm import Session
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate

def create_review(db: Session, review: ReviewCreate, reviewer_id: int):
    db_review = Review(
        assignment_id=review.assignment_id,
        reviewer_id=reviewer_id,
        review_result=review.review_result,
        review_comment=review.review_comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
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
