#!/usr/bin/env python3
"""
CloudFlare D1 資料庫初始化腳本
創建資料表結構和初始資料
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)

from app.db.d1_adapter import D1Adapter
from app.core.security import get_password_hash
import hashlib

class D1DatabaseInitializer:
    """D1 資料庫初始化工具"""
    
    def __init__(self, d1_adapter: D1Adapter):
        self.d1_adapter = d1_adapter
    
    async def create_tables(self) -> bool:
        """創建所有資料表"""
        print("正在創建 D1 資料表...")
        
        # 讀取 schema.sql 檔案
        schema_file = Path(__file__).parent.parent / "workers" / "api-d1" / "schema.sql"
        
        if not schema_file.exists():
            print(f"錯誤: 找不到 schema 檔案 {schema_file}")
            return False
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # 分割 SQL 語句（以分號分隔）
            sql_statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for i, sql in enumerate(sql_statements):
                if sql:
                    try:
                        print(f"執行 SQL 語句 {i+1}/{len(sql_statements)}")
                        await self.d1_adapter.execute_query(sql)
                    except Exception as e:
                        # 忽略 "table already exists" 錯誤
                        if "already exists" not in str(e).lower():
                            print(f"SQL 執行錯誤: {e}")
                            print(f"問題語句: {sql[:100]}...")
            
            print("✓ 資料表創建完成")
            return True
            
        except Exception as e:
            print(f"創建資料表失敗: {e}")
            return False
    
    async def create_initial_data(self) -> bool:
        """創建初始資料"""
        print("正在創建初始資料...")
        
        try:
            # 創建預設學校
            await self._create_default_school()
            
            # 創建管理員用戶
            await self._create_admin_user()
            
            # 創建測試資料
            await self._create_test_data()
            
            print("✓ 初始資料創建完成")
            return True
            
        except Exception as e:
            print(f"創建初始資料失敗: {e}")
            return False
    
    async def _create_default_school(self):
        """創建預設學校"""
        school_data = {
            "name": "測試大學",
            "domain": "test.edu.tw",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # 檢查是否已存在
        existing = await self.d1_adapter.select("schools", where={"domain": school_data["domain"]}, limit=1)
        if not existing:
            school_id = await self.d1_adapter.insert("schools", school_data)
            print(f"創建預設學校，ID: {school_id}")
        else:
            print("預設學校已存在")
    
    async def _create_admin_user(self):
        """創建管理員用戶"""
        admin_email = "admin@forumkit.com"
        admin_password = "admin123456"
        
        # 檢查管理員是否已存在
        existing = await self.d1_adapter.select("users", where={"email": admin_email}, limit=1)
        if existing:
            print("管理員用戶已存在")
            return
        
        # 獲取學校 ID
        schools = await self.d1_adapter.select("schools", limit=1)
        if not schools:
            raise Exception("找不到學校資料，無法創建管理員")
        
        school_id = schools[0]["id"]
        
        # 創建管理員用戶
        admin_data = {
            "email": admin_email,
            "email_hash": hashlib.sha256(admin_email.encode()).hexdigest(),
            "username": "admin",
            "hashed_password": get_password_hash(admin_password),
            "full_name": "系統管理員",
            "is_active": True,
            "is_superuser": True,
            "is_verified": True,
            "role": "admin",
            "school_id": school_id,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        admin_id = await self.d1_adapter.insert("users", admin_data)
        print(f"創建管理員用戶，ID: {admin_id}")
        print(f"管理員登錄資訊: {admin_email} / {admin_password}")
    
    async def _create_test_data(self):
        """創建測試資料"""
        # 獲取學校和管理員資訊
        schools = await self.d1_adapter.select("schools", limit=1)
        admin_users = await self.d1_adapter.select("users", where={"role": "admin"}, limit=1)
        
        if not schools or not admin_users:
            print("跳過測試資料創建（缺少必要資料）")
            return
        
        school_id = schools[0]["id"]
        admin_id = admin_users[0]["id"]
        
        # 創建測試用戶
        test_user_data = {
            "email": "student@test.edu.tw",
            "email_hash": hashlib.sha256("student@test.edu.tw".encode()).hexdigest(),
            "username": "student001",
            "hashed_password": get_password_hash("password123"),
            "full_name": "測試學生",
            "is_active": True,
            "is_superuser": False,
            "is_verified": True,
            "role": "user",
            "school_id": school_id,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # 檢查測試用戶是否已存在
        existing_user = await self.d1_adapter.select("users", where={"email": test_user_data["email"]}, limit=1)
        if not existing_user:
            user_id = await self.d1_adapter.insert("users", test_user_data)
            print(f"創建測試用戶，ID: {user_id}")
            
            # 創建測試貼文
            test_post_data = {
                "title": "歡迎使用 ForumKit！",
                "content": "這是一個測試貼文，用來驗證系統功能正常運作。",
                "is_anonymous": False,
                "author_id": user_id,
                "school_id": school_id,
                "status": "approved",
                "is_sensitive": False,
                "reviewed_by": admin_id,
                "reviewed_at": "2024-01-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "view_count": 0,
                "like_count": 0,
                "comment_count": 0
            }
            
            post_id = await self.d1_adapter.insert("posts", test_post_data)
            print(f"創建測試貼文，ID: {post_id}")
        else:
            print("測試用戶已存在")
    
    async def verify_setup(self) -> bool:
        """驗證資料庫設置"""
        print("正在驗證資料庫設置...")
        
        try:
            # 檢查各個表格
            tables_to_check = [
                "schools", "users", "posts", "comments", 
                "review_logs", "global_discussions"
            ]
            
            for table in tables_to_check:
                try:
                    count_result = await self.d1_adapter.custom_query(f"SELECT COUNT(*) as count FROM {table}")
                    count = count_result[0]["count"] if count_result else 0
                    print(f"  {table}: {count} 筆記錄")
                except Exception as e:
                    print(f"  {table}: 檢查失敗 - {e}")
                    return False
            
            print("✓ 資料庫驗證通過")
            return True
            
        except Exception as e:
            print(f"資料庫驗證失敗: {e}")
            return False


async def main():
    """主函數"""
    print("CloudFlare D1 資料庫初始化工具")
    print("=" * 40)
    
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
    
    # 創建 D1 適配器
    d1_adapter = D1Adapter(
        account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
        database_id=os.getenv("CLOUDFLARE_D1_DATABASE_ID"),
        api_token=os.getenv("CLOUDFLARE_API_TOKEN")
    )
    
    # 創建初始化器
    initializer = D1DatabaseInitializer(d1_adapter)
    
    try:
        print("開始初始化 D1 資料庫...")
        
        # 創建資料表
        if not await initializer.create_tables():
            print("資料表創建失敗，初始化中止")
            return
        
        # 創建初始資料
        if not await initializer.create_initial_data():
            print("初始資料創建失敗")
        
        # 驗證設置
        if await initializer.verify_setup():
            print("\n🎉 D1 資料庫初始化完成！")
            print("\n管理員登錄資訊:")
            print("  Email: admin@forumkit.com")
            print("  Password: admin123456")
        else:
            print("\n⚠️  資料庫初始化可能不完整，請檢查上述錯誤訊息")
            
    except Exception as e:
        print(f"初始化過程中發生錯誤: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 