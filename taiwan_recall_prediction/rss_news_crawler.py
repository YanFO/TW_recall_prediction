#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS和新聞API真實數據爬蟲
RSS and News API Real Data Crawler

使用RSS feeds和新聞API獲取真實的新聞和討論數據
"""

import requests
import feedparser
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from urllib.parse import quote

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSNewsCrawler:
    """RSS和新聞API爬蟲"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml'
        })
        
        # 台灣主要新聞RSS源
        self.rss_sources = {
            '中央社': 'https://feeds.cna.com.tw/rssfeed/news.xml',
            '自由時報': 'https://news.ltn.com.tw/rss/all.xml',
            '聯合新聞網': 'https://udn.com/rssfeed/news/2/6638?ch=news',
            '中時新聞網': 'https://www.chinatimes.com/rss/realtimenews.xml',
            '蘋果新聞網': 'https://tw.appledaily.com/rss',
            '風傳媒': 'https://www.storm.mg/feeds/all.xml',
            '新頭殼': 'https://newtalk.tw/rss',
            'ETtoday': 'https://feeds.ettoday.net/ettoday-news.xml'
        }
        
        self.positive_keywords = ['支持', '讚', '好', '棒', '優秀', '肯定', '贊成', '同意']
        self.negative_keywords = ['反對', '批評', '質疑', '不滿', '抗議', '譴責', '失望']
    
    def crawl_real_news_data(self, candidate_name: str) -> Dict:
        """爬取真實新聞數據"""
        logger.info(f"開始爬取真實新聞數據: {candidate_name}")
        
        all_articles = []
        successful_sources = []
        failed_sources = []
        
        for source_name, rss_url in self.rss_sources.items():
            try:
                articles = self._crawl_rss_feed(rss_url, source_name, candidate_name)
                if articles:
                    all_articles.extend(articles)
                    successful_sources.append(source_name)
                    logger.info(f"✅ {source_name}: 找到 {len(articles)} 篇相關文章")
                else:
                    failed_sources.append(source_name)
                    logger.info(f"❌ {source_name}: 無相關文章")
                
                time.sleep(1)  # 避免請求過快
                
            except Exception as e:
                failed_sources.append(source_name)
                logger.error(f"❌ {source_name} RSS爬取失敗: {e}")
        
        # 如果RSS沒有足夠數據，嘗試新聞搜尋API
        if len(all_articles) < 5:
            api_articles = self._crawl_news_apis(candidate_name)
            all_articles.extend(api_articles)
        
        # 分析結果
        if all_articles:
            analysis = self._analyze_articles(all_articles, candidate_name)
            analysis.update({
                'data_source': '✅ 真實新聞RSS數據 (Real News RSS Data)',
                'is_simulated': False,
                'successful_sources': successful_sources,
                'failed_sources': failed_sources,
                'crawl_timestamp': datetime.now().isoformat(),
                'total_sources_attempted': len(self.rss_sources),
                'successful_source_count': len(successful_sources)
            })
            return analysis
        else:
            return {
                'error': '無法獲取真實新聞數據',
                'data_source': '❌ 新聞RSS爬取失敗 (News RSS Failed)',
                'is_simulated': False,
                'total_articles': 0,
                'successful_sources': successful_sources,
                'failed_sources': failed_sources
            }
    
    def _crawl_rss_feed(self, rss_url: str, source_name: str, candidate_name: str) -> List[Dict]:
        """爬取單個RSS源"""
        articles = []
        try:
            # 使用feedparser解析RSS
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                logger.warning(f"{source_name} RSS格式可能有問題")
            
            for entry in feed.entries[:50]:  # 限制檢查最新50篇
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                content = title + ' ' + summary
                
                # 檢查是否包含候選人名字
                if candidate_name in content:
                    article = {
                        'title': title,
                        'summary': summary,
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'source': source_name,
                        'sentiment': self._analyze_sentiment(content),
                        'timestamp': self._parse_date(entry.get('published', '')),
                        'is_real': True
                    }
                    articles.append(article)
            
        except Exception as e:
            logger.error(f"{source_name} RSS解析錯誤: {e}")
        
        return articles
    
    def _crawl_news_apis(self, candidate_name: str) -> List[Dict]:
        """使用新聞API獲取數據"""
        articles = []
        
        # 嘗試免費新聞API
        apis = [
            self._try_newsapi_org(candidate_name),
            self._try_gnews_api(candidate_name),
            self._try_currents_api(candidate_name)
        ]
        
        for api_articles in apis:
            if api_articles:
                articles.extend(api_articles)
                break  # 只要有一個API成功就夠了
        
        return articles
    
    def _try_newsapi_org(self, candidate_name: str) -> List[Dict]:
        """嘗試NewsAPI.org (需要API key)"""
        try:
            # 這裡需要API key，暫時跳過
            # api_key = "YOUR_NEWSAPI_KEY"
            # url = f"https://newsapi.org/v2/everything?q={candidate_name}&language=zh&apiKey={api_key}"
            return []
        except Exception:
            return []
    
    def _try_gnews_api(self, candidate_name: str) -> List[Dict]:
        """嘗試GNews API"""
        try:
            # 免費版本有限制
            url = f"https://gnews.io/api/v4/search?q={candidate_name}&lang=zh&country=tw&max=10"
            # 需要API key
            return []
        except Exception:
            return []
    
    def _try_currents_api(self, candidate_name: str) -> List[Dict]:
        """嘗試Currents API"""
        try:
            # 免費版本
            url = f"https://api.currentsapi.services/v1/search?keywords={candidate_name}&language=zh"
            # 需要API key
            return []
        except Exception:
            return []
    
    def _analyze_sentiment(self, text: str) -> str:
        """分析文本情緒"""
        text_lower = text.lower()
        
        pos_score = sum(1 for keyword in self.positive_keywords if keyword in text)
        neg_score = sum(1 for keyword in self.negative_keywords if keyword in text)
        
        # 特殊規則：罷免相關
        if '罷免' in text:
            if any(word in text for word in ['支持罷免', '贊成罷免']):
                return 'negative'  # 支持罷免對候選人是負面
            elif any(word in text for word in ['反對罷免', '不支持罷免']):
                return 'positive'  # 反對罷免對候選人是正面
        
        if pos_score > neg_score:
            return 'positive'
        elif neg_score > pos_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        try:
            if date_str:
                # 嘗試解析常見的日期格式
                import dateutil.parser
                parsed_date = dateutil.parser.parse(date_str)
                return parsed_date.isoformat()
        except:
            pass
        
        return datetime.now().isoformat()
    
    def _analyze_articles(self, articles: List[Dict], candidate_name: str) -> Dict:
        """分析文章數據"""
        if not articles:
            return {
                'total_articles': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'positive_ratio': 0,
                'recent_articles': []
            }
        
        positive_count = sum(1 for article in articles if article['sentiment'] == 'positive')
        negative_count = sum(1 for article in articles if article['sentiment'] == 'negative')
        neutral_count = sum(1 for article in articles if article['sentiment'] == 'neutral')
        
        total_articles = len(articles)
        
        # 按時間排序，取最新的文章
        sorted_articles = sorted(articles, key=lambda x: x['timestamp'], reverse=True)
        recent_articles = sorted_articles[:10]
        
        # 來源統計
        sources = {}
        for article in articles:
            source = article['source']
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_articles': total_articles,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': positive_count / total_articles if total_articles > 0 else 0,
            'negative_ratio': negative_count / total_articles if total_articles > 0 else 0,
            'neutral_ratio': neutral_count / total_articles if total_articles > 0 else 0,
            'recent_articles': recent_articles,
            'source_distribution': sources,
            'date_range': {
                'earliest': min(article['timestamp'] for article in articles),
                'latest': max(article['timestamp'] for article in articles)
            }
        }
    
    def get_real_discussion_sample(self, candidate_name: str) -> List[Dict]:
        """獲取真實討論樣本（用於展示）"""
        try:
            result = self.crawl_real_news_data(candidate_name)
            
            if result.get('recent_articles'):
                # 轉換為PTT風格的展示格式
                discussions = []
                for i, article in enumerate(result['recent_articles'][:5], 1):
                    discussion = {
                        'title': article['title'],
                        'author': article['source'],
                        'board': 'News',
                        'sentiment': article['sentiment'],
                        'comments': len(article['title']) // 2,  # 簡單的熱度估算
                        'time': article.get('published', ''),
                        'url': article.get('link', ''),
                        'is_real': True,
                        'platform': 'RSS News'
                    }
                    discussions.append(discussion)
                
                return discussions
            
        except Exception as e:
            logger.error(f"獲取真實討論樣本錯誤: {e}")
        
        return []

if __name__ == "__main__":
    # 測試RSS新聞爬蟲
    crawler = RSSNewsCrawler()
    
    candidate = "羅智強"
    print(f"開始爬取真實新聞數據: {candidate}")
    
    # 測試新聞爬取
    result = crawler.crawl_real_news_data(candidate)
    
    print(f"\n爬取結果:")
    print(f"數據來源: {result.get('data_source', 'Unknown')}")
    print(f"文章總數: {result.get('total_articles', 0)}")
    print(f"成功來源: {len(result.get('successful_sources', []))}")
    print(f"失敗來源: {len(result.get('failed_sources', []))}")
    
    if result.get('recent_articles'):
        print(f"\n最新相關文章:")
        for i, article in enumerate(result['recent_articles'][:3], 1):
            print(f"{i}. {article['title']}")
            print(f"   來源: {article['source']} | 情緒: {article['sentiment']}")
    
    # 測試討論樣本
    discussions = crawler.get_real_discussion_sample(candidate)
    if discussions:
        print(f"\n真實討論樣本:")
        for i, discussion in enumerate(discussions, 1):
            print(f"{i}. {discussion['title']}")
            print(f"   來源: {discussion['author']} | 情緒: {discussion['sentiment']}")
    
    # 保存結果
    with open('rss_news_crawl_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細結果已保存到: rss_news_crawl_result.json")
