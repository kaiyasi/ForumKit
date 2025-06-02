from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.post import PostRead, PostList
from app.schemas.global_review_log import (
    GlobalReviewLogRead,
    GlobalReviewVote,
    GlobalReviewQuery
)
from app.models.user import User, UserRole
from app.models.review_log import ReviewAction
from app.services import post as post_service

router = APIRouter()

@router.get("/posts", response_model=List[PostList])
def list_global_posts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 20,
    status: str = None
):
    """
    獲取跨校貼文列表
    """
    return post_service.get_global_posts(
        db=db,
        skip=skip,
        limit=limit,
        status=status
    )

@router.get("/posts/pending", response_model=List[PostList])
def list_pending_global_posts(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 20
):
    """
    獲取待審核的跨校貼文
    """
    return post_service.get_pending_global_posts(
        db=db,
        skip=skip,
        limit=limit
    )

@router.get("/posts/{post_id}", response_model=PostRead)
def get_global_post(
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    獲取跨校貼文詳情
    """
    return post_service.get_global_post(
        db=db,
        post_id=post_id
    )

@router.post("/posts/{post_id}/vote", response_model=PostRead)
def vote_global_post(
    post_id: int,
    vote_in: GlobalReviewVote,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.REVIEWER))
):
    """
    跨校投票審核貼文
    """
    return post_service.vote_global_post(
        db=db,
        post_id=post_id,
        vote_in=vote_in,
        reviewer=current_user
    )

@router.get("/posts/{post_id}/reviews", response_model=List[GlobalReviewLogRead])
def get_global_post_reviews(
    post_id: int,
    query: GlobalReviewQuery = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    獲取跨校貼文審核記錄
    """
    return post_service.get_global_post_reviews(
        db=db,
        post_id=post_id,
        query=query
    )

@router.get("/users/{user_id}/reviews", response_model=List[GlobalReviewLogRead])
def get_user_global_reviews(
    user_id: int,
    query: GlobalReviewQuery = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    獲取用戶的跨校審核記錄（僅限管理員和開發者）
    """
    return post_service.get_user_global_reviews(
        db=db,
        user_id=user_id,
        query=query
    ) 