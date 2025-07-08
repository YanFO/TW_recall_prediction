#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoGen 編程工作流 - 兼容版本
支持Python 3.9和多版本AutoGen
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

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 嘗試導入AutoGen，處理版本兼容性
AUTOGEN_AVAILABLE = False
AUTOGEN_VERSION = "none"

try:
    # 嘗試新版本AutoGen (v0.4+)
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    AUTOGEN_AVAILABLE = True
    AUTOGEN_VERSION = "v0.4"
    logger.info("✅ 使用AutoGen v0.4")
except ImportError as e:
    logger.warning(f"⚠️  AutoGen v0.4導入失敗: {e}")
    try:
        # 嘗試舊版本AutoGen (v0.2)
        import autogen
        AUTOGEN_AVAILABLE = True
        AUTOGEN_VERSION = "v0.2"
        logger.info("✅ 使用AutoGen v0.2")
    except ImportError as e2:
        logger.warning(f"⚠️  AutoGen v0.2導入失敗: {e2}")
        logger.info("⚠️  使用模擬AutoGen版本")

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
        self.logger = logger
        
        # 檢查API密鑰
        if not self.api_key:
            self.logger.warning("⚠️  未設置OPENAI_API_KEY環境變量")
    
    def _get_system_messages(self):
        """獲取系統消息"""
        return {
            "coder": """你是一個專業的Python程序員。你的職責是：
1. 根據需求編寫高質量的Python代碼
2. 遵循PEP 8編碼規範
3. 添加適當的註釋和文檔字符串
4. 考慮代碼的可讀性和可維護性
5. 實現功能完整且邏輯清晰的代碼

請始終提供完整、可執行的代碼解決方案。""",
            
            "reviewer": """你是一個經驗豐富的代碼審查專家。你的職責是：
1. 仔細審查提供的代碼
2. 識別潛在的bug、安全問題和性能問題
3. 檢查代碼是否遵循最佳實踐
4. 提供具體的改進建議
5. 評估代碼的可讀性、可維護性和擴展性

請提供詳細的審查報告，包括：
- 發現的問題列表
- 改進建議
- 代碼質量評分（1-10分）
- 優先級排序的修改建議""",
            
            "optimizer": """你是一個代碼優化專家。你的職責是：
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
        }
    
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
            if not self.api_key:
                self.logger.error("❌ 需要OpenAI API密鑰")
                return False
                
            # 創建模型客戶端
            self.model_client = OpenAIChatCompletionClient(
                model=self.model,
                api_key=self.api_key
            )
            
            system_messages = self._get_system_messages()
            
            # 創建agents
            self.agents["coder"] = AssistantAgent(
                name="coder",
                model_client=self.model_client,
                system_message=system_messages["coder"]
            )
            
            self.agents["reviewer"] = AssistantAgent(
                name="reviewer",
                model_client=self.model_client,
                system_message=system_messages["reviewer"]
            )
            
            self.agents["optimizer"] = AssistantAgent(
                name="optimizer",
                model_client=self.model_client,
                system_message=system_messages["optimizer"]
            )
            
            self.agents["user"] = UserProxyAgent(
                name="user",
                human_input_mode="ALWAYS"
            )
            
            self.logger.info("✅ AutoGen v0.4 agents初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ AutoGen v0.4 agents初始化失敗: {e}")
            return False
    
    def _initialize_v02_agents(self):
        """初始化AutoGen v0.2 Agent"""
        try:
            if not self.api_key:
                self.logger.error("❌ 需要OpenAI API密鑰")
                return False
                
            # 使用舊版本AutoGen的配置
            config_list = [
                {
                    "model": self.model,
                    "api_key": self.api_key,
                }
            ]
            
            system_messages = self._get_system_messages()
            
            # 創建agents
            self.agents["coder"] = autogen.AssistantAgent(
                name="coder",
                llm_config={"config_list": config_list},
                system_message=system_messages["coder"]
            )
            
            self.agents["reviewer"] = autogen.AssistantAgent(
                name="reviewer",
                llm_config={"config_list": config_list},
                system_message=system_messages["reviewer"]
            )
            
            self.agents["optimizer"] = autogen.AssistantAgent(
                name="optimizer",
                llm_config={"config_list": config_list},
                system_message=system_messages["optimizer"]
            )
            
            self.agents["user"] = autogen.UserProxyAgent(
                name="user",
                human_input_mode="ALWAYS",
                code_execution_config={"work_dir": "autogen_workspace"}
            )
            
            self.logger.info("✅ AutoGen v0.2 agents初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ AutoGen v0.2 agents初始化失敗: {e}")
            return False
    
    def _initialize_mock_agents(self):
        """初始化模擬Agent"""
        self.logger.info("🔧 使用模擬AutoGen agents")
        
        class MockAgent:
            def __init__(self, name, system_message):
                self.name = name
                self.system_message = system_message
                self.logger = logger
            
            def generate_reply(self, message):
                self.logger.info(f"[{self.name}] 收到消息: {message[:100]}...")
                return f"[模擬回復 from {self.name}] 基於系統消息處理: {message[:50]}..."
        
        system_messages = self._get_system_messages()
        
        self.agents["coder"] = MockAgent("coder", system_messages["coder"])
        self.agents["reviewer"] = MockAgent("reviewer", system_messages["reviewer"])
        self.agents["optimizer"] = MockAgent("optimizer", system_messages["optimizer"])
        self.agents["user"] = MockAgent("user", "用戶代理")
        
        self.logger.info("✅ 模擬agents初始化成功")
        return True
    
    async def run_simple_workflow(self, task: str):
        """運行簡化的編程工作流"""
        self.logger.info(f"🚀 開始編程工作流: {task}")
        
        # 初始化agents
        if not await self.initialize_agents():
            self.logger.error("❌ Agent初始化失敗")
            return None
        
        results = {}
        
        # 步驟1: 代碼編寫
        self.logger.info("📝 步驟1: 代碼編寫")
        coder_prompt = f"請為以下需求編寫Python代碼:\n{task}"
        
        if self.autogen_available and self.autogen_version in ["v0.4", "v0.2"]:
            # 使用真實AutoGen
            try:
                if self.autogen_version == "v0.4":
                    # v0.4版本的調用方式
                    coder_response = await self.agents["coder"].generate_reply([{"content": coder_prompt, "role": "user"}])
                else:
                    # v0.2版本的調用方式
                    coder_response = self.agents["coder"].generate_reply(coder_prompt)
                results["code"] = coder_response
            except Exception as e:
                self.logger.error(f"❌ 代碼生成失敗: {e}")
                results["code"] = f"代碼生成失敗: {e}"
        else:
            # 使用模擬版本
            results["code"] = self.agents["coder"].generate_reply(coder_prompt)
        
        # 步驟2: 代碼審查
        self.logger.info("🔍 步驟2: 代碼審查")
        review_prompt = f"請審查以下代碼:\n{results['code']}"
        results["review"] = self.agents["reviewer"].generate_reply(review_prompt)
        
        # 步驟3: 代碼優化
        self.logger.info("⚡ 步驟3: 代碼優化")
        optimize_prompt = f"請基於以下審查意見優化代碼:\n審查意見: {results['review']}\n原始代碼: {results['code']}"
        results["optimized_code"] = self.agents["optimizer"].generate_reply(optimize_prompt)
        
        self.logger.info("✅ 編程工作流完成")
        return results
    
    def save_results(self, results: Dict, filename: str = None):
        """保存工作流結果"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"autogen_workflow_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            self.logger.info(f"✅ 結果已保存到: {filename}")
        except Exception as e:
            self.logger.error(f"❌ 保存結果失敗: {e}")

# 演示函數
async def demo_workflow():
    """演示AutoGen工作流"""
    print("🚀 AutoGen編程工作流演示")
    print("=" * 50)
    
    # 創建工作流
    workflow = AutoGenProgrammingWorkflow()
    
    # 示例任務
    task = """
    創建一個Python函數，用於計算斐波那契數列的第n項。
    要求：
    1. 使用遞歸實現
    2. 添加記憶化優化
    3. 包含錯誤處理
    4. 添加單元測試
    """
    
    # 運行工作流
    results = await workflow.run_simple_workflow(task)
    
    if results:
        print("\n📋 工作流結果:")
        print("-" * 30)
        for step, result in results.items():
            print(f"\n{step.upper()}:")
            print(result)
        
        # 保存結果
        workflow.save_results(results)
    else:
        print("❌ 工作流執行失敗")

if __name__ == "__main__":
    asyncio.run(demo_workflow())
