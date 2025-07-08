#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTT 爬蟲 - 收集罷免相關討論
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup

class PTTCrawler:
    def __init__(self):
        self.base_url = "https://www.ptt.cc"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_board_articles(self, board, pages=5, keywords=['罷免', '罷韓', '罷王']):
        """
        爬取指定看板的文章
        """
        articles = []
        
        # 先訪問看板首頁獲取最新頁面
        board_url = f"{self.base_url}/bbs/{board}/index.html"
        
        try:
            # 處理18歲確認頁面
            resp = self.session.get(board_url)
            if 'over18' in resp.url:
                self.session.post(f"{self.base_url}/ask/over18", 
                                data={'from': f'/bbs/{board}/index.html', 'yes': 'yes'})
                resp = self.session.get(board_url)
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 獲取當前頁面編號
            prev_link = soup.find('a', string='‹ 上頁')
            if prev_link:
                current_page = int(prev_link['href'].split('index')[1].split('.html')[0]) + 1
            else:
                current_page = 1
                
            print(f"開始爬取 {board} 看板，從第 {current_page} 頁開始...")
            
            for page in range(pages):
                page_num = current_page - page
                if page_num < 1:
                    break
                    
                page_url = f"{self.base_url}/bbs/{board}/index{page_num}.html"
                page_articles = self._parse_board_page(page_url, keywords)
                articles.extend(page_articles)
                
                print(f"已爬取第 {page_num} 頁，找到 {len(page_articles)} 篇相關文章")
                time.sleep(1)  # 避免請求過快
                
        except Exception as e:
            print(f"爬取 {board} 看板時發生錯誤: {e}")
            
        return articles
    
    def _parse_board_page(self, page_url, keywords):
        """
        解析看板頁面，提取文章連結
        """
        articles = []
        
        try:
            resp = self.session.get(page_url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 找到所有文章
            article_divs = soup.find_all('div', class_='r-ent')
            
            for div in article_divs:
                try:
                    # 獲取文章標題
                    title_div = div.find('div', class_='title')
                    if not title_div or not title_div.find('a'):
                        continue
                        
                    title = title_div.find('a').text.strip()
                    link = title_div.find('a')['href']
                    
                    # 檢查是否包含關鍵詞
                    if any(keyword in title for keyword in keywords):
                        # 獲取作者和日期
                        author_div = div.find('div', class_='author')
                        date_div = div.find('div', class_='date')
                        
                        author = author_div.text.strip() if author_div else ""
                        date = date_div.text.strip() if date_div else ""
                        
                        # 獲取文章內容
                        article_content = self._get_article_content(link)
                        
                        articles.append({
                            'title': title,
                            'author': author,
                            'date': date,
                            'link': f"{self.base_url}{link}",
                            'content': article_content['content'],
                            'comments': article_content['comments'],
                            'source': 'PTT',
                            'board': link.split('/')[2] if '/' in link else '',
                            'crawl_time': datetime.now().isoformat()
                        })
                        
                        time.sleep(0.5)  # 避免請求過快
                        
                except Exception as e:
                    print(f"解析文章時發生錯誤: {e}")
                    continue
                    
        except Exception as e:
            print(f"解析頁面 {page_url} 時發生錯誤: {e}")
            
        return articles
    
    def _get_article_content(self, article_path):
        """
        獲取文章詳細內容
        """
        try:
            article_url = f"{self.base_url}{article_path}"
            resp = self.session.get(article_url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 獲取文章內容
            main_content = soup.find('div', id='main-content')
            if not main_content:
                return {'content': '', 'comments': []}
            
            # 移除推文區域
            for span in main_content.find_all('span', class_='f2'):
                span.decompose()
            for div in main_content.find_all('div', class_='push'):
                div.decompose()
                
            content = main_content.get_text().strip()
            
            # 獲取推文
            comments = []
            push_divs = soup.find_all('div', class_='push')
            for push_div in push_divs:
                try:
                    push_tag = push_div.find('span', class_='push-tag')
                    push_userid = push_div.find('span', class_='push-userid')
                    push_content = push_div.find('span', class_='push-content')
                    
                    if push_tag and push_userid and push_content:
                        comments.append({
                            'type': push_tag.text.strip(),
                            'user': push_userid.text.strip(),
                            'content': push_content.text.strip()
                        })
                except:
                    continue
            
            return {'content': content, 'comments': comments}
            
        except Exception as e:
            print(f"獲取文章內容時發生錯誤: {e}")
            return {'content': '', 'comments': []}

def main():
    """
    主要執行函數
    """
    crawler = PTTCrawler()
    
    # 要爬取的看板列表
    boards = ['Gossiping', 'HatePolitics', 'Politics']
    
    all_articles = []
    
    for board in boards:
        print(f"\n開始爬取 {board} 看板...")
        articles = crawler.get_board_articles(board, pages=3)
        all_articles.extend(articles)
        print(f"{board} 看板爬取完成，共 {len(articles)} 篇文章")
    
    # 儲存資料
    if all_articles:
        df = pd.DataFrame(all_articles)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ptt_data_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n資料已儲存至 {filename}")
        print(f"總共收集了 {len(all_articles)} 篇文章")
        
        # 顯示基本統計
        print("\n基本統計:")
        print(f"- 不同看板數量: {df['board'].nunique()}")
        print(f"- 不同作者數量: {df['author'].nunique()}")
        print(f"- 平均文章長度: {df['content'].str.len().mean():.0f} 字")
    else:
        print("沒有收集到任何資料")

if __name__ == "__main__":
    main()
