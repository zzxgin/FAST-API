"""TaskAssignment API routes for accepting, submitting, and managing assignments.

All endpoints use OpenAPI English doc comments.
"""

import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, success_response
from app.core.security import get_current_user
from app.crud.assignment import (
    create_assignment,
    get_assignment,
    get_assignments_by_task,
    get_assignments_by_user,
    update_assignment,
)
from app.crud.review import create_review
from app.crud.task import get_task, update_task
from app.crud.user import get_first_admin
from app.models.assignment import AssignmentStatus
from app.models.review import ReviewResult, ReviewType
from app.models.task import TaskStatus
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentRead,
    AssignmentUpdate,
)
from app.schemas.review import ReviewCreate
from app.schemas.task import TaskUpdate

UPLOAD_DIR = "uploads/assignments"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/api/assignment", tags=["assignment"])


@router.post("/accept", response_model=ApiResponse[AssignmentRead])
def accept_task(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Accept a task and create an assignment.

    Args:
        assignment: The assignment creation data.
        db: Database session.
        current_user: The currently authenticated user.

    Returns:
        ApiResponse: The created assignment data wrapped in a response.

    Raises:
        HTTPException: If task not found, already accepted, or not available.
    """
    try:
        created = create_assignment(db, assignment, user_id=current_user.id)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif (
            "already accepted" in error_msg
            or "cannot accept your own" in error_msg
        ):
            raise HTTPException(status_code=409, detail=error_msg)
        elif "not available" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except IntegrityError as e:
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail=f"Task with id {assignment.task_id} not found",
            )
        raise HTTPException(status_code=409, detail="Database integrity error")

    admin_reviewer = get_first_admin(db)
    if admin_reviewer:
        review_in = ReviewCreate(
            assignment_id=created.id,
            review_result=ReviewResult.pending,
            review_type=ReviewType.acceptance_review,
            review_comment="自动生成接取任务待审核记录",
        )
        pending_review = create_review(
            db, review_in, reviewer_id=current_user.id
        )
        return success_response(
            data=AssignmentRead.from_orm(created),
            message=f"接取任务成功，已生成待审核记录 review_id={pending_review.id}",
        )


@router.get("/{assignment_id}", response_model=ApiResponse[AssignmentRead])
def get_assignment_detail(assignment_id: int, db: Session = Depends(get_db)):
    """Get assignment detail by ID.

    Args:
        assignment_id: The ID of the assignment to retrieve.
        db: Database session.

    Returns:
        ApiResponse: The assignment details.

    Raises:
        HTTPException: If assignment is not found.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return success_response(
        data=AssignmentRead.from_orm(assignment), message="获取成功"
    )


@router.get("/user/{user_id}", response_model=ApiResponse[List[AssignmentRead]])
def list_assignments_by_user(user_id: int, db: Session = Depends(get_db)):
    """List all assignments for a user.

    Args:
        user_id: The ID of the user.
        db: Database session.

    Returns:
        ApiResponse: A list of assignments for the user.
    """
    assignments = get_assignments_by_user(db, user_id)
    return success_response(
        data=[AssignmentRead.from_orm(a) for a in assignments],
        message="获取成功",
    )


@router.get("/task/{task_id}", response_model=ApiResponse[List[AssignmentRead]])
def list_assignments_by_task(task_id: int, db: Session = Depends(get_db)):
    """List all assignments for a specific task.

    Args:
        task_id: The ID of the task.
        db: Database session.

    Returns:
        ApiResponse: A list of assignments for the task.
    """
    assignments = get_assignments_by_task(db, task_id)
    return success_response(
        data=[AssignmentRead.from_orm(a) for a in assignments],
        message="获取成功",
    )


@router.post("/submit/{assignment_id}", response_model=ApiResponse[AssignmentRead])
def submit_assignment(
    assignment_id: int,
    submit_content: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Submit an assignment.

    Args:
        assignment_id: The ID of the assignment to submit.
        submit_content: The content of the submission.
        file: The file to upload.
        db: Database session.
        current_user: The currently authenticated user.

    Returns:
        ApiResponse: The updated assignment data.

    Raises:
        HTTPException: If assignment not found or permission denied.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No permission to submit for this assignment",
        )

    file_path = None
    if file:
        file_path = os.path.join(
            UPLOAD_DIR, f"{assignment_id}_{file.filename}"
        )
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        submit_content = file_path

    update = AssignmentUpdate(
        submit_content=submit_content,
        submit_time=datetime.utcnow(),
        status=AssignmentStatus.assignment_submission_pending,
    )
    updated = update_assignment(db, assignment_id, update)

    admin_reviewer = get_first_admin(db)
    if admin_reviewer:
        review_in = ReviewCreate(
            assignment_id=updated.id,
            review_result=ReviewResult.pending,
            review_type=ReviewType.submission_review,
            review_comment="自动生成作业提交待审核记录",
        )
        create_review(db, review_in, reviewer_id=current_user.id)
    return success_response(
        data=AssignmentRead.from_orm(updated), message="提交成功，已生成待审核记录"
    )


@router.patch("/{assignment_id}/progress", response_model=ApiResponse[AssignmentRead])
def update_assignment_progress(
    assignment_id: int,
    update: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update assignment progress/status.

    Args:
        assignment_id: The ID of the assignment to update.
        update: The update data.
        db: Database session.
        current_user: The currently authenticated user.

    Returns:
        ApiResponse: The updated assignment data.

    Raises:
        HTTPException: If assignment not found or permission denied.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No permission to update this assignment"
        )
    updated = update_assignment(db, assignment_id, update)
    return success_response(
        data=AssignmentRead.from_orm(updated), message="更新成功"
    )



@router.post("/appeal/{assignment_id}", response_model=ApiResponse[AssignmentRead])
def appeal_assignment(
    assignment_id: int,
    appeal_reason: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Appeal an assignment result.

    Args:
        assignment_id: The ID of the assignment to appeal.
        appeal_reason: The reason for the appeal.
        db: Database session.
        current_user: The currently authenticated user.

    Returns:
        ApiResponse: The updated assignment data.

    Raises:
        HTTPException: If assignment not found, permission denied, or invalid status.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No permission to appeal this assignment"
        )

    if assignment.status not in [
        AssignmentStatus.task_completed,
        AssignmentStatus.task_reject,
    ]:
        raise HTTPException(
            status_code=400,
            detail="Only completed or rejected assignments can be appealed",
        )

    update = AssignmentUpdate(status=AssignmentStatus.appealing)
    updated = update_assignment(db, assignment_id, update)

    admin_reviewer = get_first_admin(db)
    if admin_reviewer:
        review_in = ReviewCreate(
            assignment_id=updated.id,
            review_result=ReviewResult.pending,
            review_type=ReviewType.appeal_review,
            review_comment=f"用户申诉: {appeal_reason}",
        )
        create_review(db, review_in, reviewer_id=current_user.id)

    return success_response(
        data=AssignmentRead.from_orm(updated),
        message="申诉提交成功，已生成待审核记录",
    )


@router.post("/redo/{assignment_id}", response_model=ApiResponse[AssignmentRead])
def redo_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Redo a rejected assignment.

    Args:
        assignment_id: The ID of the assignment to redo.
        db: Database session.
        current_user: The currently authenticated user.

    Returns:
        ApiResponse: The updated assignment data.

    Raises:
        HTTPException: If assignment not found, permission denied, or invalid
            status.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No permission to redo this assignment"
        )

    if assignment.status != AssignmentStatus.task_reject:
        raise HTTPException(
            status_code=400,
            detail="Only rejected assignments can be redone",
        )

    update = AssignmentUpdate(
        status=AssignmentStatus.task_receive,
        submit_content=None,
        submit_time=None
    )
    updated = update_assignment(db, assignment_id, update)

    task = get_task(db, assignment.task_id)
    if task and task.status != TaskStatus.in_progress:
        update_task(db, task.id, TaskUpdate(status=TaskStatus.in_progress))

    return success_response(
        data=AssignmentRead.from_orm(updated),
        message="任务状态已重置，请重新提交",
    )
