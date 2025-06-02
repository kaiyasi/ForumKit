from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate

class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    def create_with_author(
        self, db: Session, *, obj_in: PostCreate, author_id: Optional[int] = None
    ) -> Post:
        """
        創建新貼文，可選擇是否匿名
        """
        db_obj = Post(
            title=obj_in.title,
            content=obj_in.content,
            is_anonymous=obj_in.is_anonymous,
            author_id=author_id if not obj_in.is_anonymous else None,
            school_id=obj_in.school_id,
            status="pending"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_school(
        self, db: Session, *, school_id: int, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """
        獲取指定學校的貼文列表
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.school_id == school_id,
                    self.model.deleted_at.is_(None)
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """
        獲取所有未刪除的貼文
        """
        return (
            db.query(self.model)
            .filter(self.model.deleted_at.is_(None))
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

post = CRUDPost(Post) 