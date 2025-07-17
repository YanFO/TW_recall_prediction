#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 儲存處理模組
SQLite Storage Handler Module

處理SQLite數據庫的連接、儲存和查詢操作
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

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

class SQLiteHandler:
    """SQLite處理類"""
    
    def __init__(self, db_file: str = None):
        """
        初始化SQLite連接
        
        Args:
            db_file: 數據庫文件路徑
        """
        self.db_file = db_file or DATABASE_CONFIG['sqlite']['database']
        self.tables = DATABASE_CONFIG['sqlite']['tables']
        
        self.conn = None
        self.cursor = None
        
        self._connect()
        self._create_tables()
        
        logger.info(f"SQLite處理器初始化完成: {self.db_file}")
    
    def _connect(self):
        """建立SQLite連接"""
        try:
            # 確保目錄存在
            db_dir = os.path.dirname(self.db_file)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            self.conn = sqlite3.connect(
                self.db_file,
                check_same_thread=False,
                timeout=30.0
            )
            self.conn.row_factory = sqlite3.Row  # 使結果可以像字典一樣訪問
            self.cursor = self.conn.cursor()
            
            # 啟用外鍵約束
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            logger.info("SQLite連接成功")
            
        except Exception as e:
            logger.error(f"SQLite連接失敗: {e}")
            raise
    
    def _create_tables(self):
        """創建數據表"""
        try:
            # 文章表
            self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.tables['articles']} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    author TEXT,
                    date TEXT,
                    link TEXT UNIQUE,
                    source TEXT,
                    forum TEXT,
                    post_id TEXT,
                    sentiment TEXT,
                    sentiment_score REAL,
                    keywords_found TEXT,
                    like_count INTEGER DEFAULT 0,
                    comment_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    share_count INTEGER DEFAULT 0,
                    engagement_rate INTEGER DEFAULT 0,
                    crawl_time TEXT,
                    inserted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    extra_data TEXT
                )
            ''')
            
            # 留言表
            self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.tables['comments']} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER,
                    content TEXT NOT NULL,
                    author TEXT,
                    date TEXT,
                    like_count INTEGER DEFAULT 0,
                    sentiment TEXT,
                    sentiment_score REAL,
                    floor INTEGER,
                    inserted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES {self.tables['articles']} (id)
                )
            ''')
            
            # 統計表
            self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.tables['statistics']} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    source TEXT,
                    total_articles INTEGER,
                    positive_count INTEGER,
                    negative_count INTEGER,
                    neutral_count INTEGER,
                    avg_sentiment_score REAL,
                    crawl_duration REAL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    extra_data TEXT
                )
            ''')
            
            # 創建索引
            self._create_indexes()
            
            self.conn.commit()
            logger.info("SQLite數據表創建完成")
            
        except Exception as e:
            logger.error(f"創建SQLite數據表時發生錯誤: {e}")
            raise
    
    def _create_indexes(self):
        """創建索引"""
        try:
            # 文章表索引
            indexes = [
                f"CREATE INDEX IF NOT EXISTS idx_articles_link ON {self.tables['articles']} (link)",
                f"CREATE INDEX IF NOT EXISTS idx_articles_date ON {self.tables['articles']} (date DESC)",
                f"CREATE INDEX IF NOT EXISTS idx_articles_source ON {self.tables['articles']} (source)",
                f"CREATE INDEX IF NOT EXISTS idx_articles_sentiment ON {self.tables['articles']} (sentiment)",
                f"CREATE INDEX IF NOT EXISTS idx_articles_inserted_at ON {self.tables['articles']} (inserted_at DESC)",
                
                # 留言表索引
                f"CREATE INDEX IF NOT EXISTS idx_comments_article_id ON {self.tables['comments']} (article_id)",
                f"CREATE INDEX IF NOT EXISTS idx_comments_date ON {self.tables['comments']} (date DESC)",
                
                # 統計表索引
                f"CREATE INDEX IF NOT EXISTS idx_statistics_date ON {self.tables['statistics']} (date DESC)",
                f"CREATE INDEX IF NOT EXISTS idx_statistics_source ON {self.tables['statistics']} (source)"
            ]
            
            for index_sql in indexes:
                self.cursor.execute(index_sql)
            
            logger.info("SQLite索引創建完成")
            
        except Exception as e:
            logger.error(f"創建SQLite索引時發生錯誤: {e}")
    
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
        
        inserted_count = 0
        duplicate_count = 0
        error_count = 0
        
        for article in articles:
            try:
                # 準備數據
                keywords_json = json.dumps(article.get('keywords_found', []), ensure_ascii=False)
                extra_data_json = json.dumps({
                    k: v for k, v in article.items() 
                    if k not in ['title', 'content', 'author', 'date', 'link', 'source', 
                               'forum', 'post_id', 'sentiment', 'sentiment_score', 
                               'keywords_found', 'like_count', 'comment_count', 
                               'reply_count', 'share_count', 'engagement_rate', 'crawl_time']
                }, ensure_ascii=False)
                
                # 插入數據
                self.cursor.execute(f'''
                    INSERT OR IGNORE INTO {self.tables['articles']} 
                    (title, content, author, date, link, source, forum, post_id, 
                     sentiment, sentiment_score, keywords_found, like_count, 
                     comment_count, reply_count, share_count, engagement_rate, 
                     crawl_time, extra_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article.get('title', ''),
                    article.get('content', ''),
                    article.get('author', ''),
                    article.get('date', ''),
                    article.get('link', ''),
                    article.get('source', ''),
                    article.get('forum', ''),
                    article.get('post_id', ''),
                    article.get('sentiment', ''),
                    article.get('sentiment_score', 0),
                    keywords_json,
                    article.get('like_count', 0),
                    article.get('comment_count', 0),
                    article.get('reply_count', 0),
                    article.get('share_count', 0),
                    article.get('engagement_rate', 0),
                    article.get('crawl_time', ''),
                    extra_data_json
                ))
                
                if self.cursor.rowcount > 0:
                    inserted_count += 1
                    
                    # 插入留言
                    if 'comments' in article and article['comments']:
                        article_id = self.cursor.lastrowid
                        self.insert_comments(article['comments'], article_id)
                else:
                    duplicate_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"插入文章時發生錯誤: {e}")
        
        self.conn.commit()
        
        result = {
            'inserted': inserted_count,
            'duplicates': duplicate_count,
            'errors': error_count
        }
        
        logger.info(f"文章插入完成: {result}")
        return result
    
    def insert_comments(self, comments: List[Dict], article_id: int) -> int:
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
        
        inserted_count = 0
        
        for comment in comments:
            try:
                self.cursor.execute(f'''
                    INSERT INTO {self.tables['comments']} 
                    (article_id, content, author, date, like_count, sentiment, 
                     sentiment_score, floor)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article_id,
                    comment.get('content', ''),
                    comment.get('author', ''),
                    comment.get('date', ''),
                    comment.get('like_count', 0),
                    comment.get('sentiment', ''),
                    comment.get('sentiment_score', 0),
                    comment.get('floor', 0)
                ))
                
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"插入留言時發生錯誤: {e}")
        
        logger.info(f"插入 {inserted_count} 條留言")
        return inserted_count
    
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
        # 構建查詢條件
        where_conditions = []
        params = []
        
        if source:
            where_conditions.append("source = ?")
            params.append(source)
        
        if days > 0:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            where_conditions.append("inserted_at >= ?")
            params.append(start_date)
        
        if sentiment:
            where_conditions.append("sentiment = ?")
            params.append(sentiment)
        
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append("keywords_found LIKE ?")
                params.append(f'%{keyword}%')
            where_conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        # 構建SQL查詢
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        sql = f'''
            SELECT * FROM {self.tables['articles']} 
            {where_clause}
            ORDER BY date DESC 
            LIMIT ?
        '''
        params.append(limit)
        
        try:
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall()
            
            articles = []
            for row in rows:
                article = dict(row)
                
                # 解析JSON字段
                try:
                    article['keywords_found'] = json.loads(article['keywords_found'] or '[]')
                except:
                    article['keywords_found'] = []
                
                try:
                    extra_data = json.loads(article['extra_data'] or '{}')
                    article.update(extra_data)
                except:
                    pass
                
                articles.append(article)
            
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
        # 構建查詢條件
        where_conditions = []
        params = []
        
        if source:
            where_conditions.append("source = ?")
            params.append(source)
        
        if days > 0:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            where_conditions.append("inserted_at >= ?")
            params.append(start_date)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        try:
            sql = f'''
                SELECT 
                    COUNT(*) as total_articles,
                    SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive_count,
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count,
                    SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_count,
                    AVG(sentiment_score) as avg_sentiment_score,
                    GROUP_CONCAT(DISTINCT source) as sources
                FROM {self.tables['articles']} 
                {where_clause}
            '''
            
            self.cursor.execute(sql, params)
            row = self.cursor.fetchone()
            
            if row:
                stats = dict(row)
                
                # 計算比例
                total = stats['total_articles'] or 0
                if total > 0:
                    stats['positive_ratio'] = (stats['positive_count'] or 0) / total
                    stats['negative_ratio'] = (stats['negative_count'] or 0) / total
                    stats['neutral_ratio'] = (stats['neutral_count'] or 0) / total
                else:
                    stats['positive_ratio'] = 0
                    stats['negative_ratio'] = 0
                    stats['neutral_ratio'] = 0
                
                # 處理來源列表
                sources_str = stats.get('sources', '')
                stats['sources'] = sources_str.split(',') if sources_str else []
                
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
    
    def save_crawl_statistics(self, stats: Dict[str, Any]):
        """
        保存爬取統計數據
        
        Args:
            stats: 統計數據
        """
        try:
            extra_data_json = json.dumps({
                k: v for k, v in stats.items() 
                if k not in ['date', 'source', 'total_articles', 'positive_count', 
                           'negative_count', 'neutral_count', 'avg_sentiment_score', 
                           'crawl_duration']
            }, ensure_ascii=False)
            
            self.cursor.execute(f'''
                INSERT INTO {self.tables['statistics']} 
                (date, source, total_articles, positive_count, negative_count, 
                 neutral_count, avg_sentiment_score, crawl_duration, extra_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stats.get('date', datetime.now().isoformat()),
                stats.get('source', ''),
                stats.get('total_articles', 0),
                stats.get('positive_count', 0),
                stats.get('negative_count', 0),
                stats.get('neutral_count', 0),
                stats.get('avg_sentiment_score', 0),
                stats.get('crawl_duration', 0),
                extra_data_json
            ))
            
            self.conn.commit()
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
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            logger.info(f"數據已備份到 {output_file}，共 {len(articles)} 篇文章")
            
        except Exception as e:
            logger.error(f"備份數據時發生錯誤: {e}")
    
    def close(self):
        """關閉數據庫連接"""
        if self.conn:
            self.conn.close()
            logger.info("SQLite連接已關閉")

def main():
    """測試函數"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 創建SQLite處理器
        sqlite = SQLiteHandler('test_recall.db')
        
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
        
        result = sqlite.insert_articles(test_articles)
        print(f"插入結果: {result}")
        
        # 測試查詢
        articles = sqlite.get_articles(limit=5)
        print(f"查詢到 {len(articles)} 篇文章")
        
        # 測試統計
        stats = sqlite.get_statistics()
        print(f"統計結果: {stats}")
        
        # 關閉連接
        sqlite.close()
        
    except Exception as e:
        print(f"測試時發生錯誤: {e}")

if __name__ == "__main__":
    main()
