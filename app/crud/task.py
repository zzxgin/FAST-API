"""
CRUD operations for Task model.
"""
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate

def create_task(db: Session, task: TaskCreate, publisher_id: int):
    try:
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
    except Exception:
        db.rollback()
        raise

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 20):
    return db.query(Task).offset(skip).limit(limit).all()

def get_task_list(db: Session, skip: int = 0, limit: int = 20, status: str = None, order_by: str = None):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    if order_by:
        # 处理排序：支持 -field_name 表示降序
        if order_by.startswith('-'):
            # 降序：-created_at -> desc(Task.created_at)
            field_name = order_by[1:]  # 去掉负号
            if hasattr(Task, field_name):
                query = query.order_by(getattr(Task, field_name).desc())
        else:
            # 升序：created_at -> asc(Task.created_at)
            if hasattr(Task, order_by):
                query = query.order_by(getattr(Task, order_by).asc())
    return query.offset(skip).limit(limit).all()

def search_tasks(db: Session, keyword: str, skip: int = 0, limit: int = 20):
    return db.query(Task).filter(Task.title.like(f"%{keyword}%")).offset(skip).limit(limit).all()

def update_task(db: Session, task_id: int, task_update: TaskUpdate):
    try:
        db_task = db.query(Task).filter(Task.id == task_id).with_for_update().first()
        if not db_task:
            return None
        for field, value in task_update.dict(exclude_unset=True).items():
            setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception:
        db.rollback()
        raise

def accept_task(db: Session, task_id: int):
    try:
        db_task = db.query(Task).filter(Task.id == task_id).with_for_update().first()
        if not db_task or db_task.status != TaskStatus.open:
            return None
        db_task.status = TaskStatus.in_progress
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception:
        db.rollback()
        raise
