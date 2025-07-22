from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class DiscordSettingsBase(BaseModel):
    school_id: int
    post_webhook_url: Optional[HttpUrl] = None
    report_webhook_url: Optional[HttpUrl] = None

class DiscordSettingsCreate(DiscordSettingsBase):
    pass

class DiscordSettingsUpdate(BaseModel):
    post_webhook_url: Optional[HttpUrl] = None
    report_webhook_url: Optional[HttpUrl] = None

class DiscordSettingsRead(DiscordSettingsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True 
