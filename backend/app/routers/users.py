from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.dependencies.auth import get_current_active_user, check_permissions
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate
from app.crud import user as user_crud

router = APIRouter()

@router.get("/", response_model=UserSchema)
def read_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    獲取當前登入用戶資訊（根路徑）
    """
    return current_user

@router.post("/", response_model=UserSchema)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db)
):
    """
    創建新用戶（註冊）
    """
    # 檢查用戶是否已存在
    existing_user = user_crud.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "USER_ALREADY_EXISTS",
                "message": "此電子郵件已被註冊"
            }
        )
    
    # 創建用戶
    user = user_crud.create(db, obj_in=user_in)
    return user

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