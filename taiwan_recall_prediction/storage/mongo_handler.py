#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB 儲存處理模組
MongoDB Storage Handler Module

處理MongoDB數據庫的連接、儲存和查詢操作
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import json

# 導入配置
try:
    from ..crawler.config import DATABASE_CONFIG
except ImportError:
    # 如果作為獨立模組運行
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from crawler.config import DATABASE_CONFIG

# 設置日誌
logger = logging.getLogger(__name__)

class MongoHandler:
    """MongoDB處理類"""
    
    def __init__(self, host: str = None, port: int = None, database: str = None):
        """
        初始化MongoDB連接
        
        Args:
            host: MongoDB主機地址
            port: MongoDB端口
            database: 數據庫名稱
        """
        self.host = host or DATABASE_CONFIG['mongodb']['host']
        self.port = port or DATABASE_CONFIG['mongodb']['port']
        self.database_name = database or DATABASE_CONFIG['mongodb']['database']
        self.collections = DATABASE_CONFIG['mongodb']['collections']
        
        self.client = None
        self.db = None
        
        self._connect()
        self._setup_indexes()
        
        logger.info(f"MongoDB處理器初始化完成: {self.host}:{self.port}/{self.database_name}")
    
    def _connect(self):
        """建立MongoDB連接"""
        try:
            self.client = MongoClient(
                host=self.host,
                port=self.port,
                serverSelectionTimeoutMS=5000,  # 5秒超時
                connectTimeoutMS=5000
            )
            
            # 測試連接
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            logger.info("MongoDB連接成功")
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB連接失敗: {e}")
            raise
        except Exception as e:
            logger.error(f"MongoDB初始化錯誤: {e}")
            raise
    
    def _setup_indexes(self):
        """設置索引"""
        try:
            # 文章集合索引
            articles_collection = self.db[self.collections['articles']]
            articles_collection.create_index([('link', ASCENDING)], unique=True)
            articles_collection.create_index([('date', DESCENDING)])
            articles_collection.create_index([('source', ASCENDING)])
            articles_collection.create_index([('sentiment', ASCENDING)])
            articles_collection.create_index([('keywords_found', ASCENDING)])
            
            # 留言集合索引
            comments_collection = self.db[self.collections['comments']]
            comments_collection.create_index([('article_id', ASCENDING)])
            comments_collection.create_index([('date', DESCENDING)])
            
            # 統計集合索引
            statistics_collection = self.db[self.collections['statistics']]
            statistics_collection.create_index([('date', DESCENDING)])
            statistics_collection.create_index([('source', ASCENDING)])
            
            logger.info("MongoDB索引設置完成")
            
        except Exception as e:
            logger.error(f"設置MongoDB索引時發生錯誤: {e}")
    
    def insert_articles(self, articles: List[Dict]) -> Dict[str, int]:
        """
        插入文章數據
        
        Args:
            articles: 文章列表
            
        Returns:
            插入結果統計
        """
        if not articles:
            return {'inserted': 0, 'duplicates': 0, 'errors': 0}
        
        collection = self.db[self.collections['articles']]
        
        inserted_count = 0
        duplicate_count = 0
        error_count = 0
        
        for article in articles:
            try:
                # 添加插入時間戳
                article['inserted_at'] = datetime.now()
                
                # 確保必要字段存在
                if 'link' not in article or not article['link']:
                    article['link'] = f"no_link_{datetime.now().timestamp()}"
                
                collection.insert_one(article)
                inserted_count += 1
                
            except DuplicateKeyError:
                duplicate_count += 1
                logger.debug(f"重複文章: {article.get('title', 'Unknown')}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"插入文章時發生錯誤: {e}")
        
        result = {
            'inserted': inserted_count,
            'duplicates': duplicate_count,
            'errors': error_count
        }
        
        logger.info(f"文章插入完成: {result}")
        return result
    
    def insert_comments(self, comments: List[Dict], article_id: str) -> int:
        """
        插入留言數據
        
        Args:
            comments: 留言列表
            article_id: 關聯的文章ID
            
        Returns:
            插入的留言數量
        """
        if not comments:
            return 0
        
        collection = self.db[self.collections['comments']]
        
        # 為每個留言添加文章ID和插入時間
        for comment in comments:
            comment['article_id'] = article_id
            comment['inserted_at'] = datetime.now()
        
        try:
            result = collection.insert_many(comments)
            inserted_count = len(result.inserted_ids)
            
            logger.info(f"插入 {inserted_count} 條留言")
            return inserted_count
            
        except Exception as e:
            logger.error(f"插入留言時發生錯誤: {e}")
            return 0
    
    def get_articles(self, source: str = None, days: int = 7, 
                    sentiment: str = None, keywords: List[str] = None,
                    limit: int = 100) -> List[Dict]:
        """
        查詢文章
        
        Args:
            source: 數據來源過濾
            days: 查詢最近N天的數據
            sentiment: 情緒過濾
            keywords: 關鍵字過濾
            limit: 結果數量限制
            
        Returns:
            文章列表
        """
        collection = self.db[self.collections['articles']]
        
        # 構建查詢條件
        query = {}
        
        if source:
            query['source'] = source
        
        if days > 0:
            start_date = datetime.now() - timedelta(days=days)
            query['inserted_at'] = {'$gte': start_date}
        
        if sentiment:
            query['sentiment'] = sentiment
        
        if keywords:
            query['keywords_found'] = {'$in': keywords}
        
        try:
            cursor = collection.find(query).sort('date', DESCENDING).limit(limit)
            articles = list(cursor)
            
            # 轉換ObjectId為字符串
            for article in articles:
                article['_id'] = str(article['_id'])
            
            logger.info(f"查詢到 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"查詢文章時發生錯誤: {e}")
            return []
    
    def get_statistics(self, source: str = None, days: int = 7) -> Dict[str, Any]:
        """
        獲取統計數據
        
        Args:
            source: 數據來源過濾
            days: 統計最近N天的數據
            
        Returns:
            統計結果
        """
        collection = self.db[self.collections['articles']]
        
        # 構建查詢條件
        match_query = {}
        
        if source:
            match_query['source'] = source
        
        if days > 0:
            start_date = datetime.now() - timedelta(days=days)
            match_query['inserted_at'] = {'$gte': start_date}
        
        try:
            # 聚合查詢
            pipeline = [
                {'$match': match_query},
                {
                    '$group': {
                        '_id': None,
                        'total_articles': {'$sum': 1},
                        'positive_count': {
                            '$sum': {'$cond': [{'$eq': ['$sentiment', 'positive']}, 1, 0]}
                        },
                        'negative_count': {
                            '$sum': {'$cond': [{'$eq': ['$sentiment', 'negative']}, 1, 0]}
                        },
                        'neutral_count': {
                            '$sum': {'$cond': [{'$eq': ['$sentiment', 'neutral']}, 1, 0]}
                        },
                        'avg_sentiment_score': {'$avg': '$sentiment_score'},
                        'sources': {'$addToSet': '$source'}
                    }
                }
            ]
            
            result = list(collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                stats.pop('_id', None)
                
                # 計算比例
                total = stats['total_articles']
                if total > 0:
                    stats['positive_ratio'] = stats['positive_count'] / total
                    stats['negative_ratio'] = stats['negative_count'] / total
                    stats['neutral_ratio'] = stats['neutral_count'] / total
                else:
                    stats['positive_ratio'] = 0
                    stats['negative_ratio'] = 0
                    stats['neutral_ratio'] = 0
                
                return stats
            else:
                return {
                    'total_articles': 0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'positive_ratio': 0,
                    'negative_ratio': 0,
                    'neutral_ratio': 0,
                    'avg_sentiment_score': 0,
                    'sources': []
                }
                
        except Exception as e:
            logger.error(f"獲取統計數據時發生錯誤: {e}")
            return {}
    
    def get_source_statistics(self, days: int = 7) -> List[Dict]:
        """
        獲取各來源的統計數據
        
        Args:
            days: 統計最近N天的數據
            
        Returns:
            各來源統計列表
        """
        collection = self.db[self.collections['articles']]
        
        # 構建查詢條件
        match_query = {}
        if days > 0:
            start_date = datetime.now() - timedelta(days=days)
            match_query['inserted_at'] = {'$gte': start_date}
        
        try:
            pipeline = [
                {'$match': match_query},
                {
                    '$group': {
                        '_id': '$source',
                        'total_articles': {'$sum': 1},
                        'positive_count': {
                            '$sum': {'$cond': [{'$eq': ['$sentiment', 'positive']}, 1, 0]}
                        },
                        'negative_count': {
                            '$sum': {'$cond': [{'$eq': ['$sentiment', 'negative']}, 1, 0]}
                        },
                        'neutral_count': {
                            '$sum': {'$cond': [{'$eq': ['$sentiment', 'neutral']}, 1, 0]}
                        },
                        'avg_sentiment_score': {'$avg': '$sentiment_score'}
                    }
                },
                {'$sort': {'total_articles': -1}}
            ]
            
            results = list(collection.aggregate(pipeline))
            
            # 計算比例
            for result in results:
                total = result['total_articles']
                result['source'] = result.pop('_id')
                
                if total > 0:
                    result['positive_ratio'] = result['positive_count'] / total
                    result['negative_ratio'] = result['negative_count'] / total
                    result['neutral_ratio'] = result['neutral_count'] / total
                else:
                    result['positive_ratio'] = 0
                    result['negative_ratio'] = 0
                    result['neutral_ratio'] = 0
            
            return results
            
        except Exception as e:
            logger.error(f"獲取來源統計時發生錯誤: {e}")
            return []
    
    def save_crawl_statistics(self, stats: Dict[str, Any]):
        """
        保存爬取統計數據
        
        Args:
            stats: 統計數據
        """
        collection = self.db[self.collections['statistics']]
        
        stats['timestamp'] = datetime.now()
        
        try:
            collection.insert_one(stats)
            logger.info("爬取統計數據已保存")
            
        except Exception as e:
            logger.error(f"保存統計數據時發生錯誤: {e}")
    
    def backup_to_json(self, output_file: str, days: int = 30):
        """
        備份數據到JSON文件
        
        Args:
            output_file: 輸出文件路徑
            days: 備份最近N天的數據
        """
        try:
            articles = self.get_articles(days=days, limit=10000)
            
            # 轉換日期格式
            for article in articles:
                if 'inserted_at' in article:
                    article['inserted_at'] = article['inserted_at'].isoformat()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            logger.info(f"數據已備份到 {output_file}，共 {len(articles)} 篇文章")
            
        except Exception as e:
            logger.error(f"備份數據時發生錯誤: {e}")
    
    def close(self):
        """關閉數據庫連接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB連接已關閉")

def main():
    """測試函數"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 創建MongoDB處理器
        mongo = MongoHandler()
        
        # 測試插入數據
        test_articles = [
            {
                'title': '測試文章1',
                'content': '這是一篇測試文章',
                'author': 'test_user',
                'date': datetime.now().isoformat(),
                'link': 'http://test.com/1',
                'source': 'Test',
                'sentiment': 'positive',
                'sentiment_score': 0.5,
                'keywords_found': ['測試']
            }
        ]
        
        result = mongo.insert_articles(test_articles)
        print(f"插入結果: {result}")
        
        # 測試查詢
        articles = mongo.get_articles(limit=5)
        print(f"查詢到 {len(articles)} 篇文章")
        
        # 測試統計
        stats = mongo.get_statistics()
        print(f"統計結果: {stats}")
        
        # 關閉連接
        mongo.close()
        
    except Exception as e:
        print(f"測試時發生錯誤: {e}")

if __name__ == "__main__":
    main()
