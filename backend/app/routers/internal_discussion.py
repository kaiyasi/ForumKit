from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.internal_discussion import (
    InternalDiscussionCreate,
    InternalDiscussionUpdate,
    InternalDiscussionRead,
    InternalDiscussionQuery,
    DiscussionTagCreate,
    DiscussionTagRead
)
from app.services.internal_discussion import internal_discussion_service
from app.models.user import User

router = APIRouter()

@router.post("/discussions", response_model=InternalDiscussionRead)
async def create_discussion(
    *,
    db: Session = Depends(deps.get_db),
    discussion_in: InternalDiscussionCreate,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    創建內部討論
    """
    return await internal_discussion_service.create_discussion(
        db=db,
        discussion_in=discussion_in,
        author=current_user
    )

@router.patch("/discussions/{discussion_id}", response_model=InternalDiscussionRead)
async def update_discussion(
    *,
    db: Session = Depends(deps.get_db),
    discussion_id: int,
    discussion_in: InternalDiscussionUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    更新內部討論
    """
    return await internal_discussion_service.update_discussion(
        db=db,
        discussion_id=discussion_id,
        discussion_in=discussion_in,
        author=current_user
    )

@router.get("/discussions", response_model=List[InternalDiscussionRead])
async def get_discussions(
    *,
    db: Session = Depends(deps.get_db),
    query: InternalDiscussionQuery = Depends(),
    current_user: User = Depends(deps.get_current_user)
) -> List[dict]:
    """
    獲取內部討論列表
    """
    return await internal_discussion_service.get_discussions(
        db=db,
        query=query,
        user=current_user
    )

@router.get("/discussions/{discussion_id}", response_model=InternalDiscussionRead)
async def get_discussion(
    *,
    db: Session = Depends(deps.get_db),
    discussion_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    獲取單個內部討論
    """
    return await internal_discussion_service.get_discussion(
        db=db,
        discussion_id=discussion_id,
        user=current_user
    )

@router.post("/tags", response_model=DiscussionTagRead)
async def create_tag(
    *,
    db: Session = Depends(deps.get_db),
    tag_in: DiscussionTagCreate,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    創建討論標籤（僅限管理員）
    """
    return await internal_discussion_service.create_tag(
        db=db,
        tag_in=tag_in,
        admin=current_user
    )

@router.get("/tags", response_model=List[DiscussionTagRead])
async def get_tags(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> List[dict]:
    """
    獲取所有討論標籤
    """
    return await internal_discussion_service.get_tags(
        db=db,
        user=current_user
    ) 