# D1 資料庫連接
from app.db.d1_adapter import get_d1_session

# 依賴注入用
async def get_db():
    async for session in get_d1_session():
        yield session 