from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    ig_enabled = Column(Boolean, default=False)
    dc_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 關聯
    users = relationship("User", back_populates="school")
    posts = relationship("Post", back_populates="school")
    global_discussions = relationship("GlobalDiscussion", back_populates="school")
    ig_account = relationship("IGAccount", back_populates="school")
    discord_settings = relationship("DiscordSettings", back_populates="school")
    feature_toggle = relationship("SchoolFeatureToggle", back_populates="school") 