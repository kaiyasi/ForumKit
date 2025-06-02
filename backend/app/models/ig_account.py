from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class IGAccount(Base):
    __tablename__ = "ig_accounts"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    ig_username = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    token_expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # 關聯
    school = relationship("School", back_populates="ig_account") 