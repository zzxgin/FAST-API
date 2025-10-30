"""
CRUD operations for TaskAssignment model.
"""
from sqlalchemy.orm import Session
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate
from datetime import datetime

def create_assignment(db: Session, assignment: AssignmentCreate, user_id: int):
    db_assignment = TaskAssignment(
        task_id=assignment.task_id,
        user_id=user_id,
        submit_content=assignment.submit_content,
        submit_time=datetime.utcnow(),
        status=AssignmentStatus.pending_review
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_assignment(db: Session, assignment_id: int):
    return db.query(TaskAssignment).filter(TaskAssignment.id == assignment_id).first()

def get_assignments_by_user(db: Session, user_id: int):
    return db.query(TaskAssignment).filter(TaskAssignment.user_id == user_id).all()

def update_assignment(db: Session, assignment_id: int, assignment_update: AssignmentUpdate):
    db_assignment = get_assignment(db, assignment_id)
    if not db_assignment:
        return None
    for field, value in assignment_update.dict(exclude_unset=True).items():
        setattr(db_assignment, field, value)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment
