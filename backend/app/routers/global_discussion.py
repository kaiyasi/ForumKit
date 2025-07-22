from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.global_discussion import (
    GlobalDiscussionCreate,
    GlobalDiscussionUpdate,
    GlobalDiscussionRead,
    GlobalDiscussionQuery
)
from app.services.global_discussion import global_discussion_service
from app.models.user import User

router = APIRouter()

@router.post("/discussions", response_model=GlobalDiscussionRead)
async def create_discussion(
    *,
    db: Session = Depends(deps.get_db),
    discussion_in: GlobalDiscussionCreate,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    創建跨校討論
    """
    return await global_discussion_service.create_discussion(
        db=db,
        discussion_in=discussion_in,
        author=current_user
    )

@router.patch("/discussions/{discussion_id}", response_model=GlobalDiscussionRead)
async def update_discussion(
    *,
    db: Session = Depends(deps.get_db),
    discussion_id: int,
    discussion_in: GlobalDiscussionUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    更新跨校討論
    """
    return await global_discussion_service.update_discussion(
        db=db,
        discussion_id=discussion_id,
        discussion_in=discussion_in,
        author=current_user
    )

@router.get("/discussions", response_model=List[GlobalDiscussionRead])
async def get_discussions(
    *,
    db: Session = Depends(deps.get_db),
    query: GlobalDiscussionQuery = Depends(),
    current_user: User = Depends(deps.get_current_user)
) -> List[dict]:
    """
    獲取跨校討論列表
    """
    return await global_discussion_service.get_discussions(
        db=db,
        query=query,
        user=current_user
    )

@router.get("/discussions/{discussion_id}", response_model=GlobalDiscussionRead)
async def get_discussion(
    *,
    db: Session = Depends(deps.get_db),
    discussion_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> dict:
    """
    獲取單個跨校討論
    """
    return await global_discussion_service.get_discussion(
        db=db,
        discussion_id=discussion_id,
        user=current_user
    ) 
