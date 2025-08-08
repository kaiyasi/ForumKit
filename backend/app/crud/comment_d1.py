"""
D1 資料庫版本的評論 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from app.crud.d1_base import CRUDBase
from app.schemas.comment import CommentCreate, CommentUpdate
from datetime import datetime

class CRUDCommentD1(CRUDBase[Dict[str, Any], CommentCreate, CommentUpdate]):
    """D1 評論 CRUD 操作"""
    
    def __init__(self):
        super().__init__("comments")
    
    async def create(self, obj_in: CommentCreate) -> Dict[str, Any]:
        """創建新評論"""
        comment_data = obj_in.model_dump()
        comment_data.update({
            "status": "pending",
            "like_count": 0,
            "created_at": datetime.utcnow().isoformat()
        })
        
        # 插入記錄並獲取 ID
        new_id = await self.adapter.insert(self.table_name, comment_data)
        
        # 增加貼文評論數量
        if comment_data.get("post_id"):
            await self._increment_post_comment_count(comment_data["post_id"])
        
        # 返回新創建的評論
        return await self.get(new_id)
    
    async def get_comments_by_post(
        self, 
        post_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = "approved"
    ) -> List[Dict[str, Any]]:
        """根據貼文 ID 獲取評論列表"""
        where_clause = {"post_id": post_id}
        if status:
            where_clause["status"] = status
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            where=where_clause,
            order_by="created_at ASC"
        )
    
    async def get_comments_by_user(
        self, 
        author_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """根據用戶 ID 獲取評論列表"""
        return await self.get_multi_by_field(
            field_name="author_id",
            field_value=author_id,
            skip=skip,
            limit=limit,
            order_by="created_at DESC"
        )
    
    async def get_pending_comments(
        self, 
        school_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """獲取待審核的評論"""
        where_clause = {"status": "pending"}
        if school_id:
            where_clause["school_id"] = school_id
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            where=where_clause,
            order_by="created_at ASC"
        )
    
    async def approve_comment(
        self, 
        comment_id: int, 
        reviewer_id: int
    ) -> Optional[Dict[str, Any]]:
        """審核通過評論"""
        return await self.update(
            id=comment_id, 
            obj_in={
                "status": "approved",
                "reviewed_by": reviewer_id,
                "reviewed_at": datetime.utcnow().isoformat()
            }
        )
    
    async def reject_comment(
        self, 
        comment_id: int, 
        reviewer_id: int
    ) -> Optional[Dict[str, Any]]:
        """拒絕評論"""
        # 獲取評論資訊以減少貼文評論數量
        comment = await self.get(comment_id)
        
        result = await self.update(
            id=comment_id, 
            obj_in={
                "status": "rejected",
                "reviewed_by": reviewer_id,
                "reviewed_at": datetime.utcnow().isoformat()
            }
        )
        
        # 減少貼文評論數量
        if comment and comment.get("post_id"):
            await self._decrement_post_comment_count(comment["post_id"])
        
        return result
    
    async def increment_like_count(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """增加按讚次數"""
        sql = "UPDATE comments SET like_count = like_count + 1 WHERE id = ?"
        await self.adapter.execute_query(sql, [comment_id])
        return await self.get(comment_id)
    
    async def decrement_like_count(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """減少按讚次數"""
        sql = "UPDATE comments SET like_count = CASE WHEN like_count > 0 THEN like_count - 1 ELSE 0 END WHERE id = ?"
        await self.adapter.execute_query(sql, [comment_id])
        return await self.get(comment_id)
    
    async def get_comment_replies(
        self, 
        parent_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """獲取評論的回覆"""
        return await self.get_multi_by_field(
            field_name="parent_id",
            field_value=parent_id,
            skip=skip,
            limit=limit,
            order_by="created_at ASC"
        )
    
    async def get_comments_by_school(
        self, 
        school_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """根據學校 ID 獲取評論列表"""
        where_clause = {"school_id": school_id}
        if status:
            where_clause["status"] = status
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            where=where_clause,
            order_by="created_at DESC"
        )
    
    async def delete_comment(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """軟刪除評論"""
        # 獲取評論資訊以減少貼文評論數量
        comment = await self.get(comment_id)
        
        result = await self.soft_delete(comment_id)
        
        # 減少貼文評論數量
        if comment and comment.get("post_id"):
            await self._decrement_post_comment_count(comment["post_id"])
        
        return result
    
    async def _increment_post_comment_count(self, post_id: int):
        """增加貼文評論數量"""
        sql = "UPDATE posts SET comment_count = comment_count + 1 WHERE id = ?"
        await self.adapter.execute_query(sql, [post_id])
    
    async def _decrement_post_comment_count(self, post_id: int):
        """減少貼文評論數量"""
        sql = "UPDATE posts SET comment_count = CASE WHEN comment_count > 0 THEN comment_count - 1 ELSE 0 END WHERE id = ?"
        await self.adapter.execute_query(sql, [post_id])

# 創建全域實例
comment_d1 = CRUDCommentD1() 