from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.ig_template import (
    IGTemplateCreate,
    IGTemplateUpdate,
    IGTemplateRead,
    IGTemplatePreview
)
from app.schemas.ig_account import (
    IGAccountCreate,
    IGAccountUpdate,
    IGAccountRead,
    IGPostPublish
)
from app.models.user import User, UserRole
from app.services.ig_render import ig_render_service
from app.services.ig_publish import ig_publish_service

router = APIRouter()

# 模板管理路由
@router.post("/templates", response_model=IGTemplateRead)
async def create_template(
    *,
    db: Session = Depends(deps.get_db),
    template_in: IGTemplateCreate = Depends(),
    background_file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    創建新的 IG 模板（僅限管理員）
    """
    return await ig_render_service.create_template(
        db=db,
        template_in=template_in,
        background_file=background_file,
        admin=current_user
    )

@router.get("/templates", response_model=List[IGTemplateRead])
def list_templates(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    獲取模板列表（僅限管理員）
    """
    return ig_render_service.get_templates(
        db=db,
        skip=skip,
        limit=limit,
        admin=current_user
    )

@router.patch("/templates/{template_id}", response_model=IGTemplateRead)
async def update_template(
    *,
    db: Session = Depends(deps.get_db),
    template_id: int,
    template_in: IGTemplateUpdate = Depends(),
    background_file: UploadFile = File(None),
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    更新模板（僅限管理員）
    """
    return await ig_render_service.update_template(
        db=db,
        template_id=template_id,
        template_in=template_in,
        background_file=background_file,
        admin=current_user
    )

# 圖片渲染路由
@router.post("/render/{post_id}")
def render_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
    template_id: int = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    渲染貼文為 IG 圖片
    """
    output_path = ig_render_service.render_post(
        db=db,
        post_id=post_id,
        template_id=template_id
    )
    return FileResponse(
        output_path,
        media_type="image/png",
        filename=f"post_{post_id}.png"
    )

@router.post("/preview")
def preview_template(
    *,
    db: Session = Depends(deps.get_db),
    preview_in: IGTemplatePreview,
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    預覽模板效果（僅限管理員）
    """
    output_path = ig_render_service.render_post(
        db=db,
        post_id=preview_in.post_id,
        template_id=preview_in.template_id
    )
    return FileResponse(
        output_path,
        media_type="image/png",
        filename=f"preview_{preview_in.post_id}.png"
    )

# IG 帳號管理路由
@router.post("/accounts", response_model=IGAccountRead)
async def create_account(
    *,
    db: Session = Depends(deps.get_db),
    account_in: IGAccountCreate,
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    創建 IG 帳號設定（僅限管理員）
    """
    return await ig_publish_service.create_account(
        db=db,
        account_in=account_in,
        admin=current_user
    )

@router.patch("/accounts/{account_id}", response_model=IGAccountRead)
async def update_account(
    *,
    db: Session = Depends(deps.get_db),
    account_id: int,
    account_in: IGAccountUpdate,
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    更新 IG 帳號設定（僅限管理員）
    """
    return await ig_publish_service.update_account(
        db=db,
        account_id=account_id,
        account_in=account_in,
        admin=current_user
    )

# IG 發布路由
@router.post("/publish/{post_id}", response_model=Dict[str, Any])
async def publish_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
    publish_in: IGPostPublish,
    current_user: User = Depends(deps.get_current_active_user_with_role(UserRole.ADMIN))
):
    """
    發布貼文到 IG（僅限管理員）
    """
    return await ig_publish_service.publish_post(
        db=db,
        post_id=post_id,
        publish_in=publish_in,
        admin=current_user
    ) 