from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.admin_log import AdminLog
from app.schemas.admin_log import AdminLogCreate, AdminLogUpdate

class CRUDAdminLog(CRUDBase[AdminLog, AdminLogCreate, AdminLogUpdate]):
    """
    CRUD operations for Admin Log
    """
    
    def get_multi_by_admin(
        self,
        db: Session,
        *,
        admin_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AdminLog]:
        """
        Get admin logs by admin id
        """
        return (
            db.query(self.model)
            .filter(AdminLog.admin_id == admin_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_admin(
        self,
        db: Session,
        *,
        obj_in: AdminLogCreate,
        admin_id: int
    ) -> AdminLog:
        """
        Create admin log with admin
        """
        obj_in_data = obj_in.model_dump()
        obj_in_data["admin_id"] = admin_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

admin_log = CRUDAdminLog(AdminLog) 