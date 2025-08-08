from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud import review_log as review_log_crud
from app.schemas.review_log import ReviewLogCreate, ReviewLogRead
from app.models.user import User

class ReviewLogService:
    """
    Review log service for handling review log operations
    """
    
    def create_review_log(
        self,
        db: Session,
        *,
        review_log_in: ReviewLogCreate,
        reviewer: User
    ) -> ReviewLogRead:
        """
        Create a new review log entry
        """
        review_log = review_log_crud.review_log.create_with_reviewer(
            db=db,
            obj_in=review_log_in,
            reviewer_id=reviewer.id
        )
        return ReviewLogRead.from_orm(review_log)
    
    def get_review_logs(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewLogRead]:
        """
        Get review logs with pagination
        """
        review_logs = review_log_crud.review_log.get_multi(
            db=db,
            skip=skip,
            limit=limit
        )
        return [ReviewLogRead.from_orm(log) for log in review_logs]

# Create service instance
review_log_service = ReviewLogService() 