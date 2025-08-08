from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.discussion_tag import DiscussionTag
from app.schemas.internal_discussion import DiscussionTagCreate


class CRUDDiscussionTag(
    CRUDBase[DiscussionTag, DiscussionTagCreate, DiscussionTagCreate]
):
    def get_by_name(self, db: Session, *, name: str) -> Optional[DiscussionTag]:
        return db.query(self.model).filter(self.model.name == name).first()

    def get_multi_by_ids(self, db: Session, *, ids: List[int]) -> List[DiscussionTag]:
        return db.query(self.model).filter(self.model.id.in_(ids)).all()


discussion_tag = CRUDDiscussionTag(DiscussionTag)
