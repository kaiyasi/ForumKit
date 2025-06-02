import os
from typing import Optional, List
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from app.crud import ig_template as template_crud
from app.crud import post as post_crud
from app.schemas.ig_template import IGTemplateCreate, IGTemplateUpdate
from app.models.user import User, UserRole
from app.core.config import settings

class IGRenderService:
    def __init__(self):
        self.upload_dir = os.path.join(settings.UPLOAD_DIR, "ig_templates")
        self.output_dir = os.path.join(settings.UPLOAD_DIR, "ig_output")
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    async def create_template(
        self,
        db: Session,
        *,
        template_in: IGTemplateCreate,
        background_file: UploadFile,
        admin: User
    ) -> dict:
        """
        創建新的 IG 模板
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        # 保存背景圖片
        background_path = os.path.join(self.upload_dir, f"{template_in.name}_{background_file.filename}")
        with open(background_path, "wb") as f:
            f.write(await background_file.read())

        # 創建模板
        template = template_crud.ig_template.create(
            db=db,
            obj_in=IGTemplateCreate(
                **template_in.dict(),
                background_image=background_path
            )
        )

        return template

    def render_post(
        self,
        db: Session,
        *,
        post_id: int,
        template_id: Optional[int] = None
    ) -> str:
        """
        渲染貼文為 IG 圖片
        """
        # 獲取貼文
        post = post_crud.post.get(db, id=post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="貼文不存在"
            )

        # 獲取模板
        if template_id:
            template = template_crud.ig_template.get(db, id=template_id)
        else:
            template = template_crud.ig_template.get_active(db)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )

        # 創建圖片
        background = Image.open(template.background_image)
        draw = ImageDraw.Draw(background)

        # 渲染文字區域
        for text_area in template.config["text_areas"]:
            if text_area["id"] == "title":
                text = post.title
            elif text_area["id"] == "content":
                text = post.content
            else:
                continue

            # 設置字體
            font = ImageFont.truetype(
                text_area["font"],
                text_area["font_size"]
            )

            # 繪製文字
            draw.text(
                (text_area["x"], text_area["y"]),
                text,
                font=font,
                fill=text_area["color"],
                align=text_area["align"]
            )

        # 添加時間戳
        timestamp_config = template.config["timestamp"]
        timestamp = datetime.now().strftime(timestamp_config["format"])
        font = ImageFont.truetype(
            timestamp_config["font"],
            timestamp_config["font_size"]
        )
        draw.text(
            (timestamp_config["x"], timestamp_config["y"]),
            timestamp,
            font=font,
            fill=timestamp_config["color"]
        )

        # 添加 LOGO
        if "logo" in template.config:
            logo_config = template.config["logo"]
            logo = Image.open(settings.LOGO_PATH)
            logo = logo.resize((logo_config["width"], logo_config["height"]))
            background.paste(logo, (logo_config["x"], logo_config["y"]))

        # 保存圖片
        output_path = os.path.join(
            self.output_dir,
            f"post_{post_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        background.save(output_path, "PNG")

        return output_path

    def get_templates(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        admin: User
    ) -> List[dict]:
        """
        獲取模板列表
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        return template_crud.ig_template.get_multi(
            db=db,
            skip=skip,
            limit=limit
        )

    def update_template(
        self,
        db: Session,
        *,
        template_id: int,
        template_in: IGTemplateUpdate,
        background_file: Optional[UploadFile] = None,
        admin: User
    ) -> dict:
        """
        更新模板
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        template = template_crud.ig_template.get(db, id=template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )

        # 更新背景圖片
        if background_file:
            background_path = os.path.join(
                self.upload_dir,
                f"{template.name}_{background_file.filename}"
            )
            with open(background_path, "wb") as f:
                f.write(await background_file.read())
            template_in.background_image = background_path

        return template_crud.ig_template.update(
            db=db,
            db_obj=template,
            obj_in=template_in
        )

ig_render_service = IGRenderService() 