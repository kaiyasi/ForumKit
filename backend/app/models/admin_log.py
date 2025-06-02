from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)  # 操作類型
    target_type = Column(String, nullable=False)  # 操作對象類型
    target_id = Column(Integer, nullable=True)  # 操作對象ID
    details = Column(JSON, nullable=True)  # 詳細資訊
    ip_address = Column(String, nullable=True)  # IP位址
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 關聯
    admin = relationship("User", back_populates="admin_logs") 