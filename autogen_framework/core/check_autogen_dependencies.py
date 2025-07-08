#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoGen依賴檢查腳本
檢查AutoGen工作流所需的依賴是否正確安裝
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """檢查Python版本"""
    print("🐍 檢查Python版本...")
    version = sys.version_info
    print(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print("   ✅ Python版本符合要求 (3.10+)")
        return True
    else:
        print("   ❌ Python版本過低，需要3.10或更高版本")
        return False

def check_package(package_name, import_name=None):
    """檢查包是否已安裝"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            print(f"   ✅ {package_name} 已安裝")
            return True
        else:
            print(f"   ❌ {package_name} 未安裝")
            return False
    except ImportError:
        print(f"   ❌ {package_name} 未安裝")
        return False

def install_package(package_name):
    """安裝包"""
    print(f"🔧 正在安裝 {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"   ✅ {package_name} 安裝成功")
        return True
    except subprocess.CalledProcessError:
        print(f"   ❌ {package_name} 安裝失敗")
        return False

def check_autogen_packages():
    """檢查AutoGen相關包"""
    print("\n📦 檢查AutoGen相關包...")
    
    packages = [
        ("autogen-agentchat", "autogen_agentchat"),
        ("autogen-ext[openai]", "autogen_ext"),
    ]
    
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    return missing_packages

def check_basic_packages():
    """檢查基本依賴包"""
    print("\n📚 檢查基本依賴包...")
    
    packages = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("asyncio", "asyncio"),
        ("json", "json"),
        ("datetime", "datetime"),
        ("typing", "typing"),
        ("dataclasses", "dataclasses"),
        ("enum", "enum"),
    ]
    
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    return missing_packages

def check_openai_api_key():
    """檢查OpenAI API密鑰"""
    print("\n🔑 檢查OpenAI API密鑰...")
    
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print(f"   ✅ OPENAI_API_KEY 已設置 (長度: {len(api_key)})")
        return True
    else:
        print("   ⚠️  OPENAI_API_KEY 未設置")
        print("   請設置環境變量: export OPENAI_API_KEY='your-api-key'")
        return False

def test_autogen_import():
    """測試AutoGen導入"""
    print("\n🧪 測試AutoGen導入...")
    
    try:
        from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
        print("   ✅ autogen_agentchat.agents 導入成功")
    except ImportError as e:
        print(f"   ❌ autogen_agentchat.agents 導入失敗: {e}")
        return False
    
    try:
        from autogen_agentchat.teams import RoundRobinGroupChat
        print("   ✅ autogen_agentchat.teams 導入成功")
    except ImportError as e:
        print(f"   ❌ autogen_agentchat.teams 導入失敗: {e}")
        return False
    
    try:
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        print("   ✅ autogen_ext.models.openai 導入成功")
    except ImportError as e:
        print(f"   ❌ autogen_ext.models.openai 導入失敗: {e}")
        return False
    
    return True

def main():
    """主函數"""
    print("🚀 AutoGen工作流依賴檢查")
    print("=" * 50)
    
    # 檢查Python版本
    if not check_python_version():
        print("\n❌ Python版本不符合要求，請升級Python")
        return False
    
    # 檢查基本包
    missing_basic = check_basic_packages()
    if missing_basic:
        print(f"\n⚠️  缺少基本依賴包: {missing_basic}")
        print("這些通常是Python標準庫，請檢查Python安裝")
    
    # 檢查AutoGen包
    missing_autogen = check_autogen_packages()
    
    if missing_autogen:
        print(f"\n❌ 缺少AutoGen包: {missing_autogen}")
        print("\n是否要自動安裝缺少的包? (y/n): ", end="")
        
        try:
            choice = input().strip().lower()
            if choice == 'y':
                print("\n🔧 開始安裝缺少的包...")
                for package in missing_autogen:
                    install_package(package)
                
                # 重新檢查
                print("\n🔄 重新檢查AutoGen包...")
                missing_autogen = check_autogen_packages()
                
                if missing_autogen:
                    print(f"\n❌ 仍有包未成功安裝: {missing_autogen}")
                    return False
            else:
                print("\n⚠️  請手動安裝缺少的包:")
                for package in missing_autogen:
                    print(f"   pip install {package}")
                return False
        except KeyboardInterrupt:
            print("\n\n👋 用戶中斷")
            return False
    
    # 測試AutoGen導入
    if not test_autogen_import():
        print("\n❌ AutoGen導入測試失敗")
        return False
    
    # 檢查API密鑰
    api_key_ok = check_openai_api_key()
    
    # 總結
    print("\n" + "=" * 50)
    print("📋 檢查結果總結:")
    print("   ✅ Python版本: 符合要求")
    print("   ✅ AutoGen包: 已安裝")
    print("   ✅ 導入測試: 通過")
    
    if api_key_ok:
        print("   ✅ API密鑰: 已設置")
        print("\n🎉 所有依賴檢查通過！可以運行AutoGen工作流")
    else:
        print("   ⚠️  API密鑰: 未設置")
        print("\n⚠️  依賴已就緒，但需要設置OpenAI API密鑰才能運行")
    
    print("\n📖 使用說明:")
    print("   1. 運行演示: python demo_autogen_workflow.py")
    print("   2. 交互式執行: python autogen_executor.py")
    print("   3. 查看文檔: 參考 AUTOGEN_README.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 檢查被中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 檢查過程中發生錯誤: {e}")
        sys.exit(1)
