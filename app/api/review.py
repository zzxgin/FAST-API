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
from app.core.response import success_response

router = APIRouter(prefix="/api/review", tags=["review"])

@router.post("/submit")
def submit_review(review: ReviewCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Submit a review for a task assignment.
    - Only admin can submit.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can submit reviews")
    created = create_review(db, review, reviewer_id=current_user.id)
    return success_response(data=ReviewRead.from_orm(created), message="审核提交成功")

@router.get("/{review_id}")
def get_review_detail(review_id: int, db: Session = Depends(get_db)):
    """
    Get review detail by ID.
    """
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return success_response(data=ReviewRead.from_orm(review), message="获取成功")

@router.get("/assignment/{assignment_id}")
def list_reviews_by_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """
    List all reviews for a specific assignment.
    """
    reviews = get_reviews_by_assignment(db, assignment_id)
    return success_response(
        data=[ReviewRead.from_orm(r) for r in reviews],
        message="获取成功"
    )

@router.put("/{review_id}")
def update_review_detail(review_id: int, review_update: ReviewUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Update review result or comment.
    - Only admin can update.
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update reviews")
    review = update_review(db, review_id, review_update)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return success_response(data=ReviewRead.from_orm(review), message="更新成功")

@router.post("/appeal/{assignment_id}")
def appeal_assignment(assignment_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Submit an appeal for a task assignment.
    - Only the assignment owner can appeal.
    - Assignment status will be set to 'appealing'.
    """
    # Assignment owner check and assignment state flow logic
    from app.crud.assignment import get_assignment, update_assignment
    from app.models.assignment import AssignmentStatus
    from app.schemas.assignment import AssignmentUpdate
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only assignment owner can appeal")
    # State flow: Only approved/rejected assignments can be appealed
    if assignment.status not in [AssignmentStatus.approved, AssignmentStatus.rejected]:
        raise HTTPException(status_code=400, detail="Assignment not eligible for appeal")
    # Update assignment status to appealing
    update_assignment(db, assignment_id, AssignmentUpdate(status=AssignmentStatus.appealing))
    # TODO: After appeal, support admin to perform second review and state flow
    # TODO: Add idempotency check to prevent duplicate appeal submissions
    # TODO: Integrate notification push for appeal result
    review_data = ReviewCreate(assignment_id=assignment_id, review_result="appealing", review_comment="Appeal submitted")
    created = create_review(db, review_data, reviewer_id=current_user.id)
    if not created:
        raise HTTPException(status_code=400, detail="Duplicate or invalid appeal")
    return success_response(data=ReviewRead.from_orm(created), message="申诉提交成功")
