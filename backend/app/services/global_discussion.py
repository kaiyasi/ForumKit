from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.crud import global_discussion as discussion_crud
from app.schemas.global_discussion import (
    GlobalDiscussionCreate,
    GlobalDiscussionUpdate,
    GlobalDiscussionQuery
)
from app.models.user import User, UserRole

class GlobalDiscussionService:
    async def create_discussion(
        self,
        db: Session,
        *,
        discussion_in: GlobalDiscussionCreate,
        author: User
    ) -> dict:
        """
        創建跨校討論
        """
        # 檢查權限
        if author.role not in [UserRole.ADMIN, UserRole.GLOBAL_REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或跨校審核員權限"
            )

        # 如果有父討論，檢查是否存在
        if discussion_in.parent_id:
            parent = discussion_crud.global_discussion.get(db, id=discussion_in.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父討論不存在"
                )

        # 創建討論
        discussion = discussion_crud.global_discussion.create_with_author(
            db=db,
            obj_in=discussion_in,
            author_id=author.id
        )

        # 添加貼文關聯
        if discussion_in.post_ids:
            posts = discussion_crud.post.get_multi_by_ids(
                db=db,
                ids=discussion_in.post_ids
            )
            discussion.posts = posts
            db.commit()

        return discussion

    async def update_discussion(
        self,
        db: Session,
        *,
        discussion_id: int,
        discussion_in: GlobalDiscussionUpdate,
        author: User
    ) -> dict:
        """
        更新跨校討論
        """
        # 檢查權限
        if author.role not in [UserRole.ADMIN, UserRole.GLOBAL_REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或跨校審核員權限"
            )

        discussion = discussion_crud.global_discussion.get(db, id=discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="討論不存在"
            )

        # 檢查是否為作者或管理員
        if discussion.author_id != author.id and author.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能修改自己的討論"
            )

        # 更新討論
        discussion = discussion_crud.global_discussion.update(
            db=db,
            db_obj=discussion,
            obj_in=discussion_in
        )

        # 更新貼文關聯
        if discussion_in.post_ids is not None:
            posts = discussion_crud.post.get_multi_by_ids(
                db=db,
                ids=discussion_in.post_ids
            )
            discussion.posts = posts
            db.commit()

        return discussion

    async def get_discussions(
        self,
        db: Session,
        *,
        query: GlobalDiscussionQuery,
        user: User
    ) -> List[dict]:
        """
        獲取跨校討論列表
        """
        # 檢查權限
        if user.role not in [UserRole.ADMIN, UserRole.GLOBAL_REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或跨校審核員權限"
            )

        return discussion_crud.global_discussion.get_multi(
            db=db,
            skip=query.skip,
            limit=query.limit,
            author_id=query.author_id,
            parent_id=query.parent_id,
            is_pinned=query.is_pinned,
            is_closed=query.is_closed,
            post_id=query.post_id,
            search=query.search
        )

    async def get_discussion(
        self,
        db: Session,
        *,
        discussion_id: int,
        user: User
    ) -> dict:
        """
        獲取單個跨校討論
        """
        # 檢查權限
        if user.role not in [UserRole.ADMIN, UserRole.GLOBAL_REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或跨校審核員權限"
            )

        discussion = discussion_crud.global_discussion.get(db, id=discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="討論不存在"
            )

        return discussion

global_discussion_service = GlobalDiscussionService() 