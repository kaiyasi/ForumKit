from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class DiscordSettings(Base):
    __tablename__ = "discord_settings"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    post_webhook_url = Column(String, nullable=True)  # 貼文推播 webhook
    report_webhook_url = Column(String, nullable=True)  # 檢舉通知 webhook
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # 關聯
    school = relationship("School", back_populates="discord_settings") 