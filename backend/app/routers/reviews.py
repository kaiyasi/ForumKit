from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.review_log import ReviewLogRead, ReviewLogCreate
from app.models.user import User, UserRole
from app.services import review_log as review_log_service

router = APIRouter()

@router.get("/", response_model=List[ReviewLogRead])
def list_reviews(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user_with_role([UserRole.REVIEWER, UserRole.ADMIN])),
    skip: int = 0,
    limit: int = 100
):
    """
    獲取審核記錄列表
    """
    return review_log_service.review_log_service.get_review_logs(
        db=db,
        skip=skip,
        limit=limit
    ) 