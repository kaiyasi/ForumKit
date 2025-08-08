from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class IGAccountBase(BaseModel):
    school_id: int
    ig_username: str = Field(..., min_length=1, max_length=100)
    access_token: str
    token_expires_at: datetime
    is_active: bool = True

class IGAccountCreate(IGAccountBase):
    pass

class IGAccountUpdate(BaseModel):
    ig_username: Optional[str] = Field(None, min_length=1, max_length=100)
    access_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class IGAccountRead(IGAccountBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class IGPostPublish(BaseModel):
    auto_publish: bool = False  # 是否自動發布
    caption: Optional[str] = None  # 自訂說明文字 