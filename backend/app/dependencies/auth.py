from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User
from app.crud import user as user_crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    獲取當前登入用戶
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "AUTH_INVALID_CREDENTIALS",
            "message": "無效的認證憑證"
        }
    )
    
    try:
        payload = verify_token(token)
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = user_crud.get(db, id=user_id)
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "AUTH_INACTIVE_USER",
                "message": "用戶已被停用"
            }
        )
        
    return user

def require_role(role: str):
    """
    檢查用戶角色是否符合要求
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "AUTH_INSUFFICIENT_PERMISSIONS",
                    "message": f"需要 {role} 權限"
                }
            )
        return current_user
    return role_checker

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    檢查當前用戶是否啟用
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用戶未啟用")
    return current_user

def check_permissions(required_roles: list[str]):
    """
    檢查用戶權限
    """
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.is_superuser:
            return current_user
        
        if not any(role in required_roles for role in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="權限不足"
            )
        return current_user
    
    return permission_checker 
