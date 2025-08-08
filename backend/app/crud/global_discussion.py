from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.global_discussion import GlobalDiscussion
from app.schemas.global_discussion import GlobalDiscussionCreate, GlobalDiscussionUpdate

class CRUDGlobalDiscussion(CRUDBase[GlobalDiscussion, GlobalDiscussionCreate, GlobalDiscussionUpdate]):
    """
    CRUD operations for Global Discussion
    """
    
    def get_multi_by_school(
        self,
        db: Session,
        *,
        school_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[GlobalDiscussion]:
        """
        Get global discussions by school
        """
        return (
            db.query(self.model)
            .filter(GlobalDiscussion.school_id == school_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_author(
        self,
        db: Session,
        *,
        obj_in: GlobalDiscussionCreate,
        author_id: Optional[int] = None
    ) -> GlobalDiscussion:
        """
        Create global discussion with author
        """
        obj_in_data = obj_in.model_dump()
        if author_id:
            obj_in_data["author_id"] = author_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

global_discussion = CRUDGlobalDiscussion(GlobalDiscussion) 