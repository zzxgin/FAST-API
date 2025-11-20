"""
TaskAssignment API routes for accepting, submitting, and managing assignments.
All endpoints use OpenAPI English doc comments.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.assignment import AssignmentCreate, AssignmentRead, AssignmentUpdate
from app.crud.assignment import create_assignment, get_assignment, get_assignments_by_user, update_assignment
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, ApiResponse
from typing import List
import os

UPLOAD_DIR = "uploads/assignments"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/api/assignment", tags=["assignment"])

@router.post("/accept", response_model=ApiResponse[AssignmentRead])
def accept_task(assignment: AssignmentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Accept a task and create an assignment.
    - Any authenticated user can accept a task.
    """
    created = create_assignment(db, assignment, user_id=current_user.id)
    if not created:
        raise HTTPException(status_code=400, detail="任务已被接取或不可用")
    return success_response(data=AssignmentRead.from_orm(created), message="接取任务成功")

@router.get("/{assignment_id}", response_model=ApiResponse[AssignmentRead])
def get_assignment_detail(assignment_id: int, db: Session = Depends(get_db)):
    """
    Get assignment detail by ID.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return success_response(data=AssignmentRead.from_orm(assignment), message="获取成功")

@router.get("/user/{user_id}", response_model=ApiResponse[List[AssignmentRead]])
def list_assignments_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    List all assignments for a user.
    """
    assignments = get_assignments_by_user(db, user_id)
    return success_response(
        data=[AssignmentRead.from_orm(a) for a in assignments],
        message="获取成功"
    )

@router.post("/submit/{assignment_id}", response_model=ApiResponse[AssignmentRead])
def submit_assignment(
    assignment_id: int,
    submit_content: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Submit assignment result (text or file).
    - Only assignment owner can submit.
    """
    from datetime import datetime
    
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to submit for this assignment")
    
    file_path = None
    if file:
        file_path = os.path.join(UPLOAD_DIR, f"{assignment_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        submit_content = file_path
    
    update = AssignmentUpdate(
        submit_content=submit_content,
        submit_time=datetime.utcnow()
    )
    updated = update_assignment(db, assignment_id, update)
    return success_response(data=AssignmentRead.from_orm(updated), message="提交成功")

@router.patch("/{assignment_id}/progress", response_model=ApiResponse[AssignmentRead])
def update_assignment_progress(
    assignment_id: int,
    update: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update assignment progress/status.
    - Only assignment owner can update progress.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to update this assignment")
    updated = update_assignment(db, assignment_id, update)
    return success_response(data=AssignmentRead.from_orm(updated), message="更新成功")
