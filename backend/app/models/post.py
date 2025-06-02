from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class PostStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    deleted = "deleted"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    is_anonymous = Column(Boolean, nullable=False, default=True)
    
    # 作者資訊（匿名時為 null）
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author = relationship("User", back_populates="posts")
    
    # 學校關聯
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    school = relationship("School", back_populates="posts")
    
    # 狀態與審核資訊
    status = Column(Enum(PostStatus), nullable=False, default=PostStatus.pending)
    is_sensitive = Column(Boolean, nullable=False, default=False)
    sensitive_reason = Column(String, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_comment = Column(String, nullable=True)
    
    # 時間戳記
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # 統計資訊
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    
    # 關聯
    comments = relationship("Comment", back_populates="post")
    review_logs = relationship("ReviewLog", back_populates="post") 