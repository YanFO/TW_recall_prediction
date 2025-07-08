# 台灣罷免預測分析系統

## 🎯 專案目標
預測台灣罷免案的投票結果，透過分析社群媒體輿論來預測最終投票數與投票結果。

## 📊 分析方法
- **MECE框架**: 互斥且完全窮盡的分析架構
- **情緒分析**: 分析民眾對罷免案的情緒傾向
- **預測模型**: 使用機器學習預測投票結果

## 📁 專案結構
```
taiwan_recall_prediction/
├── ptt_crawler.py          # PTT論壇爬蟲
├── dcard_crawler.py        # Dcard爬蟲
├── sentiment_analyzer.py   # 情緒分析模組
├── mece_analyzer.py        # MECE分析與預測模型
├── dashboard.py            # Streamlit儀表板
├── run_analysis.py         # 一鍵執行腳本
├── requirements.txt        # 套件需求
└── README.md              # 說明文件
```

## 🚀 快速開始

### 1. 環境設置
```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安裝套件
pip install -r requirements.txt
```

### 2. 執行分析
```bash
# 方法1: 一鍵執行全部流程
python run_analysis.py

# 方法2: 分步執行
python ptt_crawler.py          # 爬取PTT資料
python dcard_crawler.py        # 爬取Dcard資料
python sentiment_analyzer.py   # 情緒分析
python mece_analyzer.py        # MECE分析與預測
streamlit run dashboard.py     # 啟動儀表板
```

### 3. 查看結果
- 開啟瀏覽器訪問: http://localhost:8501
- 查看即時更新的分析儀表板

## 📈 輸出檔案
- `ptt_data_*.csv`: PTT爬取的原始資料
- `dcard_data_*.csv`: Dcard爬取的原始資料
- `sentiment_analysis_results_*.csv`: 情緒分析結果
- `mece_analysis_results_*.csv`: MECE分析結果
- `prediction_results_*.json`: 預測結果摘要
- `sentiment_analysis.png`: 情緒分析視覺化
- `mece_analysis.png`: MECE分析視覺化

## 🎛️ Dashboard功能
1. **總覽頁面**: 預測結果摘要與關鍵指標
2. **情緒分析**: 詳細的情緒分布與趨勢分析
3. **MECE分析**: 人口統計與議題交叉分析
4. **預測詳情**: 模型性能與風險評估
5. **資料探索**: 互動式資料篩選與下載

## 🔍 分析維度 (MECE)

### 人口統計維度
- **年齡**: 年輕族群、中年族群、年長族群
- **地區**: 北部、中部、南部、東部、離島
- **職業**: 學生、專業人士、商業、勞工、公務員

### 議題維度
- **政治議題**: 施政、貪腐、民主、經濟
- **罷免原因**: 表現、醜聞、理念、代表性

### 情緒維度
- **情緒類別**: 正面、負面、中性
- **罷免立場**: 支持罷免、反對罷免、中立

## ⚠️ 注意事項
1. **資料來源限制**: 僅分析PTT和Dcard，可能不完全代表全體民意
2. **樣本偏差**: 網路用戶可能偏向特定族群
3. **時效性**: 輿論變化快速，需要持續更新資料
4. **預測準確性**: 模型預測僅供參考，實際結果可能有差異

## 🛠️ 技術架構
- **爬蟲**: requests + BeautifulSoup
- **資料處理**: pandas + numpy
- **情緒分析**: 基於規則的中文情緒分析
- **機器學習**: scikit-learn (RandomForest)
- **視覺化**: matplotlib + seaborn + plotly
- **儀表板**: Streamlit

## 📝 使用建議
1. **定期更新**: 建議每日執行爬蟲更新資料
2. **多元驗證**: 結合其他資料源進行交叉驗證
3. **風險評估**: 注意模型信心度和樣本數量
4. **趨勢觀察**: 關注情緒和立場的時間變化

## 🤝 貢獻指南
歡迎提交Issue和Pull Request來改善這個專案！

## 📄 授權
MIT License

---
**免責聲明**: 本系統僅供學術研究和參考使用，預測結果不構成任何投資或政治建議。
