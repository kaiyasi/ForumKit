from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base_class import Base

class GlobalReviewAction(str, PyEnum):
    vote = "vote"  # 投票
    override = "override"  # 管理員覆蓋
    dev_override = "dev_override"  # 開發者覆蓋
    appeal = "appeal"  # 申訴
    appeal_approve = "appeal_approve"  # 申訴通過
    appeal_reject = "appeal_reject"  # 申訴拒絕

class GlobalReviewLog(Base):
    __tablename__ = "global_review_logs"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(Enum(GlobalReviewAction), nullable=False)
    vote = Column(Boolean, nullable=True)  # True 表示贊成，False 表示反對，None 表示不表意
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 關聯
    post = relationship("Post", back_populates="global_review_logs")
    user = relationship("User", back_populates="global_review_logs") 