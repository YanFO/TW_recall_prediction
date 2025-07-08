#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoGen工作流配置文件
包含Agent配置、工作流模板和執行策略
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class WorkflowType(Enum):
    """工作流類型枚舉"""
    SEQUENTIAL = "sequential"  # 順序執行
    ROUND_ROBIN = "round_robin"  # 輪詢執行
    HIERARCHICAL = "hierarchical"  # 層次執行

@dataclass
class AgentConfig:
    """Agent配置類"""
    name: str
    role: str
    system_message: str
    capabilities: List[str]
    max_consecutive_auto_reply: int = 3

class AutoGenWorkflowConfig:
    """AutoGen工作流配置管理器"""
    
    def __init__(self):
        self.agent_configs = self._initialize_agent_configs()
        self.workflow_templates = self._initialize_workflow_templates()
        
    def _initialize_agent_configs(self) -> Dict[str, AgentConfig]:
        """初始化Agent配置"""
        return {
            "coder": AgentConfig(
                name="coder",
                role="代碼編寫專家",
                system_message="""你是一個資深的Python開發工程師，專精於：

🎯 核心職責：
1. 根據需求分析編寫高質量Python代碼
2. 遵循PEP 8和Python最佳實踐
3. 實現完整的功能邏輯和錯誤處理
4. 編寫清晰的文檔字符串和註釋

💡 編程原則：
- 代碼簡潔、可讀、可維護
- 適當的設計模式應用
- 完善的異常處理機制
- 模塊化和可重用性設計

📝 輸出格式：
- 提供完整可執行的代碼
- 包含詳細的功能說明
- 標註關鍵實現邏輯
- 說明依賴庫和環境要求

請始終以專業、高效的方式完成編程任務。""",
                capabilities=[
                    "Python編程", "算法實現", "數據處理", 
                    "Web開發", "API設計", "數據庫操作"
                ]
            ),
            
            "reviewer": AgentConfig(
                name="reviewer",
                role="代碼審查專家", 
                system_message="""你是一個經驗豐富的代碼審查專家，專精於：

🔍 審查重點：
1. 代碼邏輯正確性和完整性
2. 安全漏洞和潛在風險識別
3. 性能瓶頸和優化機會
4. 代碼規範和最佳實踐遵循

📊 評估維度：
- 功能性 (Functionality): 是否正確實現需求
- 可靠性 (Reliability): 錯誤處理和邊界情況
- 性能 (Performance): 時間和空間複雜度
- 可維護性 (Maintainability): 代碼結構和可讀性
- 安全性 (Security): 潛在安全風險

📋 審查報告格式：
1. 總體評分 (1-10分)
2. 發現問題列表 (按優先級排序)
3. 具體改進建議
4. 最佳實踐推薦
5. 風險評估

請提供專業、詳細、可操作的審查意見。""",
                capabilities=[
                    "代碼審查", "安全分析", "性能評估",
                    "架構設計", "質量保證", "最佳實踐"
                ]
            ),
            
            "optimizer": AgentConfig(
                name="optimizer",
                role="代碼優化專家",
                system_message="""你是一個代碼優化專家，專精於：

⚡ 優化目標：
1. 基於審查反饋進行代碼重構
2. 提升代碼性能和執行效率
3. 改善代碼結構和設計模式
4. 增強錯誤處理和健壯性

🛠️ 優化策略：
- 算法優化：選擇更高效的算法和數據結構
- 代碼重構：改善代碼組織和模塊化
- 性能調優：減少時間和空間複雜度
- 設計模式：應用適當的設計模式
- 異常處理：完善錯誤處理機制

📈 優化報告：
1. 優化後的完整代碼
2. 主要改進點說明
3. 性能提升預期
4. 設計模式應用
5. 最佳實踐實施

🎯 質量標準：
- 代碼可讀性和可維護性
- 執行效率和資源利用
- 錯誤處理的完整性
- 擴展性和靈活性

請提供高質量的優化方案和實現。""",
                capabilities=[
                    "代碼重構", "性能優化", "架構改進",
                    "設計模式", "算法優化", "質量提升"
                ]
            )
        }
    
    def _initialize_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化工作流模板"""
        return {
            "standard_programming": {
                "name": "標準編程工作流",
                "description": "代碼編寫 -> 審查 -> 優化的標準流程",
                "participants": ["coder", "reviewer", "optimizer"],
                "workflow_type": WorkflowType.ROUND_ROBIN,
                "max_rounds": 3,
                "termination_keywords": ["WORKFLOW_COMPLETE", "優化完成"]
            },
            
            "rapid_prototyping": {
                "name": "快速原型開發",
                "description": "快速編寫原型代碼並進行基本優化",
                "participants": ["coder", "optimizer"],
                "workflow_type": WorkflowType.SEQUENTIAL,
                "max_rounds": 2,
                "termination_keywords": ["PROTOTYPE_COMPLETE", "原型完成"]
            },
            
            "code_review_only": {
                "name": "純代碼審查",
                "description": "對現有代碼進行詳細審查",
                "participants": ["reviewer"],
                "workflow_type": WorkflowType.SEQUENTIAL,
                "max_rounds": 1,
                "termination_keywords": ["REVIEW_COMPLETE", "審查完成"]
            },
            
            "comprehensive_development": {
                "name": "全面開發流程",
                "description": "包含多輪迭代的完整開發流程",
                "participants": ["coder", "reviewer", "optimizer"],
                "workflow_type": WorkflowType.ROUND_ROBIN,
                "max_rounds": 5,
                "termination_keywords": ["DEVELOPMENT_COMPLETE", "開發完成"]
            }
        }
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """獲取Agent配置"""
        return self.agent_configs.get(agent_name)
    
    def get_workflow_template(self, template_name: str) -> Dict[str, Any]:
        """獲取工作流模板"""
        return self.workflow_templates.get(template_name)
    
    def list_available_templates(self) -> List[str]:
        """列出可用的工作流模板"""
        return list(self.workflow_templates.keys())
    
    def create_custom_workflow(self, 
                             name: str,
                             participants: List[str],
                             workflow_type: WorkflowType = WorkflowType.ROUND_ROBIN,
                             max_rounds: int = 3) -> Dict[str, Any]:
        """創建自定義工作流"""
        return {
            "name": name,
            "participants": participants,
            "workflow_type": workflow_type,
            "max_rounds": max_rounds,
            "termination_keywords": ["CUSTOM_COMPLETE", "自定義完成"]
        }

# 預定義任務模板
TASK_TEMPLATES = {
    "data_analysis": """
創建一個數據分析工具，要求：
1. 讀取CSV/Excel文件
2. 進行數據清洗和預處理
3. 執行統計分析和可視化
4. 生成分析報告

技術要求：
- 使用pandas, numpy, matplotlib/seaborn
- 包含完整的錯誤處理
- 支持多種數據格式
- 生成可重用的分析模塊
""",
    
    "web_api": """
創建一個RESTful API服務，要求：
1. 實現CRUD操作
2. 數據驗證和錯誤處理
3. API文檔和測試
4. 安全認證機制

技術要求：
- 使用FastAPI或Flask
- 數據庫集成（SQLAlchemy）
- JWT認證
- 完整的API文檔
""",
    
    "automation_script": """
創建一個自動化腳本，要求：
1. 文件批量處理
2. 系統任務自動化
3. 日誌記錄和監控
4. 配置文件支持

技術要求：
- 命令行界面
- 配置文件解析
- 日誌系統
- 異常處理和恢復
"""
}

# 配置實例
config = AutoGenWorkflowConfig()
