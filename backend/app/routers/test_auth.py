from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User

router = APIRouter()

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    獲取當前用戶資訊
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "school_id": current_user.school_id
    }

@router.get("/admin")
async def admin_panel(current_user: User = Depends(require_role("admin"))):
    """
    管理員面板（需要 admin 權限）
    """
    return {
        "message": "歡迎來到管理員面板",
        "user": {
            "id": current_user.id,
            "email": current_user.email
        }
    }

@router.get("/moderator")
async def moderator_panel(current_user: User = Depends(require_role("moderator"))):
    """
    版主面板（需要 moderator 權限）
    """
    return {
        "message": "歡迎來到版主面板",
        "user": {
            "id": current_user.id,
            "email": current_user.email
        }
    } 
