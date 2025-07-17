#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台真實數據爬蟲
Multi-Platform Real Data Crawler

從多個真實平台抓取討論數據，包括PTT、Dcard、Reddit、Twitter等
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiPlatformCrawler:
    """多平台真實數據爬蟲"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        })
        
        self.positive_keywords = ['支持', '讚', '好', '棒', '優秀', '加油', '推', '贊成', '同意', '肯定']
        self.negative_keywords = ['反對', '爛', '差', '糟', '討厭', '垃圾', '失望', '不滿', '批評', '噓']
    
    def crawl_all_platforms(self, candidate_name: str) -> Dict:
        """爬取所有平台的真實數據"""
        logger.info(f"開始多平台爬取: {candidate_name}")
        
        results = {
            'candidate': candidate_name,
            'crawl_timestamp': datetime.now().isoformat(),
            'platforms': {},
            'summary': {}
        }
        
        # 1. 嘗試PTT替代方案
        ptt_result = self._crawl_ptt_alternative(candidate_name)
        results['platforms']['ptt'] = ptt_result
        
        # 2. 嘗試Dcard替代方案
        dcard_result = self._crawl_dcard_alternative(candidate_name)
        results['platforms']['dcard'] = dcard_result
        
        # 3. 爬取Google新聞
        news_result = self._crawl_google_news(candidate_name)
        results['platforms']['google_news'] = news_result
        
        # 4. 爬取Yahoo新聞
        yahoo_result = self._crawl_yahoo_news(candidate_name)
        results['platforms']['yahoo_news'] = yahoo_result
        
        # 5. 爬取Mobile01
        mobile01_result = self._crawl_mobile01(candidate_name)
        results['platforms']['mobile01'] = mobile01_result
        
        # 6. 爬取巴哈姆特
        bahamut_result = self._crawl_bahamut(candidate_name)
        results['platforms']['bahamut'] = bahamut_result
        
        # 生成總結
        results['summary'] = self._generate_summary(results['platforms'])
        
        return results
    
    def _crawl_ptt_alternative(self, candidate_name: str) -> Dict:
        """PTT替代爬取方案"""
        try:
            # 方案1: 使用PTT Web版
            web_result = self._try_ptt_web_version(candidate_name)
            if web_result['success']:
                return web_result
            
            # 方案2: 使用第三方PTT API
            api_result = self._try_third_party_ptt_api(candidate_name)
            if api_result['success']:
                return api_result
            
            # 方案3: 使用PTT爬蟲網站
            crawler_result = self._try_ptt_crawler_sites(candidate_name)
            if crawler_result['success']:
                return crawler_result
            
        except Exception as e:
            logger.error(f"PTT替代方案錯誤: {e}")
        
        return {
            'success': False,
            'platform': 'PTT',
            'error': 'All PTT alternatives failed',
            'posts': []
        }
    
    def _try_ptt_web_version(self, candidate_name: str) -> Dict:
        """嘗試PTT Web版"""
        try:
            # PTT Web版可能的URL
            urls = [
                f"https://term.ptt.cc/",
                f"https://www.pttweb.cc/bbs/Gossiping/search?q={candidate_name}",
                f"https://www.ptt.cc/bbs/Gossiping/index.html"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200 and candidate_name in response.text:
                        # 簡單解析
                        soup = BeautifulSoup(response.text, 'html.parser')
                        posts = self._extract_ptt_posts(soup, candidate_name)
                        
                        if posts:
                            return {
                                'success': True,
                                'platform': 'PTT Web',
                                'source_url': url,
                                'posts': posts,
                                'data_source': '✅ PTT Web版真實數據'
                            }
                
                except Exception:
                    continue
            
        except Exception as e:
            logger.debug(f"PTT Web版失敗: {e}")
        
        return {'success': False}
    
    def _try_third_party_ptt_api(self, candidate_name: str) -> Dict:
        """嘗試第三方PTT API"""
        try:
            # 一些可能的第三方PTT API
            apis = [
                f"https://api.ptt.cc/posts/search?q={candidate_name}",
                f"https://pttapi.herokuapp.com/posts/search?keyword={candidate_name}",
            ]
            
            for api_url in apis:
                try:
                    response = self.session.get(api_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            posts = self._parse_ptt_api_data(data)
                            return {
                                'success': True,
                                'platform': 'PTT API',
                                'source_url': api_url,
                                'posts': posts,
                                'data_source': '✅ PTT API真實數據'
                            }
                
                except Exception:
                    continue
            
        except Exception as e:
            logger.debug(f"第三方PTT API失敗: {e}")
        
        return {'success': False}
    
    def _try_ptt_crawler_sites(self, candidate_name: str) -> Dict:
        """嘗試PTT爬蟲網站"""
        try:
            # 一些PTT鏡像或爬蟲網站
            sites = [
                f"https://disp.cc/b/163-{candidate_name}",
                f"https://www.pttweb.cc/bbs/search?q={candidate_name}",
            ]
            
            for site_url in sites:
                try:
                    response = self.session.get(site_url, timeout=10)
                    if response.status_code == 200 and candidate_name in response.text:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        posts = self._extract_general_posts(soup, candidate_name, 'PTT Mirror')
                        
                        if posts:
                            return {
                                'success': True,
                                'platform': 'PTT Mirror',
                                'source_url': site_url,
                                'posts': posts,
                                'data_source': '✅ PTT鏡像真實數據'
                            }
                
                except Exception:
                    continue
            
        except Exception as e:
            logger.debug(f"PTT爬蟲網站失敗: {e}")
        
        return {'success': False}
    
    def _crawl_dcard_alternative(self, candidate_name: str) -> Dict:
        """Dcard替代爬取方案"""
        try:
            # 嘗試Dcard網頁版搜尋
            search_url = f"https://www.dcard.tw/search/posts?query={candidate_name}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = self._extract_dcard_posts(soup, candidate_name)
                
                if posts:
                    return {
                        'success': True,
                        'platform': 'Dcard',
                        'source_url': search_url,
                        'posts': posts,
                        'data_source': '✅ Dcard網頁真實數據'
                    }
            
        except Exception as e:
            logger.error(f"Dcard替代方案錯誤: {e}")
        
        return {
            'success': False,
            'platform': 'Dcard',
            'error': 'Dcard web crawling failed',
            'posts': []
        }
    
    def _crawl_google_news(self, candidate_name: str) -> Dict:
        """爬取Google新聞"""
        try:
            search_url = f"https://news.google.com/search?q={candidate_name}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = self._extract_news_articles(soup, candidate_name, 'Google News')
                
                return {
                    'success': len(articles) > 0,
                    'platform': 'Google News',
                    'source_url': search_url,
                    'posts': articles,
                    'data_source': '✅ Google新聞真實數據' if articles else '❌ Google新聞無數據'
                }
            
        except Exception as e:
            logger.error(f"Google新聞爬取錯誤: {e}")
        
        return {'success': False, 'platform': 'Google News', 'posts': []}
    
    def _crawl_yahoo_news(self, candidate_name: str) -> Dict:
        """爬取Yahoo新聞"""
        try:
            search_url = f"https://tw.news.yahoo.com/search?p={candidate_name}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = self._extract_news_articles(soup, candidate_name, 'Yahoo News')
                
                return {
                    'success': len(articles) > 0,
                    'platform': 'Yahoo News',
                    'source_url': search_url,
                    'posts': articles,
                    'data_source': '✅ Yahoo新聞真實數據' if articles else '❌ Yahoo新聞無數據'
                }
            
        except Exception as e:
            logger.error(f"Yahoo新聞爬取錯誤: {e}")
        
        return {'success': False, 'platform': 'Yahoo News', 'posts': []}
    
    def _crawl_mobile01(self, candidate_name: str) -> Dict:
        """爬取Mobile01討論"""
        try:
            search_url = f"https://www.mobile01.com/googlesearch.php?q={candidate_name}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = self._extract_general_posts(soup, candidate_name, 'Mobile01')
                
                return {
                    'success': len(posts) > 0,
                    'platform': 'Mobile01',
                    'source_url': search_url,
                    'posts': posts,
                    'data_source': '✅ Mobile01真實數據' if posts else '❌ Mobile01無數據'
                }
            
        except Exception as e:
            logger.error(f"Mobile01爬取錯誤: {e}")
        
        return {'success': False, 'platform': 'Mobile01', 'posts': []}
    
    def _crawl_bahamut(self, candidate_name: str) -> Dict:
        """爬取巴哈姆特討論"""
        try:
            search_url = f"https://forum.gamer.com.tw/search.php?q={candidate_name}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = self._extract_general_posts(soup, candidate_name, 'Bahamut')
                
                return {
                    'success': len(posts) > 0,
                    'platform': 'Bahamut',
                    'source_url': search_url,
                    'posts': posts,
                    'data_source': '✅ 巴哈姆特真實數據' if posts else '❌ 巴哈姆特無數據'
                }
            
        except Exception as e:
            logger.error(f"巴哈姆特爬取錯誤: {e}")
        
        return {'success': False, 'platform': 'Bahamut', 'posts': []}
    
    def _extract_ptt_posts(self, soup, candidate_name: str) -> List[Dict]:
        """提取PTT文章"""
        posts = []
        try:
            # 查找文章元素
            articles = soup.find_all(['div', 'tr'], class_=['r-ent', 'post-item'])
            
            for article in articles:
                title_elem = article.find('a') or article.find(['h3', 'h4'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if candidate_name in title:
                        posts.append({
                            'title': title,
                            'url': title_elem.get('href', ''),
                            'platform': 'PTT',
                            'sentiment': self._analyze_sentiment(title),
                            'timestamp': datetime.now().isoformat()
                        })
        
        except Exception as e:
            logger.error(f"PTT文章提取錯誤: {e}")
        
        return posts
    
    def _extract_dcard_posts(self, soup, candidate_name: str) -> List[Dict]:
        """提取Dcard文章"""
        posts = []
        try:
            # Dcard可能的文章元素
            articles = soup.find_all(['article', 'div'], class_=['PostEntry', 'post-item'])
            
            for article in articles:
                title_elem = article.find(['h1', 'h2', 'h3', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if candidate_name in title:
                        posts.append({
                            'title': title,
                            'url': title_elem.get('href', ''),
                            'platform': 'Dcard',
                            'sentiment': self._analyze_sentiment(title),
                            'timestamp': datetime.now().isoformat()
                        })
        
        except Exception as e:
            logger.error(f"Dcard文章提取錯誤: {e}")
        
        return posts
    
    def _extract_news_articles(self, soup, candidate_name: str, platform: str) -> List[Dict]:
        """提取新聞文章"""
        articles = []
        try:
            # 通用新聞元素查找
            news_items = soup.find_all(['article', 'div', 'li'], class_=['news-item', 'article', 'story'])
            
            for item in news_items:
                title_elem = item.find(['h1', 'h2', 'h3', 'h4', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if candidate_name in title:
                        articles.append({
                            'title': title,
                            'url': title_elem.get('href', ''),
                            'platform': platform,
                            'sentiment': self._analyze_sentiment(title),
                            'timestamp': datetime.now().isoformat()
                        })
        
        except Exception as e:
            logger.error(f"{platform}新聞提取錯誤: {e}")
        
        return articles
    
    def _extract_general_posts(self, soup, candidate_name: str, platform: str) -> List[Dict]:
        """通用文章提取"""
        posts = []
        try:
            # 通用元素查找
            items = soup.find_all(['div', 'li', 'tr'], class_=['post', 'topic', 'thread', 'item'])
            
            for item in items:
                title_elem = item.find(['a', 'h1', 'h2', 'h3', 'h4'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if candidate_name in title:
                        posts.append({
                            'title': title,
                            'url': title_elem.get('href', ''),
                            'platform': platform,
                            'sentiment': self._analyze_sentiment(title),
                            'timestamp': datetime.now().isoformat()
                        })
        
        except Exception as e:
            logger.error(f"{platform}文章提取錯誤: {e}")
        
        return posts
    
    def _parse_ptt_api_data(self, data) -> List[Dict]:
        """解析PTT API數據"""
        posts = []
        try:
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'title' in item:
                        posts.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'platform': 'PTT API',
                            'sentiment': self._analyze_sentiment(item.get('title', '')),
                            'timestamp': item.get('date', datetime.now().isoformat())
                        })
        except Exception as e:
            logger.error(f"PTT API數據解析錯誤: {e}")
        
        return posts
    
    def _analyze_sentiment(self, text: str) -> str:
        """分析文本情緒"""
        pos_score = sum(1 for keyword in self.positive_keywords if keyword in text)
        neg_score = sum(1 for keyword in self.negative_keywords if keyword in text)
        
        if pos_score > neg_score:
            return 'positive'
        elif neg_score > pos_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _generate_summary(self, platforms: Dict) -> Dict:
        """生成總結"""
        total_posts = 0
        successful_platforms = 0
        all_posts = []
        
        for platform, result in platforms.items():
            if result.get('success', False):
                successful_platforms += 1
                posts = result.get('posts', [])
                total_posts += len(posts)
                all_posts.extend(posts)
        
        # 情緒分析
        positive_count = sum(1 for post in all_posts if post.get('sentiment') == 'positive')
        negative_count = sum(1 for post in all_posts if post.get('sentiment') == 'negative')
        neutral_count = sum(1 for post in all_posts if post.get('sentiment') == 'neutral')
        
        return {
            'total_platforms': len(platforms),
            'successful_platforms': successful_platforms,
            'total_posts': total_posts,
            'sentiment_analysis': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count,
                'positive_ratio': positive_count / total_posts if total_posts > 0 else 0
            },
            'data_quality': 'high' if successful_platforms >= 3 else 'medium' if successful_platforms >= 2 else 'low',
            'is_real_data': total_posts > 0
        }

if __name__ == "__main__":
    # 測試多平台爬蟲
    crawler = MultiPlatformCrawler()
    
    candidate = "羅智強"
    print(f"開始多平台爬取: {candidate}")
    
    result = crawler.crawl_all_platforms(candidate)
    
    print(f"\n爬取總結:")
    summary = result['summary']
    print(f"成功平台: {summary['successful_platforms']}/{summary['total_platforms']}")
    print(f"總文章數: {summary['total_posts']}")
    print(f"數據品質: {summary['data_quality']}")
    print(f"真實數據: {'是' if summary['is_real_data'] else '否'}")
    
    # 顯示各平台結果
    for platform, data in result['platforms'].items():
        status = "✅" if data.get('success', False) else "❌"
        post_count = len(data.get('posts', []))
        print(f"{status} {platform}: {post_count} 篇文章")
    
    # 保存結果
    with open('multi_platform_crawl_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細結果已保存到: multi_platform_crawl_result.json")
