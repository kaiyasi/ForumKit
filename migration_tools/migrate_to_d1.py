#!/usr/bin/env python3
"""
ForumKit 資料庫遷移工具
從 PostgreSQL 遷移到 CloudFlare D1
"""

import asyncio
import os
import sys
import json
from typing import Dict, List, Any
from datetime import datetime

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.d1_adapter import D1Adapter
from app.core.config import settings

class PostgreSQLToD1Migrator:
    """PostgreSQL 到 D1 的資料遷移工具"""
    
    def __init__(self, pg_connection_string: str, d1_adapter: D1Adapter):
        self.pg_engine = create_engine(pg_connection_string)
        self.pg_session = sessionmaker(bind=self.pg_engine)()
        self.d1_adapter = d1_adapter
        
    async def migrate_table(self, table_name: str, batch_size: int = 100) -> int:
        """遷移單個資料表"""
        print(f"開始遷移表格: {table_name}")
        
        # 從 PostgreSQL 獲取資料
        query = text(f"SELECT * FROM {table_name}")
        result = self.pg_session.execute(query)
        rows = result.fetchall()
        columns = result.keys()
        
        print(f"找到 {len(rows)} 筆記錄")
        
        migrated_count = 0
        
        # 分批處理資料
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            
            # 準備批次插入的查詢
            batch_queries = []
            
            for row in batch:
                # 轉換 PostgreSQL 資料為 D1 格式
                data = self._convert_row_data(dict(zip(columns, row)))
                
                # 準備插入語句
                columns_str = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data.values()])
                sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                batch_queries.append({
                    "sql": sql,
                    "params": list(data.values())
                })
            
            # 執行批次插入
            try:
                await self.d1_adapter.execute_batch(batch_queries)
                migrated_count += len(batch)
                print(f"已遷移 {migrated_count}/{len(rows)} 筆記錄")
            except Exception as e:
                print(f"批次插入失敗: {e}")
                # 嘗試逐筆插入
                for query in batch_queries:
                    try:
                        await self.d1_adapter.execute_query(query["sql"], query["params"])
                        migrated_count += 1
                    except Exception as row_error:
                        print(f"記錄插入失敗: {row_error}")
        
        print(f"表格 {table_name} 遷移完成，共遷移 {migrated_count} 筆記錄")
        return migrated_count
    
    def _convert_row_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """轉換 PostgreSQL 資料格式為 D1 相容格式"""
        converted = {}
        
        for key, value in data.items():
            if value is None:
                converted[key] = None
            elif isinstance(value, datetime):
                # 轉換日期時間為 ISO 格式字符串
                converted[key] = value.isoformat()
            elif isinstance(value, bool):
                # 確保布林值正確轉換
                converted[key] = value
            elif isinstance(value, (dict, list)):
                # JSON 資料轉換為字符串
                converted[key] = json.dumps(value)
            else:
                converted[key] = value
        
        return converted
    
    async def verify_migration(self, table_name: str) -> bool:
        """驗證遷移結果"""
        # 計算 PostgreSQL 記錄數
        pg_query = text(f"SELECT COUNT(*) FROM {table_name}")
        pg_count = self.pg_session.execute(pg_query).scalar()
        
        # 計算 D1 記錄數
        d1_result = await self.d1_adapter.custom_query(f"SELECT COUNT(*) as count FROM {table_name}")
        d1_count = d1_result[0]['count'] if d1_result else 0
        
        print(f"表格 {table_name} 驗證: PostgreSQL({pg_count}) vs D1({d1_count})")
        
        return pg_count == d1_count
    
    async def full_migration(self) -> Dict[str, bool]:
        """執行完整遷移"""
        # 定義遷移順序（考慮外鍵依賴）
        migration_order = [
            "schools",
            "users", 
            "posts",
            "comments",
            "review_logs",
            "global_discussions",
            "global_review_logs",
            "school_feature_toggles",
            "admin_logs",
            "discord_settings",
            "ig_accounts",
            "ig_templates"
        ]
        
        results = {}
        
        print("開始完整資料庫遷移...")
        start_time = datetime.now()
        
        for table_name in migration_order:
            try:
                print(f"\n正在遷移表格: {table_name}")
                
                # 檢查表格是否存在
                try:
                    pg_query = text(f"SELECT 1 FROM {table_name} LIMIT 1")
                    self.pg_session.execute(pg_query)
                except Exception:
                    print(f"表格 {table_name} 不存在，跳過")
                    results[table_name] = True
                    continue
                
                # 執行遷移
                migrated_count = await self.migrate_table(table_name)
                
                # 驗證遷移
                verification_result = await self.verify_migration(table_name)
                results[table_name] = verification_result
                
                if verification_result:
                    print(f"✓ 表格 {table_name} 遷移成功")
                else:
                    print(f"✗ 表格 {table_name} 遷移失敗")
                    
            except Exception as e:
                print(f"✗ 表格 {table_name} 遷移錯誤: {e}")
                results[table_name] = False
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n遷移完成，耗時: {duration}")
        print("遷移結果摘要:")
        
        for table, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {table}")
        
        return results
    
    def close(self):
        """關閉連接"""
        self.pg_session.close()


async def main():
    """主函數"""
    print("ForumKit 資料庫遷移工具")
    print("從 PostgreSQL 遷移到 CloudFlare D1")
    print("=" * 50)
    
    # 檢查環境變數
    required_env_vars = [
        "CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_D1_DATABASE_ID", 
        "CLOUDFLARE_API_TOKEN"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("錯誤: 缺少必要的環境變數:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n請在 .env 檔案中設定這些變數")
        return
    
    # 獲取 PostgreSQL 連接字符串
    pg_connection = input("請輸入 PostgreSQL 連接字符串 (或按 Enter 使用默認): ").strip()
    if not pg_connection:
        pg_connection = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    
    print(f"PostgreSQL 連接: {pg_connection}")
    
    # 創建 D1 適配器
    d1_adapter = D1Adapter(
        account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
        database_id=os.getenv("CLOUDFLARE_D1_DATABASE_ID"),
        api_token=os.getenv("CLOUDFLARE_API_TOKEN")
    )
    
    # 創建遷移器
    migrator = PostgreSQLToD1Migrator(pg_connection, d1_adapter)
    
    try:
        # 執行遷移
        results = await migrator.full_migration()
        
        # 顯示最終結果
        successful_migrations = sum(1 for success in results.values() if success)
        total_migrations = len(results)
        
        print(f"\n遷移完成: {successful_migrations}/{total_migrations} 個表格成功遷移")
        
        if successful_migrations == total_migrations:
            print("🎉 所有資料表遷移成功！")
        else:
            print("⚠️  部分資料表遷移失敗，請檢查錯誤訊息")
            
    except Exception as e:
        print(f"遷移過程中發生錯誤: {e}")
    finally:
        migrator.close()


if __name__ == "__main__":
    asyncio.run(main()) 