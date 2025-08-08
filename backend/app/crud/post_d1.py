"""
D1 資料庫版本的貼文 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from app.crud.d1_base import CRUDBase
from app.schemas.post import PostCreate, PostUpdate
from datetime import datetime

class CRUDPostD1(CRUDBase[Dict[str, Any], PostCreate, PostUpdate]):
    """D1 貼文 CRUD 操作"""
    
    def __init__(self):
        super().__init__("posts")
    
    async def create(self, obj_in: PostCreate) -> Dict[str, Any]:
        """創建新貼文"""
        post_data = obj_in.model_dump()
        post_data.update({
            "status": "pending",
            "view_count": 0,
            "like_count": 0,
            "comment_count": 0,
            "created_at": datetime.utcnow().isoformat()
        })
        
        # 插入記錄並獲取 ID
        new_id = await self.adapter.insert(self.table_name, post_data)
        
        # 返回新創建的貼文
        return await self.get(new_id)
    
    async def get_posts_by_school(
        self, 
        school_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """根據學校 ID 獲取貼文列表"""
        where_clause = {"school_id": school_id}
        if status:
            where_clause["status"] = status
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            where=where_clause,
            order_by="created_at DESC"
        )
    
    async def get_posts_by_author(
        self, 
        author_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """根據作者 ID 獲取貼文列表"""
        return await self.get_multi_by_field(
            field_name="author_id",
            field_value=author_id,
            skip=skip,
            limit=limit,
            order_by="created_at DESC"
        )
    
    async def get_pending_posts(
        self, 
        school_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """獲取待審核的貼文"""
        where_clause = {"status": "pending"}
        if school_id:
            where_clause["school_id"] = school_id
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            where=where_clause,
            order_by="created_at ASC"
        )
    
    async def approve_post(
        self, 
        post_id: int, 
        reviewer_id: int,
        review_comment: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """審核通過貼文"""
        update_data = {
            "status": "approved",
            "reviewed_by": reviewer_id,
            "reviewed_at": datetime.utcnow().isoformat()
        }
        if review_comment:
            update_data["review_comment"] = review_comment
        
        return await self.update(id=post_id, obj_in=update_data)
    
    async def reject_post(
        self, 
        post_id: int, 
        reviewer_id: int,
        review_comment: str
    ) -> Optional[Dict[str, Any]]:
        """拒絕貼文"""
        update_data = {
            "status": "rejected",
            "reviewed_by": reviewer_id,
            "reviewed_at": datetime.utcnow().isoformat(),
            "review_comment": review_comment
        }
        
        return await self.update(id=post_id, obj_in=update_data)
    
    async def increment_view_count(self, post_id: int) -> Optional[Dict[str, Any]]:
        """增加瀏覽次數"""
        sql = "UPDATE posts SET view_count = view_count + 1 WHERE id = ?"
        await self.adapter.execute_query(sql, [post_id])
        return await self.get(post_id)
    
    async def increment_like_count(self, post_id: int) -> Optional[Dict[str, Any]]:
        """增加按讚次數"""
        sql = "UPDATE posts SET like_count = like_count + 1 WHERE id = ?"
        await self.adapter.execute_query(sql, [post_id])
        return await self.get(post_id)
    
    async def decrement_like_count(self, post_id: int) -> Optional[Dict[str, Any]]:
        """減少按讚次數"""
        sql = "UPDATE posts SET like_count = CASE WHEN like_count > 0 THEN like_count - 1 ELSE 0 END WHERE id = ?"
        await self.adapter.execute_query(sql, [post_id])
        return await self.get(post_id)
    
    async def increment_comment_count(self, post_id: int) -> Optional[Dict[str, Any]]:
        """增加評論次數"""
        sql = "UPDATE posts SET comment_count = comment_count + 1 WHERE id = ?"
        await self.adapter.execute_query(sql, [post_id])
        return await self.get(post_id)
    
    async def decrement_comment_count(self, post_id: int) -> Optional[Dict[str, Any]]:
        """減少評論次數"""
        sql = "UPDATE posts SET comment_count = CASE WHEN comment_count > 0 THEN comment_count - 1 ELSE 0 END WHERE id = ?"
        await self.adapter.execute_query(sql, [post_id])
        return await self.get(post_id)
    
    async def search_posts(
        self, 
        query: str, 
        school_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """搜尋貼文（根據標題或內容）"""
        sql = """
        SELECT * FROM posts 
        WHERE (title LIKE ? OR content LIKE ?) 
        AND status = 'approved'
        AND deleted_at IS NULL
        """
        params = [f"%{query}%", f"%{query}%"]
        
        if school_id:
            sql += " AND school_id = ?"
            params.append(school_id)
        
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        return await self.adapter.custom_query(sql, params)
    
    async def get_popular_posts(
        self, 
        school_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """獲取熱門貼文（根據按讚數和評論數）"""
        sql = """
        SELECT * FROM posts 
        WHERE status = 'approved'
        AND deleted_at IS NULL
        AND created_at >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        
        if school_id:
            sql += " AND school_id = ?"
            params.append(school_id)
        
        sql += " ORDER BY (like_count + comment_count * 2) DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        return await self.adapter.custom_query(sql, params)
    
    async def get_post_statistics(self, school_id: Optional[int] = None) -> Dict[str, int]:
        """獲取貼文統計資訊"""
        sql_base = "SELECT status, COUNT(*) as count FROM posts"
        params = []
        
        if school_id:
            sql_base += " WHERE school_id = ?"
            params.append(school_id)
        
        sql_base += " GROUP BY status"
        
        results = await self.adapter.custom_query(sql_base, params)
        
        stats = {
            "total": 0,
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "deleted": 0
        }
        
        for row in results:
            stats[row["status"]] = row["count"]
            stats["total"] += row["count"]
        
        return stats

# 創建全域實例
post_d1 = CRUDPostD1() 