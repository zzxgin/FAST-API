"""
CRUD operations for Review model.
"""
from sqlalchemy.orm import Session
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate

def create_review(db: Session, review: ReviewCreate, reviewer_id: int):
    # Prevent duplicate review: Only one pending/appealing review per assignment_id
    existing = db.query(Review).filter(
        Review.assignment_id == review.assignment_id,
        Review.review_result.in_("pending", "appealing")
    ).first()
    if existing:
        return None  # Or raise Exception("Duplicate review for this assignment")
    db_review = Review(
        assignment_id=review.assignment_id,
        reviewer_id=reviewer_id,
        review_result=review.review_result,
        review_comment=review.review_comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    # TODO: Auto state flow: Update assignment status here, e.g. after review approved/rejected
    # TODO: Example: if review_result == "approved", then assignment.status = "approved" (assignment logic to be added)
    # TODO: Write assignment.review_time when review is approved/rejected
    # TODO: Add idempotency check to prevent duplicate review/appeal submissions
    # TODO: Integrate notification push for review/assignment result
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
