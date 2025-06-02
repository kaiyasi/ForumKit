from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.crud import comment as comment_crud
from app.crud import post as post_crud
from app.schemas.comment import CommentCreate, CommentDetail
from app.models.user import User

def create_comment(
    db: Session,
    *,
    comment_in: CommentCreate,
    current_user: Optional[User] = None
) -> CommentDetail:
    """
    創建新留言
    """
    # 驗證內容不為空
    if not comment_in.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "COMMENT_EMPTY_CONTENT",
                "message": "留言內容不得為空"
            }
        )
    
    # 驗證貼文存在
    post = post_crud.post.get(db, id=comment_in.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "POST_NOT_FOUND",
                "message": "貼文不存在"
            }
        )
    
    # 如果選擇不匿名，必須是登入用戶
    if not comment_in.is_anonymous and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "COMMENT_AUTH_REQUIRED",
                "message": "非匿名留言需要登入"
            }
        )
    
    # 如果是回覆，驗證父留言存在
    if comment_in.parent_id:
        parent_comment = comment_crud.comment.get(db, id=comment_in.parent_id)
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "PARENT_COMMENT_NOT_FOUND",
                    "message": "父留言不存在"
                }
            )
    
    # 創建留言
    comment = comment_crud.comment.create_with_author(
        db=db,
        obj_in=comment_in,
        author_id=current_user.id if current_user else None
    )
    
    return CommentDetail.from_orm(comment)

def get_post_comments(
    db: Session,
    *,
    post_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[CommentDetail]:
    """
    獲取貼文的所有留言（包含回覆）
    """
    # 獲取根留言
    root_comments = comment_crud.comment.get_by_post(
        db=db,
        post_id=post_id,
        skip=skip,
        limit=limit
    )
    
    # 轉換為 CommentDetail 並獲取回覆
    result = []
    for comment in root_comments:
        comment_detail = CommentDetail.from_orm(comment)
        # 獲取回覆
        replies = comment_crud.comment.get_replies(db=db, comment_id=comment.id)
        comment_detail.replies = [CommentDetail.from_orm(reply) for reply in replies]
        result.append(comment_detail)
    
    return result 