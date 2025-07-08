#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定時任務調度器 - 自動更新資料分析
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
import os
import json

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AnalysisScheduler:
    def __init__(self):
        self.ensure_directories()
        
    def ensure_directories(self):
        """確保必要目錄存在"""
        directories = ['/app/data', '/app/logs', '/app/output']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def run_crawler(self, script_name):
        """執行爬蟲腳本"""
        try:
            logger.info(f"開始執行 {script_name}")
            result = subprocess.run(
                f"python {script_name}",
                shell=True,
                capture_output=True,
                text=True,
                cwd='/app'
            )
            
            if result.returncode == 0:
                logger.info(f"{script_name} 執行成功")
                return True
            else:
                logger.error(f"{script_name} 執行失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"執行 {script_name} 時發生錯誤: {e}")
            return False
    
    def run_analysis(self, script_name):
        """執行分析腳本"""
        try:
            logger.info(f"開始執行 {script_name}")
            result = subprocess.run(
                f"python {script_name}",
                shell=True,
                capture_output=True,
                text=True,
                cwd='/app'
            )
            
            if result.returncode == 0:
                logger.info(f"{script_name} 執行成功")
                return True
            else:
                logger.error(f"{script_name} 執行失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"執行 {script_name} 時發生錯誤: {e}")
            return False
    
    def full_analysis_pipeline(self):
        """完整分析流程"""
        logger.info("開始執行完整分析流程")
        
        start_time = datetime.now()
        
        # 執行順序
        steps = [
            ("ptt_crawler.py", "PTT爬蟲"),
            ("dcard_crawler.py", "Dcard爬蟲"),
            ("sentiment_analyzer.py", "情緒分析"),
            ("mece_analyzer.py", "MECE分析")
        ]
        
        results = {}
        
        for script, description in steps:
            logger.info(f"執行 {description}...")
            success = self.run_analysis(script)
            results[script] = success
            
            if not success:
                logger.warning(f"{description} 執行失敗，但繼續執行後續步驟")
            
            # 每個步驟之間稍作休息
            time.sleep(30)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # 記錄執行結果
        summary = {
            'execution_time': start_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'results': results,
            'success_count': sum(results.values()),
            'total_steps': len(steps)
        }
        
        # 儲存執行摘要
        summary_file = f"/app/logs/execution_summary_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"完整分析流程執行完成，耗時 {duration}")
        logger.info(f"成功執行 {summary['success_count']}/{summary['total_steps']} 個步驟")
        
        return summary
    
    def quick_update(self):
        """快速更新 - 只執行爬蟲和情緒分析"""
        logger.info("開始執行快速更新")
        
        steps = [
            ("ptt_crawler.py", "PTT爬蟲"),
            ("dcard_crawler.py", "Dcard爬蟲"),
            ("sentiment_analyzer.py", "情緒分析")
        ]
        
        for script, description in steps:
            logger.info(f"執行 {description}...")
            self.run_analysis(script)
            time.sleep(15)
        
        logger.info("快速更新完成")
    
    def health_check(self):
        """健康檢查"""
        logger.info("執行系統健康檢查")
        
        # 檢查必要檔案
        required_files = [
            'ptt_crawler.py',
            'dcard_crawler.py', 
            'sentiment_analyzer.py',
            'mece_analyzer.py',
            'dashboard.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(f'/app/{file}'):
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"缺少必要檔案: {missing_files}")
        else:
            logger.info("所有必要檔案都存在")
        
        # 檢查資料目錄
        data_files = os.listdir('/app/data') if os.path.exists('/app/data') else []
        logger.info(f"資料目錄包含 {len(data_files)} 個檔案")
        
        return len(missing_files) == 0

def main():
    """主要執行函數"""
    scheduler_instance = AnalysisScheduler()
    
    logger.info("🤖 分析調度器啟動")
    
    # 執行初始健康檢查
    if not scheduler_instance.health_check():
        logger.error("健康檢查失敗，請檢查系統配置")
        return
    
    # 設定定時任務
    
    # 每天早上8點執行完整分析
    schedule.every().day.at("08:00").do(scheduler_instance.full_analysis_pipeline)
    
    # 每天下午2點和晚上8點執行快速更新
    schedule.every().day.at("14:00").do(scheduler_instance.quick_update)
    schedule.every().day.at("20:00").do(scheduler_instance.quick_update)
    
    # 每小時執行健康檢查
    schedule.every().hour.do(scheduler_instance.health_check)
    
    logger.info("定時任務已設定:")
    logger.info("- 每天 08:00: 完整分析流程")
    logger.info("- 每天 14:00, 20:00: 快速更新")
    logger.info("- 每小時: 健康檢查")
    
    # 如果是首次啟動且沒有資料，立即執行一次完整分析
    if not os.path.exists('/app/data/analysis_complete.flag'):
        logger.info("首次啟動，執行初始分析...")
        summary = scheduler_instance.full_analysis_pipeline()
        
        if summary['success_count'] > 0:
            # 標記初始分析完成
            with open('/app/data/analysis_complete.flag', 'w') as f:
                f.write(datetime.now().isoformat())
    
    # 開始調度循環
    logger.info("調度器開始運行...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
            
        except KeyboardInterrupt:
            logger.info("收到停止信號，調度器正在關閉...")
            break
        except Exception as e:
            logger.error(f"調度器運行時發生錯誤: {e}")
            time.sleep(300)  # 發生錯誤時等待5分鐘再繼續
    
    logger.info("調度器已停止")

if __name__ == "__main__":
    main()
