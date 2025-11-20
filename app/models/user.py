"""User SQLAlchemy model definition.

Defines the User ORM model and role enumeration for database mapping.
"""

from typing import Optional
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy import Boolean
from app.models import Base
import enum
from datetime import datetime

class UserRole(enum.Enum):
    """Enumeration of user roles."""
    user = 'user'
    publisher = 'publisher'
    admin = 'admin'

class User(Base):
    """User ORM model for the users table."""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(128))
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
