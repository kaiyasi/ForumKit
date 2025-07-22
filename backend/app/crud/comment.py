from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate

class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    def create_with_author(
        self, db: Session, *, obj_in: CommentCreate, author_id: Optional[int] = None
    ) -> Comment:
        """
        創建新留言，可選擇是否匿名
        """
        db_obj = Comment(
            content=obj_in.content,
            is_anonymous=obj_in.is_anonymous,
            author_id=author_id if not obj_in.is_anonymous else None,
            post_id=obj_in.post_id,
            parent_id=obj_in.parent_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_post(
        self, db: Session, *, post_id: int, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """
        獲取指定貼文的所有根留言（不含回覆）
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.post_id == post_id,
                    self.model.parent_id.is_(None),
                    self.model.deleted_at.is_(None)
                )
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_replies(
        self, db: Session, *, comment_id: int, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """
        獲取指定留言的所有回覆
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.parent_id == comment_id,
                    self.model.deleted_at.is_(None)
                )
            )
            .order_by(self.model.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

comment = CRUDComment(Comment) 
