from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base_class import Base

class ReviewAction(str, PyEnum):
    approve = "approve"
    reject = "reject"
    delete = "delete"
    override = "override"
    dev_override = "dev_override"  # 開發者覆蓋操作
    reset = "reset"  # 重置狀態

class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(Enum(ReviewAction), nullable=False)
    override_action = Column(Enum(ReviewAction), nullable=True)  # 用於記錄覆蓋操作時的原始動作
    reason = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 關聯
    post = relationship("Post", back_populates="review_logs")
    reviewer = relationship("User", back_populates="review_logs") 