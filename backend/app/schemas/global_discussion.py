from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class GlobalDiscussionBase(BaseModel):
    title: str
    content: str
    parent_id: Optional[int] = None
    is_pinned: bool = False
    is_closed: bool = False
    post_ids: Optional[List[int]] = None

class GlobalDiscussionCreate(GlobalDiscussionBase):
    pass

class GlobalDiscussionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_closed: Optional[bool] = None
    post_ids: Optional[List[int]] = None

class GlobalDiscussionRead(GlobalDiscussionBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    reply_count: int = 0
    posts: List[dict] = []

    class Config:
        from_attributes = True

class GlobalDiscussionQuery(BaseModel):
    skip: int = 0
    limit: int = 20
    author_id: Optional[int] = None
    parent_id: Optional[int] = None
    is_pinned: Optional[bool] = None
    is_closed: Optional[bool] = None
    post_id: Optional[int] = None
    search: Optional[str] = None 