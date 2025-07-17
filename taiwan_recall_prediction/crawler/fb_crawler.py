#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook 爬蟲模組
Facebook Crawler Module

使用Facebook Graph API爬取公開粉專的貼文和留言
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

# 導入配置和工具
try:
    from .config import FACEBOOK_CONFIG, BASE_CONFIG, KEYWORDS
    from ..utils.common import text_processor, date_processor, data_processor, create_request_helper
except ImportError:
    # 如果作為獨立模組運行
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from crawler.config import FACEBOOK_CONFIG, BASE_CONFIG, KEYWORDS
    from utils.common import text_processor, date_processor, data_processor, create_request_helper

# 設置日誌
logger = logging.getLogger(__name__)

class FacebookCrawler:
    """Facebook爬蟲類"""
    
    def __init__(self, access_token: str = None):
        self.graph_api_base = FACEBOOK_CONFIG['graph_api_base']
        self.access_token = access_token or FACEBOOK_CONFIG['access_token']
        self.pages = FACEBOOK_CONFIG['pages']
        self.posts_limit = FACEBOOK_CONFIG['posts_limit']
        
        # 創建請求輔助工具
        self.request_helper = create_request_helper(
            delay=BASE_CONFIG['request_delay'],
            max_retries=BASE_CONFIG['max_retries']
        )
        
        if not self.access_token:
            logger.warning("Facebook access token未設置，某些功能可能無法使用")
        
        logger.info("Facebook爬蟲初始化完成")
    
    def get_page_posts(self, page_id: str, keywords: List[str] = None, 
                      limit: int = None) -> List[Dict]:
        """
        獲取粉專貼文
        
        Args:
            page_id: 粉專ID
            keywords: 關鍵字列表
            limit: 貼文數量限制
            
        Returns:
            貼文列表
        """
        if not self.access_token:
            logger.error("需要Facebook access token才能爬取數據")
            return []
        
        if keywords is None:
            keywords = KEYWORDS['recall'] + KEYWORDS['candidates']
        
        if limit is None:
            limit = self.posts_limit
        
        posts = []
        
        logger.info(f"開始爬取Facebook粉專 {page_id} 的貼文，關鍵字: {keywords}")
        
        try:
            # 構建API URL
            url = f"{self.graph_api_base}/{page_id}/posts"
            params = {
                'access_token': self.access_token,
                'fields': 'id,message,created_time,updated_time,permalink_url,reactions.summary(true),comments.summary(true),shares',
                'limit': limit
            }
            
            response = self.request_helper.get(url, params=params)
            if not response:
                logger.error(f"無法獲取Facebook粉專 {page_id} 的貼文")
                return posts
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Facebook API返回無效JSON: {page_id}")
                return posts
            
            if 'error' in data:
                logger.error(f"Facebook API錯誤: {data['error']}")
                return posts
            
            # 處理貼文
            for post_data in data.get('data', []):
                post = self._process_post(post_data, page_id, keywords)
                if post:
                    posts.append(post)
            
            logger.info(f"Facebook粉專 {page_id} 爬取完成，共 {len(posts)} 篇相關貼文")
            
        except Exception as e:
            logger.error(f"爬取Facebook粉專 {page_id} 時發生錯誤: {e}")
        
        return posts
    
    def _process_post(self, post_data: Dict, page_id: str, 
                     keywords: List[str]) -> Optional[Dict]:
        """
        處理單篇貼文
        
        Args:
            post_data: API返回的貼文數據
            page_id: 粉專ID
            keywords: 關鍵字列表
            
        Returns:
            處理後的貼文數據或None
        """
        try:
            message = post_data.get('message', '')
            
            # 檢查是否包含關鍵字
            if not any(keyword.lower() in message.lower() for keyword in keywords):
                return None
            
            # 解析日期
            created_time = post_data.get('created_time', '')
            parsed_date = date_processor.parse_date(created_time)
            
            # 獲取互動數據
            reactions = post_data.get('reactions', {}).get('summary', {})
            comments = post_data.get('comments', {}).get('summary', {})
            shares = post_data.get('shares', {})
            
            reaction_count = reactions.get('total_count', 0)
            comment_count = comments.get('total_count', 0)
            share_count = shares.get('count', 0)
            
            # 情緒分析
            sentiment_result = text_processor.analyze_sentiment(message)
            
            # 獲取貼文留言
            post_id = post_data.get('id', '')
            post_comments = self.get_post_comments(post_id, limit=20)
            
            post = {
                'title': text_processor.clean_text(message[:100] + '...' if len(message) > 100 else message),
                'content': text_processor.clean_text(message),
                'author': page_id,
                'date': date_processor.format_date(parsed_date) if parsed_date else created_time,
                'link': post_data.get('permalink_url', ''),
                'source': 'Facebook',
                'page': page_id,
                'post_id': post_id,
                'reaction_count': reaction_count,
                'comment_count': comment_count,
                'share_count': share_count,
                'engagement_rate': (reaction_count + comment_count + share_count),
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['score'],
                'keywords_found': text_processor.extract_keywords(message, keywords),
                'comments': post_comments,
                'crawl_time': datetime.now().isoformat()
            }
            
            return post
            
        except Exception as e:
            logger.error(f"處理Facebook貼文時發生錯誤: {e}")
            return None
    
    def get_post_comments(self, post_id: str, limit: int = 20) -> List[Dict]:
        """
        獲取貼文留言
        
        Args:
            post_id: 貼文ID
            limit: 留言數量限制
            
        Returns:
            留言列表
        """
        if not self.access_token:
            return []
        
        comments = []
        
        try:
            url = f"{self.graph_api_base}/{post_id}/comments"
            params = {
                'access_token': self.access_token,
                'fields': 'id,message,created_time,from,like_count',
                'limit': limit
            }
            
            response = self.request_helper.get(url, params=params)
            if not response:
                return comments
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"獲取Facebook留言時發生錯誤: {data['error']}")
                return comments
            
            for comment_data in data.get('data', []):
                try:
                    message = comment_data.get('message', '')
                    created_time = comment_data.get('created_time', '')
                    parsed_date = date_processor.parse_date(created_time)
                    
                    from_data = comment_data.get('from', {})
                    author = from_data.get('name', 'Unknown')
                    
                    # 情緒分析
                    sentiment_result = text_processor.analyze_sentiment(message)
                    
                    comment = {
                        'content': text_processor.clean_text(message),
                        'author': author,
                        'date': date_processor.format_date(parsed_date) if parsed_date else created_time,
                        'like_count': comment_data.get('like_count', 0),
                        'sentiment': sentiment_result['sentiment'],
                        'sentiment_score': sentiment_result['score']
                    }
                    
                    comments.append(comment)
                    
                except Exception as e:
                    logger.error(f"處理Facebook留言時發生錯誤: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"獲取Facebook留言時發生錯誤: {e}")
        
        return comments
    
    def crawl_all_pages(self, keywords: List[str] = None, 
                       posts_per_page: int = None) -> List[Dict]:
        """
        爬取所有配置的粉專
        
        Args:
            keywords: 關鍵字列表
            posts_per_page: 每個粉專爬取的貼文數
            
        Returns:
            所有貼文列表
        """
        if not self.access_token:
            logger.error("需要Facebook access token才能爬取數據")
            return []
        
        if keywords is None:
            keywords = KEYWORDS['recall'] + KEYWORDS['candidates']
        
        if posts_per_page is None:
            posts_per_page = self.posts_limit
        
        all_posts = []
        
        logger.info(f"開始爬取所有Facebook粉專: {list(self.pages.keys())}")
        
        for page_name, page_id in self.pages.items():
            try:
                page_posts = self.get_page_posts(page_id, keywords, posts_per_page)
                all_posts.extend(page_posts)
                
                logger.info(f"Facebook {page_name} 粉專完成，獲得 {len(page_posts)} 篇貼文")
                
                # 粉專間休息
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"爬取Facebook {page_name} 粉專時發生錯誤: {e}")
                continue
        
        # 去重和排序
        all_posts = data_processor.deduplicate_articles(all_posts)
        all_posts = data_processor.sort_by_date(all_posts)
        
        logger.info(f"Facebook爬取完成，總共 {len(all_posts)} 篇貼文")
        return all_posts
    
    def get_page_info(self, page_id: str) -> Dict:
        """
        獲取粉專基本資訊
        
        Args:
            page_id: 粉專ID
            
        Returns:
            粉專資訊
        """
        if not self.access_token:
            return {}
        
        try:
            url = f"{self.graph_api_base}/{page_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,category,fan_count,talking_about_count,link'
            }
            
            response = self.request_helper.get(url, params=params)
            if not response:
                return {}
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"獲取Facebook粉專資訊時發生錯誤: {data['error']}")
                return {}
            
            return data
            
        except Exception as e:
            logger.error(f"獲取Facebook粉專資訊時發生錯誤: {e}")
            return {}
    
    def search_posts(self, query: str, limit: int = 20) -> List[Dict]:
        """
        搜尋公開貼文 (需要特殊權限)
        
        Args:
            query: 搜尋關鍵字
            limit: 結果數量限制
            
        Returns:
            搜尋結果列表
        """
        if not self.access_token:
            return []
        
        posts = []
        
        try:
            url = f"{self.graph_api_base}/search"
            params = {
                'access_token': self.access_token,
                'q': query,
                'type': 'post',
                'limit': limit
            }
            
            response = self.request_helper.get(url, params=params)
            if not response:
                return posts
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"Facebook搜尋時發生錯誤: {data['error']}")
                return posts
            
            for post_data in data.get('data', []):
                post = self._process_post(post_data, 'search', [query])
                if post:
                    posts.append(post)
            
        except Exception as e:
            logger.error(f"Facebook搜尋時發生錯誤: {e}")
        
        return posts

def main():
    """測試函數"""
    logging.basicConfig(level=logging.INFO)
    
    # 注意：需要有效的Facebook access token才能測試
    access_token = "YOUR_FACEBOOK_ACCESS_TOKEN"
    
    if access_token == "YOUR_FACEBOOK_ACCESS_TOKEN":
        print("請設置有效的Facebook access token")
        return
    
    crawler = FacebookCrawler(access_token)
    
    # 測試爬取KMT粉專
    print("=== 測試Facebook爬蟲 ===")
    
    keywords = ['罷免', '羅智強']
    posts = crawler.get_page_posts('kmt.tw', keywords, limit=5)
    
    print(f"爬取結果: {len(posts)} 篇貼文")
    
    if posts:
        print("\n前3篇貼文:")
        for i, post in enumerate(posts[:3], 1):
            print(f"{i}. {post['title']}")
            print(f"   作者: {post['author']}")
            print(f"   日期: {post['date']}")
            print(f"   情緒: {post['sentiment']}")
            print(f"   互動數: {post['engagement_rate']}")
            print()

if __name__ == "__main__":
    main()
