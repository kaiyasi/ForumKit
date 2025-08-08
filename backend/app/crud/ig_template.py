from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.ig_template import IGTemplate
from app.schemas.ig_template import IGTemplateCreate, IGTemplateUpdate

class CRUDIGTemplate(CRUDBase[IGTemplate, IGTemplateCreate, IGTemplateUpdate]):
    def get_active_templates(self, db: Session) -> List[IGTemplate]:
        return db.query(IGTemplate).filter(IGTemplate.is_active == True).all()

ig_template = CRUDIGTemplate(IGTemplate)
