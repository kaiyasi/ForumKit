from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.admin_log import AdminLogQuery
from app.models.user import User, UserRole
from app.services.admin import admin_service
from app.schemas.user import User as UserSchema, RoleAssignment, UserQuery
from app.services.user import user_service
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_stats(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user_with_role([UserRole.ADMIN, UserRole.REVIEWER]))
):
    """
    獲取儀表板統計資料
    """
    return await admin_service.get_dashboard_stats(
        db=db,
        user=current_user
    )

@router.get("/logs", response_model=List[Dict[str, Any]])
async def get_admin_logs(
    *,
    db: Session = Depends(deps.get_db),
    query: AdminLogQuery = Depends(),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    獲取管理日誌（僅限管理員）
    """
    return await admin_service.get_admin_logs(
        db=db,
        query=query,
        user=current_user
    )

@router.get("/me", response_model=Dict[str, Any])
async def get_admin_info(
    *,
    current_user: User = Depends(deps.get_current_active_user_with_role([UserRole.ADMIN, UserRole.REVIEWER]))
):
    """
    獲取當前管理員資訊
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "school_id": current_user.school_id,
        "permissions": {
            "can_manage_users": current_user.role == UserRole.ADMIN,
            "can_manage_schools": current_user.role == UserRole.ADMIN,
            "can_manage_posts": True,
            "can_view_logs": current_user.role == UserRole.ADMIN,
            "can_manage_features": current_user.role == UserRole.ADMIN
        }
    }

@router.post("/assign-role", response_model=UserSchema)
async def assign_role(
    *,
    db: Session = Depends(deps.get_db),
    role_assignment: RoleAssignment,
    current_user: UserModel = Depends(deps.get_current_user)
) -> dict:
    """
    指派用戶角色（僅限管理員）
    """
    return await user_service.assign_role(
        db=db,
        role_assignment=role_assignment,
        admin=current_user
    )

@router.get("/users", response_model=List[UserSchema])
async def get_users(
    *,
    db: Session = Depends(deps.get_db),
    query: UserQuery = Depends(),
    current_user: UserModel = Depends(deps.get_current_user)
) -> List[dict]:
    """
    獲取用戶列表（僅限管理員）
    """
    return await user_service.get_users(
        db=db,
        query=query,
        admin=current_user
    ) 