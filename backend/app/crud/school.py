from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolUpdate

class CRUDSchool(CRUDBase[School, SchoolCreate, SchoolUpdate]):
    def get_by_code(self, db: Session, *, code: str) -> School | None:
        # Assuming the 'slug' field stores the school code.
        return db.query(School).filter(School.slug == code.lower()).first()


school = CRUDSchool(School)
