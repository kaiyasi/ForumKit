"""
D1 資料庫版本的用戶 CRUD 操作
"""
from typing import Optional, Dict, Any
from app.crud.d1_base import CRUDBase
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
import hashlib
from datetime import datetime

class CRUDUserD1(CRUDBase[Dict[str, Any], UserCreate, UserUpdate]):
    """D1 用戶 CRUD 操作"""
    
    def __init__(self):
        super().__init__("users")
    
    async def create(self, obj_in: UserCreate) -> Dict[str, Any]:
        """創建新用戶"""
        # 哈希密碼
        hashed_password = get_password_hash(obj_in.password)
        
        # 創建 email_hash
        email_hash = hashlib.sha256(obj_in.email.encode()).hexdigest()
        
        # 準備用戶資料
        user_data = obj_in.model_dump(exclude={"password"})
        user_data.update({
            "hashed_password": hashed_password,
            "email_hash": email_hash,
            "role": obj_in.role or "user",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "created_at": datetime.utcnow().isoformat()
        })
        
        # 插入記錄並獲取 ID
        new_id = await self.adapter.insert(self.table_name, user_data)
        
        # 返回新創建的用戶
        return await self.get(new_id)
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根據 email 獲取用戶"""
        return await self.get_by_field("email", email)
    
    async def get_by_email_hash(self, email_hash: str) -> Optional[Dict[str, Any]]:
        """根據 email_hash 獲取用戶"""
        return await self.get_by_field("email_hash", email_hash)
    
    async def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """認證用戶的電子郵件和密碼"""
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        return user
    
    def is_active(self, user: Dict[str, Any]) -> bool:
        """檢查用戶是否為活躍狀態"""
        return user.get("is_active", False)
    
    def is_superuser(self, user: Dict[str, Any]) -> bool:
        """檢查用戶是否為超級用戶"""
        return user.get("is_superuser", False)
    
    async def update_password(self, user_id: int, new_password: str) -> Optional[Dict[str, Any]]:
        """更新用戶密碼"""
        hashed_password = get_password_hash(new_password)
        return await self.update(
            id=user_id,
            obj_in={"hashed_password": hashed_password}
        )
    
    async def update_last_login(self, user_id: int) -> Optional[Dict[str, Any]]:
        """更新用戶最後登錄時間"""
        return await self.update(
            id=user_id,
            obj_in={"last_login": datetime.utcnow().isoformat()}
        )
    
    async def activate_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """激活用戶"""
        return await self.update(
            id=user_id,
            obj_in={"is_active": True}
        )
    
    async def deactivate_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """停用用戶"""
        return await self.update(
            id=user_id,
            obj_in={"is_active": False}
        )
    
    async def verify_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """驗證用戶"""
        return await self.update(
            id=user_id,
            obj_in={"is_verified": True}
        )
    
    async def get_users_by_school(
        self, 
        school_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """根據學校 ID 獲取用戶列表"""
        return await self.get_multi_by_field(
            field_name="school_id",
            field_value=school_id,
            skip=skip,
            limit=limit,
            order_by="created_at DESC"
        )
    
    async def get_users_by_role(
        self, 
        role: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """根據角色獲取用戶列表"""
        return await self.get_multi_by_field(
            field_name="role",
            field_value=role,
            skip=skip,
            limit=limit,
            order_by="created_at DESC"
        )
    
    async def search_users(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """搜尋用戶（根據用戶名或全名）"""
        sql = """
        SELECT * FROM users 
        WHERE (username LIKE ? OR full_name LIKE ?) 
        AND deleted_at IS NULL
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
        """
        search_term = f"%{query}%"
        
        return await self.adapter.custom_query(
            sql, 
            [search_term, search_term, limit, skip]
        )

# 創建全域實例
user_d1 = CRUDUserD1() 