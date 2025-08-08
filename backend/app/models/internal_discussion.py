from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from .discussion_tag import DiscussionTagAssociation


class InternalDiscussion(Base):
    __tablename__ = "internal_discussions"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("internal_discussions.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, nullable=False, default=False)
    is_closed = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="internal_discussions")
    school = relationship("School", back_populates="internal_discussions")
    parent = relationship(
        "InternalDiscussion", remote_side=[id], back_populates="replies"
    )
    replies = relationship("InternalDiscussion", back_populates="parent")
    tags = relationship(
        "DiscussionTag",
        secondary=DiscussionTagAssociation,
        back_populates="discussions",
    )
