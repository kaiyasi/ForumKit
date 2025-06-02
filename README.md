# 匿名校園討論平台 (Anon Campus Platform)

一個支援多校、高中匿名討論區平台。

## 技術棧

### 後端
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic

### 前端
- React
- TailwindCSS
- Vite

## 前置作業

### 1. 環境需求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 2. 後端設置

#### 2.1 環境變數
1. 複製環境變數範本：
```bash
cd backend
cp .env.example .env
```

2. 修改 `.env` 檔案中的設定：
- 資料庫連線資訊
- Redis 連線資訊
- JWT 密鑰

#### 2.2 資料庫遷移
1. 建立資料庫：
```bash
createdb anon_campus
```

2. 執行資料庫遷移：
```bash
cd backend
alembic upgrade head
```

### 3. 前端設置

#### 3.1 安裝依賴
```bash
cd frontend
npm install
```

#### 3.2 環境變數
1. 複製環境變數範本：
```bash
cp .env.example .env
```

2. 修改 API 端點設定

## 快速開始

### 使用 Docker Compose

1. 確保已安裝 Docker 和 Docker Compose
2. 在專案根目錄執行：
```bash
docker-compose -f infra/docker-compose.yml up -d
```

### 本地開發

#### 後端
1. 進入後端目錄：
```bash
cd backend
```

2. 建立虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. 安裝依賴：
```bash
pip install -r requirements.txt
```

4. 啟動服務：
```bash
uvicorn app.main:app --reload
```

#### 前端
1. 進入前端目錄：
```bash
cd frontend
```

2. 安裝依賴：
```bash
npm install
```

3. 啟動開發服務器：
```bash
npm run dev
```

## API 文檔

啟動後端服務後，可訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 開發指南

### 資料庫遷移
- 創建新的遷移：`alembic revision --autogenerate -m "migration message"`
- 執行遷移：`alembic upgrade head`
- 回滾遷移：`alembic downgrade -1`

### 代碼風格
- 後端：使用 Black 進行代碼格式化
- 前端：使用 ESLint 和 Prettier 進行代碼格式化

### Git 提交規範
- feat: 新功能
- fix: 修復問題
- docs: 文檔修改
- style: 代碼格式修改
- refactor: 代碼重構
- test: 測試用例修改
- chore: 其他修改 