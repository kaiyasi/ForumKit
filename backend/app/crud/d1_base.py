"""
D1 資料庫專用的 CRUD 基類
提供基本的 CRUD 操作
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from app.db.d1_adapter import D1Adapter, get_d1_adapter

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """D1 CRUD 基類"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.adapter = get_d1_adapter()
    
    async def get(self, id: Any) -> Optional[Dict[str, Any]]:
        """根據 ID 獲取單筆記錄"""
        results = await self.adapter.select(
            table=self.table_name,
            where={"id": id},
            limit=1
        )
        return results[0] if results else None
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """獲取多筆記錄"""
        return await self.adapter.select(
            table=self.table_name,
            where=where,
            limit=limit,
            offset=skip,
            order_by=order_by
        )
    
    async def create(self, obj_in: CreateSchemaType) -> Dict[str, Any]:
        """創建新記錄"""
        obj_in_data = obj_in.model_dump()
        
        # 添加創建時間
        if "created_at" not in obj_in_data:
            from datetime import datetime
            obj_in_data["created_at"] = datetime.utcnow().isoformat()
        
        # 插入記錄並獲取 ID
        new_id = await self.adapter.insert(self.table_name, obj_in_data)
        
        # 返回新創建的記錄
        return await self.get(new_id)
    
    async def update(
        self, 
        id: Any, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """更新記錄"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # 添加更新時間
        if update_data:
            from datetime import datetime
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # 執行更新
            changes = await self.adapter.update(
                table=self.table_name,
                data=update_data,
                where={"id": id}
            )
            
            if changes > 0:
                return await self.get(id)
        
        return None
    
    async def remove(self, id: Any) -> Optional[Dict[str, Any]]:
        """刪除記錄"""
        # 先獲取要刪除的記錄
        db_obj = await self.get(id)
        
        if db_obj:
            # 執行刪除
            changes = await self.adapter.delete(
                table=self.table_name,
                where={"id": id}
            )
            
            if changes > 0:
                return db_obj
        
        return None
    
    async def soft_delete(self, id: Any) -> Optional[Dict[str, Any]]:
        """軟刪除記錄（設置 deleted_at）"""
        from datetime import datetime
        
        return await self.update(
            id=id,
            obj_in={"deleted_at": datetime.utcnow().isoformat()}
        )
    
    async def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        """計算記錄數量"""
        sql = f"SELECT COUNT(*) as count FROM {self.table_name}"
        params = []
        
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            sql += f" WHERE {' AND '.join(conditions)}"
        
        result = await self.adapter.custom_query(sql, params)
        return result[0]['count'] if result else 0
    
    async def exists(self, id: Any) -> bool:
        """檢查記錄是否存在"""
        result = await self.get(id)
        return result is not None
    
    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Dict[str, Any]]:
        """根據指定欄位獲取記錄"""
        results = await self.adapter.select(
            table=self.table_name,
            where={field_name: field_value},
            limit=1
        )
        return results[0] if results else None
    
    async def get_multi_by_field(
        self, 
        field_name: str, 
        field_value: Any,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """根據指定欄位獲取多筆記錄"""
        return await self.adapter.select(
            table=self.table_name,
            where={field_name: field_value},
            limit=limit,
            offset=skip,
            order_by=order_by
        ) 