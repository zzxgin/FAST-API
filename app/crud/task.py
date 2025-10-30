"""
CRUD operations for Task model.
"""
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate

def create_task(db: Session, task: TaskCreate, publisher_id: int):
    db_task = Task(
        title=task.title,
        description=task.description,
        reward_amount=task.reward_amount,
        publisher_id=publisher_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Task).offset(skip).limit(limit).all()

def update_task(db: Session, task_id: int, task_update: TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def accept_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task or db_task.status != TaskStatus.open:
        return None
    db_task.status = TaskStatus.in_progress
    db.commit()
    db.refresh(db_task)
    return db_task
