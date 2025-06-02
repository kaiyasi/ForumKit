from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.post import PostCreate, PostRead, PostList, PostReview
from app.services import post as post_service
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=PostRead)
def create_post(
    *,
    db: Session = Depends(deps.get_db),
    post_in: PostCreate,
    current_user: User = Depends(deps.get_current_user_optional)
) -> PostRead:
    """
    創建新貼文
    - 可選擇是否匿名
    - 非匿名發文需要登入
    - 內容不得為空
    """
    return post_service.create_post(
        db=db,
        post_in=post_in,
        current_user=current_user
    )

@router.patch("/{post_id}/status", response_model=PostRead)
def review_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
    review_in: PostReview,
    current_user: User = Depends(deps.require_role("reviewer"))
) -> PostRead:
    """
    審核貼文狀態
    - 僅限 reviewer 以上角色操作
    - 可更新為 approved/rejected/deleted
    - 需提供審核理由
    """
    return post_service.review_post(
        db=db,
        post_id=post_id,
        review_in=review_in,
        reviewer=current_user
    ) 