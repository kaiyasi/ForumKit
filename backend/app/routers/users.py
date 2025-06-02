from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.auth import get_current_active_user, check_permissions
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    獲取當前登入用戶資訊
    """
    return current_user

@router.get("/admin-only")
def admin_only(
    current_user: User = Depends(check_permissions(["admin"]))
):
    """
    僅管理員可訪問的端點
    """
    return {"message": "您有管理員權限"}

@router.get("/reviewer-only")
def reviewer_only(
    current_user: User = Depends(check_permissions(["reviewer"]))
):
    """
    僅審核員可訪問的端點
    """
    return {"message": "您有審核員權限"} 