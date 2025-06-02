from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    is_anonymous = Column(Boolean, nullable=False, default=True)
    
    # 作者資訊（匿名時為 null）
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author = relationship("User", back_populates="comments")
    
    # 貼文關聯
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    post = relationship("Post", back_populates="comments")
    
    # Thread 結構支援
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    replies = relationship("Comment", backref="parent", remote_side=[id])
    
    # 時間戳記
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # 統計資訊
    like_count = Column(Integer, nullable=False, default=0)
    reply_count = Column(Integer, nullable=False, default=0) 