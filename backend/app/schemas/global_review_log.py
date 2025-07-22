from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.global_review_log import GlobalReviewAction

class GlobalReviewLogBase(BaseModel):
    post_id: int
    user_id: Optional[int]
    action: GlobalReviewAction
    vote: Optional[bool] = None
    reason: Optional[str] = None

class GlobalReviewLogCreate(GlobalReviewLogBase):
    pass

class GlobalReviewLogRead(GlobalReviewLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class GlobalReviewVote(BaseModel):
    vote: bool
    reason: Optional[str] = None

class GlobalReviewQuery(BaseModel):
    skip: int = 0
    limit: int = 100
    action: Optional[GlobalReviewAction] = None
    vote: Optional[bool] = None 
