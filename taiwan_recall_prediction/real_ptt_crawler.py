#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真實PTT數據爬蟲
Real PTT Data Crawler

專門抓取真實的PTT討論數據，不使用任何模擬數據
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

class RealPTTCrawler:
    """真實PTT數據爬蟲類"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
        # 情緒分析關鍵字
        self.positive_keywords = ['支持', '讚', '好', '棒', '優秀', '加油', '推', '贊成', '同意', '肯定', '厲害', '強']
        self.negative_keywords = ['反對', '爛', '差', '糟', '討厭', '垃圾', '失望', '不滿', '批評', '噓', '廢', '爛透']
    
    def crawl_real_ptt_data(self, candidate_name: str) -> Dict:
        """爬取真實PTT數據的主要方法"""
        logger.info(f"開始爬取真實PTT數據: {candidate_name}")
        
        try:
            # 方法1: 直接爬取八卦板最新文章
            gossiping_posts = self._crawl_gossiping_board(candidate_name)
            
            # 方法2: 爬取政黑板
            hatepolitics_posts = self._crawl_hatepolitics_board(candidate_name)
            
            # 方法3: 爬取政治板
            politics_posts = self._crawl_politics_board(candidate_name)
            
            # 合併所有真實數據
            all_posts = gossiping_posts + hatepolitics_posts + politics_posts
            
            if all_posts:
                analysis_result = self._analyze_real_posts(all_posts, candidate_name)
                analysis_result['data_source'] = '✅ 真實PTT爬蟲數據 (Real PTT Crawler Data)'
                analysis_result['is_simulated'] = False
                analysis_result['crawl_timestamp'] = datetime.now().isoformat()
                return analysis_result
            else:
                return {
                    'error': '無法獲取真實PTT數據',
                    'reason': '所有爬取方法都失敗',
                    'data_source': '❌ PTT爬蟲失敗 (PTT Crawler Failed)',
                    'is_simulated': False,
                    'post_count': 0
                }
                
        except Exception as e:
            logger.error(f"PTT爬蟲錯誤: {e}")
            return {
                'error': str(e),
                'data_source': '❌ PTT爬蟲錯誤 (PTT Crawler Error)',
                'is_simulated': False,
                'post_count': 0
            }
    
    def _crawl_gossiping_board(self, candidate_name: str) -> List[Dict]:
        """爬取八卦板真實數據"""
        posts = []
        try:
            # 先處理年齡驗證
            self._handle_age_verification()
            
            # 爬取八卦板首頁
            board_url = "https://www.ptt.cc/bbs/Gossiping/index.html"
            response = self._safe_get(board_url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找文章列表
                articles = soup.find_all('div', class_='r-ent')
                
                for article in articles:
                    post_data = self._extract_post_data(article, candidate_name, 'Gossiping')
                    if post_data:
                        posts.append(post_data)
                
                # 如果首頁沒找到，嘗試翻頁
                if len(posts) < 3:
                    posts.extend(self._crawl_previous_pages(soup, candidate_name, 'Gossiping', max_pages=3))
            
        except Exception as e:
            logger.error(f"八卦板爬取錯誤: {e}")
        
        return posts
    
    def _crawl_hatepolitics_board(self, candidate_name: str) -> List[Dict]:
        """爬取政黑板真實數據"""
        posts = []
        try:
            board_url = "https://www.ptt.cc/bbs/HatePolitics/index.html"
            response = self._safe_get(board_url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('div', class_='r-ent')
                
                for article in articles:
                    post_data = self._extract_post_data(article, candidate_name, 'HatePolitics')
                    if post_data:
                        posts.append(post_data)
                
                # 嘗試翻頁
                if len(posts) < 2:
                    posts.extend(self._crawl_previous_pages(soup, candidate_name, 'HatePolitics', max_pages=2))
            
        except Exception as e:
            logger.error(f"政黑板爬取錯誤: {e}")
        
        return posts
    
    def _crawl_politics_board(self, candidate_name: str) -> List[Dict]:
        """爬取政治板真實數據"""
        posts = []
        try:
            board_url = "https://www.ptt.cc/bbs/Politics/index.html"
            response = self._safe_get(board_url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('div', class_='r-ent')
                
                for article in articles:
                    post_data = self._extract_post_data(article, candidate_name, 'Politics')
                    if post_data:
                        posts.append(post_data)
            
        except Exception as e:
            logger.error(f"政治板爬取錯誤: {e}")
        
        return posts
    
    def _handle_age_verification(self):
        """處理PTT年齡驗證"""
        try:
            # 訪問年齡驗證頁面
            over18_url = "https://www.ptt.cc/ask/over18"
            response = self.session.get(over18_url, timeout=10)
            
            if response.status_code == 200 and "over18" in response.text:
                # 提交年齡驗證
                verify_data = {
                    'from': '/bbs/Gossiping/index.html',
                    'yes': 'yes'
                }
                self.session.post(over18_url, data=verify_data, timeout=10)
                logger.info("PTT年齡驗證完成")
                
        except Exception as e:
            logger.warning(f"年齡驗證失敗: {e}")
    
    def _safe_get(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        """安全的GET請求"""
        try:
            response = self.session.get(url, timeout=timeout)
            time.sleep(1)  # 避免請求過快
            return response
        except Exception as e:
            logger.error(f"請求失敗 {url}: {e}")
            return None
    
    def _extract_post_data(self, article_element, candidate_name: str, board: str) -> Optional[Dict]:
        """從文章元素中提取數據"""
        try:
            # 提取標題和連結
            title_elem = article_element.find('a')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            post_url = title_elem.get('href', '')
            
            # 檢查是否包含候選人名字
            if candidate_name not in title:
                return None
            
            # 提取作者
            author_elem = article_element.find('div', class_='author')
            author = author_elem.get_text(strip=True) if author_elem else 'unknown'
            
            # 提取推文數
            nrec_elem = article_element.find('div', class_='nrec')
            nrec_text = nrec_elem.get_text(strip=True) if nrec_elem else '0'
            
            # 解析推文數
            if nrec_text == '爆':
                comments = 100
            elif nrec_text.startswith('X'):
                comments = -10  # 噓文
            elif nrec_text.isdigit():
                comments = int(nrec_text)
            else:
                comments = 0
            
            # 提取日期
            date_elem = article_element.find('div', class_='date')
            date_text = date_elem.get_text(strip=True) if date_elem else ''
            
            # 分析情緒
            sentiment = self._analyze_title_sentiment(title)
            
            return {
                'title': title,
                'author': author,
                'board': board,
                'url': f"https://www.ptt.cc{post_url}" if post_url.startswith('/') else post_url,
                'comments': comments,
                'date': date_text,
                'sentiment': sentiment,
                'is_real': True
            }
            
        except Exception as e:
            logger.error(f"文章數據提取錯誤: {e}")
            return None
    
    def _crawl_previous_pages(self, current_soup, candidate_name: str, board: str, max_pages: int = 3) -> List[Dict]:
        """爬取前幾頁的文章"""
        posts = []
        try:
            # 查找上一頁連結
            prev_link = current_soup.find('a', string='‹ 上頁')
            
            for page in range(max_pages):
                if not prev_link or not prev_link.get('href'):
                    break
                
                prev_url = f"https://www.ptt.cc{prev_link['href']}"
                response = self._safe_get(prev_url)
                
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    articles = soup.find_all('div', class_='r-ent')
                    
                    for article in articles:
                        post_data = self._extract_post_data(article, candidate_name, board)
                        if post_data:
                            posts.append(post_data)
                    
                    # 更新上一頁連結
                    prev_link = soup.find('a', string='‹ 上頁')
                else:
                    break
                    
        except Exception as e:
            logger.error(f"翻頁爬取錯誤: {e}")
        
        return posts
    
    def _analyze_title_sentiment(self, title: str) -> str:
        """分析標題情緒"""
        title_lower = title.lower()
        
        pos_score = sum(1 for keyword in self.positive_keywords if keyword in title)
        neg_score = sum(1 for keyword in self.negative_keywords if keyword in title)
        
        # 特殊規則
        if '罷免' in title and any(word in title for word in ['支持', '贊成', '同意']):
            return 'negative'  # 支持罷免 = 對候選人負面
        elif '罷免' in title and any(word in title for word in ['反對', '不同意']):
            return 'positive'  # 反對罷免 = 對候選人正面
        
        if pos_score > neg_score:
            return 'positive'
        elif neg_score > pos_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_real_posts(self, posts: List[Dict], candidate_name: str) -> Dict:
        """分析真實文章數據"""
        if not posts:
            return {
                'post_count': 0,
                'positive_posts': 0,
                'negative_posts': 0,
                'neutral_posts': 0,
                'positive_ratio': 0,
                'hot_posts': []
            }
        
        positive_count = sum(1 for post in posts if post['sentiment'] == 'positive')
        negative_count = sum(1 for post in posts if post['sentiment'] == 'negative')
        neutral_count = sum(1 for post in posts if post['sentiment'] == 'neutral')
        
        total_posts = len(posts)
        
        # 按推文數排序，取前5篇作為熱門文章
        hot_posts = sorted(posts, key=lambda x: x['comments'], reverse=True)[:5]
        
        return {
            'post_count': total_posts,
            'positive_posts': positive_count,
            'negative_posts': negative_count,
            'neutral_posts': neutral_count,
            'positive_ratio': positive_count / total_posts if total_posts > 0 else 0,
            'negative_ratio': negative_count / total_posts if total_posts > 0 else 0,
            'neutral_ratio': neutral_count / total_posts if total_posts > 0 else 0,
            'hot_posts': hot_posts,
            'boards_crawled': list(set([post['board'] for post in posts])),
            'total_comments': sum(post['comments'] for post in posts),
            'avg_comments': sum(post['comments'] for post in posts) / total_posts if total_posts > 0 else 0
        }

if __name__ == "__main__":
    # 測試真實PTT爬蟲
    crawler = RealPTTCrawler()
    
    candidate = "羅智強"
    print(f"開始爬取 {candidate} 的真實PTT討論...")
    
    result = crawler.crawl_real_ptt_data(candidate)
    
    print(f"\n爬取結果:")
    print(f"數據來源: {result.get('data_source', 'Unknown')}")
    print(f"文章數量: {result.get('post_count', 0)}")
    
    if result.get('hot_posts'):
        print(f"\n熱門討論:")
        for i, post in enumerate(result['hot_posts'][:3], 1):
            print(f"{i}. {post['title']}")
            print(f"   作者: {post['author']} | 看板: {post['board']} | 推文: {post['comments']}")
    
    # 保存結果
    with open('real_ptt_crawl_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n結果已保存到: real_ptt_crawl_result.json")
