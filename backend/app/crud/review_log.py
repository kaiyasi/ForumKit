from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.review_log import ReviewLog
from app.schemas.review_log import ReviewLogCreate, ReviewLogUpdate

class CRUDReviewLog(CRUDBase[ReviewLog, ReviewLogCreate, ReviewLogUpdate]):
    pass

review_log = CRUDReviewLog(ReviewLog)
