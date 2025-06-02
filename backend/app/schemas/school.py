from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# 共享屬性
class SchoolBase(BaseModel):
    name: str
    slug: str
    ig_enabled: bool = False
    dc_enabled: bool = False

# 創建時需要的屬性
class SchoolCreate(SchoolBase):
    pass

# 更新時可選的屬性
class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    ig_enabled: Optional[bool] = None
    dc_enabled: Optional[bool] = None

# 資料庫中的屬性
class SchoolInDBBase(SchoolBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 返回給 API 的屬性
class School(SchoolInDBBase):
    pass 