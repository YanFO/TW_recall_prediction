#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控制爬蟲模組
Main Crawler Controller Module

統一調用所有平台爬蟲，整合數據並儲存到數據庫
"""

import logging
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import argparse

# 導入爬蟲模組
from crawler.config import get_config, KEYWORDS
from crawler.dcard_crawler import DcardCrawler
from crawler.mobile01_crawler import Mobile01Crawler
from crawler.fb_crawler import FacebookCrawler

# 導入儲存模組
from storage.mongo_handler import MongoHandler
from storage.sqlite_handler import SQLiteHandler

# 導入工具
from utils.common import data_processor, statistics_calculator

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'crawler_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MainCrawler:
    """主控制爬蟲類"""
    
    def __init__(self, use_mongodb: bool = True, use_sqlite: bool = True,
                 facebook_token: str = None):
        """
        初始化主控制爬蟲
        
        Args:
            use_mongodb: 是否使用MongoDB
            use_sqlite: 是否使用SQLite
            facebook_token: Facebook access token
        """
        self.config = get_config()
        self.keywords = KEYWORDS['recall'] + KEYWORDS['candidates']
        
        # 初始化爬蟲
        self.crawlers = {}
        self._init_crawlers(facebook_token)
        
        # 初始化儲存
        self.storage_handlers = {}
        self._init_storage(use_mongodb, use_sqlite)
        
        logger.info("主控制爬蟲初始化完成")
    
    def _init_crawlers(self, facebook_token: str = None):
        """初始化所有爬蟲"""
        try:
            # Dcard爬蟲
            self.crawlers['dcard'] = DcardCrawler()
            logger.info("Dcard爬蟲初始化完成")
            
            # Mobile01爬蟲
            self.crawlers['mobile01'] = Mobile01Crawler()
            logger.info("Mobile01爬蟲初始化完成")
            
            # Facebook爬蟲
            if facebook_token:
                self.crawlers['facebook'] = FacebookCrawler(facebook_token)
                logger.info("Facebook爬蟲初始化完成")
            else:
                logger.warning("Facebook access token未提供，跳過Facebook爬蟲")
            
            # PTT爬蟲 (使用現有的)
            try:
                from ptt_crawler import PTTCrawler
                self.crawlers['ptt'] = PTTCrawler()
                logger.info("PTT爬蟲初始化完成")
            except ImportError:
                logger.warning("PTT爬蟲模組未找到，跳過PTT爬蟲")
            
        except Exception as e:
            logger.error(f"初始化爬蟲時發生錯誤: {e}")
    
    def _init_storage(self, use_mongodb: bool, use_sqlite: bool):
        """初始化儲存處理器"""
        try:
            if use_mongodb:
                try:
                    self.storage_handlers['mongodb'] = MongoHandler()
                    logger.info("MongoDB儲存處理器初始化完成")
                except Exception as e:
                    logger.error(f"MongoDB初始化失敗: {e}")
            
            if use_sqlite:
                try:
                    self.storage_handlers['sqlite'] = SQLiteHandler()
                    logger.info("SQLite儲存處理器初始化完成")
                except Exception as e:
                    logger.error(f"SQLite初始化失敗: {e}")
            
        except Exception as e:
            logger.error(f"初始化儲存處理器時發生錯誤: {e}")
    
    def crawl_all_platforms(self, keywords: List[str] = None, 
                           pages_per_platform: int = 3) -> Dict[str, List[Dict]]:
        """
        爬取所有平台數據
        
        Args:
            keywords: 關鍵字列表
            pages_per_platform: 每個平台爬取的頁數
            
        Returns:
            各平台爬取結果
        """
        if keywords is None:
            keywords = self.keywords
        
        results = {}
        start_time = time.time()
        
        logger.info(f"開始爬取所有平台，關鍵字: {keywords}")
        
        # 爬取Dcard
        if 'dcard' in self.crawlers:
            try:
                logger.info("開始爬取Dcard...")
                dcard_articles = self.crawlers['dcard'].crawl_all_forums(
                    keywords, pages_per_platform
                )
                results['dcard'] = dcard_articles
                logger.info(f"Dcard爬取完成: {len(dcard_articles)} 篇文章")
            except Exception as e:
                logger.error(f"Dcard爬取失敗: {e}")
                results['dcard'] = []
        
        # 爬取Mobile01
        if 'mobile01' in self.crawlers:
            try:
                logger.info("開始爬取Mobile01...")
                mobile01_articles = self.crawlers['mobile01'].crawl_all_forums(
                    keywords, pages_per_platform
                )
                results['mobile01'] = mobile01_articles
                logger.info(f"Mobile01爬取完成: {len(mobile01_articles)} 篇文章")
            except Exception as e:
                logger.error(f"Mobile01爬取失敗: {e}")
                results['mobile01'] = []
        
        # 爬取Facebook
        if 'facebook' in self.crawlers:
            try:
                logger.info("開始爬取Facebook...")
                facebook_posts = self.crawlers['facebook'].crawl_all_pages(
                    keywords, pages_per_platform * 10  # Facebook每頁文章較少
                )
                results['facebook'] = facebook_posts
                logger.info(f"Facebook爬取完成: {len(facebook_posts)} 篇貼文")
            except Exception as e:
                logger.error(f"Facebook爬取失敗: {e}")
                results['facebook'] = []
        
        # 爬取PTT
        if 'ptt' in self.crawlers:
            try:
                logger.info("開始爬取PTT...")
                ptt_articles = self.crawlers['ptt'].get_board_articles(
                    'Gossiping', pages_per_platform, keywords
                )
                results['ptt'] = ptt_articles
                logger.info(f"PTT爬取完成: {len(ptt_articles)} 篇文章")
            except Exception as e:
                logger.error(f"PTT爬取失敗: {e}")
                results['ptt'] = []
        
        end_time = time.time()
        crawl_duration = end_time - start_time
        
        # 統計總結
        total_articles = sum(len(articles) for articles in results.values())
        logger.info(f"所有平台爬取完成，總共 {total_articles} 篇文章，耗時 {crawl_duration:.2f} 秒")
        
        return results
    
    def process_and_store_data(self, crawl_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        處理和儲存爬取數據
        
        Args:
            crawl_results: 爬取結果
            
        Returns:
            處理統計結果
        """
        logger.info("開始處理和儲存數據...")
        
        # 合併所有文章
        all_articles = []
        for platform, articles in crawl_results.items():
            all_articles.extend(articles)
        
        # 數據處理
        logger.info(f"處理前文章數: {len(all_articles)}")
        
        # 去重
        all_articles = data_processor.deduplicate_articles(all_articles)
        logger.info(f"去重後文章數: {len(all_articles)}")
        
        # 按日期排序
        all_articles = data_processor.sort_by_date(all_articles)
        
        # 儲存到數據庫
        storage_results = {}
        
        for storage_name, handler in self.storage_handlers.items():
            try:
                result = handler.insert_articles(all_articles)
                storage_results[storage_name] = result
                logger.info(f"{storage_name} 儲存結果: {result}")
            except Exception as e:
                logger.error(f"{storage_name} 儲存失敗: {e}")
                storage_results[storage_name] = {'error': str(e)}
        
        # 計算統計數據
        stats = statistics_calculator.calculate_sentiment_distribution(all_articles)
        engagement_stats = statistics_calculator.calculate_engagement_rate(all_articles)
        
        # 保存統計數據
        crawl_stats = {
            'date': datetime.now().isoformat(),
            'platforms': list(crawl_results.keys()),
            'total_articles': len(all_articles),
            'platform_breakdown': {
                platform: len(articles) for platform, articles in crawl_results.items()
            },
            **stats,
            **engagement_stats,
            'storage_results': storage_results
        }
        
        for handler in self.storage_handlers.values():
            try:
                handler.save_crawl_statistics(crawl_stats)
            except Exception as e:
                logger.error(f"保存統計數據失敗: {e}")
        
        logger.info("數據處理和儲存完成")
        return crawl_stats
    
    def run_full_crawl(self, keywords: List[str] = None, 
                      pages_per_platform: int = 3) -> Dict[str, Any]:
        """
        執行完整的爬取流程
        
        Args:
            keywords: 關鍵字列表
            pages_per_platform: 每個平台爬取的頁數
            
        Returns:
            完整的爬取和處理結果
        """
        logger.info("開始執行完整爬取流程")
        
        try:
            # 爬取數據
            crawl_results = self.crawl_all_platforms(keywords, pages_per_platform)
            
            # 處理和儲存數據
            process_stats = self.process_and_store_data(crawl_results)
            
            # 生成報告
            report = self.generate_report(crawl_results, process_stats)
            
            logger.info("完整爬取流程執行完成")
            return report
            
        except Exception as e:
            logger.error(f"執行完整爬取流程時發生錯誤: {e}")
            return {'error': str(e)}
    
    def generate_report(self, crawl_results: Dict[str, List[Dict]], 
                       process_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成爬取報告
        
        Args:
            crawl_results: 爬取結果
            process_stats: 處理統計
            
        Returns:
            完整報告
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_platforms': len(crawl_results),
                'total_articles': process_stats.get('total_articles', 0),
                'successful_platforms': len([p for p, articles in crawl_results.items() if articles]),
                'data_quality': 'high' if process_stats.get('total_articles', 0) > 50 else 'medium'
            },
            'platform_details': {},
            'sentiment_analysis': {
                'positive_ratio': process_stats.get('positive_ratio', 0),
                'negative_ratio': process_stats.get('negative_ratio', 0),
                'neutral_ratio': process_stats.get('neutral_ratio', 0)
            },
            'storage_status': process_stats.get('storage_results', {}),
            'recommendations': []
        }
        
        # 各平台詳情
        for platform, articles in crawl_results.items():
            platform_stats = statistics_calculator.calculate_sentiment_distribution(articles)
            report['platform_details'][platform] = {
                'article_count': len(articles),
                'sentiment_distribution': platform_stats,
                'status': 'success' if articles else 'no_data'
            }
        
        # 生成建議
        if report['summary']['total_articles'] < 20:
            report['recommendations'].append("建議增加爬取頁數或擴展關鍵字")
        
        if report['summary']['successful_platforms'] < 3:
            report['recommendations'].append("建議檢查失敗平台的連接和配置")
        
        return report
    
    def close(self):
        """關閉所有連接"""
        for handler in self.storage_handlers.values():
            try:
                handler.close()
            except Exception as e:
                logger.error(f"關閉儲存處理器時發生錯誤: {e}")
        
        logger.info("主控制爬蟲已關閉")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='台灣罷免預測爬蟲系統')
    parser.add_argument('--keywords', nargs='+', help='爬取關鍵字')
    parser.add_argument('--pages', type=int, default=3, help='每個平台爬取頁數')
    parser.add_argument('--no-mongodb', action='store_true', help='不使用MongoDB')
    parser.add_argument('--no-sqlite', action='store_true', help='不使用SQLite')
    parser.add_argument('--facebook-token', help='Facebook access token')
    parser.add_argument('--output', help='輸出報告文件路徑')
    
    args = parser.parse_args()
    
    # 設置關鍵字
    keywords = args.keywords or (KEYWORDS['recall'] + KEYWORDS['candidates'])
    
    try:
        # 創建主控制爬蟲
        crawler = MainCrawler(
            use_mongodb=not args.no_mongodb,
            use_sqlite=not args.no_sqlite,
            facebook_token=args.facebook_token
        )
        
        # 執行爬取
        report = crawler.run_full_crawl(keywords, args.pages)
        
        # 輸出報告
        print("\n" + "="*50)
        print("爬取報告")
        print("="*50)
        print(f"時間: {report['timestamp']}")
        print(f"總文章數: {report['summary']['total_articles']}")
        print(f"成功平台: {report['summary']['successful_platforms']}/{report['summary']['total_platforms']}")
        print(f"數據品質: {report['summary']['data_quality']}")
        
        print("\n各平台結果:")
        for platform, details in report['platform_details'].items():
            print(f"  {platform}: {details['article_count']} 篇文章 ({details['status']})")
        
        print(f"\n情緒分析:")
        print(f"  正面: {report['sentiment_analysis']['positive_ratio']:.1%}")
        print(f"  負面: {report['sentiment_analysis']['negative_ratio']:.1%}")
        print(f"  中性: {report['sentiment_analysis']['neutral_ratio']:.1%}")
        
        if report.get('recommendations'):
            print(f"\n建議:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        # 保存報告
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n報告已保存到: {args.output}")
        
        # 關閉連接
        crawler.close()
        
    except Exception as e:
        logger.error(f"執行主程序時發生錯誤: {e}")
        print(f"錯誤: {e}")

if __name__ == "__main__":
    main()
