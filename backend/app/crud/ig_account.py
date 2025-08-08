from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.ig_account import IGAccount
from app.schemas.ig_account import IGAccountCreate, IGAccountUpdate

class CRUDIGAccount(CRUDBase[IGAccount, IGAccountCreate, IGAccountUpdate]):
    def get_by_school(self, db: Session, *, school_id: int) -> Optional[IGAccount]:
        return db.query(IGAccount).filter(IGAccount.school_id == school_id).first()
    
    def get_active_by_school(self, db: Session, *, school_id: int) -> Optional[IGAccount]:
        return db.query(IGAccount).filter(
            IGAccount.school_id == school_id,
            IGAccount.is_active == True
        ).first()

ig_account = CRUDIGAccount(IGAccount)
