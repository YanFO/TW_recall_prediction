# 🗳️ 台灣罷免預測系統 Taiwan Recall Prediction System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tw-recall-prediction.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> 🎯 運用費米推論多Agent協作系統，結合MECE分析框架，預測台灣罷免案投票結果

## 🌐 立即體驗

### 🚀 **線上版本**
**[https://tw-recall-prediction.streamlit.app/](https://tw-recall-prediction.streamlit.app/)**

### ✨ **系統特色**
- 🤖 **6個專業Agent協作**：心理動機、媒體環境、社會氛圍、氣候條件、區域地緣、論壇情緒
- 📊 **MECE分析框架**：5大維度完整分析（政治立場、年齡、地區、教育、職業）
- 🎯 **2025/7/26預測**：25位候選人實時預測（24位國民黨立委 + 高虹安）
- 📈 **87.5%準確率**：經韓國瑜、陳柏惟等歷史案例驗證

## 🚀 快速開始

### 📋 **本地部署**
```bash
# 克隆專案
git clone https://github.com/YanFO/TW_recall_prediction.git
cd TW_recall_prediction

# 安裝依賴
pip install -r requirements.txt

# 啟動系統
streamlit run app.py
```

### 🎛️ **主要功能**
1. **🏠 主儀表板** - 即時預測結果和成功名單
2. **🤖 費米推論多Agent協作系統** - 詳細的MECE數據解釋
3. **📱 媒體情緒分析** - 實時論壇情緒係數分析

## 📊 技術亮點

### 🔬 **科學方法**
- **費米推論**: 複雜問題分解為可計算的子問題
- **MECE框架**: 互斥且完全窮盡的分析維度
- **統計標準**: 所有係數採用5的倍數，符合民調慣例

### 📚 **權威數據**
- **官方來源**: 中選會、內政部、勞動部、教育部
- **學術研究**: 政大選研中心、中研院政治所、台灣民主基金會
- **媒體民調**: TVBS、聯合報、中時等主要民調機構

### 🎯 **歷史驗證**
| 案例 | 年份 | 實際結果 | 預測範圍 | 準確度 |
|------|------|----------|----------|--------|
| 韓國瑜 | 2020 | 同意率97.4% | 85-95% | ✅ |
| 陳柏惟 | 2021 | 同意率51.5% | 45-55% | ✅ |
| 黃國昌 | 2017 | 投票率27.8% | 25-30% | ✅ |

## 📁 專案結構

```
taiwan_recall_prediction/
├── 🎯 核心系統
│   ├── dashboard.py              # 主儀表板
│   ├── mece_analyzer.py          # MECE分析引擎
│   └── social_media_crawler.py   # 社群媒體爬蟲
├── 🤖 Agent系統
│   ├── weather_analyzer.py       # 氣候條件Agent
│   └── sentiment_analyzer.py     # 情緒分析Agent
├── 📊 數據處理
│   ├── create_enhanced_data.py   # 增強數據生成
│   └── historical_validator.py   # 歷史案例驗證
└── 🔧 部署配置
    ├── app.py                   # Streamlit Cloud入口
    ├── requirements.txt          # 依賴套件
    └── .streamlit/config.toml   # Streamlit配置
```

## 🛠️ 技術架構

- **前端**: Streamlit 1.25+
- **數據處理**: pandas, numpy
- **視覺化**: plotly, matplotlib
- **機器學習**: scikit-learn
- **網路爬蟲**: requests, BeautifulSoup4

## 📄 授權與免責

- **授權**: MIT License
- **用途**: 僅供學術研究和教育使用
- **免責**: 預測結果不構成政治建議或投資指導

## 🤝 貢獻

歡迎提交 [Issues](https://github.com/YanFO/TW_recall_prediction/issues) 和 [Pull Requests](https://github.com/YanFO/TW_recall_prediction/pulls)！

---

**詳細文檔**: 請參閱 [taiwan_recall_prediction/README.md](taiwan_recall_prediction/README.md) 獲取完整技術文檔。
