from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class SchoolFeatureToggleBase(BaseModel):
    school_id: int
    enable_ig: bool = False
    enable_discord: bool = False
    enable_comments: bool = True
    enable_cross_school: bool = True
    ig_template_id: Optional[int] = None
    ig_publish_auto: bool = False
    discord_webhook_url: Optional[str] = None
    discord_channel_name: Optional[str] = None
    discord_report_webhook_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class SchoolFeatureToggleCreate(SchoolFeatureToggleBase):
    pass

class SchoolFeatureToggleUpdate(BaseModel):
    enable_ig: Optional[bool] = None
    enable_discord: Optional[bool] = None
    enable_comments: Optional[bool] = None
    enable_cross_school: Optional[bool] = None
    ig_template_id: Optional[int] = None
    ig_publish_auto: Optional[bool] = None
    discord_webhook_url: Optional[str] = None
    discord_channel_name: Optional[str] = None
    discord_report_webhook_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class SchoolFeatureToggleRead(SchoolFeatureToggleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True 
