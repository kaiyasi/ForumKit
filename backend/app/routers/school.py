from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.post import PostRead, PostList
from app.schemas.review_log import ReviewLogRead
from app.models.user import User, UserRole
from app.models.review_log import ReviewAction
from app.services import post as post_service
from app.services import review_log as review_log_service

router = APIRouter()

@router.get("/posts", response_model=List[PostList])
def list_school_posts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 20,
    status: str = None
):
    """
    獲取本校貼文列表
    """
    return post_service.get_school_posts(
        db=db,
        school_id=current_user.school_id,
        skip=skip,
        limit=limit,
        status=status
    )

@router.get("/posts/{post_id}", response_model=PostRead)
def get_school_post(
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    獲取本校貼文詳情
    """
    return post_service.get_school_post(
        db=db,
        post_id=post_id,
        school_id=current_user.school_id
    )

@router.patch("/posts/{post_id}/review", response_model=PostRead)
def review_school_post(
    post_id: int,
    action: ReviewAction,
    reason: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.REVIEWER))
):
    """
    校內審核貼文
    """
    return post_service.review_school_post(
        db=db,
        post_id=post_id,
        action=action,
        reason=reason,
        reviewer=current_user
    )

@router.get("/posts/{post_id}/review-logs", response_model=List[ReviewLogRead])
def get_school_post_review_logs(
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.REVIEWER))
):
    """
    獲取本校貼文審核記錄
    """
    return review_log_service.get_post_review_logs(
        db=db,
        post_id=post_id,
        school_id=current_user.school_id
    ) 