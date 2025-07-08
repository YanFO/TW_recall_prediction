#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoGen工作流執行器
整合工作流配置和執行邏輯
"""

import asyncio
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SequentialGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from autogen_config import AutoGenWorkflowConfig, WorkflowType, TASK_TEMPLATES

class AutoGenExecutor:
    """AutoGen工作流執行器"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        初始化執行器
        
        Args:
            api_key: OpenAI API密鑰
            model: 使用的模型
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.config = AutoGenWorkflowConfig()
        self.model_client = None
        self.agents = {}
        self.execution_history = []
        
    async def initialize(self):
        """初始化執行器"""
        # 創建模型客戶端
        self.model_client = OpenAIChatCompletionClient(
            model=self.model,
            api_key=self.api_key
        )
        
        # 創建所有配置的agents
        await self._create_agents()
        
    async def _create_agents(self):
        """創建所有agents"""
        for agent_name, agent_config in self.config.agent_configs.items():
            self.agents[agent_name] = AssistantAgent(
                name=agent_config.name,
                model_client=self.model_client,
                system_message=agent_config.system_message
            )
            
        # 創建用戶代理
        self.agents["user"] = UserProxyAgent(
            name="user",
            human_input_mode="NEVER"  # 自動模式
        )
        
    async def execute_workflow(self, 
                             template_name: str,
                             task: str,
                             include_user: bool = False) -> Dict[str, Any]:
        """
        執行工作流
        
        Args:
            template_name: 工作流模板名稱
            task: 任務描述
            include_user: 是否包含用戶交互
            
        Returns:
            執行結果字典
        """
        # 獲取工作流模板
        template = self.config.get_workflow_template(template_name)
        if not template:
            raise ValueError(f"未找到工作流模板: {template_name}")
            
        # 準備參與者
        participants = []
        for participant_name in template["participants"]:
            if participant_name in self.agents:
                participants.append(self.agents[participant_name])
                
        if include_user and "user" in self.agents:
            participants.insert(0, self.agents["user"])
            
        # 創建終止條件
        termination_conditions = [
            MaxMessageTermination(max_messages=template["max_rounds"] * len(participants)),
            TextMentionTermination(template["termination_keywords"])
        ]
        
        # 根據工作流類型創建團隊
        if template["workflow_type"] == WorkflowType.ROUND_ROBIN:
            team = RoundRobinGroupChat(
                participants=participants,
                termination_condition=termination_conditions[0]
            )
        else:  # SEQUENTIAL
            team = SequentialGroupChat(
                participants=participants,
                termination_condition=termination_conditions[0]
            )
            
        # 構建任務描述
        enhanced_task = self._enhance_task_description(task, template)
        
        # 記錄執行開始
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "template": template_name,
            "task": task,
            "participants": template["participants"],
            "status": "started"
        }
        
        try:
            # 執行工作流
            result = await team.run(task=enhanced_task)
            
            # 記錄成功
            execution_record["status"] = "completed"
            execution_record["result"] = str(result)
            
            return {
                "success": True,
                "result": result,
                "execution_record": execution_record
            }
            
        except Exception as e:
            # 記錄錯誤
            execution_record["status"] = "failed"
            execution_record["error"] = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "execution_record": execution_record
            }
            
        finally:
            # 保存執行記錄
            self.execution_history.append(execution_record)
            
    def _enhance_task_description(self, task: str, template: Dict[str, Any]) -> str:
        """增強任務描述"""
        enhanced = f"""
🎯 工作流任務: {template['name']}
📋 任務描述: {task}

👥 參與角色:
"""
        for participant in template["participants"]:
            agent_config = self.config.get_agent_config(participant)
            if agent_config:
                enhanced += f"- {agent_config.name}: {agent_config.role}\n"
                
        enhanced += f"""
🔄 工作流程: {template['workflow_type'].value}
🎯 最大輪次: {template['max_rounds']}

請按照各自的專業職責協作完成任務。
"""
        return enhanced
        
    async def execute_predefined_task(self, task_type: str, template_name: str = "standard_programming") -> Dict[str, Any]:
        """執行預定義任務"""
        if task_type not in TASK_TEMPLATES:
            raise ValueError(f"未找到預定義任務類型: {task_type}")
            
        task = TASK_TEMPLATES[task_type]
        return await self.execute_workflow(template_name, task)
        
    async def interactive_workflow(self):
        """交互式工作流執行"""
        print("🚀 AutoGen編程工作流執行器")
        print("=" * 50)
        
        # 顯示可用模板
        templates = self.config.list_available_templates()
        print("📋 可用工作流模板:")
        for i, template in enumerate(templates, 1):
            template_info = self.config.get_workflow_template(template)
            print(f"{i}. {template_info['name']} - {template_info['description']}")
            
        # 顯示預定義任務
        print("\n📝 預定義任務類型:")
        for i, task_type in enumerate(TASK_TEMPLATES.keys(), 1):
            print(f"{i}. {task_type}")
            
        print("\n" + "=" * 50)
        
        while True:
            print("\n選擇操作:")
            print("1. 執行預定義任務")
            print("2. 自定義任務")
            print("3. 查看執行歷史")
            print("4. 退出")
            
            choice = input("請輸入選擇 (1-4): ").strip()
            
            if choice == "1":
                await self._handle_predefined_task()
            elif choice == "2":
                await self._handle_custom_task()
            elif choice == "3":
                self._show_execution_history()
            elif choice == "4":
                break
            else:
                print("❌ 無效選擇，請重新輸入")
                
    async def _handle_predefined_task(self):
        """處理預定義任務"""
        task_types = list(TASK_TEMPLATES.keys())
        print("\n選擇任務類型:")
        for i, task_type in enumerate(task_types, 1):
            print(f"{i}. {task_type}")
            
        try:
            choice = int(input("請輸入選擇: ")) - 1
            if 0 <= choice < len(task_types):
                task_type = task_types[choice]
                print(f"\n🚀 執行任務: {task_type}")
                result = await self.execute_predefined_task(task_type)
                
                if result["success"]:
                    print("✅ 任務執行成功!")
                else:
                    print(f"❌ 任務執行失敗: {result['error']}")
            else:
                print("❌ 無效選擇")
        except ValueError:
            print("❌ 請輸入有效數字")
            
    async def _handle_custom_task(self):
        """處理自定義任務"""
        templates = self.config.list_available_templates()
        print("\n選擇工作流模板:")
        for i, template in enumerate(templates, 1):
            template_info = self.config.get_workflow_template(template)
            print(f"{i}. {template_info['name']}")
            
        try:
            choice = int(input("請輸入選擇: ")) - 1
            if 0 <= choice < len(templates):
                template_name = templates[choice]
                task = input("請輸入任務描述: ").strip()
                
                if task:
                    print(f"\n🚀 執行自定義任務...")
                    result = await self.execute_workflow(template_name, task)
                    
                    if result["success"]:
                        print("✅ 任務執行成功!")
                    else:
                        print(f"❌ 任務執行失敗: {result['error']}")
                else:
                    print("❌ 任務描述不能為空")
            else:
                print("❌ 無效選擇")
        except ValueError:
            print("❌ 請輸入有效數字")
            
    def _show_execution_history(self):
        """顯示執行歷史"""
        if not self.execution_history:
            print("📝 暫無執行歷史")
            return
            
        print("\n📊 執行歷史:")
        for i, record in enumerate(self.execution_history, 1):
            status_icon = "✅" if record["status"] == "completed" else "❌"
            print(f"{i}. {status_icon} {record['timestamp']} - {record['template']} ({record['status']})")
            
    async def cleanup(self):
        """清理資源"""
        if self.model_client:
            await self.model_client.close()

# 主執行函數
async def main():
    """主函數"""
    executor = AutoGenExecutor()
    
    try:
        await executor.initialize()
        await executor.interactive_workflow()
    finally:
        await executor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
