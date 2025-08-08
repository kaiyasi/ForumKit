from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.models.user import UserRole

# 共享屬性
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    school_id: Optional[int] = None
    role: Optional[UserRole] = None

# 創建時需要的屬性
class UserCreate(UserBase):
    email: EmailStr
    password: str

# 更新時可選的屬性
class UserUpdate(UserBase):
    password: Optional[str] = None

# 資料庫中的屬性
class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 返回給 API 的屬性
class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class RoleAssignment(BaseModel):
    email: EmailStr
    role: UserRole

class UserQuery(BaseModel):
    skip: int = 0
    limit: int = 20
    school_id: Optional[int] = None
    role: Optional[UserRole] = None
    search: Optional[str] = None 