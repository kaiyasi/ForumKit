from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.internal_discussion import InternalDiscussion
from app.models.discussion_tag import DiscussionTag
from app.schemas.internal_discussion import (
    InternalDiscussionCreate,
    InternalDiscussionUpdate,
)


class CRUDInternalDiscussion(
    CRUDBase[InternalDiscussion, InternalDiscussionCreate, InternalDiscussionUpdate]
):
    def create_with_author(
        self, db: Session, *, obj_in: InternalDiscussionCreate, author_id: int
    ) -> InternalDiscussion:
        db_obj = InternalDiscussion(
            school_id=obj_in.school_id,
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
        school_id: Optional[int] = None,
        author_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        is_pinned: Optional[bool] = None,
        is_closed: Optional[bool] = None,
        tag_ids: Optional[List[int]] = None,
        search: Optional[str] = None,
    ) -> List[InternalDiscussion]:
        query = db.query(self.model)
        if school_id is not None:
            query = query.filter(self.model.school_id == school_id)
        if author_id is not None:
            query = query.filter(self.model.author_id == author_id)
        if parent_id is not None:
            query = query.filter(self.model.parent_id == parent_id)
        if is_pinned is not None:
            query = query.filter(self.model.is_pinned == is_pinned)
        if is_closed is not None:
            query = query.filter(self.model.is_closed == is_closed)
        if tag_ids:
            query = query.join(self.model.tags).filter(DiscussionTag.id.in_(tag_ids))
        if search:
            query = query.filter(
                or_(
                    self.model.title.ilike(f"%{search}%"),
                    self.model.content.ilike(f"%{search}%"),
                )
            )
        return query.offset(skip).limit(limit).all()


internal_discussion = CRUDInternalDiscussion(InternalDiscussion)
