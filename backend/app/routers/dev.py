from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.post import PostRead
from app.schemas.review_log import ReviewLogRead
from app.models.user import User, UserRole
from app.models.review_log import ReviewAction
from app.services import post as post_service

router = APIRouter()

@router.patch("/posts/{post_id}/force", response_model=PostRead)
def force_post_status(
    post_id: int,
    action: ReviewAction,
    reason: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.DEV))
):
    """
    開發者強制變更貼文狀態
    """
    return post_service.dev_force_post_status(
        db=db,
        post_id=post_id,
        action=action,
        reason=reason,
        dev=current_user
    )

@router.get("/override-logs", response_model=List[ReviewLogRead])
def get_dev_override_logs(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.DEV)),
    skip: int = 0,
    limit: int = 100
):
    """
    獲取開發者覆蓋記錄
    """
    return post_service.get_dev_override_logs(
        db=db,
        skip=skip,
        limit=limit
    ) 