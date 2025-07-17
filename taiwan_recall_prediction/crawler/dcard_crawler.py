#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dcard 爬蟲模組
Dcard Crawler Module

爬取Dcard平台的討論文章和留言
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin

# 導入配置和工具
try:
    from .config import DCARD_CONFIG, BASE_CONFIG, KEYWORDS
    from ..utils.common import text_processor, date_processor, data_processor, create_request_helper
except ImportError:
    # 如果作為獨立模組運行
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from crawler.config import DCARD_CONFIG, BASE_CONFIG, KEYWORDS
    from utils.common import text_processor, date_processor, data_processor, create_request_helper

# 設置日誌
logger = logging.getLogger(__name__)

class DcardCrawler:
    """Dcard爬蟲類"""
    
    def __init__(self):
        self.base_url = DCARD_CONFIG['base_url']
        self.api_base = DCARD_CONFIG['api_base']
        self.forums = DCARD_CONFIG['forums']
        self.posts_per_forum = DCARD_CONFIG['posts_per_forum']
        
        # 創建請求輔助工具
        self.request_helper = create_request_helper(
            delay=BASE_CONFIG['request_delay'],
            max_retries=BASE_CONFIG['max_retries']
        )
        
        logger.info("Dcard爬蟲初始化完成")
    
    def get_forum_articles(self, forum: str, keywords: List[str] = None, 
                          pages: int = 3) -> List[Dict]:
        """
        爬取指定論壇的文章
        
        Args:
            forum: 論壇名稱 (如 'politics', 'trending')
            keywords: 關鍵字列表
            pages: 爬取頁數
            
        Returns:
            文章列表
        """
        if keywords is None:
            keywords = KEYWORDS['recall'] + KEYWORDS['candidates']
        
        articles = []
        before_id = None
        
        logger.info(f"開始爬取Dcard {forum} 論壇，關鍵字: {keywords}")
        
        try:
            for page in range(pages):
                # 構建API URL
                url = f"{self.api_base}/forums/{forum}/posts"
                params = {
                    'popular': 'false',
                    'limit': 30
                }
                
                if before_id:
                    params['before'] = before_id
                
                # 發送請求
                response = self.request_helper.get(url, params=params)
                if not response:
                    logger.error(f"無法獲取 {forum} 論壇第 {page + 1} 頁")
                    break
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    logger.error(f"JSON解析失敗: {forum} 論壇第 {page + 1} 頁")
                    break
                
                if not data:
                    logger.info(f"{forum} 論壇沒有更多文章")
                    break
                
                # 處理文章
                page_articles = []
                for post in data:
                    article = self._process_post(post, forum, keywords)
                    if article:
                        page_articles.append(article)
                
                articles.extend(page_articles)
                
                # 設置下一頁的before_id
                if data:
                    before_id = data[-1]['id']
                
                logger.info(f"Dcard {forum} 第 {page + 1} 頁: 找到 {len(page_articles)} 篇相關文章")
                
                # 避免請求過快
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"爬取Dcard {forum} 論壇時發生錯誤: {e}")
        
        logger.info(f"Dcard {forum} 論壇爬取完成，共 {len(articles)} 篇文章")
        return articles
    
    def _process_post(self, post: Dict, forum: str, keywords: List[str]) -> Optional[Dict]:
        """
        處理單篇文章
        
        Args:
            post: API返回的文章數據
            forum: 論壇名稱
            keywords: 關鍵字列表
            
        Returns:
            處理後的文章數據或None
        """
        try:
            title = post.get('title', '')
            excerpt = post.get('excerpt', '')
            content = title + ' ' + excerpt
            
            # 檢查是否包含關鍵字
            if not any(keyword.lower() in content.lower() for keyword in keywords):
                return None
            
            # 解析日期
            created_at = post.get('createdAt', '')
            parsed_date = date_processor.parse_date(created_at)
            
            # 構建文章URL
            post_id = post.get('id', '')
            article_url = f"{self.base_url}/f/{forum}/p/{post_id}"
            
            # 獲取詳細內容
            detailed_content = self._get_post_content(post_id)
            
            # 情緒分析
            sentiment_result = text_processor.analyze_sentiment(content)
            
            article = {
                'title': text_processor.clean_text(title),
                'content': text_processor.clean_text(detailed_content or excerpt),
                'excerpt': text_processor.clean_text(excerpt),
                'author': post.get('school', '') + ' ' + post.get('department', ''),
                'date': date_processor.format_date(parsed_date) if parsed_date else created_at,
                'link': article_url,
                'source': 'Dcard',
                'forum': forum,
                'post_id': post_id,
                'like_count': post.get('likeCount', 0),
                'comment_count': post.get('commentCount', 0),
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['score'],
                'keywords_found': text_processor.extract_keywords(content, keywords),
                'crawl_time': datetime.now().isoformat(),
                'is_anonymous': post.get('anonymous', False),
                'gender': post.get('gender', ''),
                'topics': post.get('topics', [])
            }
            
            return article
            
        except Exception as e:
            logger.error(f"處理Dcard文章時發生錯誤: {e}")
            return None
    
    def _get_post_content(self, post_id: str) -> Optional[str]:
        """
        獲取文章詳細內容
        
        Args:
            post_id: 文章ID
            
        Returns:
            文章內容或None
        """
        try:
            url = f"{self.api_base}/posts/{post_id}"
            response = self.request_helper.get(url)
            
            if not response:
                return None
            
            data = response.json()
            content = data.get('content', '')
            
            return text_processor.clean_text(content)
            
        except Exception as e:
            logger.error(f"獲取Dcard文章內容時發生錯誤: {e}")
            return None
    
    def get_post_comments(self, post_id: str, limit: int = 50) -> List[Dict]:
        """
        獲取文章留言
        
        Args:
            post_id: 文章ID
            limit: 留言數量限制
            
        Returns:
            留言列表
        """
        comments = []
        
        try:
            url = f"{self.api_base}/posts/{post_id}/comments"
            params = {'limit': limit}
            
            response = self.request_helper.get(url, params=params)
            if not response:
                return comments
            
            data = response.json()
            
            for comment_data in data:
                try:
                    # 解析留言日期
                    created_at = comment_data.get('createdAt', '')
                    parsed_date = date_processor.parse_date(created_at)
                    
                    # 情緒分析
                    comment_content = comment_data.get('content', '')
                    sentiment_result = text_processor.analyze_sentiment(comment_content)
                    
                    comment = {
                        'content': text_processor.clean_text(comment_content),
                        'author': comment_data.get('school', '') + ' ' + comment_data.get('department', ''),
                        'date': date_processor.format_date(parsed_date) if parsed_date else created_at,
                        'like_count': comment_data.get('likeCount', 0),
                        'sentiment': sentiment_result['sentiment'],
                        'sentiment_score': sentiment_result['score'],
                        'is_anonymous': comment_data.get('anonymous', False),
                        'gender': comment_data.get('gender', ''),
                        'floor': comment_data.get('floor', 0)
                    }
                    
                    comments.append(comment)
                    
                except Exception as e:
                    logger.error(f"處理Dcard留言時發生錯誤: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"獲取Dcard留言時發生錯誤: {e}")
        
        return comments
    
    def crawl_all_forums(self, keywords: List[str] = None, 
                        pages_per_forum: int = 3) -> List[Dict]:
        """
        爬取所有配置的論壇
        
        Args:
            keywords: 關鍵字列表
            pages_per_forum: 每個論壇爬取的頁數
            
        Returns:
            所有文章列表
        """
        if keywords is None:
            keywords = KEYWORDS['recall'] + KEYWORDS['candidates']
        
        all_articles = []
        
        logger.info(f"開始爬取所有Dcard論壇: {self.forums}")
        
        for forum in self.forums:
            try:
                forum_articles = self.get_forum_articles(forum, keywords, pages_per_forum)
                all_articles.extend(forum_articles)
                
                logger.info(f"Dcard {forum} 論壇完成，獲得 {len(forum_articles)} 篇文章")
                
                # 論壇間休息
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"爬取Dcard {forum} 論壇時發生錯誤: {e}")
                continue
        
        # 去重和排序
        all_articles = data_processor.deduplicate_articles(all_articles)
        all_articles = data_processor.sort_by_date(all_articles)
        
        logger.info(f"Dcard爬取完成，總共 {len(all_articles)} 篇文章")
        return all_articles
    
    def search_posts(self, query: str, limit: int = 30) -> List[Dict]:
        """
        搜尋文章
        
        Args:
            query: 搜尋關鍵字
            limit: 結果數量限制
            
        Returns:
            搜尋結果列表
        """
        articles = []
        
        try:
            url = f"{self.api_base}/search/posts"
            params = {
                'query': query,
                'limit': limit
            }
            
            response = self.request_helper.get(url, params=params)
            if not response:
                return articles
            
            data = response.json()
            
            for post in data:
                article = self._process_post(post, 'search', [query])
                if article:
                    articles.append(article)
            
        except Exception as e:
            logger.error(f"Dcard搜尋時發生錯誤: {e}")
        
        return articles

def main():
    """測試函數"""
    logging.basicConfig(level=logging.INFO)
    
    crawler = DcardCrawler()
    
    # 測試爬取政治論壇
    print("=== 測試Dcard爬蟲 ===")
    
    keywords = ['罷免', '羅智強']
    articles = crawler.get_forum_articles('politics', keywords, pages=1)
    
    print(f"爬取結果: {len(articles)} 篇文章")
    
    if articles:
        print("\n前3篇文章:")
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article['title']}")
            print(f"   作者: {article['author']}")
            print(f"   日期: {article['date']}")
            print(f"   情緒: {article['sentiment']}")
            print(f"   讚數: {article['like_count']}")
            print()

if __name__ == "__main__":
    main()
