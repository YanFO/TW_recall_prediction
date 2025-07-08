#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoGen編程工作流演示
展示三個Agent協作編程的完整流程
"""

import asyncio
import os
import json
import sys
from datetime import datetime
from autogen_workflow_compatible import AutoGenProgrammingWorkflow

def print_banner():
    """打印橫幅"""
    print("🚀 AutoGen編程工作流演示")
    print("=" * 60)
    print("實現三個Agent的協作編程流程：")
    print("  🤖 Agent1 (Coder): 代碼編寫者")
    print("  🔍 Agent2 (Reviewer): 代碼審查者")
    print("  ⚡ Agent3 (Optimizer): 代碼優化者")
    print("=" * 60)

def check_environment():
    """檢查環境配置"""
    print("\n🔧 環境檢查")
    print("-" * 30)
    
    # 檢查Python版本
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    # 檢查AutoGen
    try:
        import autogen
        print(f"✅ AutoGen版本: {autogen.__version__}")
    except ImportError:
        print("❌ AutoGen未安裝")
        return False
    
    # 檢查API密鑰
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API密鑰: 已設置 (長度: {len(api_key)})")
        return True
    else:
        print("⚠️  OpenAI API密鑰: 未設置")
        print("   請設置環境變量: export OPENAI_API_KEY='your-api-key'")
        return False

def get_demo_tasks():
    """獲取演示任務列表"""
    return {
        "1": {
            "name": "斐波那契數列計算器",
            "description": """創建一個Python函數，用於計算斐波那契數列的第n項。
要求：
1. 使用遞歸實現
2. 添加記憶化優化
3. 包含錯誤處理
4. 添加單元測試
5. 提供使用示例"""
        },
        "2": {
            "name": "文件處理工具",
            "description": """創建一個Python類，用於處理文本文件。
要求：
1. 支持讀取、寫入、追加操作
2. 實現文件備份功能
3. 添加異常處理
4. 支持不同編碼格式
5. 包含完整的文檔字符串"""
        },
        "3": {
            "name": "數據分析助手",
            "description": """創建一個Python腳本，用於分析CSV數據。
要求：
1. 讀取CSV文件
2. 計算基本統計信息
3. 生成數據可視化圖表
4. 導出分析報告
5. 處理缺失值和異常數據"""
        },
        "4": {
            "name": "API客戶端",
            "description": """創建一個Python類，用於與REST API交互。
要求：
1. 支持GET、POST、PUT、DELETE請求
2. 實現認證機制
3. 添加重試邏輯
4. 包含錯誤處理
5. 提供異步支持"""
        }
    }

def select_task():
    """選擇演示任務"""
    tasks = get_demo_tasks()
    
    print("\n📋 可用的演示任務:")
    print("-" * 30)
    for key, task in tasks.items():
        print(f"{key}. {task['name']}")
    
    print("0. 自定義任務")
    
    while True:
        choice = input("\n請選擇任務 (0-4): ").strip()
        
        if choice == "0":
            custom_task = input("請輸入自定義任務描述: ").strip()
            if custom_task:
                return custom_task
            else:
                print("❌ 任務描述不能為空")
                continue
        elif choice in tasks:
            return tasks[choice]["description"]
        else:
            print("❌ 無效選擇，請重新輸入")

async def run_demo_workflow(task_description):
    """運行演示工作流"""
    print(f"\n🚀 開始執行編程工作流")
    print("-" * 40)
    print(f"📝 任務: {task_description.strip()[:100]}...")
    
    # 創建工作流實例
    workflow = AutoGenProgrammingWorkflow()
    
    # 運行工作流
    results = await workflow.run_simple_workflow(task_description)
    
    if results:
        print("\n✅ 工作流執行完成！")
        return results
    else:
        print("\n❌ 工作流執行失敗")
        return None

def display_results(results):
    """顯示結果"""
    if not results:
        return
    
    print("\n📊 工作流結果")
    print("=" * 60)
    
    # 代碼編寫結果
    print("\n🤖 Agent1 (Coder) - 代碼編寫:")
    print("-" * 40)
    print(results.get("code", "無結果"))
    
    # 代碼審查結果
    print("\n🔍 Agent2 (Reviewer) - 代碼審查:")
    print("-" * 40)
    print(results.get("review", "無結果"))
    
    # 代碼優化結果
    print("\n⚡ Agent3 (Optimizer) - 代碼優化:")
    print("-" * 40)
    print(results.get("optimized_code", "無結果"))

def save_demo_results(results, task_description):
    """保存演示結果"""
    if not results:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"autogen_demo_results_{timestamp}.json"
    
    demo_data = {
        "timestamp": timestamp,
        "task_description": task_description,
        "workflow_results": results,
        "metadata": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "autogen_available": True,
            "demo_version": "1.0"
        }
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(demo_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 結果已保存到: {filename}")
    except Exception as e:
        print(f"\n❌ 保存結果失敗: {e}")

async def interactive_demo():
    """交互式演示"""
    print_banner()
    
    # 環境檢查
    if not check_environment():
        print("\n❌ 環境檢查失敗，無法運行真實AutoGen工作流")
        print("💡 提示: 設置OPENAI_API_KEY環境變量後重試")
        print("   或者運行模擬模式查看工作流結構")
        
        choice = input("\n是否運行模擬模式? (y/n): ").strip().lower()
        if choice != 'y':
            return
        
        print("\n🔧 運行模擬模式...")
    
    # 選擇任務
    task_description = select_task()
    
    # 運行工作流
    results = await run_demo_workflow(task_description)
    
    # 顯示結果
    display_results(results)
    
    # 保存結果
    if results:
        save_choice = input("\n💾 是否保存結果? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_demo_results(results, task_description)
    
    print("\n🎉 演示完成！")
    print("📖 更多信息請參考: AUTOGEN_README.md")

def quick_demo():
    """快速演示模式"""
    print_banner()
    
    # 使用預設任務
    task = get_demo_tasks()["1"]["description"]
    print(f"\n🚀 快速演示: {get_demo_tasks()['1']['name']}")
    
    # 運行工作流
    async def run():
        results = await run_demo_workflow(task)
        display_results(results)
        if results:
            save_demo_results(results, task)
    
    asyncio.run(run())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 快速演示模式
        quick_demo()
    else:
        # 交互式演示模式
        asyncio.run(interactive_demo())
