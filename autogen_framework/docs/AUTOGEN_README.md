# AutoGen編程工作流系統

基於最新AutoGen框架 (v0.4+) 的多Agent協作編程工作流系統，實現代碼編寫、審查、優化的自動化流程。

## 🎯 系統概述

### Agent角色分工
- **🔧 Agent1 (Coder)**: 專業Python程序員，負責根據需求編寫高質量代碼
- **🔍 Agent2 (Reviewer)**: 代碼審查專家，負責代碼質量評估和改進建議
- **⚡ Agent3 (Optimizer)**: 代碼優化專家，負責性能優化和重構

### 工作流程
1. **代碼編寫**: Coder根據需求編寫初始代碼
2. **代碼審查**: Reviewer進行全面的代碼審查
3. **代碼優化**: Optimizer基於審查意見優化代碼
4. **迭代改進**: 重複上述流程直到達到質量標準

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 安裝AutoGen核心包
pip install -U "autogen-agentchat" "autogen-ext[openai]"

# 安裝其他依賴
pip install pandas numpy matplotlib seaborn plotly streamlit
```

### 2. 設置API密鑰

```bash
# 設置OpenAI API密鑰
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. 運行演示

```bash
# 運行完整演示
python demo_autogen_workflow.py

# 或者直接使用工作流
python autogen_executor.py
```

## 📁 文件結構

```
autogen_workflow/
├── autogen_workflow.py      # 核心工作流實現
├── autogen_config.py        # Agent配置和模板
├── autogen_executor.py      # 工作流執行器
├── demo_autogen_workflow.py # 演示腳本
└── AUTOGEN_README.md        # 說明文檔
```

## 🔧 核心組件

### AutoGenProgrammingWorkflow
主要的工作流管理器，提供以下功能：
- Agent初始化和配置
- 工作流執行和管理
- 資源清理和錯誤處理

### AutoGenWorkflowConfig
配置管理器，包含：
- Agent系統消息配置
- 工作流模板定義
- 預定義任務模板

### AutoGenExecutor
執行器，支持：
- 多種工作流模板
- 交互式和自動化模式
- 執行歷史記錄

## 📋 使用示例

### 基本使用

```python
import asyncio
from autogen_workflow import AutoGenProgrammingWorkflow

async def main():
    # 初始化工作流
    workflow = AutoGenProgrammingWorkflow()
    await workflow.initialize_agents()
    
    # 定義任務
    task = """
    創建一個Python函數來處理CSV數據：
    1. 讀取CSV文件
    2. 進行數據清洗
    3. 生成統計報告
    4. 保存結果
    """
    
    # 執行工作流
    result = await workflow.run_simple_workflow(task)
    
    # 清理資源
    await workflow.cleanup()

asyncio.run(main())
```

### 使用執行器

```python
import asyncio
from autogen_executor import AutoGenExecutor

async def main():
    executor = AutoGenExecutor()
    await executor.initialize()
    
    # 執行預定義任務
    result = await executor.execute_predefined_task("data_analysis")
    
    # 或執行自定義任務
    result = await executor.execute_workflow(
        "standard_programming", 
        "創建一個Web API服務"
    )
    
    await executor.cleanup()

asyncio.run(main())
```

## 🎮 交互式模式

運行交互式工作流：

```bash
python autogen_executor.py
```

選擇操作：
1. **執行預定義任務** - 選擇內建的任務模板
2. **自定義任務** - 輸入自己的編程需求
3. **查看執行歷史** - 檢視之前的執行記錄

## 📊 工作流模板

### 標準編程工作流
- **參與者**: Coder → Reviewer → Optimizer
- **輪次**: 3輪
- **適用**: 一般編程任務

### 快速原型開發
- **參與者**: Coder → Optimizer
- **輪次**: 2輪
- **適用**: 快速原型開發

### 純代碼審查
- **參與者**: Reviewer
- **輪次**: 1輪
- **適用**: 現有代碼審查

### 全面開發流程
- **參與者**: Coder → Reviewer → Optimizer
- **輪次**: 5輪
- **適用**: 複雜項目開發

## 🎯 預定義任務

### 數據分析任務
創建數據分析工具，包含：
- CSV/Excel文件讀取
- 數據清洗和預處理
- 統計分析和可視化
- 分析報告生成

### Web API任務
創建RESTful API服務，包含：
- CRUD操作實現
- 數據驗證和錯誤處理
- API文檔和測試
- 安全認證機制

### 自動化腳本任務
創建自動化腳本，包含：
- 文件批量處理
- 系統任務自動化
- 日誌記錄和監控
- 配置文件支持

## ⚙️ 配置選項

### Agent配置
每個Agent都可以自定義：
- 系統消息和角色定義
- 能力範圍和專長領域
- 最大連續回復次數

### 工作流配置
支持配置：
- 參與者列表和順序
- 執行模式（順序/輪詢）
- 最大輪次和終止條件

## 🔍 最佳實踐

### 任務描述
- 明確具體的功能需求
- 指定技術棧和依賴
- 包含質量標準和約束
- 提供示例和測試案例

### 工作流選擇
- 簡單任務：快速原型開發
- 中等複雜度：標準編程工作流
- 複雜項目：全面開發流程
- 代碼審查：純代碼審查

### 錯誤處理
- 檢查API密鑰設置
- 監控執行日誌
- 處理網絡連接問題
- 管理資源清理

## 🚨 注意事項

1. **API密鑰**: 確保設置有效的OpenAI API密鑰
2. **網絡連接**: 需要穩定的網絡連接訪問OpenAI API
3. **資源管理**: 及時清理模型客戶端資源
4. **成本控制**: 注意API調用成本，特別是長時間運行的工作流

## 🔧 故障排除

### 常見問題

**Q: 提示"未設置OPENAI_API_KEY"**
A: 設置環境變量：`export OPENAI_API_KEY="your-key"`

**Q: 工作流執行失敗**
A: 檢查網絡連接和API密鑰有效性

**Q: Agent回復不完整**
A: 增加最大輪次或調整終止條件

**Q: 內存使用過高**
A: 及時調用cleanup()方法清理資源

## 📈 擴展開發

### 添加新Agent
1. 在`autogen_config.py`中定義Agent配置
2. 在工作流中註冊新Agent
3. 更新工作流模板

### 自定義工作流
1. 定義參與者和執行順序
2. 設置終止條件
3. 配置最大輪次

### 集成外部工具
1. 擴展Agent能力
2. 添加工具調用接口
3. 實現結果處理邏輯

## 📞 支持

如有問題或建議，請：
1. 檢查文檔和示例代碼
2. 查看執行日誌和錯誤信息
3. 參考AutoGen官方文檔
4. 提交Issue或Pull Request

---

**AutoGen編程工作流系統 v1.0**  
基於AutoGen v0.4+ | 支持Python 3.10+
