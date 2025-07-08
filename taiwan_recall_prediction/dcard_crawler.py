#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dcard 爬蟲 - 收集罷免相關討論
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import re

class DcardCrawler:
    def __init__(self):
        self.base_url = "https://www.dcard.tw"
        self.api_url = "https://www.dcard.tw/service/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.dcard.tw/'
        })
        
    def search_posts(self, keywords=['罷免', '罷韓', '罷王'], limit=100):
        """
        搜尋相關文章
        """
        all_posts = []
        
        for keyword in keywords:
            print(f"搜尋關鍵字: {keyword}")
            posts = self._search_by_keyword(keyword, limit//len(keywords))
            all_posts.extend(posts)
            time.sleep(2)  # 避免請求過快
            
        return all_posts
    
    def _search_by_keyword(self, keyword, limit=50):
        """
        根據關鍵字搜尋文章
        """
        posts = []
        
        try:
            # 使用搜尋API
            search_url = f"{self.api_url}/search/posts"
            params = {
                'query': keyword,
                'limit': min(limit, 30),  # API限制
                'offset': 0
            }
            
            resp = self.session.get(search_url, params=params)
            
            if resp.status_code == 200:
                data = resp.json()
                
                for post in data:
                    try:
                        # 獲取文章詳細內容
                        post_detail = self._get_post_detail(post['id'])
                        
                        if post_detail:
                            posts.append({
                                'id': post['id'],
                                'title': post.get('title', ''),
                                'content': post_detail.get('content', ''),
                                'excerpt': post.get('excerpt', ''),
                                'author': 'Anonymous',  # Dcard匿名
                                'forum': post.get('forumName', ''),
                                'like_count': post.get('likeCount', 0),
                                'comment_count': post.get('commentCount', 0),
                                'created_at': post.get('createdAt', ''),
                                'updated_at': post.get('updatedAt', ''),
                                'link': f"{self.base_url}/f/{post.get('forumAlias', 'all')}/p/{post['id']}",
                                'source': 'Dcard',
                                'keyword': keyword,
                                'crawl_time': datetime.now().isoformat()
                            })
                            
                        time.sleep(1)  # 避免請求過快
                        
                    except Exception as e:
                        print(f"處理文章 {post.get('id')} 時發生錯誤: {e}")
                        continue
                        
            else:
                print(f"搜尋 {keyword} 時發生錯誤，狀態碼: {resp.status_code}")
                
        except Exception as e:
            print(f"搜尋關鍵字 {keyword} 時發生錯誤: {e}")
            
        return posts
    
    def _get_post_detail(self, post_id):
        """
        獲取文章詳細內容
        """
        try:
            detail_url = f"{self.api_url}/posts/{post_id}"
            resp = self.session.get(detail_url)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"獲取文章 {post_id} 詳情失敗，狀態碼: {resp.status_code}")
                return None
                
        except Exception as e:
            print(f"獲取文章 {post_id} 詳情時發生錯誤: {e}")
            return None
    
    def get_forum_posts(self, forum_alias, limit=50):
        """
        獲取特定版面的文章
        """
        posts = []
        
        try:
            forum_url = f"{self.api_url}/forums/{forum_alias}/posts"
            params = {
                'limit': min(limit, 30),
                'offset': 0
            }
            
            resp = self.session.get(forum_url, params=params)
            
            if resp.status_code == 200:
                data = resp.json()
                
                for post in data:
                    # 檢查標題是否包含相關關鍵字
                    title = post.get('title', '').lower()
                    if any(keyword in title for keyword in ['罷免', '罷韓', '罷王', '政治', '選舉']):
                        try:
                            post_detail = self._get_post_detail(post['id'])
                            
                            if post_detail:
                                posts.append({
                                    'id': post['id'],
                                    'title': post.get('title', ''),
                                    'content': post_detail.get('content', ''),
                                    'excerpt': post.get('excerpt', ''),
                                    'author': 'Anonymous',
                                    'forum': post.get('forumName', ''),
                                    'like_count': post.get('likeCount', 0),
                                    'comment_count': post.get('commentCount', 0),
                                    'created_at': post.get('createdAt', ''),
                                    'updated_at': post.get('updatedAt', ''),
                                    'link': f"{self.base_url}/f/{forum_alias}/p/{post['id']}",
                                    'source': 'Dcard',
                                    'keyword': 'forum_crawl',
                                    'crawl_time': datetime.now().isoformat()
                                })
                                
                            time.sleep(1)
                            
                        except Exception as e:
                            print(f"處理版面文章 {post.get('id')} 時發生錯誤: {e}")
                            continue
                            
            else:
                print(f"獲取版面 {forum_alias} 文章失敗，狀態碼: {resp.status_code}")
                
        except Exception as e:
            print(f"獲取版面 {forum_alias} 文章時發生錯誤: {e}")
            
        return posts

def main():
    """
    主要執行函數
    """
    crawler = DcardCrawler()
    
    all_posts = []
    
    # 1. 關鍵字搜尋
    print("開始關鍵字搜尋...")
    search_posts = crawler.search_posts(limit=60)
    all_posts.extend(search_posts)
    print(f"關鍵字搜尋完成，共 {len(search_posts)} 篇文章")
    
    # 2. 特定版面爬取
    forums = ['talk', 'mood', 'relationship']  # 熱門版面
    
    for forum in forums:
        print(f"\n開始爬取 {forum} 版面...")
        forum_posts = crawler.get_forum_posts(forum, limit=30)
        all_posts.extend(forum_posts)
        print(f"{forum} 版面爬取完成，共 {len(forum_posts)} 篇相關文章")
        time.sleep(2)
    
    # 儲存資料
    if all_posts:
        df = pd.DataFrame(all_posts)
        # 去除重複文章
        df = df.drop_duplicates(subset=['id'])
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dcard_data_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n資料已儲存至 {filename}")
        print(f"總共收集了 {len(df)} 篇文章")
        
        # 顯示基本統計
        print("\n基本統計:")
        print(f"- 不同版面數量: {df['forum'].nunique()}")
        print(f"- 平均按讚數: {df['like_count'].mean():.1f}")
        print(f"- 平均留言數: {df['comment_count'].mean():.1f}")
        print(f"- 平均文章長度: {df['content'].str.len().mean():.0f} 字")
    else:
        print("沒有收集到任何資料")

if __name__ == "__main__":
    main()
