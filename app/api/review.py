"""
Review API routes for review, appeal, and arbitration.
All endpoints use OpenAPI English doc comments.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.crud.review import create_review, get_review, get_reviews_by_assignment, update_review
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/review", tags=["review"])

@router.post("/submit", response_model=ReviewRead)
def submit_review(review: ReviewCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Submit a review for a task assignment.
    - Only reviewer or admin can submit.
    """
    # 权限校验可根据实际业务调整
    created = create_review(db, review, reviewer_id=current_user.id)
    return ReviewRead.from_orm(created)

@router.get("/{review_id}", response_model=ReviewRead)
def get_review_detail(review_id: int, db: Session = Depends(get_db)):
    """
    Get review detail by ID.
    """
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewRead.from_orm(review)

@router.get("/assignment/{assignment_id}", response_model=list[ReviewRead])
def list_reviews_by_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """
    List all reviews for a specific assignment.
    """
    reviews = get_reviews_by_assignment(db, assignment_id)
    return [ReviewRead.from_orm(r) for r in reviews]

@router.put("/{review_id}", response_model=ReviewRead)
def update_review_detail(review_id: int, review_update: ReviewUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Update review result or comment.
    - Only reviewer or admin can update.
    """
    review = update_review(db, review_id, review_update)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewRead.from_orm(review)
