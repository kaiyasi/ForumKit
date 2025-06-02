from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.sql import func
from sqlalchemy import and_

from app.crud import post as post_crud
from app.crud import review_log as review_log_crud
from app.crud import notification as notification_crud
from app.crud import global_review_log as global_review_log_crud
from app.schemas.post import PostCreate, PostRead, PostReview, PostUpdate
from app.schemas.review_log import ReviewLogCreate
from app.schemas.notification import NotificationCreate
from app.schemas.global_review_log import (
    GlobalReviewLogCreate,
    GlobalReviewVote,
    GlobalReviewQuery
)
from app.models.user import User, UserRole
from app.models.post import PostStatus
from app.models.review_log import ReviewAction
from app.models.global_review_log import GlobalReviewAction
from app.services.school_feature import school_feature_service
from app.services.ig_publish import ig_publish_service
from app.services.discord import discord_service

class PostService:
    async def create_post(
        self,
        db: Session,
        *,
        post_in: PostCreate,
        author: User
    ) -> dict:
        """
        創建貼文
        """
        post = post_crud.post.create(
            db=db,
            obj_in=post_in
        )

        # 檢查並觸發 IG 推播
        if await school_feature_service.is_feature_enabled(db, school_id=post.school_id, feature="ig"):
            try:
                await ig_publish_service.publish_post(
                    db=db,
                    post_id=post.id,
                    admin=author
                )
            except Exception as e:
                # 記錄錯誤但不中斷流程
                print(f"IG 推播失敗: {str(e)}")

        # 檢查並觸發 Discord 推播
        if await school_feature_service.is_feature_enabled(db, school_id=post.school_id, feature="discord"):
            try:
                await discord_service.publish_post(
                    db=db,
                    post_id=post.id,
                    admin=author
                )
            except Exception as e:
                # 記錄錯誤但不中斷流程
                print(f"Discord 推播失敗: {str(e)}")

        return post

    async def update_post(
        self,
        db: Session,
        *,
        post_id: int,
        post_in: PostUpdate,
        author: User
    ) -> dict:
        """
        更新貼文
        """
        post = post_crud.post.get(db, id=post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="貼文不存在"
            )

        # 檢查權限
        if post.author_id != author.id and author.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="沒有權限修改此貼文"
            )

        post = post_crud.post.update(
            db=db,
            db_obj=post,
            obj_in=post_in
        )

        # 檢查並觸發 IG 推播
        if await school_feature_service.is_feature_enabled(db, school_id=post.school_id, feature="ig"):
            try:
                await ig_publish_service.publish_post(
                    db=db,
                    post_id=post.id,
                    admin=author
                )
            except Exception as e:
                # 記錄錯誤但不中斷流程
                print(f"IG 推播失敗: {str(e)}")

        # 檢查並觸發 Discord 推播
        if await school_feature_service.is_feature_enabled(db, school_id=post.school_id, feature="discord"):
            try:
                await discord_service.publish_post(
                    db=db,
                    post_id=post.id,
                    admin=author
                )
            except Exception as e:
                # 記錄錯誤但不中斷流程
                print(f"Discord 推播失敗: {str(e)}")

        return post

post_service = PostService()

def create_post(
    db: Session,
    *,
    post_in: PostCreate,
    current_user: Optional[User] = None
) -> PostRead:
    """
    創建新貼文
    """
    # 驗證內容不為空
    if not post_in.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "POST_EMPTY_CONTENT",
                "message": "貼文內容不得為空"
            }
        )
    
    # 如果選擇不匿名，必須是登入用戶
    if not post_in.is_anonymous and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "POST_AUTH_REQUIRED",
                "message": "非匿名發文需要登入"
            }
        )
    
    # 創建貼文
    post = post_crud.post.create_with_author(
        db=db,
        obj_in=post_in,
        author_id=current_user.id if current_user else None
    )
    
    return PostRead.from_orm(post)

def review_post(
    db: Session,
    *,
    post_id: int,
    review_in: PostReview,
    reviewer: User
) -> PostRead:
    """
    審核貼文
    """
    # 檢查貼文是否存在
    post = post_crud.post.get(db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "POST_NOT_FOUND",
                "message": "貼文不存在"
            }
        )
    
    # 檢查貼文是否已被刪除
    if post.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "POST_ALREADY_DELETED",
                "message": "貼文已被刪除"
            }
        )
    
    # 更新貼文狀態
    update_data = {
        "status": review_in.status,
        "reviewed_by": reviewer.id,
        "reviewed_at": func.now(),
        "review_comment": review_in.review_comment
    }
    
    # 如果被標記為敏感內容
    if review_in.status == PostStatus.rejected:
        update_data.update({
            "is_sensitive": True,
            "sensitive_reason": review_in.review_comment
        })
    
    post = post_crud.post.update(db, db_obj=post, obj_in=update_data)
    
    # 記錄審核日誌
    action_map = {
        PostStatus.approved: ReviewAction.approve,
        PostStatus.rejected: ReviewAction.reject,
        PostStatus.deleted: ReviewAction.delete
    }
    
    review_log_in = ReviewLogCreate(
        post_id=post_id,
        reviewer_id=reviewer.id,
        action=action_map[review_in.status],
        reason=review_in.review_comment
    )
    review_log_crud.review_log.create_with_reviewer(db=db, obj_in=review_log_in)
    
    return PostRead.from_orm(post)

def review_school_post(
    db: Session,
    *,
    post_id: int,
    action: ReviewAction,
    reason: str,
    reviewer: User
) -> PostRead:
    """
    校內審核貼文
    """
    # 檢查權限
    if reviewer.role not in [UserRole.REVIEWER, UserRole.ADMIN, UserRole.DEV]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INSUFFICIENT_PERMISSIONS",
                "message": "需要審核員權限"
            }
        )
    
    # 檢查貼文是否存在
    post = post_crud.post.get(db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "POST_NOT_FOUND",
                "message": "貼文不存在"
            }
        )
    
    # 檢查是否為同校貼文
    if post.school_id != reviewer.school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "DIFFERENT_SCHOOL",
                "message": "只能審核本校貼文"
            }
        )
    
    # 檢查貼文是否已被刪除
    if post.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "POST_ALREADY_DELETED",
                "message": "貼文已被刪除"
            }
        )
    
    # 檢查貼文是否已有審核記錄
    if post.reviewed_at and post.status != PostStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "POST_ALREADY_REVIEWED",
                "message": "貼文已被審核"
            }
        )
    
    # 更新貼文狀態
    status_map = {
        ReviewAction.approve: PostStatus.approved,
        ReviewAction.reject: PostStatus.rejected
    }
    
    update_data = {
        "status": status_map[action],
        "reviewed_by": reviewer.id,
        "reviewed_at": func.now(),
        "review_comment": reason
    }
    
    # 如果被拒絕，標記為敏感內容
    if action == ReviewAction.reject:
        update_data.update({
            "is_sensitive": True,
            "sensitive_reason": reason
        })
    
    post = post_crud.post.update(db, db_obj=post, obj_in=update_data)
    
    # 記錄審核日誌
    review_log_in = ReviewLogCreate(
        post_id=post_id,
        reviewer_id=reviewer.id,
        action=action,
        reason=reason
    )
    review_log_crud.review_log.create_with_reviewer(db=db, obj_in=review_log_in)
    
    return PostRead.from_orm(post)

def override_school_post(
    db: Session,
    *,
    post_id: int,
    action: ReviewAction,
    reason: str,
    admin: User
) -> PostRead:
    """
    校內管理員強制操作貼文
    """
    # 檢查權限
    if admin.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INSUFFICIENT_PERMISSIONS",
                "message": "需要管理員權限"
            }
        )
    
    # 檢查貼文是否存在
    post = post_crud.post.get(db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "POST_NOT_FOUND",
                "message": "貼文不存在"
            }
        )
    
    # 檢查是否為同校貼文
    if post.school_id != admin.school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "DIFFERENT_SCHOOL",
                "message": "只能操作本校貼文"
            }
        )
    
    # 檢查貼文是否已被刪除
    if post.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "POST_ALREADY_DELETED",
                "message": "貼文已被刪除"
            }
        )
    
    # 更新貼文狀態
    status_map = {
        ReviewAction.approve: PostStatus.approved,
        ReviewAction.reject: PostStatus.rejected,
        ReviewAction.delete: PostStatus.deleted
    }
    
    update_data = {
        "status": status_map[action],
        "reviewed_by": admin.id,
        "reviewed_at": func.now(),
        "review_comment": reason
    }
    
    # 如果被拒絕或刪除，標記為敏感內容
    if action in [ReviewAction.reject, ReviewAction.delete]:
        update_data.update({
            "is_sensitive": True,
            "sensitive_reason": reason
        })
    
    # 如果被刪除，設置刪除時間
    if action == ReviewAction.delete:
        update_data["deleted_at"] = func.now()
    
    post = post_crud.post.update(db, db_obj=post, obj_in=update_data)
    
    # 記錄審核日誌
    review_log_in = ReviewLogCreate(
        post_id=post_id,
        reviewer_id=admin.id,
        action=ReviewAction.override,
        reason=reason,
        override_action=action
    )
    review_log_crud.review_log.create_with_reviewer(db=db, obj_in=review_log_in)
    
    # 發送通知給原貼文作者
    if post.author_id:
        notification_in = NotificationCreate(
            user_id=post.author_id,
            title="貼文狀態更新通知",
            content=f"您的貼文已被管理員強制{action.value}，原因：{reason}",
            type="post_status_change"
        )
        notification_crud.notification.create_with_user(db=db, obj_in=notification_in)
    
    # 發送通知給原審核者
    if post.reviewed_by and post.reviewed_by != admin.id:
        notification_in = NotificationCreate(
            user_id=post.reviewed_by,
            title="貼文審核覆蓋通知",
            content=f"您審核的貼文已被管理員強制{action.value}，原因：{reason}",
            type="review_override"
        )
        notification_crud.notification.create_with_user(db=db, obj_in=notification_in)
    
    return PostRead.from_orm(post)

def vote_global_post(
    db: Session,
    *,
    post_id: int,
    vote_in: GlobalReviewVote,
    reviewer: User
) -> PostRead:
    """
    跨校投票審核貼文
    """
    # 檢查權限
    if reviewer.role not in [UserRole.REVIEWER, UserRole.ADMIN, UserRole.DEV]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INSUFFICIENT_PERMISSIONS",
                "message": "需要審核員權限"
            }
        )
    
    # 檢查貼文是否存在
    post = post_crud.post.get(db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "POST_NOT_FOUND",
                "message": "貼文不存在"
            }
        )
    
    # 檢查貼文是否已被刪除
    if post.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "POST_ALREADY_DELETED",
                "message": "貼文已被刪除"
            }
        )
    
    # 檢查貼文是否已被審核
    if post.status != PostStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "POST_ALREADY_REVIEWED",
                "message": "貼文已被審核"
            }
        )
    
    # 檢查是否已投票
    existing_vote = global_review_log_crud.global_review_log.get_by_reviewer(
        db=db,
        post_id=post_id,
        reviewer_id=reviewer.id
    )
    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "ALREADY_VOTED",
                "message": "您已經投過票了"
            }
        )
    
    # 記錄投票
    vote_log_in = GlobalReviewLogCreate(
        post_id=post_id,
        reviewer_id=reviewer.id,
        vote=vote_in.vote,
        reason=vote_in.reason
    )
    global_review_log_crud.global_review_log.create_with_reviewer(
        db=db,
        obj_in=vote_log_in
    )
    
    # 統計投票結果
    total_votes = global_review_log_crud.global_review_log.count_by_post(
        db=db,
        post_id=post_id
    )
    approve_votes = global_review_log_crud.global_review_log.count_by_post_and_vote(
        db=db,
        post_id=post_id,
        vote=True
    )
    
    # 如果贊成票達到 80%，自動通過
    if total_votes >= 5 and approve_votes / total_votes >= 0.8:
        update_data = {
            "status": PostStatus.approved,
            "reviewed_by": reviewer.id,
            "reviewed_at": func.now(),
            "review_comment": "跨校投票通過"
        }
        post = post_crud.post.update(db, db_obj=post, obj_in=update_data)
        
        # 發送通知給原貼文作者
        if post.author_id:
            notification_in = NotificationCreate(
                user_id=post.author_id,
                title="貼文審核通過通知",
                content="您的貼文已通過跨校投票審核",
                type="post_approved"
            )
            notification_crud.notification.create_with_user(db=db, obj_in=notification_in)
    
    return PostRead.from_orm(post)

def get_global_post_votes(
    db: Session,
    *,
    post_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[GlobalReviewLogRead]:
    """
    獲取跨校貼文投票記錄
    """
    return global_review_log_crud.global_review_log.get_multi_by_post(
        db=db,
        post_id=post_id,
        skip=skip,
        limit=limit
    )

def dev_force_post_status(
    db: Session,
    *,
    post_id: int,
    action: ReviewAction,
    reason: Optional[str],
    dev: User
) -> PostRead:
    """
    開發者強制變更貼文狀態
    """
    # 檢查權限
    if dev.role != UserRole.DEV:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INSUFFICIENT_PERMISSIONS",
                "message": "需要開發者權限"
            }
        )
    
    # 檢查貼文是否存在
    post = post_crud.post.get(db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "POST_NOT_FOUND",
                "message": "貼文不存在"
            }
        )
    
    # 更新貼文狀態
    status_map = {
        ReviewAction.approve: PostStatus.approved,
        ReviewAction.reject: PostStatus.rejected,
        ReviewAction.delete: PostStatus.deleted,
        ReviewAction.reset: PostStatus.pending
    }
    
    update_data = {
        "status": status_map[action],
        "reviewed_by": dev.id,
        "reviewed_at": func.now(),
        "review_comment": reason or f"開發者強制{action.value}"
    }
    
    # 如果被拒絕或刪除，標記為敏感內容
    if action in [ReviewAction.reject, ReviewAction.delete]:
        update_data.update({
            "is_sensitive": True,
            "sensitive_reason": reason or f"開發者強制{action.value}"
        })
    
    # 如果被刪除，設置刪除時間
    if action == ReviewAction.delete:
        update_data["deleted_at"] = func.now()
    
    # 如果是重置，清除相關欄位
    if action == ReviewAction.reset:
        update_data.update({
            "reviewed_by": None,
            "reviewed_at": None,
            "review_comment": None,
            "is_sensitive": False,
            "sensitive_reason": None,
            "deleted_at": None
        })
    
    post = post_crud.post.update(db, db_obj=post, obj_in=update_data)
    
    # 記錄審核日誌
    review_log_in = ReviewLogCreate(
        post_id=post_id,
        reviewer_id=dev.id,
        action=ReviewAction.dev_override,
        reason=reason or f"開發者強制{action.value}",
        override_action=action
    )
    review_log_crud.review_log.create_with_reviewer(db=db, obj_in=review_log_in)
    
    # 發送通知給原貼文作者
    if post.author_id:
        notification_in = NotificationCreate(
            user_id=post.author_id,
            title="貼文狀態變更通知",
            content=f"您的貼文已被開發者強制{action.value}，原因：{reason or '無'}",
            type="post_status_change"
        )
        notification_crud.notification.create_with_user(db=db, obj_in=notification_in)
    
    # 發送通知給原審核者
    if post.reviewed_by and post.reviewed_by != dev.id:
        notification_in = NotificationCreate(
            user_id=post.reviewed_by,
            title="貼文審核覆蓋通知",
            content=f"您審核的貼文已被開發者強制{action.value}，原因：{reason or '無'}",
            type="review_override"
        )
        notification_crud.notification.create_with_user(db=db, obj_in=notification_in)
    
    return PostRead.from_orm(post)

def get_dev_override_logs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100
) -> List[ReviewLogRead]:
    """
    獲取開發者覆蓋記錄
    """
    return review_log_crud.review_log.get_multi_by_action(
        db=db,
        action=ReviewAction.dev_override,
        skip=skip,
        limit=limit
    )

def get_global_post_reviews(
    db: Session,
    *,
    post_id: int,
    query: GlobalReviewQuery
) -> List[GlobalReviewLogRead]:
    """
    獲取跨校貼文審核記錄
    """
    return global_review_log_crud.global_review_log.get_multi_by_post(
        db=db,
        post_id=post_id,
        skip=query.skip,
        limit=query.limit,
        action=query.action,
        vote=query.vote
    )

def get_pending_global_posts(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20
) -> List[PostList]:
    """
    獲取待審核的跨校貼文
    """
    return post_crud.post.get_multi_by_status(
        db=db,
        status=PostStatus.pending,
        skip=skip,
        limit=limit
    )

def get_user_global_reviews(
    db: Session,
    *,
    user_id: int,
    query: GlobalReviewQuery
) -> List[GlobalReviewLogRead]:
    """
    獲取用戶的跨校審核記錄
    """
    return global_review_log_crud.global_review_log.get_multi_by_user(
        db=db,
        user_id=user_id,
        skip=query.skip,
        limit=query.limit,
        action=query.action,
        vote=query.vote
    ) 