"""
D1 資料庫版本的學校 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from app.crud.d1_base import CRUDBase
from app.schemas.school import SchoolCreate, SchoolUpdate
from datetime import datetime

class CRUDSchoolD1(CRUDBase[Dict[str, Any], SchoolCreate, SchoolUpdate]):
    """D1 學校 CRUD 操作"""
    
    def __init__(self):
        super().__init__("schools")
    
    async def create(self, obj_in: SchoolCreate) -> Dict[str, Any]:
        """創建新學校"""
        school_data = obj_in.model_dump()
        school_data.update({
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        })
        
        # 插入記錄並獲取 ID
        new_id = await self.adapter.insert(self.table_name, school_data)
        
        # 返回新創建的學校
        return await self.get(new_id)
    
    async def get_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """根據域名獲取學校"""
        return await self.get_by_field("domain", domain)
    
    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根據名稱獲取學校"""
        return await self.get_by_field("name", name)
    
    async def get_active_schools(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """獲取啟用的學校列表"""
        return await self.get_multi(
            skip=skip,
            limit=limit,
            where={"is_active": True},
            order_by="name"
        )
    
    async def activate_school(self, school_id: int) -> Optional[Dict[str, Any]]:
        """啟用學校"""
        return await self.update(
            id=school_id,
            obj_in={"is_active": True}
        )
    
    async def deactivate_school(self, school_id: int) -> Optional[Dict[str, Any]]:
        """停用學校"""
        return await self.update(
            id=school_id,
            obj_in={"is_active": False}
        )
    
    async def search_schools(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """搜尋學校（根據名稱或域名）"""
        sql = """
        SELECT * FROM schools 
        WHERE (name LIKE ? OR domain LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]
        
        if active_only:
            sql += " AND is_active = ?"
            params.append(True)
        
        sql += " ORDER BY name LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        return await self.adapter.custom_query(sql, params)
    
    async def get_school_statistics(self, school_id: int) -> Dict[str, int]:
        """獲取學校統計資訊"""
        # 用戶數量
        user_count_result = await self.adapter.custom_query(
            "SELECT COUNT(*) as count FROM users WHERE school_id = ? AND is_active = ?",
            [school_id, True]
        )
        user_count = user_count_result[0]["count"] if user_count_result else 0
        
        # 貼文數量
        post_count_result = await self.adapter.custom_query(
            "SELECT COUNT(*) as count FROM posts WHERE school_id = ? AND status = 'approved'",
            [school_id]
        )
        post_count = post_count_result[0]["count"] if post_count_result else 0
        
        # 評論數量
        comment_count_result = await self.adapter.custom_query(
            "SELECT COUNT(*) as count FROM comments WHERE school_id = ? AND status = 'approved'",
            [school_id]
        )
        comment_count = comment_count_result[0]["count"] if comment_count_result else 0
        
        return {
            "user_count": user_count,
            "post_count": post_count,
            "comment_count": comment_count
        }

# 創建全域實例
school_d1 = CRUDSchoolD1() 