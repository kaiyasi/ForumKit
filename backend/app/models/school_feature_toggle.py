from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class SchoolFeatureToggle(Base):
    __tablename__ = "school_feature_toggles"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    
    # 基本功能開關
    enable_ig = Column(Boolean, default=False)  # IG 模組開關
    enable_discord = Column(Boolean, default=False)  # Discord 模組開關
    enable_comments = Column(Boolean, default=True)  # 留言功能開關
    enable_cross_school = Column(Boolean, default=True)  # 跨校功能開關
    
    # IG 設定
    ig_template_id = Column(Integer, ForeignKey("ig_templates.id", ondelete="SET NULL"), nullable=True)  # IG 模板
    ig_publish_auto = Column(Boolean, default=False)  # 自動發布到 IG
    
    # Discord 設定
    discord_webhook_url = Column(String, nullable=True)  # Discord Webhook URL
    discord_channel_name = Column(String, nullable=True)  # Discord 頻道名稱
    discord_report_webhook_url = Column(String, nullable=True)  # Discord 檢舉通知 Webhook URL
    
    # 其他設定
    settings = Column(JSON, nullable=True)  # 其他自訂設定
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # 關聯
    school = relationship("School", back_populates="feature_toggle")
    ig_template = relationship("IGTemplate", back_populates="school_toggles") 
