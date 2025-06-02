from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.school_feature_toggle import (
    SchoolFeatureToggleCreate,
    SchoolFeatureToggleUpdate,
    SchoolFeatureToggleRead
)
from app.models.user import User, UserRole
from app.services.school_feature import school_feature_service

router = APIRouter()

@router.post("/features", response_model=SchoolFeatureToggleRead)
async def create_feature_toggle(
    *,
    db: Session = Depends(deps.get_db),
    toggle_in: SchoolFeatureToggleCreate,
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    創建學校功能開關設定（僅限管理員）
    """
    return await school_feature_service.create_toggle(
        db=db,
        toggle_in=toggle_in,
        admin=current_user
    )

@router.patch("/features/{toggle_id}", response_model=SchoolFeatureToggleRead)
async def update_feature_toggle(
    *,
    db: Session = Depends(deps.get_db),
    toggle_id: int,
    toggle_in: SchoolFeatureToggleUpdate,
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    更新學校功能開關設定（僅限管理員）
    """
    return await school_feature_service.update_toggle(
        db=db,
        toggle_id=toggle_id,
        toggle_in=toggle_in,
        admin=current_user
    )

@router.get("/features/{school_id}", response_model=SchoolFeatureToggleRead)
async def get_feature_toggle(
    *,
    db: Session = Depends(deps.get_db),
    school_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    獲取學校功能開關設定
    """
    toggle = await school_feature_service.get_toggle(
        db=db,
        school_id=school_id
    )
    if not toggle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="功能開關設定不存在"
        )
    return toggle

@router.get("/features", response_model=List[SchoolFeatureToggleRead])
async def get_all_feature_toggles(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    獲取所有學校功能開關設定（僅限管理員）
    """
    return await school_feature_service.get_all_toggles(
        db=db,
        skip=skip,
        limit=limit
    ) 