from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.comment import CommentCreate, CommentDetail
from app.services import comment as comment_service
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=CommentDetail)
def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    comment_in: CommentCreate,
    current_user: User = Depends(deps.get_current_user_optional)
) -> CommentDetail:
    """
    創建新留言
    - 可選擇是否匿名
    - 非匿名留言需要登入
    - 內容不得為空
    - 支援回覆其他留言
    """
    return comment_service.create_comment(
        db=db,
        comment_in=comment_in,
        current_user=current_user
    )

@router.get("/posts/{post_id}/comments", response_model=List[CommentDetail])
def get_post_comments(
    post_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[CommentDetail]:
    """
    獲取貼文的所有留言
    - 包含回覆
    - 依時間排序
    - 支援分頁
    """
    return comment_service.get_post_comments(
        db=db,
        post_id=post_id,
        skip=skip,
        limit=limit
    ) 
