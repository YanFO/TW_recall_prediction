#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mobile01 爬蟲模組
Mobile01 Crawler Module

爬取Mobile01論壇的討論文章
"""

import requests
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# 導入配置和工具
try:
    from .config import MOBILE01_CONFIG, BASE_CONFIG, KEYWORDS
    from ..utils.common import text_processor, date_processor, data_processor, create_request_helper
except ImportError:
    # 如果作為獨立模組運行
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from crawler.config import MOBILE01_CONFIG, BASE_CONFIG, KEYWORDS
    from utils.common import text_processor, date_processor, data_processor, create_request_helper

# 設置日誌
logger = logging.getLogger(__name__)

class Mobile01Crawler:
    """Mobile01爬蟲類"""
    
    def __init__(self):
        self.base_url = MOBILE01_CONFIG['base_url']
        self.forums = MOBILE01_CONFIG['forums']
        self.pages_per_forum = MOBILE01_CONFIG['pages_per_forum']
        
        # 創建請求輔助工具
        self.request_helper = create_request_helper(
            delay=BASE_CONFIG['request_delay'],
            max_retries=BASE_CONFIG['max_retries']
        )
        
        logger.info("Mobile01爬蟲初始化完成")
    
    def get_forum_articles(self, forum_name: str, forum_id: int, 
                          keywords: List[str] = None, pages: int = 3) -> List[Dict]:
        """
        爬取指定論壇的文章
        
        Args:
            forum_name: 論壇名稱
            forum_id: 論壇ID
            keywords: 關鍵字列表
            pages: 爬取頁數
            
        Returns:
            文章列表
        """
        if keywords is None:
            keywords = KEYWORDS['recall'] + KEYWORDS['candidates']
        
        articles = []
        
        logger.info(f"開始爬取Mobile01 {forum_name} 論壇 (ID: {forum_id})，關鍵字: {keywords}")
        
        try:
            for page in range(1, pages + 1):
                # 構建論壇URL
                forum_url = f"{self.base_url}/topiclist.php?f={forum_id}&p={page}"
                
                # 發送請求
                response = self.request_helper.get(forum_url)
                if not response:
                    logger.error(f"無法獲取Mobile01 {forum_name} 第 {page} 頁")
                    continue
                
                # 解析頁面
                soup = BeautifulSoup(response.text, 'html.parser')
                page_articles = self._parse_forum_page(soup, forum_name, keywords)
                
                articles.extend(page_articles)
                
                logger.info(f"Mobile01 {forum_name} 第 {page} 頁: 找到 {len(page_articles)} 篇相關文章")
                
                # 避免請求過快
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"爬取Mobile01 {forum_name} 論壇時發生錯誤: {e}")
        
        logger.info(f"Mobile01 {forum_name} 論壇爬取完成，共 {len(articles)} 篇文章")
        return articles
    
    def _parse_forum_page(self, soup: BeautifulSoup, forum_name: str, 
                         keywords: List[str]) -> List[Dict]:
        """
        解析論壇頁面
        
        Args:
            soup: BeautifulSoup對象
            forum_name: 論壇名稱
            keywords: 關鍵字列表
            
        Returns:
            文章列表
        """
        articles = []
        
        try:
            # 查找文章列表 (Mobile01的HTML結構可能需要調整)
            topic_rows = soup.find_all('tr', class_=['topic-row', 'c-listTableTr'])
            
            if not topic_rows:
                # 嘗試其他可能的選擇器
                topic_rows = soup.find_all('tr')[1:]  # 跳過表頭
            
            for row in topic_rows:
                try:
                    article = self._parse_topic_row(row, forum_name, keywords)
                    if article:
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"解析Mobile01文章行時發生錯誤: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析Mobile01論壇頁面時發生錯誤: {e}")
        
        return articles
    
    def _parse_topic_row(self, row: BeautifulSoup, forum_name: str, 
                        keywords: List[str]) -> Optional[Dict]:
        """
        解析單個主題行
        
        Args:
            row: 主題行的BeautifulSoup對象
            forum_name: 論壇名稱
            keywords: 關鍵字列表
            
        Returns:
            文章數據或None
        """
        try:
            # 查找標題連結
            title_link = row.find('a', href=True)
            if not title_link:
                return None
            
            title = title_link.get_text(strip=True)
            article_url = urljoin(self.base_url, title_link['href'])
            
            # 檢查是否包含關鍵字
            if not any(keyword.lower() in title.lower() for keyword in keywords):
                return None
            
            # 查找作者
            author_cell = row.find('td', class_=['author', 'c-listTableTd'])
            author = ""
            if author_cell:
                author_link = author_cell.find('a')
                author = author_link.get_text(strip=True) if author_link else author_cell.get_text(strip=True)
            
            # 查找日期
            date_cell = row.find('td', class_=['date', 'c-listTableTd'])
            date_str = ""
            if date_cell:
                date_str = date_cell.get_text(strip=True)
            
            # 查找回覆數
            reply_cell = row.find('td', class_=['reply', 'c-listTableTd'])
            reply_count = 0
            if reply_cell:
                reply_text = reply_cell.get_text(strip=True)
                try:
                    reply_count = int(reply_text) if reply_text.isdigit() else 0
                except:
                    reply_count = 0
            
            # 獲取文章詳細內容
            content = self._get_article_content(article_url)
            
            # 解析日期
            parsed_date = date_processor.parse_date(date_str)
            
            # 情緒分析
            full_text = title + ' ' + content
            sentiment_result = text_processor.analyze_sentiment(full_text)
            
            article = {
                'title': text_processor.clean_text(title),
                'content': text_processor.clean_text(content),
                'author': text_processor.clean_text(author),
                'date': date_processor.format_date(parsed_date) if parsed_date else date_str,
                'link': article_url,
                'source': 'Mobile01',
                'forum': forum_name,
                'reply_count': reply_count,
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['score'],
                'keywords_found': text_processor.extract_keywords(full_text, keywords),
                'crawl_time': datetime.now().isoformat()
            }
            
            return article
            
        except Exception as e:
            logger.error(f"解析Mobile01主題行時發生錯誤: {e}")
            return None
    
    def _get_article_content(self, article_url: str) -> str:
        """
        獲取文章詳細內容
        
        Args:
            article_url: 文章URL
            
        Returns:
            文章內容
        """
        try:
            response = self.request_helper.get(article_url)
            if not response:
                return ""
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章內容 (Mobile01的HTML結構)
            content_div = soup.find('div', class_=['single-post-content', 'articleContent'])
            
            if not content_div:
                # 嘗試其他可能的選擇器
                content_div = soup.find('div', id='content')
                if not content_div:
                    content_div = soup.find('article')
            
            if content_div:
                # 移除不需要的元素
                for unwanted in content_div.find_all(['script', 'style', 'nav', 'footer']):
                    unwanted.decompose()
                
                content = content_div.get_text(separator=' ', strip=True)
                return content[:1000]  # 限制長度
            
            return ""
            
        except Exception as e:
            logger.error(f"獲取Mobile01文章內容時發生錯誤: {e}")
            return ""
    
    def search_articles(self, query: str, limit: int = 20) -> List[Dict]:
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
            # Mobile01搜尋URL
            search_url = f"{self.base_url}/googlesearch.php"
            params = {
                'q': query,
                'cx': 'partner-pub-1234567890123456:1234567890'  # 需要實際的搜尋引擎ID
            }
            
            response = self.request_helper.get(search_url, params=params)
            if not response:
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析搜尋結果
            result_items = soup.find_all('div', class_=['search-result', 'gsc-webResult'])
            
            for item in result_items[:limit]:
                try:
                    title_link = item.find('a', href=True)
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    url = title_link['href']
                    
                    # 獲取摘要
                    snippet_div = item.find('div', class_=['snippet', 'gsc-snippet'])
                    snippet = snippet_div.get_text(strip=True) if snippet_div else ""
                    
                    # 情緒分析
                    full_text = title + ' ' + snippet
                    sentiment_result = text_processor.analyze_sentiment(full_text)
                    
                    article = {
                        'title': text_processor.clean_text(title),
                        'content': text_processor.clean_text(snippet),
                        'link': url,
                        'source': 'Mobile01',
                        'forum': 'search',
                        'sentiment': sentiment_result['sentiment'],
                        'sentiment_score': sentiment_result['score'],
                        'keywords_found': text_processor.extract_keywords(full_text, [query]),
                        'crawl_time': datetime.now().isoformat()
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"處理Mobile01搜尋結果時發生錯誤: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Mobile01搜尋時發生錯誤: {e}")
        
        return articles
    
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
        
        logger.info(f"開始爬取所有Mobile01論壇: {list(self.forums.keys())}")
        
        for forum_name, forum_id in self.forums.items():
            try:
                forum_articles = self.get_forum_articles(
                    forum_name, forum_id, keywords, pages_per_forum
                )
                all_articles.extend(forum_articles)
                
                logger.info(f"Mobile01 {forum_name} 論壇完成，獲得 {len(forum_articles)} 篇文章")
                
                # 論壇間休息
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"爬取Mobile01 {forum_name} 論壇時發生錯誤: {e}")
                continue
        
        # 去重和排序
        all_articles = data_processor.deduplicate_articles(all_articles)
        all_articles = data_processor.sort_by_date(all_articles)
        
        logger.info(f"Mobile01爬取完成，總共 {len(all_articles)} 篇文章")
        return all_articles

def main():
    """測試函數"""
    logging.basicConfig(level=logging.INFO)
    
    crawler = Mobile01Crawler()
    
    # 測試爬取政治討論版
    print("=== 測試Mobile01爬蟲 ===")
    
    keywords = ['罷免', '羅智強']
    articles = crawler.get_forum_articles('politics', 376, keywords, pages=1)
    
    print(f"爬取結果: {len(articles)} 篇文章")
    
    if articles:
        print("\n前3篇文章:")
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article['title']}")
            print(f"   作者: {article['author']}")
            print(f"   日期: {article['date']}")
            print(f"   情緒: {article['sentiment']}")
            print(f"   回覆數: {article['reply_count']}")
            print()

if __name__ == "__main__":
    main()
