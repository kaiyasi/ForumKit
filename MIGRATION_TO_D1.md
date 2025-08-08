# ForumKit 資料庫遷移指南

從 PostgreSQL 遷移到 CloudFlare D1 的完整指南

## 🎯 遷移概述

本指南將協助您將 ForumKit 從 PostgreSQL 資料庫遷移到 CloudFlare D1。D1 是 CloudFlare 提供的無伺服器 SQLite 資料庫，具有全球分佈、自動擴展和成本效益等優勢。

## 📋 前置作業

### 1. CloudFlare 帳戶設置

1. 註冊或登入 [CloudFlare Dashboard](https://dash.cloudflare.com/)
2. 導航至 Workers & Pages > D1
3. 創建新的 D1 資料庫：
   ```bash
   npx wrangler d1 create forumkit-db
   ```
4. 記錄以下資訊：
   - Account ID
   - Database ID
   - API Token

### 2. 獲取必要的憑證

1. **Account ID**: CloudFlare Dashboard 右側邊欄
2. **D1 Database ID**: 創建資料庫後顯示
3. **API Token**: 
   - 前往 "My Profile" > "API Tokens"
   - 創建自定義 Token，權限包含：
     - Zone:Zone Settings:Edit
     - Zone:Zone:Read
     - Account:Cloudflare Workers:Edit
     - Account:D1:Edit

## 🚀 遷移步驟

### 第一步：環境配置

1. 複製環境變數範例：
   ```bash
   cp backend/env.d1.example backend/.env
   ```

2. 編輯 `.env` 檔案，填入您的 CloudFlare 憑證：
   ```env
   USE_D1=true
   CLOUDFLARE_ACCOUNT_ID=your-account-id
   CLOUDFLARE_D1_DATABASE_ID=your-database-id
   CLOUDFLARE_API_TOKEN=your-api-token
   ```

### 第二步：初始化 D1 資料庫

1. 安裝相依套件：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. 執行 D1 資料庫初始化：
   ```bash
   python migration_tools/init_d1_database.py
   ```

   這個腳本會：
   - 創建所有必要的資料表
   - 設置初始管理員帳戶
   - 創建測試資料

### 第三步：資料遷移（可選）

如果您有現有的 PostgreSQL 資料需要遷移：

1. 確保 PostgreSQL 資料庫可以連接
2. 執行遷移腳本：
   ```bash
   python migration_tools/migrate_to_d1.py
   ```

3. 按照提示輸入 PostgreSQL 連接字符串

### 第四步：更新應用程式配置

1. 確認 `backend/app/core/config.py` 中 `USE_D1=True`
2. 重啟後端服務：
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## 🔧 資料庫結構

### 主要資料表

- **users**: 用戶資訊
- **schools**: 學校資訊
- **posts**: 貼文資料
- **comments**: 評論資料
- **review_logs**: 審核記錄
- **global_discussions**: 全域討論
- **admin_logs**: 管理員操作記錄

### 索引優化

D1 資料庫已建立以下索引以提升查詢效能：
- 用戶 email 索引
- 貼文學校關聯索引
- 評論貼文關聯索引
- 時間排序索引

## 📊 效能比較

| 特性 | PostgreSQL | CloudFlare D1 |
|------|------------|---------------|
| 部署複雜度 | 高 | 極低 |
| 維護成本 | 高 | 極低 |
| 全球分佈 | 需設置 | 內建 |
| 自動擴展 | 有限 | 無限 |
| 成本 | 固定 | 按使用量 |

## 🛠 開發工具

### 1. 資料庫查詢

使用 Wrangler CLI 查詢 D1：
```bash
npx wrangler d1 execute forumkit-db --command "SELECT * FROM users LIMIT 5"
```

### 2. 本地開發

D1 提供本地開發模式：
```bash
npx wrangler d1 execute forumkit-db --local --command "SELECT COUNT(*) FROM posts"
```

### 3. 資料庫備份

導出資料庫：
```bash
npx wrangler d1 export forumkit-db --output backup.sql
```

## 🔍 常見問題

### Q: 遷移過程中斷怎麼辦？
A: 遷移腳本支援斷點續傳，重新執行即可。

### Q: D1 有查詢限制嗎？
A: D1 單次查詢最多返回 10MB 資料，可以透過分頁處理大量資料。

### Q: 如何監控 D1 效能？
A: 使用 CloudFlare Analytics 和 Workers Analytics 監控資料庫效能。

### Q: 可以回滾到 PostgreSQL 嗎？
A: 可以，保持原始配置並修改 `USE_D1=false` 即可。

## 📱 Worker API 整合

### 邊緣運算優勢

D1 與 CloudFlare Workers 緊密整合，提供：
- 全球邊緣快取
- 超低延遲回應
- 自動 DDoS 防護
- 無伺服器擴展

### API 部署

```bash
cd workers/api-d1
npx wrangler deploy
```

## 🚨 注意事項

1. **資料一致性**: D1 最終一致性模型，適合讀多寫少的應用
2. **交易支援**: D1 支援 SQLite 交易，但有一定限制
3. **備份策略**: 定期執行資料備份，確保資料安全
4. **監控告警**: 設置 CloudFlare 告警監控資料庫狀態

## 📞 技術支援

如遇到遷移問題，請：
1. 檢查 CloudFlare 控制台日誌
2. 驗證 API Token 權限
3. 確認網路連接狀態
4. 查看詳細錯誤訊息

---

🎉 **恭喜！** 您已成功將 ForumKit 遷移到 CloudFlare D1！

享受無伺服器資料庫帶來的便利和效能提升吧！ 