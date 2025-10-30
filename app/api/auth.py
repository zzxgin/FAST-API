"""
Auth API routes for authentication and authorization.

OneAPI doc:
- All endpoints require JWT authentication via Bearer Token in the header.
- All responses are standard JSON; errors return HTTPException.

Endpoints:
- GET /api/auth/role/{role}  Check if current user has the specified role

Security:
- All endpoints require login.
- Role check endpoint can be used for frontend permission control.

"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/role/{role}", response_model=UserRead)
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
    return UserRead.from_orm(current_user)
