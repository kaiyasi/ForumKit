from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class GlobalDiscussion(Base):
    """
    Global Discussion model for cross-school discussions
    """
    __tablename__ = "global_discussions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    is_anonymous = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="global_discussions")
    school = relationship("School", back_populates="global_discussions") 