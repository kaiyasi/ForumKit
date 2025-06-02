from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .user import User
from .school import School
from .comment import Comment
from app.models.post import PostStatus

# 基礎 Post Schema
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    is_anonymous: bool = True
    school_id: int

# 創建 Post 時的 Schema
class PostCreate(PostBase):
    pass

# 更新 Post 時的 Schema
class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    is_anonymous: Optional[bool] = None
    status: Optional[PostStatus] = None
    is_sensitive: Optional[bool] = None
    sensitive_reason: Optional[str] = None

# 審核 Post 時的 Schema
class PostReview(BaseModel):
    status: PostStatus
    review_comment: Optional[str] = Field(None, max_length=500)

# 讀取 Post 時的 Schema
class PostRead(PostBase):
    id: int
    status: PostStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    author_id: Optional[int] = None
    is_sensitive: bool = False
    sensitive_reason: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_comment: Optional[str] = None
    
    class Config:
        from_attributes = True

# 列表用的簡化 Schema
class PostList(BaseModel):
    id: int
    title: str
    is_anonymous: bool
    school_id: int
    status: PostStatus
    created_at: datetime
    view_count: int
    like_count: int
    comment_count: int
    
    class Config:
        from_attributes = True

class PostInDBBase(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Post(PostInDBBase):
    author: Optional[User] = None
    school: School
    comments: List[Comment] = [] 