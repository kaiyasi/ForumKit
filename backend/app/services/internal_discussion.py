from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.crud import internal_discussion as discussion_crud
from app.crud import discussion_tag as tag_crud
from app.schemas.internal_discussion import (
    InternalDiscussionCreate,
    InternalDiscussionUpdate,
    InternalDiscussionQuery,
    DiscussionTagCreate
)
from app.models.user import User, UserRole

class InternalDiscussionService:
    async def create_discussion(
        self,
        db: Session,
        *,
        discussion_in: InternalDiscussionCreate,
        author: User
    ) -> dict:
        """
        創建內部討論
        """
        # 檢查權限
        if author.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或審核員權限"
            )

        # 檢查是否為同校
        if discussion_in.school_id != author.school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能在本校討論區發文"
            )

        # 如果有父討論，檢查是否存在且為同校
        if discussion_in.parent_id:
            parent = discussion_crud.internal_discussion.get(db, id=discussion_in.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父討論不存在"
                )
            if parent.school_id != author.school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能回覆本校討論"
                )

        # 創建討論
        discussion = discussion_crud.internal_discussion.create_with_author(
            db=db,
            obj_in=discussion_in,
            author_id=author.id
        )

        # 添加標籤
        if discussion_in.tag_ids:
            tags = tag_crud.discussion_tag.get_multi_by_ids(
                db=db,
                ids=discussion_in.tag_ids
            )
            discussion.tags = tags
            db.commit()

        return discussion

    async def update_discussion(
        self,
        db: Session,
        *,
        discussion_id: int,
        discussion_in: InternalDiscussionUpdate,
        author: User
    ) -> dict:
        """
        更新內部討論
        """
        # 檢查權限
        if author.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或審核員權限"
            )

        discussion = discussion_crud.internal_discussion.get(db, id=discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="討論不存在"
            )

        # 檢查是否為同校
        if discussion.school_id != author.school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能修改本校討論"
            )

        # 檢查是否為作者或管理員
        if discussion.author_id != author.id and author.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能修改自己的討論"
            )

        # 更新討論
        discussion = discussion_crud.internal_discussion.update(
            db=db,
            db_obj=discussion,
            obj_in=discussion_in
        )

        # 更新標籤
        if discussion_in.tag_ids is not None:
            tags = tag_crud.discussion_tag.get_multi_by_ids(
                db=db,
                ids=discussion_in.tag_ids
            )
            discussion.tags = tags
            db.commit()

        return discussion

    async def get_discussions(
        self,
        db: Session,
        *,
        query: InternalDiscussionQuery,
        user: User
    ) -> List[dict]:
        """
        獲取內部討論列表
        """
        # 檢查權限
        if user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或審核員權限"
            )

        # 如果是審核員，只能看到本校討論
        if user.role == UserRole.REVIEWER:
            query.school_id = user.school_id

        return discussion_crud.internal_discussion.get_multi(
            db=db,
            skip=query.skip,
            limit=query.limit,
            school_id=query.school_id,
            author_id=query.author_id,
            parent_id=query.parent_id,
            is_pinned=query.is_pinned,
            is_closed=query.is_closed,
            tag_ids=query.tag_ids,
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
        獲取單個內部討論
        """
        # 檢查權限
        if user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或審核員權限"
            )

        discussion = discussion_crud.internal_discussion.get(db, id=discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="討論不存在"
            )

        # 如果是審核員，只能看到本校討論
        if user.role == UserRole.REVIEWER and discussion.school_id != user.school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能查看本校討論"
            )

        return discussion

    async def create_tag(
        self,
        db: Session,
        *,
        tag_in: DiscussionTagCreate,
        admin: User
    ) -> dict:
        """
        創建討論標籤（僅限管理員）
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        # 檢查標籤名稱是否已存在
        existing = tag_crud.discussion_tag.get_by_name(db, name=tag_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="標籤名稱已存在"
            )

        return tag_crud.discussion_tag.create(db=db, obj_in=tag_in)

    async def get_tags(
        self,
        db: Session,
        *,
        user: User
    ) -> List[dict]:
        """
        獲取所有討論標籤
        """
        # 檢查權限
        if user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或審核員權限"
            )

        return tag_crud.discussion_tag.get_multi(db=db)

internal_discussion_service = InternalDiscussionService() 