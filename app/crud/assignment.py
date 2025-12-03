"""
CRUD operations for TaskAssignment model.
"""
from sqlalchemy.orm import Session
from app.models.assignment import TaskAssignment, AssignmentStatus
from app.models.task import Task, TaskStatus
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate

def create_assignment(db: Session, assignment: AssignmentCreate, user_id: int):
    """Create a new assignment.
    
    Args:
        db: Database session.
        assignment: Assignment data to create.
        user_id: User ID accepting the task.
    
    Returns:
        Created TaskAssignment object.
    
    Raises:
        ValueError: If task does not exist, task status invalid, or user already accepted.
    """

    task = db.query(Task).filter(Task.id == assignment.task_id).first()
    if not task:
        raise ValueError(f"Task with id {assignment.task_id} not found")
    
    if task.status != TaskStatus.open:
        raise ValueError(f"Task is not available for acceptance (current status: {task.status.value})")
    

    existing_assignment = db.query(TaskAssignment).filter(
        TaskAssignment.task_id == assignment.task_id,
        TaskAssignment.user_id == user_id
    ).first()
    
    if existing_assignment:
        raise ValueError(f"You have already accepted this task (Assignment ID: {existing_assignment.id})")
    

    if task.publisher_id == user_id:
        raise ValueError("You cannot accept your own published task")
    

    db_assignment = TaskAssignment(
        task_id=assignment.task_id,
        user_id=user_id,
        submit_content=assignment.submit_content,
        status=AssignmentStatus.task_pending  
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

def reject_other_pending_assignments(db: Session, task_id: int, accepted_assignment_id: int):
    """Reject all other pending assignments for a task once one is accepted."""
    db.query(TaskAssignment).filter(
        TaskAssignment.task_id == task_id,
        TaskAssignment.id != accepted_assignment_id,
        TaskAssignment.status == AssignmentStatus.task_pending
    ).update(
        {TaskAssignment.status: AssignmentStatus.task_receivement_rejected},
        synchronize_session=False
    )
    db.commit()
