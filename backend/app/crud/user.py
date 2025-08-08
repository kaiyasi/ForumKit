from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
import hashlib

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        # 哈希密碼
        hashed_password = get_password_hash(obj_in.password)
        
        # 創建 email_hash
        email_hash = hashlib.sha256(obj_in.email.encode()).hexdigest()
        
        # 創建用戶對象
        db_obj = User(
            email=obj_in.email,
            email_hash=email_hash,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            school_id=obj_in.school_id,
            role=obj_in.role or UserRole.USER
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_google_id(self, db: Session, *, google_id: str) -> Optional[User]:
        return db.query(User).filter(User.google_id == google_id).first()
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        認證用戶的電子郵件和密碼
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """
        檢查用戶是否為活躍狀態
        """
        return user.is_active
    
    def update_last_login(self, db: Session, *, user: User) -> User:
        """
        更新用戶最後登錄時間
        """
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

user = CRUDUser(User)
