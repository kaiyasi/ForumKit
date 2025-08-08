from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.school_feature_toggle import SchoolFeatureToggle
from app.schemas.school_feature_toggle import SchoolFeatureToggleCreate, SchoolFeatureToggleUpdate

class CRUDSchoolFeatureToggle(CRUDBase[SchoolFeatureToggle, SchoolFeatureToggleCreate, SchoolFeatureToggleUpdate]):
    def get_by_school(self, db: Session, *, school_id: int) -> Optional[SchoolFeatureToggle]:
        return db.query(SchoolFeatureToggle).filter(SchoolFeatureToggle.school_id == school_id).first()

school_feature_toggle = CRUDSchoolFeatureToggle(SchoolFeatureToggle)
