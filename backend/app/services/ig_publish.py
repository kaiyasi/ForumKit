import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import ig_account as account_crud
from app.crud import post as post_crud
from app.schemas.ig_account import IGAccountCreate, IGAccountUpdate
from app.schemas.ig_post import IGPostPublish
from app.models.user import User, UserRole
from app.services.ig_render import ig_render_service
from app.core.config import settings

class IGPublishService:
    def __init__(self):
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    async def create_account(
        self,
        db: Session,
        *,
        account_in: IGAccountCreate,
        admin: User
    ) -> dict:
        """
        創建 IG 帳號設定
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        # 檢查是否已存在
        existing = account_crud.ig_account.get_by_school(
            db=db,
            school_id=account_in.school_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="該學校已有 IG 帳號設定"
            )

        # 驗證 token
        try:
            await self._validate_token(account_in.access_token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無效的 access token: {str(e)}"
            )

        return account_crud.ig_account.create(
            db=db,
            obj_in=account_in
        )

    async def update_account(
        self,
        db: Session,
        *,
        account_id: int,
        account_in: IGAccountUpdate,
        admin: User
    ) -> dict:
        """
        更新 IG 帳號設定
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        account = account_crud.ig_account.get(db, id=account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IG 帳號不存在"
            )

        # 如果更新 token，驗證新 token
        if account_in.access_token:
            try:
                await self._validate_token(account_in.access_token)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"無效的 access token: {str(e)}"
                )

        return account_crud.ig_account.update(
            db=db,
            db_obj=account,
            obj_in=account_in
        )

    async def publish_post(
        self,
        db: Session,
        *,
        post_id: int,
        publish_in: IGPostPublish,
        admin: User
    ) -> Dict[str, Any]:
        """
        發布貼文到 IG
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        # 獲取貼文
        post = post_crud.post.get(db, id=post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="貼文不存在"
            )

        # 獲取 IG 帳號
        account = account_crud.ig_account.get_by_school(
            db=db,
            school_id=post.school_id
        )
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="學校未設定 IG 帳號"
            )

        # 檢查 token 是否過期
        if datetime.now() >= account.token_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IG access token 已過期，請更新"
            )

        try:
            # 生成圖片
            image_path = ig_render_service.render_post(
                db=db,
                post_id=post_id
            )

            # 上傳圖片到 IG
            container_id = await self._create_media_container(
                account.access_token,
                image_path,
                publish_in.caption or post.title
            )

            # 發布貼文
            result = await self._publish_media(
                account.access_token,
                container_id
            )

            return {
                "success": True,
                "post_id": result["id"],
                "permalink": result.get("permalink", "")
            }

        except Exception as e:
            # 記錄錯誤
            error_msg = f"發布失敗: {str(e)}"
            if "token" in str(e).lower():
                error_msg += " (可能是 token 過期)"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

    async def _validate_token(self, token: str) -> bool:
        """
        驗證 access token
        """
        try:
            response = requests.get(
                f"{self.base_url}/me",
                params={"access_token": token}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            raise Exception(f"Token 驗證失敗: {str(e)}")

    async def _create_media_container(
        self,
        token: str,
        image_path: str,
        caption: str
    ) -> str:
        """
        創建媒體容器
        """
        # 上傳圖片
        with open(image_path, "rb") as image:
            response = requests.post(
                f"{self.base_url}/me/media",
                params={
                    "access_token": token,
                    "image_url": image_path,
                    "caption": caption
                }
            )
            response.raise_for_status()
            return response.json()["id"]

    async def _publish_media(
        self,
        token: str,
        container_id: str
    ) -> Dict[str, Any]:
        """
        發布媒體
        """
        response = requests.post(
            f"{self.base_url}/me/media_publish",
            params={
                "access_token": token,
                "creation_id": container_id
            }
        )
        response.raise_for_status()
        return response.json()

ig_publish_service = IGPublishService() 
