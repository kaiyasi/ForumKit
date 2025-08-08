from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.discord_settings import DiscordSettings
from app.schemas.discord_settings import DiscordSettingsCreate, DiscordSettingsUpdate

class CRUDDiscordSettings(CRUDBase[DiscordSettings, DiscordSettingsCreate, DiscordSettingsUpdate]):
    def get_by_school(self, db: Session, *, school_id: int) -> Optional[DiscordSettings]:
        return db.query(DiscordSettings).filter(DiscordSettings.school_id == school_id).first()

discord_settings = CRUDDiscordSettings(DiscordSettings)
