"""
Auth API routes for authentication and authorization.

"""

from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.user import UserRead
from app.core.response import success_response

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/role/{role}")
def check_role(role: str, current_user = Depends(get_current_user)):
    """
    Check if the current user has the specified role.
    - Header: Authorization: Bearer <token>
    - Path parameter: role (str)
    - Response: UserRead info if permission granted
    - Error: 403 Forbidden
    """
    if current_user.role.value != role:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return success_response(data=UserRead.from_orm(current_user), message="权限验证成功")
