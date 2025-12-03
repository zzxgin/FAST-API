"""Review API routes for review, appeal, and arbitration.

All endpoints use OpenAPI English doc comments.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.response import ApiResponse, success_response
from app.core.security import get_current_user
from app.crud.assignment import (
    get_assignment,
    update_assignment,
    reject_other_pending_assignments,
)
from app.crud.notification import create_notification
from app.crud.review import (
    create_review,
    get_pending_review,
    get_review,
    get_reviews_by_assignment,
    list_reviews,
    update_review,
)
from app.crud.task import update_task
from app.crud.reward import (
    create_reward,
    update_reward,
    get_reward_by_assignment_id,
)
from app.models.assignment import AssignmentStatus, TaskAssignment
from app.models.review import ReviewResult, ReviewType
from app.models.reward import Reward ,  RewardStatus  
from app.models.task import Task, TaskStatus
from app.schemas.reward import RewardCreate, RewardStatus, RewardUpdate
from app.schemas.assignment import AssignmentUpdate
from app.schemas.notification import NotificationCreate
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.schemas.task import TaskUpdate

router = APIRouter(prefix="/api/review", tags=["review"])


def admin_only(user=Depends(get_current_user)):
    """Verify admin privileges.

    Args:
        user: The current user.

    Returns:
        The user if they are an admin.

    Raises:
        HTTPException: If the user is not an admin.
    """
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
    old_result: ReviewResult = ReviewResult.pending,
):
    """Apply business logic for review decisions.

    Handles state transitions, rewards, and notifications.

    Args:
        db: Database session.
        assignment: The assignment being reviewed.
        task: The task associated with the assignment.
        review_type: The type of review.
        new_result: The new review result.
        comment: Review comment.
        old_result: The previous review result.
    """
    notification_content = ""

    if review_type == ReviewType.acceptance_review:
        if new_result == ReviewResult.approved:
            update_assignment(
                db,
                assignment.id,
                AssignmentUpdate(
                    status=AssignmentStatus.task_receive,
                    review_time=datetime.utcnow(),
                ),
            )

            if task.status == TaskStatus.open:
                update_task(
                    db, task.id, TaskUpdate(status=TaskStatus.in_progress)
                )

            # Reject other pending assignments for this task
            reject_other_pending_assignments(db, task.id, assignment.id)
            
            notification_content = (
                f"您接取任务《{task.title}》的申请已通过，可以开始做任务了！"
            )

        elif new_result == ReviewResult.rejected:
            update_assignment(
                db,
                assignment.id,
                AssignmentUpdate(
                    status=AssignmentStatus.task_receivement_rejected,
                    review_time=datetime.utcnow(),
                ),
            )
            update_task(db, task.id, TaskUpdate(status=TaskStatus.open))
            reason = f"，原因：{comment}" if comment else ""
            notification_content = f"您接取任务《{task.title}》的申请被拒绝{reason}"

    elif review_type == ReviewType.submission_review:
        if new_result == ReviewResult.approved:
            update_assignment(
                db,
                assignment.id,
                AssignmentUpdate(
                    status=AssignmentStatus.task_completed,
                    review_time=datetime.utcnow(),
                ),
            )
            update_task(db, task.id, TaskUpdate(status=TaskStatus.completed))
            
            existing_reward = get_reward_by_assignment_id(db, assignment.id)
            if not existing_reward:
                create_reward(
                    db,
                    RewardCreate(
                        assignment_id=assignment.id,
                        amount=task.reward_amount,
                        created_at=datetime.utcnow(),
                        RewardStatus=RewardStatus.pending,
                    ),
                )
            notification_content = (
                f"恭喜！您提交的任务《{task.title}》作业已通过审核，奖励发放中..."
            )

        elif new_result == ReviewResult.rejected:
            update_assignment(
                db,
                assignment.id,
                AssignmentUpdate(
                    status=AssignmentStatus.task_reject,
                    review_time=datetime.utcnow(),
                ),
            )

            if task.status == TaskStatus.completed:
                update_task(
                    db, task.id, TaskUpdate(status=TaskStatus.in_progress)
                )

            reason = f"，原因：{comment}" if comment else ""
            notification_content = (
                f"您提交的任务《{task.title}》作业未通过审核{reason}，可以申诉"
            )

    elif review_type == ReviewType.appeal_review:
        if new_result != old_result:
            if new_result == ReviewResult.approved:
                if task.status == TaskStatus.completed:
                    update_task(
                        db, task.id, TaskUpdate(status=TaskStatus.in_progress)
                    )
                    update_assignment(
                        db,
                        assignment.id,
                        AssignmentUpdate(status=AssignmentStatus.task_receive),
                    )
                    # Reward logic omitted as per original code structure
                    notification_content = (
                        f"您的申诉已通过，任务《{task.title}》已重置，请重新提交。"
                    )

                elif task.status == TaskStatus.in_progress:
                    update_task(
                        db, task.id, TaskUpdate(status=TaskStatus.completed)
                    )
                    update_assignment(
                        db,
                        assignment.id,
                        AssignmentUpdate(
                            status=AssignmentStatus.task_completed
                        ),
                    )
                    # Reward logic omitted as per original code structure
                    notification_content = (
                        f"您的申诉已通过，任务《{task.title}》判定为合格，奖励已发放。"
                    )

            elif new_result == ReviewResult.rejected:
                if old_result == ReviewResult.approved:
                    if task.status == TaskStatus.in_progress:
                        update_task(
                            db,
                            task.id,
                            TaskUpdate(status=TaskStatus.completed),
                        )
                        update_assignment(
                            db,
                            assignment.id,
                            AssignmentUpdate(
                                status=AssignmentStatus.task_completed
                            ),
                        )
                        notification_content = (
                            f"您的申诉被拒绝，任务《{task.title}》维持完成状态。"
                        )

                    elif task.status == TaskStatus.completed:
                        update_task(
                            db,
                            task.id,
                            TaskUpdate(status=TaskStatus.in_progress),
                        )
                        update_assignment(
                            db,
                            assignment.id,
                            AssignmentUpdate(
                                status=AssignmentStatus.task_receive
                            ),
                        )
                        notification_content = (
                            f"您的申诉被拒绝，请继续完善任务《{task.title}》。"
                        )
                else:
                    if task.status == TaskStatus.completed:
                        update_assignment(
                            db,
                            assignment.id,
                            AssignmentUpdate(
                                status=AssignmentStatus.task_completed
                            ),
                        )
                        notification_content = (
                            f"您的申诉被拒绝，任务《{task.title}》维持完成状态。"
                        )
                    elif task.status == TaskStatus.in_progress:
                        update_assignment(
                            db,
                            assignment.id,
                            AssignmentUpdate(
                                status=AssignmentStatus.task_receive
                            ),
                        )
                        notification_content = (
                            f"您的申诉被拒绝，请继续完善任务《{task.title}》。"
                        )
                # === 申诉审核 (appeal_review) ===
    elif review_type == ReviewType.appeal_review:
        # Only toggle state if the decision has changed (e.g. Approved -> Rejected or vice versa)
        # or if it's the first decision (Pending -> Approved/Rejected)
        if new_result != old_result:
            if new_result == ReviewResult.approved:
                if task.status == TaskStatus.completed:
                    # Case: Completed task appeal -> Re-open (User wants to redo?)
                    update_task(db, task.id, TaskUpdate(status=TaskStatus.in_progress))
                    update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.task_receive))
                    reward = get_reward_by_assignment_id(db, assignment.id)
                    if reward:
                        update_reward(db, reward.id, RewardUpdate(status=RewardStatus.pending))
                    notification_content = f"您的申诉已通过，任务《{task.title}》已重置，请重新提交。"
                
                elif task.status == TaskStatus.in_progress:
                    # Case: Rejected task appeal -> Overturn rejection (User did good)
                    update_task(db, task.id, TaskUpdate(status=TaskStatus.completed))
                    update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.task_completed))
                    reward = get_reward_by_assignment_id(db, assignment.id)
                    if reward:
                        update_reward(db, reward.id, RewardUpdate(status=RewardStatus.issued))
                    else:
                        create_reward(db, RewardCreate(
                            assignment_id=assignment.id,
                            amount=task.reward_amount
                        ))
                        new_reward = get_reward_by_assignment_id(db, assignment.id)
                        if new_reward:
                             update_reward(db, new_reward.id, RewardUpdate(status=RewardStatus.issued))
                    notification_content = f"您的申诉已通过，任务《{task.title}》判定为合格，奖励已发放。"

            elif new_result == ReviewResult.rejected:
                # Switching to Rejected (User loses)
                # Only toggle if we are undoing a previous Approval (Approved -> Rejected)
                if old_result == ReviewResult.approved:
                    if task.status == TaskStatus.in_progress:
                        # Was "Redo" (Approved) -> Undo -> Back to Completed
                        update_task(db, task.id, TaskUpdate(status=TaskStatus.completed))
                        update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.task_completed))
                        reward = get_reward_by_assignment_id(db, assignment.id)
                        if reward:
                            update_reward(db, reward.id, RewardUpdate(status=RewardStatus.issued))
                        notification_content = f"您的申诉被拒绝，任务《{task.title}》维持完成状态。"
                    
                    elif task.status == TaskStatus.completed:
                        # Was "Overturn" (Approved) -> Undo -> Back to In_Progress
                        update_task(db, task.id, TaskUpdate(status=TaskStatus.in_progress))
                        update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.task_receive))
                        reward = get_reward_by_assignment_id(db, assignment.id)
                        if reward:
                            update_reward(db, reward.id, RewardUpdate(status=RewardStatus.pending))
                        notification_content = f"您的申诉被拒绝，请继续完善任务《{task.title}》。"
                else:
                    # Pending -> Rejected or Rejected -> Rejected
                    # State stays as is (Original State)
                    if task.status == TaskStatus.completed:
                         update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.task_completed))
                         notification_content = f"您的申诉被拒绝，任务《{task.title}》维持完成状态。"
                    elif task.status == TaskStatus.in_progress:
                         update_assignment(db, assignment.id, AssignmentUpdate(status=AssignmentStatus.task_receive))
                         notification_content = f"您的申诉被拒绝，请继续完善任务《{task.title}》。"

    if notification_content:
        create_notification(
            db,
            NotificationCreate(
                user_id=assignment.user_id,
                content=notification_content,
            ),
        )


@router.post("/submit", response_model=ApiResponse[ReviewRead])
def submit_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Submit a review for a task assignment.

    Supports three review types: acceptance_review, submission_review,
    appeal_review.

    Args:
        review: The review data.
        db: Database session.
        current_user: The currently authenticated user.

    Returns:
        ApiResponse: The created or updated review data.

    Raises:
        HTTPException: If assignment/task not found, permission denied, or
            invalid review type.
    """
    assignment = get_assignment(db, review.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    task = db.query(Task).filter(Task.id == assignment.task_id).first()
    if not task:
        raise HTTPException(
            status_code=404, detail="Associated task not found"
        )

    if review.review_type in [
        ReviewType.acceptance_review,
        ReviewType.submission_review,
        ReviewType.appeal_review,
    ]:
        is_admin = current_user.role.value == "admin"
        is_publisher = (
            current_user.role.value == "publisher"
            and task.publisher_id == current_user.id
        )

        if not (is_admin or is_publisher):
            raise HTTPException(
                status_code=403,
                detail="Permission denied. Only admin or task publisher can review.",
            )
    else:
        raise HTTPException(status_code=400, detail="Invalid review type")

    validate_review_preconditions(
        review_type=review.review_type,
        review_result=review.review_result,
        assignment=assignment,
    )

    apply_review_action(
        db=db,
        assignment=assignment,
        task=task,
        review_type=review.review_type,
        new_result=review.review_result,
        comment=review.review_comment,
        old_result=ReviewResult.pending,
    )

    pending_review = get_pending_review(db, assignment.id, review.review_type)

    if pending_review:
        update_kwargs = {
            "review_result": review.review_result,
            "reviewer_id": current_user.id,
            "review_time": datetime.utcnow(),
        }

        if review.review_type != ReviewType.appeal_review:
            update_kwargs["review_comment"] = review.review_comment

        final_review = update_review(
            db, pending_review.id, ReviewUpdate(**update_kwargs)
        )
    else:
        final_review = create_review(db, review, reviewer_id=current_user.id)

    message_map = {
        ReviewType.acceptance_review: "接取审核成功",
        ReviewType.submission_review: "作业审核成功",
        ReviewType.appeal_review: "申诉审核成功",
    }
    message = message_map.get(review.review_type, "审核成功")

    return success_response(
        data=ReviewRead.from_orm(final_review), message=message
    )


@router.get("/list", response_model=ApiResponse[List[ReviewRead]])
def list_reviews_api(
    skip: int = 0,
    limit: int = 20,
    review_type: Optional[ReviewType] = None,
    review_result: Optional[ReviewResult] = None,
    task_title: Optional[str] = None,
    submitter_username: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List reviews with pagination and filters (admin only).

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        review_type: Filter by review type.
        review_result: Filter by review result.
        task_title: Filter by task title (fuzzy search).
        submitter_username: Filter by submitter username (fuzzy search).
        start_time: Filter by start time.
        end_time: Filter by end time.
        db: Database session.
        current_user: The currently authenticated user.

    Returns:
        ApiResponse: A list of reviews.

    Raises:
        HTTPException: If user is not an admin or publisher.
    """
    is_admin = current_user.role.value == "admin"
    is_publisher = current_user.role.value == "publisher"

    if not (is_admin or is_publisher):
        raise HTTPException(
            status_code=403, detail="Only admin or publisher can list reviews"
        )

    publisher_filter = current_user.id if is_publisher else None

    reviews = list_reviews(
        db=db,
        skip=skip,
        limit=limit,
        review_type=review_type,
        review_result=review_result,
        task_title=task_title,
        submitter_username=submitter_username,
        publisher_id=publisher_filter,
        start_time=start_time,
        end_time=end_time,
    )
    return success_response(
        data=[ReviewRead.from_orm(r) for r in reviews], message="获取成功"
    )


@router.get("/{review_id}", response_model=ApiResponse[ReviewRead])
def get_review_detail(review_id: int, db: Session = Depends(get_db)):
    """Get review detail by ID.

    Args:
        review_id: The ID of the review.
        db: Database session.

    Returns:
        ApiResponse: The review details.

    Raises:
        HTTPException: If review not found.
    """
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return success_response(data=ReviewRead.from_orm(review), message="获取成功")


@router.get(
    "/assignment/{assignment_id}", response_model=ApiResponse[List[ReviewRead]]
)
def list_reviews_by_assignment(
    assignment_id: int, db: Session = Depends(get_db)
):
    """List all reviews for a specific assignment.

    Args:
        assignment_id: The ID of the assignment.
        db: Database session.

    Returns:
        ApiResponse: A list of reviews for the assignment.
    """
    reviews = get_reviews_by_assignment(db, assignment_id)
    return success_response(
        data=[ReviewRead.from_orm(r) for r in reviews], message="获取成功"
    )


@router.post("/{review_id}", response_model=ApiResponse[ReviewRead])
def update_review_detail(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update review and apply business logic.

    Args:
        review_id: The ID of the review to update.
        review_update: The update data.
    Raises:
        HTTPException: If review/assignment/task not found, permission denied,
            or invalid review type.
    """
    db_review = get_review(db, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")

    assignment = get_assignment(db, db_review.assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=404, detail="Associated assignment not found"
        )
    task = db.query(Task).filter(Task.id == assignment.task_id).first()
    if not task:
        raise HTTPException(
            status_code=404, detail="Associated task not found"
        )

    is_admin = current_user.role.value == "admin"
    is_publisher = (
        current_user.role.value == "publisher"
        and task.publisher_id == current_user.id
    )

    if not (is_admin or is_publisher):
        raise HTTPException(
            status_code=403,
            detail="Permission denied. Only admin or task publisher can update reviews",
        )

    new_result = review_update.review_result or db_review.review_result
    if not task:
        raise HTTPException(
            status_code=404, detail="Associated task not found"
        )

    new_result = review_update.review_result or db_review.review_result
    new_comment = (
        review_update.review_comment
        if review_update.review_comment is not None
        else db_review.review_comment
    )

    if db_review.review_type not in [
        ReviewType.acceptance_review,
        ReviewType.submission_review,
        ReviewType.appeal_review,
    ]:
        raise HTTPException(status_code=400, detail="Invalid review type")

    validate_review_preconditions(
        review_type=db_review.review_type,
        review_result=new_result,
        assignment=assignment,
        old_review_result=db_review.review_result,
    )

    apply_review_action(
        db=db,
        assignment=assignment,
        task=task,
        review_type=db_review.review_type,
        new_result=new_result,
        comment=new_comment,
        old_result=db_review.review_result,
    )

    updated_review = update_review(
        db,
        db_review.id,
        ReviewUpdate(
            review_result=new_result,
            review_comment=new_comment,
            review_time=datetime.utcnow(),
        ),
    )

    return success_response(
        data=ReviewRead.from_orm(updated_review), message="审核更新成功"
    )


def validate_review_preconditions(
    review_type: ReviewType,
    review_result: ReviewResult,
    assignment: TaskAssignment,
    old_review_result: ReviewResult = ReviewResult.pending,
):
    """Validate preconditions for review actions.

    Args:
        review_type: The type of review.
        review_result: The result of the review.
        assignment: The assignment being reviewed.
        old_review_result: The previous review result.

    Raises:
        HTTPException: If preconditions are not met.
    """
    if review_type == ReviewType.acceptance_review:
        if (
            old_review_result == ReviewResult.pending
            and assignment.status != AssignmentStatus.task_pending
        ):
            raise HTTPException(
                status_code=400,
                detail="Only task_pending assignments can be reviewed for acceptance",
            )
        if assignment.submit_content:
            raise HTTPException(
                status_code=400,
                detail="This assignment has submission content, cannot review as acceptance",
            )

        if review_result not in [ReviewResult.approved, ReviewResult.rejected]:
            raise HTTPException(
                status_code=400,
                detail="Invalid review_result for acceptance review",
            )

    elif review_type == ReviewType.submission_review:
        if (
            old_review_result == ReviewResult.pending
            and assignment.status
            != AssignmentStatus.assignment_submission_pending
        ):
            raise HTTPException(
                status_code=400,
                detail="Only assignment_submission_pending assignments can be reviewed for submission",
            )
        if not assignment.submit_content:
            raise HTTPException(
                status_code=400,
                detail="This assignment has no submission content, cannot review as submission",
            )

        if review_result not in [ReviewResult.approved, ReviewResult.rejected]:
            raise HTTPException(
                status_code=400,
                detail="Invalid review_result for submission review",
            )

    elif review_type == ReviewType.appeal_review:
        if (
            old_review_result == ReviewResult.pending
            and assignment.status != AssignmentStatus.appealing
        ):
            raise HTTPException(
                status_code=400,
                detail="Assignment is not in appealing status",
            )