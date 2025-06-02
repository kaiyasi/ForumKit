from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.config import settings
from app.core.security import create_access_token
from app.core.school_mapper import is_valid_edu_email, get_school_id_by_email
from app.db.session import get_db
from app.crud import user as user_crud
from app.schemas.token import Token
from app.schemas.user import UserCreate

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class GoogleToken(BaseModel):
    id_token: str

@router.post("/google", response_model=Token)
async def google_auth(
    id_token_str: str,
    db: Session = Depends(get_db)
):
    """
    使用 Google OAuth 登入
    """
    try:
        # 驗證 Google ID token
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # 檢查是否為教育信箱
        email = idinfo['email']
        if not is_valid_edu_email(email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "AUTH_INVALID_EMAIL",
                    "message": "請使用教育信箱登入"
                }
            )
        
        # 獲取學校 ID
        school_id = get_school_id_by_email(db, email)
        if not school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "AUTH_INVALID_SCHOOL",
                    "message": "不支援的學校信箱"
                }
            )
        
        # 查找或創建用戶
        user = user_crud.get_by_email(db, email=email)
        if not user:
            user_in = UserCreate(
                email=email,
                school_id=school_id,
                role="user",
                is_verified=True
            )
            user = user_crud.create(db, obj_in=user_in)
        
        # 創建訪問令牌
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_INVALID_TOKEN",
                "message": "無效的 Google token"
            }
        )

@router.post("/register", response_model=User)
def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    註冊新用戶
    """
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="此電子郵件已被註冊"
        )
    user = user_crud.create(db, obj_in=user_in)
    return user

@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用戶登入
    """
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    } 