#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲系統測試
Crawler System Test

測試整個模組化爬蟲系統
"""

import sys
import os
import logging
import json
from datetime import datetime

# 添加路徑
sys.path.append(os.path.dirname(__file__))

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """測試配置模組"""
    print("=== 測試配置模組 ===")
    try:
        from crawler.config import get_config, KEYWORDS
        
        config = get_config()
        print(f"✅ 配置載入成功")
        print(f"關鍵字數量: {len(KEYWORDS['recall'])} + {len(KEYWORDS['candidates'])}")
        print(f"PTT看板: {config['ptt']['boards']}")
        print(f"Dcard論壇: {config['dcard']['forums']}")
        
        return True
    except Exception as e:
        print(f"❌ 配置測試失敗: {e}")
        return False

def test_utils():
    """測試工具模組"""
    print("\n=== 測試工具模組 ===")
    try:
        from utils.common import text_processor, date_processor, data_processor
        
        # 測試文本處理
        test_text = "這個候選人真的很爛，我不支持他！"
        sentiment = text_processor.analyze_sentiment(test_text)
        print(f"✅ 情緒分析: {sentiment['sentiment']} (分數: {sentiment['score']:.2f})")
        
        # 測試日期處理
        test_date = "2小時前"
        parsed_date = date_processor.parse_date(test_date)
        print(f"✅ 日期解析: {parsed_date}")
        
        # 測試數據處理
        test_articles = [
            {'title': '測試1', 'content': '內容1'},
            {'title': '測試1', 'content': '內容1'},  # 重複
            {'title': '測試2', 'content': '內容2'}
        ]
        unique_articles = data_processor.deduplicate_articles(test_articles)
        print(f"✅ 去重處理: {len(test_articles)} -> {len(unique_articles)}")
        
        return True
    except Exception as e:
        print(f"❌ 工具測試失敗: {e}")
        return False

def test_sqlite_storage():
    """測試SQLite儲存"""
    print("\n=== 測試SQLite儲存 ===")
    try:
        from storage.sqlite_handler import SQLiteHandler
        
        # 創建測試數據庫
        sqlite = SQLiteHandler('test_crawler.db')
        
        # 測試插入
        test_articles = [
            {
                'title': '測試文章',
                'content': '這是測試內容',
                'author': 'test_user',
                'date': datetime.now().isoformat(),
                'link': 'http://test.com/1',
                'source': 'Test',
                'sentiment': 'positive',
                'sentiment_score': 0.5,
                'keywords_found': ['測試']
            }
        ]
        
        result = sqlite.insert_articles(test_articles)
        print(f"✅ 插入結果: {result}")
        
        # 測試查詢
        articles = sqlite.get_articles(limit=5)
        print(f"✅ 查詢結果: {len(articles)} 篇文章")
        
        # 測試統計
        stats = sqlite.get_statistics()
        print(f"✅ 統計結果: {stats['total_articles']} 篇文章")
        
        sqlite.close()
        return True
    except Exception as e:
        print(f"❌ SQLite測試失敗: {e}")
        return False

def test_dcard_crawler():
    """測試Dcard爬蟲"""
    print("\n=== 測試Dcard爬蟲 ===")
    try:
        from crawler.dcard_crawler import DcardCrawler
        
        crawler = DcardCrawler()
        
        # 測試爬取一個論壇的少量數據
        keywords = ['政治', '選舉']
        articles = crawler.get_forum_articles('politics', keywords, pages=1)
        
        print(f"✅ Dcard爬取結果: {len(articles)} 篇文章")
        
        if articles:
            print("前3篇文章:")
            for i, article in enumerate(articles[:3], 1):
                print(f"  {i}. {article['title'][:50]}...")
                print(f"     情緒: {article['sentiment']}")
        
        return True
    except Exception as e:
        print(f"❌ Dcard爬蟲測試失敗: {e}")
        return False

def test_mobile01_crawler():
    """測試Mobile01爬蟲"""
    print("\n=== 測試Mobile01爬蟲 ===")
    try:
        from crawler.mobile01_crawler import Mobile01Crawler
        
        crawler = Mobile01Crawler()
        
        # 測試爬取政治討論版
        keywords = ['政治', '選舉']
        articles = crawler.get_forum_articles('politics', 376, keywords, pages=1)
        
        print(f"✅ Mobile01爬取結果: {len(articles)} 篇文章")
        
        if articles:
            print("前3篇文章:")
            for i, article in enumerate(articles[:3], 1):
                print(f"  {i}. {article['title'][:50]}...")
                print(f"     作者: {article['author']}")
                print(f"     情緒: {article['sentiment']}")
        
        return True
    except Exception as e:
        print(f"❌ Mobile01爬蟲測試失敗: {e}")
        return False

def test_facebook_crawler():
    """測試Facebook爬蟲"""
    print("\n=== 測試Facebook爬蟲 ===")
    try:
        from crawler.fb_crawler import FacebookCrawler
        
        # 不提供token，測試初始化
        crawler = FacebookCrawler()
        
        print("✅ Facebook爬蟲初始化成功 (需要access token才能爬取)")
        print("⚠️ 請設置Facebook access token以測試實際爬取功能")
        
        return True
    except Exception as e:
        print(f"❌ Facebook爬蟲測試失敗: {e}")
        return False

def test_integration():
    """測試整合功能"""
    print("\n=== 測試整合功能 ===")
    try:
        from crawler.dcard_crawler import DcardCrawler
        from storage.sqlite_handler import SQLiteHandler
        from utils.common import statistics_calculator
        
        # 創建爬蟲和儲存
        crawler = DcardCrawler()
        storage = SQLiteHandler('integration_test.db')
        
        # 爬取少量數據
        keywords = ['政治']
        articles = crawler.get_forum_articles('politics', keywords, pages=1)
        
        if articles:
            # 儲存數據
            result = storage.insert_articles(articles)
            print(f"✅ 整合測試 - 爬取: {len(articles)} 篇，儲存: {result['inserted']} 篇")
            
            # 計算統計
            stats = statistics_calculator.calculate_sentiment_distribution(articles)
            print(f"✅ 情緒統計: 正面 {stats['positive']}, 負面 {stats['negative']}, 中性 {stats['neutral']}")
        else:
            print("⚠️ 未爬取到數據，但整合流程正常")
        
        storage.close()
        return True
    except Exception as e:
        print(f"❌ 整合測試失敗: {e}")
        return False

def generate_test_report():
    """生成測試報告"""
    print("\n" + "="*60)
    print("🕷️ 模組化爬蟲系統測試報告")
    print("="*60)
    
    tests = [
        ("配置模組", test_config),
        ("工具模組", test_utils),
        ("SQLite儲存", test_sqlite_storage),
        ("Dcard爬蟲", test_dcard_crawler),
        ("Mobile01爬蟲", test_mobile01_crawler),
        ("Facebook爬蟲", test_facebook_crawler),
        ("整合功能", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
            results[test_name] = False
    
    # 總結
    print("\n" + "="*60)
    print("📊 測試總結")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:15} : {status}")
    
    print(f"\n總體結果: {passed}/{total} 項測試通過 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有測試通過！爬蟲系統準備就緒")
    elif passed >= total * 0.7:
        print("⚠️ 大部分測試通過，系統基本可用")
    else:
        print("❌ 多項測試失敗，請檢查系統配置")
    
    # 保存報告
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_results': results,
        'summary': {
            'total_tests': total,
            'passed_tests': passed,
            'success_rate': passed / total,
            'status': 'ready' if passed == total else 'partial' if passed >= total * 0.7 else 'failed'
        }
    }
    
    with open('crawler_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 詳細報告已保存到: crawler_test_report.json")
    
    return report

if __name__ == "__main__":
    print("🚀 開始測試模組化爬蟲系統...")
    report = generate_test_report()
    
    print(f"\n🔗 系統架構說明:")
    print(f"   📁 crawler/     - 各平台爬蟲模組")
    print(f"   📁 storage/     - 數據庫儲存模組")
    print(f"   📁 utils/       - 通用工具模組")
    print(f"   📄 main_crawler.py - 主控制程序")
    
    print(f"\n💡 使用建議:")
    if report['summary']['status'] == 'ready':
        print(f"   ✅ 系統完全就緒，可以開始正式爬取")
        print(f"   🚀 執行: python main_crawler.py --keywords 羅智強 罷免 --pages 2")
    else:
        print(f"   ⚠️ 請先解決失敗的測試項目")
        print(f"   🔧 檢查網絡連接和依賴安裝")
