"""
CloudFlare D1 Database Adapter
提供與 D1 資料庫的連接和操作介面
"""
import httpx
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from app.core.config import settings

class D1Adapter:
    """CloudFlare D1 資料庫適配器"""
    
    def __init__(self, account_id: str, database_id: str, api_token: str):
        self.account_id = account_id
        self.database_id = database_id
        self.api_token = api_token
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def execute_query(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """執行 SQL 查詢"""
        async with httpx.AsyncClient() as client:
            payload = {
                "sql": sql
            }
            if params:
                payload["params"] = params
            
            response = await client.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"D1 Query failed: {response.text}")
            
            return response.json()
    
    async def execute_batch(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批次執行多個 SQL 查詢"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=queries
            )
            
            if response.status_code != 200:
                raise Exception(f"D1 Batch query failed: {response.text}")
            
            return response.json()
    
    async def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入資料並返回新增記錄的 ID"""
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]
        values = [data[col] for col in columns]
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        result = await self.execute_query(sql, values)
        
        # 獲取插入的 ID
        if result['success'] and result['result']:
            return result['result'][0]['meta']['last_row_id']
        else:
            raise Exception(f"Insert failed: {result}")
    
    async def select(self, table: str, where: Optional[Dict[str, Any]] = None, 
                    limit: Optional[int] = None, offset: Optional[int] = None,
                    order_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """查詢資料"""
        sql = f"SELECT * FROM {table}"
        params = []
        
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            sql += f" WHERE {' AND '.join(conditions)}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
            if offset:
                sql += f" OFFSET {offset}"
        
        result = await self.execute_query(sql, params)
        
        if result['success']:
            return result['result'][0]['results']
        else:
            raise Exception(f"Select failed: {result}")
    
    async def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """更新資料"""
        set_clauses = []
        params = []
        
        for key, value in data.items():
            set_clauses.append(f"{key} = ?")
            params.append(value)
        
        conditions = []
        for key, value in where.items():
            conditions.append(f"{key} = ?")
            params.append(value)
        
        sql = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(conditions)}"
        
        result = await self.execute_query(sql, params)
        
        if result['success']:
            return result['result'][0]['meta']['changes']
        else:
            raise Exception(f"Update failed: {result}")
    
    async def delete(self, table: str, where: Dict[str, Any]) -> int:
        """刪除資料"""
        conditions = []
        params = []
        
        for key, value in where.items():
            conditions.append(f"{key} = ?")
            params.append(value)
        
        sql = f"DELETE FROM {table} WHERE {' AND '.join(conditions)}"
        
        result = await self.execute_query(sql, params)
        
        if result['success']:
            return result['result'][0]['meta']['changes']
        else:
            raise Exception(f"Delete failed: {result}")
    
    async def custom_query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """執行自定義 SQL 查詢"""
        result = await self.execute_query(sql, params)
        
        if result['success']:
            return result['result'][0]['results']
        else:
            raise Exception(f"Custom query failed: {result}")

class D1Session:
    """模擬 SQLAlchemy Session 的 D1 會話類別"""
    
    def __init__(self, adapter: D1Adapter):
        self.adapter = adapter
        self._pending_operations = []
    
    def add(self, instance):
        """添加新實例（模擬 SQLAlchemy）"""
        self._pending_operations.append(('add', instance))
    
    def delete(self, instance):
        """刪除實例（模擬 SQLAlchemy）"""
        self._pending_operations.append(('delete', instance))
    
    async def commit(self):
        """提交所有待處理的操作"""
        # 這裡實現批次操作
        for operation, instance in self._pending_operations:
            if operation == 'add':
                await self._insert_instance(instance)
            elif operation == 'delete':
                await self._delete_instance(instance)
        
        self._pending_operations.clear()
    
    def rollback(self):
        """回滾操作"""
        self._pending_operations.clear()
    
    def close(self):
        """關閉會話"""
        self._pending_operations.clear()
    
    async def _insert_instance(self, instance):
        """插入實例到資料庫"""
        table_name = getattr(instance, '__tablename__', None)
        if not table_name:
            raise ValueError("Instance must have __tablename__ attribute")
        
        data = {}
        for column in instance.__table__.columns:
            value = getattr(instance, column.name, None)
            if value is not None:
                data[column.name] = value
        
        result_id = await self.adapter.insert(table_name, data)
        setattr(instance, 'id', result_id)
    
    async def _delete_instance(self, instance):
        """從資料庫刪除實例"""
        table_name = getattr(instance, '__tablename__', None)
        if not table_name:
            raise ValueError("Instance must have __tablename__ attribute")
        
        id_value = getattr(instance, 'id', None)
        if id_value is None:
            raise ValueError("Instance must have an id to be deleted")
        
        await self.adapter.delete(table_name, {'id': id_value})

# 全域 D1 適配器實例
d1_adapter = None

def get_d1_adapter() -> D1Adapter:
    """獲取 D1 適配器實例"""
    global d1_adapter
    if d1_adapter is None:
        d1_adapter = D1Adapter(
            account_id=settings.CLOUDFLARE_ACCOUNT_ID,
            database_id=settings.CLOUDFLARE_D1_DATABASE_ID,
            api_token=settings.CLOUDFLARE_API_TOKEN
        )
    return d1_adapter

async def get_d1_session():
    """獲取 D1 會話（依賴注入用）"""
    adapter = get_d1_adapter()
    session = D1Session(adapter)
    try:
        yield session
    finally:
        session.close() 