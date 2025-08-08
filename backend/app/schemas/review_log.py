from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.review_log import ReviewAction

class ReviewLogBase(BaseModel):
    post_id: int
    reviewer_id: Optional[int]
    action: ReviewAction
    override_action: Optional[ReviewAction] = None
    reason: str

class ReviewLogCreate(ReviewLogBase):
    pass

class ReviewLogUpdate(BaseModel):
    reason: Optional[str] = None
    action: Optional[ReviewAction] = None
    override_action: Optional[ReviewAction] = None

class ReviewLogRead(ReviewLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True