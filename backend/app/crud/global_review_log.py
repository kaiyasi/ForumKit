from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.global_review_log import GlobalReviewLog
from app.schemas.global_review_log import GlobalReviewLogCreate, GlobalReviewLogUpdate

class CRUDGlobalReviewLog(CRUDBase[GlobalReviewLog, GlobalReviewLogCreate, GlobalReviewLogUpdate]):
    pass

global_review_log = CRUDGlobalReviewLog(GlobalReviewLog)
