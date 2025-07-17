#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具模組
Common Utilities Module

提供關鍵字過濾、日期轉換、文本清洗等通用功能
"""

import re
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# 設置日誌
logger = logging.getLogger(__name__)

class TextProcessor:
    """文本處理工具類"""
    
    def __init__(self):
        # 常見的無用字符和符號
        self.noise_patterns = [
            r'[^\w\s\u4e00-\u9fff]',  # 保留中文、英文、數字和空格
            r'\s+',  # 多個空格
            r'^\s+|\s+$'  # 首尾空格
        ]
        
        # 情緒關鍵字
        self.positive_keywords = ['支持', '讚', '好', '棒', '優秀', '加油', '推', '贊成', '同意', '肯定']
        self.negative_keywords = ['反對', '爛', '差', '糟', '討厭', '垃圾', '失望', '不滿', '批評', '噓']
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除HTML標籤
        text = BeautifulSoup(text, 'html.parser').get_text()
        
        # 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除首尾空格
        text = text.strip()
        
        return text
    
    def extract_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """提取關鍵字"""
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """簡單的情緒分析"""
        if not text:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        score = (positive_count - negative_count) / total_count
        confidence = total_count / len(text.split()) if text.split() else 0
        
        if score > 0.1:
            sentiment = 'positive'
        elif score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': min(confidence, 1.0),
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def generate_summary(self, text: str, max_length: int = 100) -> str:
        """生成文本摘要"""
        if not text or len(text) <= max_length:
            return text
        
        # 簡單的摘要：取前面的句子
        sentences = re.split(r'[。！？\n]', text)
        summary = ""
        
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break
        
        return summary.strip() or text[:max_length] + "..."

class DateProcessor:
    """日期處理工具類"""
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """解析各種日期格式"""
        if not date_str:
            return None
        
        # 常見的日期格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%m/%d',
            '%Y/%m/%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # 處理相對時間
        if '小時前' in date_str:
            hours = int(re.search(r'(\d+)', date_str).group(1))
            return datetime.now() - timedelta(hours=hours)
        elif '天前' in date_str:
            days = int(re.search(r'(\d+)', date_str).group(1))
            return datetime.now() - timedelta(days=days)
        elif '分鐘前' in date_str:
            minutes = int(re.search(r'(\d+)', date_str).group(1))
            return datetime.now() - timedelta(minutes=minutes)
        
        return None
    
    @staticmethod
    def format_date(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """格式化日期"""
        if not dt:
            return ""
        return dt.strftime(format_str)
    
    @staticmethod
    def is_recent(dt: datetime, days: int = 7) -> bool:
        """檢查日期是否在最近N天內"""
        if not dt:
            return False
        return (datetime.now() - dt).days <= days

class URLProcessor:
    """URL處理工具類"""
    
    @staticmethod
    def normalize_url(url: str, base_url: str = "") -> str:
        """標準化URL"""
        if not url:
            return ""
        
        # 如果是相對URL，轉換為絕對URL
        if url.startswith('/') and base_url:
            return urljoin(base_url, url)
        
        return url
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """檢查URL是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """提取域名"""
        try:
            return urlparse(url).netloc
        except:
            return ""

class DataProcessor:
    """數據處理工具類"""
    
    @staticmethod
    def generate_hash(data: str) -> str:
        """生成數據哈希值"""
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def deduplicate_articles(articles: List[Dict]) -> List[Dict]:
        """去除重複文章"""
        seen_hashes = set()
        unique_articles = []
        
        for article in articles:
            # 使用標題和內容生成哈希
            content_hash = DataProcessor.generate_hash(
                f"{article.get('title', '')}{article.get('content', '')}"
            )
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                article['content_hash'] = content_hash
                unique_articles.append(article)
        
        return unique_articles
    
    @staticmethod
    def filter_by_keywords(articles: List[Dict], keywords: List[str], 
                          fields: List[str] = ['title', 'content']) -> List[Dict]:
        """根據關鍵字過濾文章"""
        filtered_articles = []
        
        for article in articles:
            text_to_search = ""
            for field in fields:
                text_to_search += article.get(field, "") + " "
            
            if any(keyword.lower() in text_to_search.lower() for keyword in keywords):
                filtered_articles.append(article)
        
        return filtered_articles
    
    @staticmethod
    def sort_by_date(articles: List[Dict], date_field: str = 'date', 
                    reverse: bool = True) -> List[Dict]:
        """按日期排序文章"""
        def get_date_key(article):
            date_str = article.get(date_field, '')
            parsed_date = DateProcessor.parse_date(date_str)
            return parsed_date if parsed_date else datetime.min
        
        return sorted(articles, key=get_date_key, reverse=reverse)

class RequestHelper:
    """請求輔助工具類"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """安全的GET請求"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=10, **kwargs)
                response.raise_for_status()
                
                if attempt > 0:
                    logger.info(f"Request succeeded on attempt {attempt + 1}")
                
                time.sleep(self.delay)
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.delay * (attempt + 1))
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {url}")
        
        return None
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """安全的POST請求"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(url, timeout=10, **kwargs)
                response.raise_for_status()
                
                time.sleep(self.delay)
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"POST request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.delay * (attempt + 1))
        
        return None

class StatisticsCalculator:
    """統計計算工具類"""
    
    @staticmethod
    def calculate_engagement_rate(articles: List[Dict]) -> Dict[str, float]:
        """計算參與度統計"""
        if not articles:
            return {'avg_comments': 0, 'total_engagement': 0}
        
        total_comments = 0
        total_articles = len(articles)
        
        for article in articles:
            comments = article.get('comments', [])
            if isinstance(comments, list):
                total_comments += len(comments)
            elif isinstance(comments, int):
                total_comments += comments
        
        return {
            'avg_comments': total_comments / total_articles if total_articles > 0 else 0,
            'total_engagement': total_comments,
            'total_articles': total_articles
        }
    
    @staticmethod
    def calculate_sentiment_distribution(articles: List[Dict]) -> Dict[str, Any]:
        """計算情緒分布"""
        if not articles:
            return {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        text_processor = TextProcessor()
        
        for article in articles:
            content = article.get('content', '') + ' ' + article.get('title', '')
            sentiment_result = text_processor.analyze_sentiment(content)
            sentiment = sentiment_result['sentiment']
            
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
        
        total = len(articles)
        return {
            **sentiment_counts,
            'total': total,
            'positive_ratio': sentiment_counts['positive'] / total if total > 0 else 0,
            'negative_ratio': sentiment_counts['negative'] / total if total > 0 else 0,
            'neutral_ratio': sentiment_counts['neutral'] / total if total > 0 else 0
        }

# 創建全局實例
text_processor = TextProcessor()
date_processor = DateProcessor()
url_processor = URLProcessor()
data_processor = DataProcessor()
statistics_calculator = StatisticsCalculator()

def create_request_helper(delay: float = 1.0, max_retries: int = 3) -> RequestHelper:
    """創建請求輔助實例"""
    return RequestHelper(delay, max_retries)

if __name__ == "__main__":
    # 測試工具函數
    print("=== 通用工具測試 ===")
    
    # 測試文本處理
    test_text = "這個候選人真的很爛，我不支持他！"
    sentiment = text_processor.analyze_sentiment(test_text)
    print(f"情緒分析結果: {sentiment}")
    
    # 測試日期處理
    test_date = "2小時前"
    parsed_date = date_processor.parse_date(test_date)
    print(f"日期解析結果: {parsed_date}")
    
    # 測試URL處理
    test_url = "/bbs/Gossiping/index.html"
    normalized_url = url_processor.normalize_url(test_url, "https://www.ptt.cc")
    print(f"URL標準化結果: {normalized_url}")
    
    print("✅ 工具測試完成")
