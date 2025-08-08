#!/usr/bin/env python3
"""
D1 API 測試腳本
測試後端 API 與 D1 資料庫的整合
"""

import asyncio
import httpx
import json
from typing import Dict, Any

class D1APITester:
    """D1 API 測試器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.auth_token = None
    
    async def test_health_check(self):
        """測試健康檢查端點"""
        print("🔍 測試健康檢查...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/ping")
            
            if response.status_code == 200:
                print("✅ 健康檢查通過")
                return True
            else:
                print(f"❌ 健康檢查失敗: {response.status_code}")
                return False
    
    async def test_user_registration(self):
        """測試用戶註冊"""
        print("🔍 測試用戶註冊...")
        
        user_data = {
            "email": "test@test.edu.tw",
            "password": "testpass123",
            "full_name": "測試用戶",
            "school_id": 1
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/register",
                    headers=self.headers,
                    json=user_data
                )
                
                if response.status_code in [200, 201]:
                    print("✅ 用戶註冊成功")
                    print(f"   用戶資訊: {response.json()}")
                    return True
                elif response.status_code == 400:
                    print("ℹ️  用戶已存在（這是正常的）")
                    return True
                else:
                    print(f"❌ 用戶註冊失敗: {response.status_code}")
                    print(f"   錯誤訊息: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ 用戶註冊異常: {e}")
                return False
    
    async def test_user_login(self):
        """測試用戶登入"""
        print("🔍 測試用戶登入...")
        
        login_data = {
            "username": "test@test.edu.tw",
            "password": "testpass123"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data=login_data
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.auth_token = token_data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.auth_token}"
                    print("✅ 用戶登入成功")
                    print(f"   Token: {self.auth_token[:50]}...")
                    return True
                else:
                    print(f"❌ 用戶登入失敗: {response.status_code}")
                    print(f"   錯誤訊息: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ 用戶登入異常: {e}")
                return False
    
    async def test_get_current_user(self):
        """測試獲取當前用戶資訊"""
        print("🔍 測試獲取當前用戶...")
        
        if not self.auth_token:
            print("❌ 沒有認證 token，跳過測試")
            return False
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/me",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    print("✅ 獲取用戶資訊成功")
                    print(f"   用戶 ID: {user_data.get('id')}")
                    print(f"   用戶名: {user_data.get('full_name')}")
                    return True
                else:
                    print(f"❌ 獲取用戶資訊失敗: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ 獲取用戶資訊異常: {e}")
                return False
    
    async def test_create_post(self):
        """測試創建貼文"""
        print("🔍 測試創建貼文...")
        
        if not self.auth_token:
            print("❌ 沒有認證 token，跳過測試")
            return False
        
        post_data = {
            "title": "D1 測試貼文",
            "content": "這是一個測試 D1 資料庫的貼文",
            "is_anonymous": False,
            "school_id": 1
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/posts/",
                    headers=self.headers,
                    json=post_data
                )
                
                if response.status_code in [200, 201]:
                    post_result = response.json()
                    print("✅ 創建貼文成功")
                    print(f"   貼文 ID: {post_result.get('id')}")
                    print(f"   貼文標題: {post_result.get('title')}")
                    return post_result.get('id')
                else:
                    print(f"❌ 創建貼文失敗: {response.status_code}")
                    print(f"   錯誤訊息: {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ 創建貼文異常: {e}")
                return None
    
    async def test_get_posts(self):
        """測試獲取貼文列表"""
        print("🔍 測試獲取貼文列表...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/posts/?skip=0&limit=10"
                )
                
                if response.status_code == 200:
                    posts = response.json()
                    print("✅ 獲取貼文列表成功")
                    print(f"   貼文數量: {len(posts)}")
                    return True
                else:
                    print(f"❌ 獲取貼文列表失敗: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ 獲取貼文列表異常: {e}")
                return False
    
    async def test_api_docs(self):
        """測試 API 文檔"""
        print("🔍 測試 API 文檔...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/docs")
                
                if response.status_code == 200:
                    print("✅ API 文檔可訪問")
                    return True
                else:
                    print(f"❌ API 文檔不可訪問: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ API 文檔訪問異常: {e}")
                return False
    
    async def run_all_tests(self):
        """執行所有測試"""
        print("🚀 開始 D1 API 測試")
        print("=" * 50)
        
        tests = [
            ("健康檢查", self.test_health_check),
            ("API 文檔", self.test_api_docs),
            ("用戶註冊", self.test_user_registration),
            ("用戶登入", self.test_user_login),
            ("獲取用戶資訊", self.test_get_current_user),
            ("創建貼文", self.test_create_post),
            ("獲取貼文列表", self.test_get_posts),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 執行測試: {test_name}")
            try:
                result = await test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ 測試 {test_name} 發生異常: {e}")
        
        print("\n" + "=" * 50)
        print(f"🎯 測試結果: {passed}/{total} 通過")
        
        if passed == total:
            print("🎉 所有測試通過！D1 API 運作正常")
        else:
            print("⚠️  部分測試失敗，請檢查錯誤訊息")
        
        return passed == total


async def main():
    """主函數"""
    print("D1 API 測試工具")
    print("確保後端服務已啟動在 http://localhost:8000")
    print()
    
    tester = D1APITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 