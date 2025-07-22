from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class DiscussionTagBase(BaseModel):
    name: str
    color: str

class DiscussionTagCreate(DiscussionTagBase):
    pass

class DiscussionTagRead(DiscussionTagBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class InternalDiscussionBase(BaseModel):
    school_id: int
    title: str
    content: str
    parent_id: Optional[int] = None
    is_pinned: bool = False
    is_closed: bool = False
    tag_ids: Optional[List[int]] = None

class InternalDiscussionCreate(InternalDiscussionBase):
    pass

class InternalDiscussionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_closed: Optional[bool] = None
    tag_ids: Optional[List[int]] = None

class InternalDiscussionRead(InternalDiscussionBase):
    id: int
    author_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[DiscussionTagRead] = []
    reply_count: int = 0

    class Config:
        orm_mode = True

class InternalDiscussionQuery(BaseModel):
    skip: int = 0
    limit: int = 20
    school_id: Optional[int] = None
    author_id: Optional[int] = None
    parent_id: Optional[int] = None
    is_pinned: Optional[bool] = None
    is_closed: Optional[bool] = None
    tag_ids: Optional[List[int]] = None
    search: Optional[str] = None 
