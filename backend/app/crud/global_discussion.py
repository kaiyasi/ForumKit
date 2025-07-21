from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.global_discussion import GlobalDiscussion
from app.crud.post import post
from app.schemas.global_discussion import GlobalDiscussionCreate, GlobalDiscussionUpdate


class CRUDGlobalDiscussion(
    CRUDBase[GlobalDiscussion, GlobalDiscussionCreate, GlobalDiscussionUpdate]
):
    def create_with_author(
        self, db: Session, *, obj_in: GlobalDiscussionCreate, author_id: int
    ) -> GlobalDiscussion:
        db_obj = GlobalDiscussion(
            title=obj_in.title,
            content=obj_in.content,
            parent_id=obj_in.parent_id,
            is_pinned=obj_in.is_pinned,
            is_closed=obj_in.is_closed,
            author_id=author_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        author_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        is_pinned: Optional[bool] = None,
        is_closed: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[GlobalDiscussion]:
        query = db.query(self.model)
        if author_id is not None:
            query = query.filter(self.model.author_id == author_id)
        if parent_id is not None:
            query = query.filter(self.model.parent_id == parent_id)
        if is_pinned is not None:
            query = query.filter(self.model.is_pinned == is_pinned)
        if is_closed is not None:
            query = query.filter(self.model.is_closed == is_closed)
        if search:
            query = query.filter(
                or_(
                    self.model.title.ilike(f"%{search}%"),
                    self.model.content.ilike(f"%{search}%"),
                )
            )
        return query.offset(skip).limit(limit).all()


global_discussion = CRUDGlobalDiscussion(GlobalDiscussion)
