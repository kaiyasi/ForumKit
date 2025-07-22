from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import school_feature_toggle as toggle_crud
from app.crud import ig_template as template_crud
from app.schemas.school_feature_toggle import (
    SchoolFeatureToggleCreate,
    SchoolFeatureToggleUpdate
)
from app.models.user import User, UserRole

class SchoolFeatureService:
    async def create_toggle(
        self,
        db: Session,
        *,
        toggle_in: SchoolFeatureToggleCreate,
        admin: User
    ) -> dict:
        """
        創建學校功能開關設定
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        # 檢查是否已存在
        existing = toggle_crud.school_feature_toggle.get_by_school(
            db=db,
            school_id=toggle_in.school_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="該學校已有功能開關設定"
            )

        # 檢查 IG 模板是否存在
        if toggle_in.ig_template_id:
            template = template_crud.ig_template.get(db, id=toggle_in.ig_template_id)
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IG 模板不存在"
                )

        return toggle_crud.school_feature_toggle.create(
            db=db,
            obj_in=toggle_in
        )

    async def update_toggle(
        self,
        db: Session,
        *,
        toggle_id: int,
        toggle_in: SchoolFeatureToggleUpdate,
        admin: User
    ) -> dict:
        """
        更新學校功能開關設定
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        toggle = toggle_crud.school_feature_toggle.get(db, id=toggle_id)
        if not toggle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="功能開關設定不存在"
            )

        # 檢查 IG 模板是否存在
        if toggle_in.ig_template_id:
            template = template_crud.ig_template.get(db, id=toggle_in.ig_template_id)
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="IG 模板不存在"
                )

        return toggle_crud.school_feature_toggle.update(
            db=db,
            db_obj=toggle,
            obj_in=toggle_in
        )

    async def get_toggle(
        self,
        db: Session,
        *,
        school_id: int
    ) -> Optional[dict]:
        """
        獲取學校功能開關設定
        """
        return toggle_crud.school_feature_toggle.get_by_school(
            db=db,
            school_id=school_id
        )

    async def get_all_toggles(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        獲取所有學校功能開關設定
        """
        return toggle_crud.school_feature_toggle.get_multi(
            db=db,
            skip=skip,
            limit=limit
        )

    async def is_feature_enabled(
        self,
        db: Session,
        *,
        school_id: int,
        feature: str
    ) -> bool:
        """
        檢查特定功能是否啟用
        """
        toggle = await self.get_toggle(db, school_id=school_id)
        if not toggle:
            return False

        feature_map = {
            "ig": toggle.enable_ig,
            "discord": toggle.enable_discord,
            "comments": toggle.enable_comments,
            "cross_school": toggle.enable_cross_school
        }

        return feature_map.get(feature, False)

school_feature_service = SchoolFeatureService() 
