#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一鍵執行完整分析流程
"""

import subprocess
import sys
import time
from datetime import datetime

def run_command(command, description):
    """執行命令並顯示進度"""
    print(f"\n{'='*50}")
    print(f"🚀 {description}")
    print(f"{'='*50}")
    print(f"執行命令: {command}")
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"執行時間: {duration:.1f} 秒")
        
        if result.returncode == 0:
            print("✅ 執行成功!")
            if result.stdout:
                print("輸出:")
                print(result.stdout)
        else:
            print("❌ 執行失敗!")
            if result.stderr:
                print("錯誤訊息:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 執行時發生錯誤: {e}")
        return False
    
    return True

def install_requirements():
    """安裝必要套件"""
    requirements = [
        "requests",
        "beautifulsoup4", 
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "streamlit",
        "plotly",
        "textblob",
        "jieba",
        "wordcloud",
        "scikit-learn",
        "selenium",
        "webdriver-manager"
    ]
    
    print("📦 安裝必要套件...")
    for package in requirements:
        command = f"pip install {package}"
        if not run_command(command, f"安裝 {package}"):
            print(f"⚠️ 安裝 {package} 失敗，但繼續執行...")

def main():
    """主要執行流程"""
    print("🗳️ 台灣罷免預測分析 - 完整執行流程")
    print("=" * 60)
    
    # 詢問用戶要執行哪些步驟
    print("\n請選擇要執行的步驟:")
    print("1. 安裝套件")
    print("2. PTT 爬蟲")
    print("3. Dcard 爬蟲") 
    print("4. 情緒分析")
    print("5. MECE 分析")
    print("6. 啟動 Dashboard")
    print("7. 執行全部 (2-6)")
    
    choice = input("\n請輸入選項 (1-7): ").strip()
    
    if choice == "1" or choice == "7":
        install_requirements()
    
    if choice == "2" or choice == "7":
        if not run_command("python ptt_crawler.py", "執行 PTT 爬蟲"):
            print("PTT 爬蟲執行失敗，但繼續執行後續步驟...")
    
    if choice == "3" or choice == "7":
        if not run_command("python dcard_crawler.py", "執行 Dcard 爬蟲"):
            print("Dcard 爬蟲執行失敗，但繼續執行後續步驟...")
    
    if choice == "4" or choice == "7":
        if not run_command("python sentiment_analyzer.py", "執行情緒分析"):
            print("情緒分析執行失敗，但繼續執行後續步驟...")
    
    if choice == "5" or choice == "7":
        if not run_command("python mece_analyzer.py", "執行 MECE 分析"):
            print("MECE 分析執行失敗，但繼續執行後續步驟...")
    
    if choice == "6" or choice == "7":
        print("\n🌐 啟動 Streamlit Dashboard...")
        print("Dashboard 將在瀏覽器中開啟: http://localhost:8501")
        print("按 Ctrl+C 停止 Dashboard")
        
        try:
            subprocess.run("streamlit run dashboard.py", shell=True)
        except KeyboardInterrupt:
            print("\n👋 Dashboard 已停止")
    
    print("\n🎉 分析流程完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
