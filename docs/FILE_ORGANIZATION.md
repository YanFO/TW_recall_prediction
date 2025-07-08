# 文件組織結構說明

## 📁 完整項目結構

```
Recall_TW/                                    # 項目根目錄
├── 📄 README.md                             # 主要項目說明文檔
├── 📄 start.py                              # 快速啟動腳本 ⭐
│
├── 📂 taiwan_recall_prediction/              # 台灣罷免預測系統 🎯
│   ├── 🐳 Docker相關文件
│   │   ├── Dockerfile                       # Docker鏡像定義
│   │   ├── docker-compose.yml               # 多容器編排
│   │   ├── docker-run.sh                    # Docker啟動腳本
│   │   └── init.sql                         # 數據庫初始化
│   │
│   ├── 📊 核心分析模組
│   │   ├── dashboard.py                     # Streamlit主儀表板 ⭐
│   │   ├── mece_analyzer.py                 # MECE框架分析器
│   │   ├── sentiment_analyzer.py            # 情緒分析引擎
│   │   ├── weather_analyzer.py              # 天氣影響分析
│   │   ├── historical_validator.py          # 歷史數據驗證
│   │   └── model_optimizer.py               # 模型優化器
│   │
│   ├── 🌐 數據收集系統
│   │   ├── data_collector.py                # 主數據收集器
│   │   ├── ptt_crawler.py                   # PTT爬蟲
│   │   ├── dcard_crawler.py                 # Dcard爬蟲
│   │   ├── social_media_crawler.py          # 社群媒體整合爬蟲
│   │   └── survey_system.py                 # 問卷調查系統
│   │
│   ├── 🔧 工具和配置
│   │   ├── requirements.txt                 # Python依賴包
│   │   ├── fix_quotes.py                    # 引號修復工具
│   │   ├── scheduler.py                     # 任務調度器
│   │   ├── run_analysis.py                  # 分析執行器
│   │   └── test_enhancements.py             # 功能測試
│   │
│   ├── 📁 數據目錄
│   │   ├── data/                           # 原始數據存儲
│   │   ├── logs/                           # 系統日誌
│   │   └── output/                         # 分析結果輸出
│   │
│   ├── 📚 文檔
│   │   ├── README.md                       # 系統說明文檔
│   │   └── docker-README.md                # Docker使用說明
│   │
│   └── 🧪 數據生成工具
│       ├── create_sample_data.py           # 樣本數據生成
│       └── create_enhanced_data.py         # 增強數據生成
│
├── 📂 autogen_framework/                    # AutoGen編程工作流 🤖
│   ├── 📂 core/                            # 核心實現
│   │   ├── autogen_workflow_compatible.py  # 多版本兼容工作流 ⭐
│   │   ├── autogen_workflow.py             # 原始v0.4工作流
│   │   ├── autogen_executor.py             # 執行引擎
│   │   └── check_autogen_dependencies.py   # 依賴檢查工具
│   │
│   ├── 📂 config/                          # 配置管理
│   │   └── autogen_config.py               # Agent配置和模板
│   │
│   ├── 📂 demos/                           # 演示腳本
│   │   └── demo_autogen_workflow.py        # 完整演示程序 ⭐
│   │
│   ├── 📂 docs/                            # 專用文檔
│   │   ├── AUTOGEN_README.md               # 詳細使用文檔
│   │   └── AUTOGEN_IMPLEMENTATION_SUMMARY.md # 實現總結
│   │
│   ├── 📂 results/                         # 執行結果
│   │   └── (自動生成的結果文件)
│   │
│   └── 📄 README.md                        # AutoGen框架說明
│
├── 📂 scripts/                             # 工具腳本 🔧
│   ├── project_manager.py                  # 項目管理器 ⭐
│   └── fix_dashboard.py                    # 儀表板修復工具
│
└── 📂 docs/                                # 項目文檔 📚
    ├── PROJECT_OVERVIEW.md                 # 項目概覽
    └── FILE_ORGANIZATION.md                # 本文件
```

## 🎯 關鍵文件說明

### ⭐ 主要入口點
- **`start.py`**: 項目快速啟動腳本，提供交互式選單
- **`scripts/project_manager.py`**: 完整的項目管理工具
- **`taiwan_recall_prediction/dashboard.py`**: Streamlit主儀表板
- **`autogen_framework/demos/demo_autogen_workflow.py`**: AutoGen演示

### 🎯 核心系統文件
- **`taiwan_recall_prediction/mece_analyzer.py`**: MECE框架核心邏輯
- **`taiwan_recall_prediction/sentiment_analyzer.py`**: 中文情緒分析引擎
- **`autogen_framework/core/autogen_workflow_compatible.py`**: 多版本AutoGen支援

### 🐳 部署相關
- **`taiwan_recall_prediction/docker-compose.yml`**: 完整的容器編排
- **`taiwan_recall_prediction/Dockerfile`**: 系統鏡像定義
- **`taiwan_recall_prediction/requirements.txt`**: Python依賴管理

## 🚀 快速啟動指南

### 1. 使用快速啟動腳本 (推薦)
```bash
# 在項目根目錄執行
python start.py
```

### 2. 使用項目管理器
```bash
# 交互式選單
python scripts/project_manager.py --interactive

# 直接啟動儀表板
python scripts/project_manager.py --start-dashboard

# 啟動AutoGen演示
python scripts/project_manager.py --start-autogen
```

### 3. 直接啟動組件
```bash
# 啟動台灣罷免預測系統
cd taiwan_recall_prediction
docker-compose up -d

# 啟動AutoGen演示
cd autogen_framework
python demos/demo_autogen_workflow.py --quick
```

## 📋 文件組織原則

### 1. 功能分離
- **taiwan_recall_prediction/**: 專注於罷免預測分析
- **autogen_framework/**: 專注於編程工作流自動化
- **scripts/**: 通用工具和管理腳本
- **docs/**: 項目文檔和說明

### 2. 層次結構
- **根目錄**: 項目級別的文件 (README, 啟動腳本)
- **子系統目錄**: 各自獨立的功能模組
- **專用目錄**: core/, config/, demos/, docs/ 等功能分類

### 3. 命名規範
- **描述性命名**: 文件名清楚表達功能
- **一致性**: 相同類型文件使用相同命名模式
- **可讀性**: 避免縮寫，使用完整單詞

## 🔧 維護指南

### 添加新功能
1. **確定歸屬**: 判斷功能屬於哪個子系統
2. **遵循結構**: 按照現有目錄結構放置文件
3. **更新文檔**: 同步更新相關README文件
4. **測試整合**: 確保不破壞現有功能

### 文件移動
1. **檢查依賴**: 確認文件間的導入關係
2. **更新路徑**: 修改相關的import語句
3. **測試功能**: 驗證移動後功能正常
4. **更新文檔**: 同步更新文檔中的路徑

### 清理無用文件
1. **備份重要數據**: 確保不丟失重要信息
2. **檢查引用**: 確認文件沒有被其他地方使用
3. **逐步清理**: 分批次清理，避免一次性大改動
4. **版本控制**: 使用git記錄變更歷史

## 📊 目錄統計

### 文件數量統計
- **台灣罷免預測系統**: 20+ 個Python文件
- **AutoGen框架**: 8 個核心文件
- **工具腳本**: 2 個管理工具
- **文檔文件**: 10+ 個說明文檔

### 代碼行數統計 (估算)
- **核心邏輯**: ~3000 行
- **數據處理**: ~2000 行  
- **界面代碼**: ~1500 行
- **配置文件**: ~500 行
- **文檔內容**: ~2000 行

## 🎉 組織完成狀態

### ✅ 已完成
- [x] AutoGen框架文件整理到 `autogen_framework/`
- [x] 工具腳本移動到 `scripts/`
- [x] 項目文檔整理到 `docs/`
- [x] 創建項目管理器 `scripts/project_manager.py`
- [x] 創建快速啟動腳本 `start.py`
- [x] 完善各級README文檔
- [x] 建立清晰的目錄結構

### 📈 組織效果
- **可維護性**: 大幅提升，文件分類清晰
- **可擴展性**: 新功能有明確的歸屬位置
- **用戶體驗**: 提供多種啟動方式，降低使用門檻
- **開發效率**: 開發者能快速定位相關文件

---

**文檔版本**: v1.0.0  
**創建日期**: 2025年7月5日  
**維護狀態**: 活躍維護 ✅
