#!/usr/bin/env python3
"""
Taiwan Recall Prediction System - Project Manager
項目管理器 - 快速啟動和管理系統組件

Usage:
    python scripts/project_manager.py --help
    python scripts/project_manager.py --start-dashboard
    python scripts/project_manager.py --start-autogen
    python scripts/project_manager.py --check-status
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

class ProjectManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.taiwan_dir = self.root_dir / "taiwan_recall_prediction"
        self.autogen_dir = self.root_dir / "autogen_framework"
        
    def print_banner(self):
        """顯示項目橫幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                Taiwan Recall Prediction System              ║
║                    台灣罷免預測系統                          ║
║                      Project Manager                        ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_dependencies(self):
        """檢查系統依賴"""
        print("🔍 檢查系統依賴...")
        
        # 檢查Python版本
        python_version = sys.version_info
        print(f"   Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 檢查Docker
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Docker: {result.stdout.strip()}")
            else:
                print("   ❌ Docker未安裝或無法訪問")
        except FileNotFoundError:
            print("   ❌ Docker未找到")
        
        # 檢查AutoGen
        try:
            import autogen
            print(f"   ✅ AutoGen已安裝")
        except ImportError:
            print("   ⚠️  AutoGen未安裝 (可選)")
        
        # 檢查主要Python包
        required_packages = ['streamlit', 'pandas', 'numpy', 'requests']
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package} 未安裝")
    
    def start_dashboard(self):
        """啟動台灣罷免預測儀表板"""
        print("🚀 啟動台灣罷免預測儀表板...")
        
        if not self.taiwan_dir.exists():
            print("❌ 台灣罷免預測系統目錄不存在")
            return False
        
        # 檢查是否使用Docker
        docker_compose_file = self.taiwan_dir / "docker-compose.yml"
        if docker_compose_file.exists():
            print("   使用Docker Compose啟動...")
            try:
                os.chdir(self.taiwan_dir)
                subprocess.run(['docker-compose', 'up', '-d'], check=True)
                print("   ✅ Docker服務已啟動")
                print("   🌐 儀表板地址: http://localhost:8501")
                return True
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Docker啟動失敗: {e}")
                return False
        else:
            # 直接運行Streamlit
            print("   使用Streamlit直接啟動...")
            try:
                dashboard_file = self.taiwan_dir / "dashboard.py"
                if dashboard_file.exists():
                    os.chdir(self.taiwan_dir)
                    subprocess.Popen(['streamlit', 'run', 'dashboard.py'])
                    print("   ✅ Streamlit已啟動")
                    print("   🌐 儀表板地址: http://localhost:8501")
                    return True
                else:
                    print("   ❌ dashboard.py文件不存在")
                    return False
            except Exception as e:
                print(f"   ❌ Streamlit啟動失敗: {e}")
                return False
    
    def start_autogen_demo(self):
        """啟動AutoGen編程工作流演示"""
        print("🤖 啟動AutoGen編程工作流演示...")
        
        if not self.autogen_dir.exists():
            print("❌ AutoGen框架目錄不存在")
            return False
        
        demo_file = self.autogen_dir / "demos" / "demo_autogen_workflow.py"
        if not demo_file.exists():
            print("❌ AutoGen演示文件不存在")
            return False
        
        try:
            os.chdir(self.autogen_dir)
            print("   啟動快速演示模式...")
            subprocess.run([sys.executable, "demos/demo_autogen_workflow.py", "--quick"])
            return True
        except Exception as e:
            print(f"   ❌ AutoGen演示啟動失敗: {e}")
            return False
    
    def check_system_status(self):
        """檢查系統狀態"""
        print("📊 檢查系統狀態...")
        
        # 檢查Docker容器狀態
        try:
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    print("   🐳 運行中的Docker容器:")
                    for line in lines[1:]:  # 跳過標題行
                        if 'taiwan' in line.lower() or 'recall' in line.lower():
                            print(f"      ✅ {line}")
                else:
                    print("   📭 沒有運行中的Docker容器")
            else:
                print("   ❌ 無法檢查Docker狀態")
        except FileNotFoundError:
            print("   ⚠️  Docker未安裝")
        
        # 檢查端口使用情況
        try:
            import socket
            ports_to_check = [8501, 5432, 6379]  # Streamlit, PostgreSQL, Redis
            for port in ports_to_check:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    print(f"   🟢 端口 {port} 正在使用中")
                else:
                    print(f"   🔴 端口 {port} 空閒")
                sock.close()
        except Exception as e:
            print(f"   ⚠️  端口檢查失敗: {e}")
    
    def stop_services(self):
        """停止所有服務"""
        print("🛑 停止所有服務...")
        
        # 停止Docker服務
        docker_compose_file = self.taiwan_dir / "docker-compose.yml"
        if docker_compose_file.exists():
            try:
                os.chdir(self.taiwan_dir)
                subprocess.run(['docker-compose', 'down'], check=True)
                print("   ✅ Docker服務已停止")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Docker停止失敗: {e}")
    
    def show_project_structure(self):
        """顯示項目結構"""
        print("📁 項目結構:")
        structure = """
Recall_TW/
├── 📂 taiwan_recall_prediction/     # 主要預測系統
│   ├── 🐳 Docker相關文件
│   ├── 📊 數據分析模組
│   ├── 🌐 Streamlit儀表板
│   └── 📈 MECE分析框架
│
├── 📂 autogen_framework/           # AutoGen編程工作流
│   ├── 📂 core/                   # 核心實現
│   ├── 📂 config/                 # 配置文件
│   ├── 📂 demos/                  # 演示腳本
│   ├── 📂 docs/                   # 文檔
│   └── 📂 results/                # 執行結果
│
├── 📂 scripts/                    # 工具腳本
│   ├── project_manager.py         # 本腳本
│   └── fix_dashboard.py          # 儀表板修復工具
│
└── 📄 README.md                   # 項目說明
        """
        print(structure)
    
    def interactive_menu(self):
        """交互式選單"""
        while True:
            print("\n" + "="*60)
            print("🎮 Taiwan Recall Prediction System - 交互式選單")
            print("="*60)
            print("1. 🚀 啟動罷免預測儀表板")
            print("2. 🤖 啟動AutoGen編程工作流演示")
            print("3. 📊 檢查系統狀態")
            print("4. 🔍 檢查系統依賴")
            print("5. 📁 顯示項目結構")
            print("6. 🛑 停止所有服務")
            print("0. 🚪 退出")
            print("="*60)
            
            choice = input("請選擇操作 (0-6): ").strip()
            
            if choice == '1':
                self.start_dashboard()
            elif choice == '2':
                self.start_autogen_demo()
            elif choice == '3':
                self.check_system_status()
            elif choice == '4':
                self.check_dependencies()
            elif choice == '5':
                self.show_project_structure()
            elif choice == '6':
                self.stop_services()
            elif choice == '0':
                print("👋 再見！")
                break
            else:
                print("❌ 無效選擇，請重試")
            
            input("\n按Enter鍵繼續...")

def main():
    parser = argparse.ArgumentParser(
        description="Taiwan Recall Prediction System Project Manager"
    )
    parser.add_argument('--start-dashboard', action='store_true',
                       help='啟動罷免預測儀表板')
    parser.add_argument('--start-autogen', action='store_true',
                       help='啟動AutoGen編程工作流演示')
    parser.add_argument('--check-status', action='store_true',
                       help='檢查系統狀態')
    parser.add_argument('--check-deps', action='store_true',
                       help='檢查系統依賴')
    parser.add_argument('--stop', action='store_true',
                       help='停止所有服務')
    parser.add_argument('--interactive', action='store_true',
                       help='啟動交互式選單')
    
    args = parser.parse_args()
    
    manager = ProjectManager()
    manager.print_banner()
    
    if args.start_dashboard:
        manager.start_dashboard()
    elif args.start_autogen:
        manager.start_autogen_demo()
    elif args.check_status:
        manager.check_system_status()
    elif args.check_deps:
        manager.check_dependencies()
    elif args.stop:
        manager.stop_services()
    elif args.interactive:
        manager.interactive_menu()
    else:
        # 默認顯示交互式選單
        manager.interactive_menu()

if __name__ == "__main__":
    main()
