"""Security utilities for authentication and authorization.

Implements JWT token creation, user retrieval from token, and role-based access control.
"""

from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.crud.user import get_user_by_username
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token.

    Args:
        data: Payload data.
        expires_delta: Expiration timedelta.

    Returns:
        Encoded JWT token as string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Retrieve current user from JWT token.

    Args:
        token: JWT token from request.
        db: SQLAlchemy session.

    Returns:
        User instance.

    Raises:
        HTTPException: If credentials are invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: str):
    """Dependency for role-based access control.

    Args:
        required_role: Role required for access.

    Returns:
        Dependency function for FastAPI.

    Raises:
        HTTPException: If user role is insufficient.
    """
    def role_checker(user = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
