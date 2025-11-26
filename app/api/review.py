"""
Review API routes for review, appeal, and arbitration.
All endpoints use OpenAPI English doc comments.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, ApiResponse
from typing import List, Optional
from app.models.review import  ReviewType, ReviewResult
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.task import Task, TaskStatus
from app.crud.assignment import get_assignment, update_assignment
from app.crud.task import update_task
from app.crud.review import create_review, get_review, get_reviews_by_assignment, update_review, list_reviews, get_pending_review
from app.crud.notification import create_notification
from app.schemas.assignment import AssignmentUpdate
from app.schemas.task import TaskUpdate
from app.schemas.notification import NotificationCreate
from datetime import datetime

router = APIRouter(prefix="/api/review", tags=["review"])


def admin_only(user = Depends(get_current_user)):
    """Verify admin privileges."""
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

def apply_review_action(
    db: Session,
    assignment: TaskAssignment,
    task: Task,
    review_type: ReviewType,
    new_result: ReviewResult,
    comment: Optional[str],
    old_result: ReviewResult = ReviewResult.pending
):
    """
    Apply business logic for review decisions (state transitions, rewards, notifications).
    """
    notification_content = ""

    # === 接取申请审核 (acceptance_review) ===
    if review_type == ReviewType.acceptance_review:
        if new_result == ReviewResult.approved:
            update_assignment(db, assignment.id, AssignmentUpdate(
                status=AssignmentStatus.task_receive,
                review_time=datetime.utcnow()
            ))

            if task.status == TaskStatus.open:
                update_task(db, task.id, TaskUpdate(status=TaskStatus.in_progress))


            notification_content = f"您接取任务《{task.title}》的申请已通过，可以开始做任务了！"
        
        elif new_result == ReviewResult.rejected:
            update_assignment(db, assignment.id, AssignmentUpdate(
                status=AssignmentStatus.task_receivement_rejected,
                review_time=datetime.utcnow()
            ))

            reason = f"，原因：{comment}" if comment else ""
            notification_content = f"您接取任务《{task.title}》的申请被拒绝{reason}"

    # === 作业提交审核 (submission_review) ===
    elif review_type == ReviewType.submission_review:
        if new_result == ReviewResult.approved:
            update_assignment(db, assignment.id, AssignmentUpdate(
                status=AssignmentStatus.task_completed,
                review_time=datetime.utcnow()
            ))
            update_task(db, task.id, TaskUpdate(status=TaskStatus.completed))
            notification_content = f"恭喜！您提交的任务《{task.title}》作业已通过审核，奖励发放中..."
        
        elif new_result == ReviewResult.rejected:
            update_assignment(db, assignment.id, AssignmentUpdate(
                status=AssignmentStatus.task_reject,
                review_time=datetime.utcnow()
            ))

            # 管理员只会将任务给一个人，因此作业审核拒绝后任务应回到 in_progress
            if task.status == TaskStatus.completed:
                update_task(db, task.id, TaskUpdate(status=TaskStatus.in_progress))

            reason = f"，原因：{comment}" if comment else ""
            notification_content = f"您提交的任务《{task.title}》作业未通过审核{reason}，可以申诉"
    if notification_content:
        create_notification(db, NotificationCreate(
            user_id=assignment.user_id,
            content=notification_content,
        ))

@router.post("/submit", response_model=ApiResponse[ReviewRead])
def submit_review(review: ReviewCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Submit a review for a task assignment.
    - Supports three review types: acceptance_review, submission_review, appeal_review
    - Admin only for acceptance_review and submission_review
    - Assignment owner only for appeal_review
    
    Business Logic:
    - acceptance_review (approved): assignment -> task_receive, task -> in_progress
    - acceptance_review (rejected): assignment -> task_receivement_rejected
    - submission_review (approved): assignment -> task_completed, task -> completed, create reward
    - submission_review (rejected): assignment -> task_reject, check if task should reopen
    - appeal_review: assignment -> appealing
    """
    # ==== 通用：加载 assignment & task（除 appeal 权限检查外也需要） ====
    assignment = get_assignment(db, review.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    task = db.query(Task).filter(Task.id == assignment.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Associated task not found")

    # 权限检查
    if review.review_type in [ReviewType.acceptance_review, ReviewType.submission_review,ReviewType.appeal_review]:
        if current_user.role.value != "admin":
            raise HTTPException(status_code=403, detail="Only admin can review acceptance and submission")
    else:
        raise HTTPException(status_code=400, detail="Invalid review type")

    # Validate preconditions
    validate_review_preconditions(
        review_type=review.review_type,
        review_result=review.review_result,
        assignment=assignment
    )

    # Apply Business Logic
    apply_review_action(
        db=db,
        assignment=assignment,
        task=task,
        review_type=review.review_type,
        new_result=review.review_result,
        comment=review.review_comment,
        old_result=ReviewResult.pending # New review implies previous state was pending/none
    )

    # 查找是否存在待审核记录（由系统自动创建或用户申诉创建）
    pending_review = get_pending_review(db, assignment.id, review.review_type)

    if pending_review:
        # 更新现有的待审核记录
        update_kwargs = {
            "review_result": review.review_result,
            "reviewer_id": current_user.id,
            "review_time": datetime.utcnow()
        }
        
        # 对于申诉，保留用户的申诉理由；对于其他类型，更新审核意见
        if review.review_type != ReviewType.appeal_review:
            update_kwargs["review_comment"] = review.review_comment
            
        final_review = update_review(db, pending_review.id, ReviewUpdate(**update_kwargs))
    else:
        # 如果没有待审核记录（异常情况或历史数据），创建新记录
        final_review = create_review(db, review, reviewer_id=current_user.id)
   #不确定需不需要创建review
    #created = create_review(db, review, reviewer_id=current_user.id)

    message_map = {
        ReviewType.acceptance_review: "接取审核成功",
        ReviewType.submission_review: "作业审核成功",
        ReviewType.appeal_review: "申诉审核成功",
    }
    message = message_map.get(review.review_type, "审核成功")

    return success_response(data=ReviewRead.from_orm(final_review), message=message)


@router.get("/list", response_model=ApiResponse[List[ReviewRead]])
def list_reviews_api(
    skip: int = 0,
    limit: int = 20,
    review_type: Optional[ReviewType] = None,
    review_result: Optional[ReviewResult] = None,
    assignment_id: Optional[int] = None,
    task_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List reviews with pagination and filters (admin only).

    Supports filtering by review_type, review_result, assignment_id, task_id,
    and review_time range (start_time, end_time).
    """
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can list reviews")

    reviews = list_reviews(
        db=db,
        skip=skip,
        limit=limit,
        review_type=review_type,
        review_result=review_result,
        assignment_id=assignment_id,
        task_id=task_id,
        start_time=start_time,
        end_time=end_time,
    )
    return success_response(data=[ReviewRead.from_orm(r) for r in reviews], message="获取成功")

@router.get("/{review_id}", response_model=ApiResponse[ReviewRead])
def get_review_detail(review_id: int, db: Session = Depends(get_db)):
    """
    Get review detail by ID.
    """
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return success_response(data=ReviewRead.from_orm(review), message="获取成功")

@router.get("/assignment/{assignment_id}", response_model=ApiResponse[List[ReviewRead]])
def list_reviews_by_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """
    List all reviews for a specific assignment.
    """
    reviews = get_reviews_by_assignment(db, assignment_id)
    return success_response(
        data=[ReviewRead.from_orm(r) for r in reviews],
        message="获取成功"
    )

@router.post("/{review_id}", response_model=ApiResponse[ReviewRead])
def update_review_detail(review_id: int, review_update: ReviewUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Update review and apply business logic (acceptance/submission on pending reviews)."""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update reviews")
    db_review = get_review(db, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    assignment = get_assignment(db, db_review.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Associated assignment not found")
    task = db.query(Task).filter(Task.id == assignment.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Associated task not found")

    new_result = review_update.review_result or db_review.review_result
    new_comment = review_update.review_comment if review_update.review_comment is not None else db_review.review_comment

    if db_review.review_type not in [ReviewType.acceptance_review, ReviewType.submission_review, ReviewType.appeal_review]:
        raise HTTPException(status_code=400, detail="Invalid review type")

    # Validate preconditions
    validate_review_preconditions(
        review_type=db_review.review_type,
        review_result=new_result,
        assignment=assignment,
        old_review_result=db_review.review_result
    )

    # Apply Business Logic
    apply_review_action(
        db=db,
        assignment=assignment,
        task=task,
        review_type=db_review.review_type,
        new_result=new_result,
        comment=new_comment,
        old_result=db_review.review_result
    )

    # 最后更新 Review 自身（使用瘦 CRUD）
    updated_review = update_review(db, db_review.id, ReviewUpdate(
        review_result=new_result,
        review_comment=new_comment,
        review_time=datetime.utcnow()
    ))


    return success_response(data=ReviewRead.from_orm(updated_review), message="审核更新成功")

def validate_review_preconditions(
    review_type: ReviewType,
    review_result: ReviewResult,
    assignment: TaskAssignment,
    old_review_result: ReviewResult = ReviewResult.pending
):
    """
    Validate preconditions for review actions.
    """
    # === 接取申请审核 (acceptance_review) ===
    if review_type == ReviewType.acceptance_review:
        if old_review_result == ReviewResult.pending and assignment.status != AssignmentStatus.task_pending:
            raise HTTPException(status_code=400, detail="Only task_pending assignments can be reviewed for acceptance")
        if assignment.submit_content:
            raise HTTPException(status_code=400, detail="This assignment has submission content, cannot review as acceptance")
        
        if review_result not in [ReviewResult.approved, ReviewResult.rejected]:
             raise HTTPException(status_code=400, detail="Invalid review_result for acceptance review")

    # === 作业提交审核 (submission_review) ===
    elif review_type == ReviewType.submission_review:
        if old_review_result == ReviewResult.pending and assignment.status != AssignmentStatus.assignment_submission_pending:
            raise HTTPException(status_code=400, detail="Only assignment_submission_pending assignments can be reviewed for submission")
        if not assignment.submit_content:
            raise HTTPException(status_code=400, detail="This assignment has no submission content, cannot review as submission")
        
        if review_result not in [ReviewResult.approved, ReviewResult.rejected]:
             raise HTTPException(status_code=400, detail="Invalid review_result for submission review")

    # === 申诉审核 (appeal_review) ===
    elif review_type == ReviewType.appeal_review:
        if old_review_result == ReviewResult.pending and assignment.status != AssignmentStatus.appealing:
            raise HTTPException(status_code=400, detail="Assignment is not in appealing status")