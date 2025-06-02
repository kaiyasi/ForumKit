import aiohttp
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import discord_settings as settings_crud
from app.crud import post as post_crud
from app.schemas.discord_settings import DiscordSettingsCreate, DiscordSettingsUpdate
from app.models.user import User, UserRole
from app.core.config import settings

class DiscordService:
    async def create_settings(
        self,
        db: Session,
        *,
        settings_in: DiscordSettingsCreate,
        admin: User
    ) -> dict:
        """
        創建 Discord 設定
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        # 檢查是否已存在
        existing = settings_crud.discord_settings.get_by_school(
            db=db,
            school_id=settings_in.school_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="該學校已有 Discord 設定"
            )

        return settings_crud.discord_settings.create(
            db=db,
            obj_in=settings_in
        )

    async def update_settings(
        self,
        db: Session,
        *,
        settings_id: int,
        settings_in: DiscordSettingsUpdate,
        admin: User
    ) -> dict:
        """
        更新 Discord 設定
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        settings = settings_crud.discord_settings.get(db, id=settings_id)
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discord 設定不存在"
            )

        return settings_crud.discord_settings.update(
            db=db,
            db_obj=settings,
            obj_in=settings_in
        )

    async def publish_post(
        self,
        db: Session,
        *,
        post_id: int,
        admin: User
    ) -> Dict[str, Any]:
        """
        發布貼文到 Discord
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

        # 獲取 Discord 設定
        settings = settings_crud.discord_settings.get_by_school(
            db=db,
            school_id=post.school_id
        )
        if not settings or not settings.post_webhook_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="學校未設定 Discord webhook"
            )

        # 準備訊息內容
        post_url = f"{settings.FRONTEND_URL}/posts/{post.id}"
        embed = {
            "title": post.title,
            "description": post.content[:1000],  # Discord 限制描述長度
            "url": post_url,
            "color": 0x3498db,  # 藍色
            "fields": [
                {
                    "name": "作者",
                    "value": f"匿名用戶",
                    "inline": True
                },
                {
                    "name": "發布時間",
                    "value": post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }
            ]
        }

        # 發送 webhook
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.post_webhook_url,
                    json={"embeds": [embed]}
                ) as response:
                    if response.status != 204:
                        raise Exception(f"Discord API 回應錯誤: {response.status}")
                    return {"success": True}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Discord 推播失敗: {str(e)}"
            )

    async def send_report(
        self,
        db: Session,
        *,
        post_id: int,
        report_reason: str,
        reporter: User
    ) -> Dict[str, Any]:
        """
        發送檢舉通知到 Discord
        """
        # 獲取貼文
        post = post_crud.post.get(db, id=post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="貼文不存在"
            )

        # 獲取 Discord 設定
        settings = settings_crud.discord_settings.get_by_school(
            db=db,
            school_id=post.school_id
        )
        if not settings or not settings.report_webhook_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="學校未設定 Discord 檢舉 webhook"
            )

        # 準備訊息內容
        post_url = f"{settings.FRONTEND_URL}/posts/{post.id}"
        embed = {
            "title": "⚠️ 新檢舉通知",
            "description": f"**檢舉原因：**\n{report_reason}",
            "url": post_url,
            "color": 0xe74c3c,  # 紅色
            "fields": [
                {
                    "name": "被檢舉貼文",
                    "value": post.title,
                    "inline": False
                },
                {
                    "name": "檢舉者",
                    "value": reporter.username,
                    "inline": True
                },
                {
                    "name": "檢舉時間",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }
            ]
        }

        # 發送 webhook
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.report_webhook_url,
                    json={"embeds": [embed]}
                ) as response:
                    if response.status != 204:
                        raise Exception(f"Discord API 回應錯誤: {response.status}")
                    return {"success": True}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Discord 檢舉通知失敗: {str(e)}"
            )

discord_service = DiscordService() 