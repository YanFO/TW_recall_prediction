#!/usr/bin/env python3
"""
Taiwan Recall Prediction System - Quick Start
台灣罷免預測系統 - 快速啟動

這是項目的主要入口點，提供簡單的啟動選項。

Usage:
    python start.py
"""

import sys
import os
from pathlib import Path

# 添加scripts目錄到Python路徑
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from project_manager import ProjectManager
    
    def main():
        """主函數 - 啟動項目管理器"""
        manager = ProjectManager()
        manager.print_banner()
        
        print("🎮 歡迎使用 Taiwan Recall Prediction System!")
        print("   啟動交互式項目管理器...")
        print()
        
        manager.interactive_menu()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print("❌ 無法導入項目管理器")
    print(f"   錯誤: {e}")
    print()
    print("🔧 請確認以下事項:")
    print("   1. Python環境正確設置")
    print("   2. scripts/project_manager.py 文件存在")
    print("   3. 當前目錄為項目根目錄")
    print()
    print("💡 手動啟動選項:")
    print("   python scripts/project_manager.py --interactive")
    sys.exit(1)
except Exception as e:
    print(f"❌ 啟動失敗: {e}")
    sys.exit(1)
