"""
TaskAssignment API routes for accepting, submitting, and managing assignments.
All endpoints use OpenAPI English doc comments.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.assignment import AssignmentCreate, AssignmentRead, AssignmentUpdate
from app.crud.assignment import create_assignment, get_assignment, get_assignments_by_user, update_assignment
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/assignment", tags=["assignment"])

@router.post("/accept", response_model=AssignmentRead)
def accept_task(assignment: AssignmentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Accept a task and create an assignment.
    - Any authenticated user can accept a task.
    """
    created = create_assignment(db, assignment, user_id=current_user.id)
    return AssignmentRead.from_orm(created)

@router.get("/{assignment_id}", response_model=AssignmentRead)
def get_assignment_detail(assignment_id: int, db: Session = Depends(get_db)):
    """
    Get assignment detail by ID.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return AssignmentRead.from_orm(assignment)

@router.get("/user/{user_id}", response_model=list[AssignmentRead])
def list_assignments_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    List all assignments for a user.
    """
    assignments = get_assignments_by_user(db, user_id)
    return [AssignmentRead.from_orm(a) for a in assignments]

@router.put("/{assignment_id}", response_model=AssignmentRead)
def update_assignment_detail(assignment_id: int, assignment_update: AssignmentUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Update assignment info (submit content, status, review time).
    - Only assignment owner or admin can update.
    """
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="No permission to update this assignment")
    updated = update_assignment(db, assignment_id, assignment_update)
    return AssignmentRead.from_orm(updated)
