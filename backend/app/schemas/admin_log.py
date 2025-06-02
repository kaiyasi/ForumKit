from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AdminLogBase(BaseModel):
    action: str
    target_type: str
    target_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None

class AdminLogCreate(AdminLogBase):
    admin_id: int

class AdminLogRead(AdminLogBase):
    id: int
    admin_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class AdminLogQuery(BaseModel):
    skip: int = 0
    limit: int = 100
    action: Optional[str] = None
    target_type: Optional[str] = None
    admin_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None 