# 🐳 台灣罷免預測分析系統 - Docker版本

## 🚀 快速開始

### 1. 前置需求
- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose
- 至少 4GB 可用記憶體
- 至少 2GB 可用磁碟空間

### 2. 一鍵啟動
```bash
# 下載專案
git clone <repository-url>
cd taiwan_recall_prediction

# 給予執行權限 (Linux/Mac)
chmod +x docker-run.sh

# 執行啟動腳本
./docker-run.sh
# 或在Windows上: bash docker-run.sh
```

### 3. 手動啟動
```bash
# 建立必要目錄
mkdir -p data output logs

# 啟動完整服務
docker-compose up -d

# 僅啟動主要應用
docker-compose up -d recall-analyzer

# 查看服務狀態
docker-compose ps
```

## 📊 服務架構

### 核心服務
- **recall-analyzer**: 主要分析應用 + Streamlit Dashboard
- **scheduler**: 定時任務調度器
- **postgres**: PostgreSQL 資料庫
- **redis**: Redis 快取

### 端口配置
- `8501`: Streamlit Dashboard
- `5432`: PostgreSQL 資料庫
- `6379`: Redis 快取

## 🎛️ 使用方式

### Dashboard 訪問
開啟瀏覽器訪問: http://localhost:8501

### 資料持久化
- `./data/`: 分析資料檔案
- `./output/`: 輸出結果檔案
- `./logs/`: 系統日誌檔案

### 定時任務
- **每天 08:00**: 完整分析流程
- **每天 14:00, 20:00**: 快速更新
- **每小時**: 健康檢查

## 🔧 管理命令

### 基本操作
```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重新啟動
docker-compose restart

# 查看日誌
docker-compose logs -f recall-analyzer

# 進入容器
docker-compose exec recall-analyzer bash
```

### 資料管理
```bash
# 備份資料
docker-compose exec postgres pg_dump -U recall_user recall_analysis > backup.sql

# 清理所有資料
docker-compose down -v
rm -rf data output logs

# 重新建構映像
docker-compose build --no-cache
```

### 除錯模式
```bash
# 查看特定服務日誌
docker-compose logs -f scheduler

# 執行單次分析
docker-compose exec recall-analyzer python ptt_crawler.py

# 檢查資料庫連線
docker-compose exec postgres psql -U recall_user -d recall_analysis
```

## 📈 監控與維護

### 健康檢查
```bash
# 檢查服務狀態
docker-compose ps

# 檢查資源使用
docker stats

# 檢查磁碟使用
du -sh data output logs
```

### 日誌管理
```bash
# 查看最新日誌
docker-compose logs --tail=100 -f recall-analyzer

# 清理舊日誌
docker-compose exec recall-analyzer find /app/logs -name "*.log" -mtime +7 -delete
```

## ⚙️ 配置選項

### 環境變數
在 `docker-compose.yml` 中可以調整以下設定:

```yaml
environment:
  - TZ=Asia/Taipei              # 時區設定
  - PYTHONUNBUFFERED=1          # Python輸出緩衝
  - POSTGRES_DB=recall_analysis # 資料庫名稱
  - POSTGRES_USER=recall_user   # 資料庫用戶
  - POSTGRES_PASSWORD=recall_password # 資料庫密碼
```

### 資源限制
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

## 🔒 安全考量

### 生產環境建議
1. **更改預設密碼**
   ```yaml
   environment:
     - POSTGRES_PASSWORD=your_secure_password
   ```

2. **限制網路訪問**
   ```yaml
   ports:
     - "127.0.0.1:8501:8501"  # 僅本機訪問
   ```

3. **使用 secrets**
   ```yaml
   secrets:
     - postgres_password
   ```

### 資料備份
```bash
# 定期備份腳本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U recall_user recall_analysis > "backup_${DATE}.sql"
tar -czf "data_backup_${DATE}.tar.gz" data output
```

## 🐛 常見問題

### Q: 容器啟動失敗
```bash
# 檢查日誌
docker-compose logs recall-analyzer

# 重新建構
docker-compose build --no-cache recall-analyzer
```

### Q: 記憶體不足
```bash
# 檢查資源使用
docker stats

# 清理未使用的映像
docker system prune -a
```

### Q: 資料庫連線失敗
```bash
# 檢查資料庫狀態
docker-compose exec postgres pg_isready -U recall_user

# 重新啟動資料庫
docker-compose restart postgres
```

### Q: Dashboard 無法訪問
```bash
# 檢查端口是否被佔用
netstat -an | grep 8501

# 檢查防火牆設定
# Windows: 檢查 Windows Defender 防火牆
# Linux: 檢查 iptables 或 ufw
```

## 📋 開發模式

### 本地開發
```bash
# 掛載本地代碼
docker-compose -f docker-compose.dev.yml up -d

# 即時重載
docker-compose exec recall-analyzer streamlit run dashboard.py --server.fileWatcherType poll
```

### 測試環境
```bash
# 執行測試
docker-compose exec recall-analyzer python -m pytest tests/

# 程式碼品質檢查
docker-compose exec recall-analyzer flake8 .
```

## 📞 支援

如有問題，請檢查:
1. Docker 和 Docker Compose 版本
2. 系統資源是否充足
3. 網路連線是否正常
4. 日誌檔案中的錯誤訊息

---

**注意**: 這是一個分析工具，預測結果僅供參考，不構成任何投資或政治建議。
