from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TimestampModel(BaseModel):
    created_at: datetime
    updated_at: datetime

class IDModel(BaseModel):
    id: int

class BaseDBModel(TimestampModel, IDModel):
    class Config:
        from_attributes = True 
