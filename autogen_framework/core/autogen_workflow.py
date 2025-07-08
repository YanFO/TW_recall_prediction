#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoGen 編程工作流 - 基於最新AutoGen框架
實現三個Agent的協作編程流程：
- Agent1: 代碼編寫者 (Coder)
- Agent2: 代碼審查者 (Reviewer) 
- Agent3: 代碼優化者 (Optimizer)
"""

import asyncio
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

# 嘗試導入AutoGen，處理版本兼容性
try:
    # 嘗試新版本AutoGen (v0.4+)
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_agentchat.ui import Console
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    AUTOGEN_AVAILABLE = True
    AUTOGEN_VERSION = "v0.4"
    print("✅ 使用AutoGen v0.4")
except ImportError as e:
    print(f"⚠️  AutoGen v0.4導入失敗: {e}")
    try:
        # 嘗試舊版本AutoGen (v0.2)
        import autogen
        from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
        AUTOGEN_AVAILABLE = True
        AUTOGEN_VERSION = "v0.2"
        print("✅ 使用AutoGen v0.2")
    except ImportError as e2:
        print(f"⚠️  AutoGen v0.2導入失敗: {e2}")
        # 使用模擬版本
        AUTOGEN_AVAILABLE = False
        AUTOGEN_VERSION = "mock"
        print("⚠️  使用模擬AutoGen版本")

class AutoGenProgrammingWorkflow:
    """AutoGen編程工作流管理器 - 兼容多版本AutoGen"""

    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        初始化工作流

        Args:
            api_key: OpenAI API密鑰
            model: 使用的模型名稱
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.model_client = None
        self.agents = {}
        self.team = None
        self.autogen_version = AUTOGEN_VERSION
        self.autogen_available = AUTOGEN_AVAILABLE

        # 設置日誌
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def initialize_agents(self):
        """初始化所有Agent - 兼容多版本"""
        if not self.autogen_available:
            self.logger.warning("AutoGen不可用，使用模擬模式")
            return self._initialize_mock_agents()

        if self.autogen_version == "v0.4":
            return await self._initialize_v04_agents()
        elif self.autogen_version == "v0.2":
            return self._initialize_v02_agents()
        else:
            return self._initialize_mock_agents()

    async def _initialize_v04_agents(self):
        """初始化AutoGen v0.4 Agent"""
        try:
            # 創建模型客戶端
            self.model_client = OpenAIChatCompletionClient(
                model=self.model,
                api_key=self.api_key
            )
        
        # Agent1: 代碼編寫者
        self.agents["coder"] = AssistantAgent(
            name="coder",
            model_client=self.model_client,
            system_message="""你是一個專業的Python程序員。你的職責是：
1. 根據需求編寫高質量的Python代碼
2. 遵循PEP 8編碼規範
3. 添加適當的註釋和文檔字符串
4. 考慮代碼的可讀性和可維護性
5. 實現功能完整且邏輯清晰的代碼

請始終提供完整、可執行的代碼解決方案。"""
        )
        
        # Agent2: 代碼審查者
        self.agents["reviewer"] = AssistantAgent(
            name="reviewer",
            model_client=self.model_client,
            system_message="""你是一個經驗豐富的代碼審查專家。你的職責是：
1. 仔細審查提供的代碼
2. 識別潛在的bug、安全問題和性能問題
3. 檢查代碼是否遵循最佳實踐
4. 提供具體的改進建議
5. 評估代碼的可讀性、可維護性和擴展性

請提供詳細的審查報告，包括：
- 發現的問題列表
- 改進建議
- 代碼質量評分（1-10分）
- 優先級排序的修改建議"""
        )
        
        # Agent3: 代碼優化者
        self.agents["optimizer"] = AssistantAgent(
            name="optimizer",
            model_client=self.model_client,
            system_message="""你是一個代碼優化專家。你的職責是：
1. 基於審查者的反饋優化代碼
2. 提升代碼性能和效率
3. 改善代碼結構和設計模式
4. 增強錯誤處理和異常管理
5. 優化代碼的可讀性和可維護性

請提供：
- 優化後的完整代碼
- 優化說明和改進點
- 性能提升預期
- 最佳實踐應用說明"""
        )
        
        # 用戶代理
        self.agents["user"] = UserProxyAgent(
            name="user",
            human_input_mode="ALWAYS"
        )
        
    async def create_workflow_team(self, max_rounds: int = 10):
        """創建工作流團隊"""
        # 設置終止條件
        termination_conditions = [
            MaxMessageTermination(max_messages=max_rounds),
            TextMentionTermination(["WORKFLOW_COMPLETE", "完成工作流"])
        ]
        
        # 創建輪詢式群組聊天
        self.team = RoundRobinGroupChat(
            participants=[
                self.agents["user"],
                self.agents["coder"], 
                self.agents["reviewer"],
                self.agents["optimizer"]
            ],
            termination_condition=termination_conditions[0]  # 使用最大消息數終止
        )
        
    async def run_programming_workflow(self, task: str):
        """
        運行編程工作流
        
        Args:
            task: 編程任務描述
        """
        if not self.team:
            await self.create_workflow_team()
            
        # 構建工作流任務
        workflow_task = f"""
編程工作流任務: {task}

工作流程：
1. Coder: 根據需求編寫初始代碼
2. Reviewer: 審查代碼並提供改進建議  
3. Optimizer: 基於審查意見優化代碼
4. 重複此流程直到代碼質量滿足要求

請開始工作流程。
"""
        
        try:
            # 運行工作流
            await Console(self.team.run_stream(task=workflow_task))
        except Exception as e:
            print(f"工作流執行錯誤: {e}")
            
    async def run_simple_workflow(self, task: str, auto_mode: bool = True):
        """
        運行簡化的自動工作流（無用戶交互）
        
        Args:
            task: 編程任務描述
            auto_mode: 是否自動模式
        """
        if auto_mode:
            # 創建自動化團隊（無用戶交互）
            auto_team = RoundRobinGroupChat(
                participants=[
                    self.agents["coder"],
                    self.agents["reviewer"], 
                    self.agents["optimizer"]
                ],
                termination_condition=MaxMessageTermination(max_messages=6)
            )
            
            workflow_task = f"""
編程任務: {task}

自動工作流程：
1. Coder編寫代碼
2. Reviewer審查並提供建議
3. Optimizer優化代碼
請按順序完成任務。
"""
            
            try:
                result = await auto_team.run(task=workflow_task)
                return result
            except Exception as e:
                print(f"自動工作流執行錯誤: {e}")
                return None
                
    async def cleanup(self):
        """清理資源"""
        if self.model_client:
            await self.model_client.close()

# 使用示例
async def main():
    """主函數示例"""
    # 初始化工作流
    workflow = AutoGenProgrammingWorkflow()
    
    try:
        # 初始化agents
        await workflow.initialize_agents()
        
        # 示例任務
        task = """
創建一個Python函數，實現以下功能：
1. 讀取CSV文件
2. 對數據進行基本統計分析
3. 生成可視化圖表
4. 保存結果到文件

要求：
- 使用pandas處理數據
- 使用matplotlib生成圖表
- 包含錯誤處理
- 添加完整的文檔字符串
"""
        
        # 運行工作流
        print("🚀 啟動AutoGen編程工作流...")
        await workflow.run_simple_workflow(task, auto_mode=True)
        
    finally:
        # 清理資源
        await workflow.cleanup()

if __name__ == "__main__":
    # 運行示例
    asyncio.run(main())
