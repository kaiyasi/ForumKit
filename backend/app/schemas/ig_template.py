from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class IGTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_content: str
    is_active: bool = True

class IGTemplateCreate(IGTemplateBase):
    pass

class IGTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_content: Optional[str] = None
    is_active: Optional[bool] = None

class IGTemplateRead(IGTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
