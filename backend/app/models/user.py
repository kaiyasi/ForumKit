from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    REVIEWER = "reviewer"
    DESIGNER = "designer"
    SYNC = "sync"
    GLOBAL_REVIEWER = "global_reviewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    email_hash = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 關聯
    school = relationship("School", back_populates="users")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    internal_discussions = relationship("InternalDiscussion", back_populates="author")
    global_discussions = relationship("GlobalDiscussion", back_populates="author")
    review_logs = relationship("ReviewLog", back_populates="reviewer") 