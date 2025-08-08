from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

GlobalDiscussionPostAssociation = Table(
    "global_discussion_post_associations",
    Base.metadata,
    Column(
        "discussion_id", Integer, ForeignKey("global_discussions.id"), primary_key=True
    ),
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
)


class GlobalDiscussion(Base):
    __tablename__ = "global_discussions"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("global_discussions.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, nullable=False, default=False)
    is_closed = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="global_discussions")
    parent = relationship(
        "GlobalDiscussion", remote_side=[id], back_populates="replies"
    )
    replies = relationship("GlobalDiscussion", back_populates="parent")
    posts = relationship(
        "Post",
        secondary=GlobalDiscussionPostAssociation,
        back_populates="global_discussions",
    )
