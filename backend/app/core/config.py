from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from pydantic.networks import AnyHttpUrl
import os
from pathlib import Path

# Build a path to the .env file from the location of this config file.
# This config file is in I:/ForumKit/backend/app/core/config.py
# The .env file is in I:/ForumKit/backend/.env
# So we need to go up two directories.
env_path = Path(__file__).parent.parent.parent / ".env"

class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=env_path,
        extra="ignore"  # 忽略額外字段
    )
    
    # 專案設定
    PROJECT_NAME: str = "ForumKit"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 安全設定
    SECRET_KEY: str = "3a7f8c9e2b1d4a6f5e8c7b9a0d3f6e2c1a4b7e9f8c5d2a6b3e7f1a9c4b8e5d2f7a"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth 設定
    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"
    
    # PostgreSQL 設定（僅用於資料遷移）
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "forumkit"
    POSTGRES_PORT: str = "5432"
    
    # SMTP 郵件設定（可選）
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    EMAILS_FROM_EMAIL: str = "your-email@gmail.com"
    EMAILS_FROM_NAME: str = "ForumKit"
    
    # 超級用戶設定
    FIRST_SUPERUSER: str = "admin@forumkit.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123456"
    
    # CORS 設定 - 使用環境變數或默認值
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # 檔案上傳設定
    UPLOAD_DIR: str = "uploads"
    
    # CloudFlare D1 設定
    USE_D1: bool = True
    CLOUDFLARE_ACCOUNT_ID: str = ""
    CLOUDFLARE_D1_DATABASE_ID: str = ""
    CLOUDFLARE_API_TOKEN: str = ""
    
    def get_cors_origins(self) -> List[str]:
        """獲取 CORS 來源列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def get_postgres_uri(self) -> str:
        """獲取 PostgreSQL 連接字串（僅用於遷移）"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings() 