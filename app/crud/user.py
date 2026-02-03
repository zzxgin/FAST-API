"""CRUD operations for User model.

Provides functions for user creation, authentication, and retrieval.
"""

from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead, UserLogin
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    """Retrieve a user by username.

    Args:
        db: SQLAlchemy session.
        username: Username to search.

    Returns:
        User instance or None.
    """
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    """Create a new user with hashed password.

    Args:
        db: SQLAlchemy session.
        user: UserCreate schema.

    Returns:
        User instance.
    """
    try:
        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            username=user.username,
            password_hash=hashed_password,
            email=user.email,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user credentials.

    Args:
        db: SQLAlchemy session.
        username: Username.
        password: Plain password.

    Returns:
        User instance if authenticated, else None.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not pwd_context.verify(password, user.password_hash):
        return None
    return user

def get_first_admin(db: Session):
    """Retrieve the first admin user.

    Args:
        db: SQLAlchemy session.

    Returns:
        User instance or None.
    """
    return db.query(User).filter(User.role == UserRole.admin).order_by(User.id.asc()).first()
