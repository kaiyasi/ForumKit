from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

# Association table for tags and discussions
DiscussionTagAssociation = Table(
    "discussion_tag_associations",
    Base.metadata,
    Column(
        "discussion_id",
        Integer,
        ForeignKey("internal_discussions.id"),
        primary_key=True,
    ),
    Column("tag_id", Integer, ForeignKey("discussion_tags.id"), primary_key=True),
)


class DiscussionTag(Base):
    __tablename__ = "discussion_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    discussions = relationship(
        "InternalDiscussion",
        secondary=DiscussionTagAssociation,
        back_populates="tags",
    )
