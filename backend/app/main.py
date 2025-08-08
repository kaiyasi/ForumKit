from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.routers import auth, users, test_auth, posts, comments, reviews
from app.api.api_v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ForumKit - 匿名校園討論平台 API (使用 CloudFlare D1)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS 設定 - 允許前端訪問
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 掛載路由
app.include_router(test_auth.router, prefix=f"{settings.API_V1_STR}/test")
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "歡迎使用 ForumKit API", 
        "version": settings.VERSION,
        "database": "CloudFlare D1",
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/ping")
async def ping():
    return {"message": "pong", "status": "healthy"}

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "ForumKit API",
        "database": "CloudFlare D1",
        "version": settings.VERSION
    }

# 全域錯誤處理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全域異常處理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "內部伺服器錯誤",
            "message": "請稍後再試或聯繫管理員"
        }
    ) 