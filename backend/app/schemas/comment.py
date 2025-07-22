from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from .user import User

# 基礎 Schema
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)
    is_anonymous: bool = True
    post_id: int
    parent_id: Optional[int] = None

# 創建留言
class CommentCreate(CommentBase):
    pass

# 更新留言
class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

# 讀取留言
class CommentRead(CommentBase):
    id: int
    author_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    like_count: int = 0
    reply_count: int = 0
    
    class Config:
        from_attributes = True

# 完整留言資訊（包含作者和回覆）
class CommentDetail(CommentRead):
    author: Optional[User] = None
    replies: List['CommentDetail'] = []
    
    class Config:
        from_attributes = True

# 避免循環引用
CommentDetail.model_rebuild() 
