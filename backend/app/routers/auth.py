from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.config import settings
from app.core.security import create_access_token
from app.core.school_mapper import is_valid_edu_email, get_school_id_by_email_d1
from app.db.database import get_db
from app.crud.user_d1 import user_d1
from app.crud.school_d1 import school_d1
from app.schemas.token import Token
from app.schemas.user import UserCreate, User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

class GoogleToken(BaseModel):
    id_token: str

@router.post("/google", response_model=Token)
async def google_auth(
    id_token_str: str,
    db = Depends(get_db)
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
        school_id = await get_school_id_by_email_d1(email)
        if not school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "AUTH_INVALID_SCHOOL",
                    "message": "不支援的學校信箱"
                }
            )
        
        # 查找或創建用戶
        user = await user_d1.get_by_email(email)
        if not user:
            user_in = UserCreate(
                email=email,
                school_id=school_id,
                role="user",
                is_verified=True,
                password="google_oauth"  # Google OAuth 用戶不需要密碼
            )
            user = await user_d1.create(user_in)
        
        # 創建訪問令牌
        access_token = create_access_token(
            data={"sub": str(user["id"])}
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

@router.post("/register")
async def register(*, db = Depends(get_db), user_in: UserCreate) -> Any:
    """
    註冊新用戶
    """
    user = await user_d1.get_by_email(user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="此電子郵件已被註冊"
        )
    user = await user_d1.create(user_in)
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    db = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 兼容令牌端點
    """
    user = await user_d1.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login", response_model=Token)
async def login(
    db = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    用戶登入
    """
    user = await user_d1.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    } 