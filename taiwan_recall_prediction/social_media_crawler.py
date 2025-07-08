#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台社群媒體數據收集器
整合Facebook、Instagram、Twitter、YouTube等平台
"""

import os
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Any
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaCrawler:
    """多平台社群媒體爬蟲"""
    
    def __init__(self):
        self.recall_keywords = [
            '罷免', '罷韓', '罷王', '罷陳', '罷免投票', '不同意票', '同意票',
            '罷免案', '罷免連署', '罷免門檻', '罷免成功', '罷免失敗',
            '立委罷免', '議員罷免', '市長罷免', '縣長罷免'
        ]
        
        # API配置 (需要在環境變數中設置)
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.facebook_access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        self.results = []
        
    def search_twitter(self, max_results: int = 100) -> List[Dict]:
        """搜索Twitter數據"""
        if not self.twitter_bearer_token:
            logger.warning("Twitter API token not found, skipping Twitter search")
            return []
            
        try:
            import tweepy
            
            # 初始化Twitter API
            client = tweepy.Client(bearer_token=self.twitter_bearer_token)
            
            tweets_data = []
            
            for keyword in self.recall_keywords[:3]:  # 限制關鍵字數量避免API限制
                try:
                    # 搜索推文
                    tweets = client.search_recent_tweets(
                        query=f"{keyword} lang:zh",
                        max_results=min(max_results // len(self.recall_keywords[:3]), 100),
                        tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations']
                    )
                    
                    if tweets.data:
                        for tweet in tweets.data:
                            tweets_data.append({
                                'platform': 'Twitter',
                                'id': tweet.id,
                                'content': tweet.text,
                                'author_id': tweet.author_id,
                                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                                'metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                                'keyword': keyword,
                                'collected_at': datetime.now().isoformat()
                            })
                    
                    time.sleep(1)  # 避免API限制
                    
                except Exception as e:
                    logger.error(f"Error searching Twitter for keyword '{keyword}': {e}")
                    continue
                    
            logger.info(f"Collected {len(tweets_data)} tweets")
            return tweets_data
            
        except ImportError:
            logger.error("tweepy not installed, skipping Twitter search")
            return []
        except Exception as e:
            logger.error(f"Twitter search failed: {e}")
            return []
    
    def search_youtube(self, max_results: int = 50) -> List[Dict]:
        """搜索YouTube數據"""
        if not self.youtube_api_key:
            logger.warning("YouTube API key not found, skipping YouTube search")
            return []
            
        try:
            from googleapiclient.discovery import build
            
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            videos_data = []
            
            for keyword in self.recall_keywords[:2]:  # 限制關鍵字數量
                try:
                    # 搜索視頻
                    search_response = youtube.search().list(
                        q=keyword,
                        part='id,snippet',
                        maxResults=min(max_results // len(self.recall_keywords[:2]), 25),
                        type='video',
                        order='relevance',
                        regionCode='TW',
                        relevanceLanguage='zh'
                    ).execute()
                    
                    for item in search_response['items']:
                        video_id = item['id']['videoId']
                        snippet = item['snippet']
                        
                        # 獲取視頻統計數據
                        stats_response = youtube.videos().list(
                            part='statistics',
                            id=video_id
                        ).execute()
                        
                        stats = stats_response['items'][0]['statistics'] if stats_response['items'] else {}
                        
                        videos_data.append({
                            'platform': 'YouTube',
                            'id': video_id,
                            'title': snippet.get('title', ''),
                            'description': snippet.get('description', ''),
                            'content': f"{snippet.get('title', '')} {snippet.get('description', '')}",
                            'channel': snippet.get('channelTitle', ''),
                            'published_at': snippet.get('publishedAt', ''),
                            'metrics': {
                                'viewCount': stats.get('viewCount', 0),
                                'likeCount': stats.get('likeCount', 0),
                                'commentCount': stats.get('commentCount', 0)
                            },
                            'keyword': keyword,
                            'collected_at': datetime.now().isoformat()
                        })
                    
                    time.sleep(1)  # 避免API限制
                    
                except Exception as e:
                    logger.error(f"Error searching YouTube for keyword '{keyword}': {e}")
                    continue
                    
            logger.info(f"Collected {len(videos_data)} YouTube videos")
            return videos_data
            
        except ImportError:
            logger.error("google-api-python-client not installed, skipping YouTube search")
            return []
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []
    
    def search_facebook_public(self, max_results: int = 50) -> List[Dict]:
        """搜索Facebook公開內容 (使用Graph API)"""
        if not self.facebook_access_token:
            logger.warning("Facebook access token not found, skipping Facebook search")
            return []
            
        try:
            facebook_data = []
            
            # 注意：Facebook Graph API對搜索有很多限制
            # 這裡提供基本框架，實際使用需要適當的權限和配置
            
            for keyword in self.recall_keywords[:2]:
                try:
                    # Facebook Graph API搜索 (需要適當權限)
                    url = f"https://graph.facebook.com/v18.0/search"
                    params = {
                        'q': keyword,
                        'type': 'post',
                        'access_token': self.facebook_access_token,
                        'limit': min(max_results // len(self.recall_keywords[:2]), 25)
                    }
                    
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for post in data.get('data', []):
                            facebook_data.append({
                                'platform': 'Facebook',
                                'id': post.get('id', ''),
                                'content': post.get('message', ''),
                                'created_time': post.get('created_time', ''),
                                'keyword': keyword,
                                'collected_at': datetime.now().isoformat()
                            })
                    
                    time.sleep(1)  # 避免API限制
                    
                except Exception as e:
                    logger.error(f"Error searching Facebook for keyword '{keyword}': {e}")
                    continue
                    
            logger.info(f"Collected {len(facebook_data)} Facebook posts")
            return facebook_data
            
        except Exception as e:
            logger.error(f"Facebook search failed: {e}")
            return []
    
    def search_instagram_public(self, max_results: int = 50) -> List[Dict]:
        """搜索Instagram公開內容"""
        try:
            import instaloader
            
            L = instaloader.Instaloader()
            instagram_data = []
            
            for keyword in self.recall_keywords[:2]:
                try:
                    # 搜索hashtag
                    hashtag = instaloader.Hashtag.from_name(L.context, keyword.replace('#', ''))
                    
                    count = 0
                    for post in hashtag.get_posts():
                        if count >= max_results // len(self.recall_keywords[:2]):
                            break
                            
                        instagram_data.append({
                            'platform': 'Instagram',
                            'id': post.shortcode,
                            'content': post.caption if post.caption else '',
                            'author': post.owner_username,
                            'created_at': post.date.isoformat(),
                            'metrics': {
                                'likes': post.likes,
                                'comments': post.comments
                            },
                            'keyword': keyword,
                            'collected_at': datetime.now().isoformat()
                        })
                        
                        count += 1
                        time.sleep(2)  # 避免被限制
                        
                except Exception as e:
                    logger.error(f"Error searching Instagram for keyword '{keyword}': {e}")
                    continue
                    
            logger.info(f"Collected {len(instagram_data)} Instagram posts")
            return instagram_data
            
        except ImportError:
            logger.error("instaloader not installed, skipping Instagram search")
            return []
        except Exception as e:
            logger.error(f"Instagram search failed: {e}")
            return []
    
    def collect_all_platforms(self, max_results_per_platform: int = 100) -> pd.DataFrame:
        """收集所有平台數據"""
        logger.info("Starting multi-platform data collection...")
        
        all_data = []
        
        # 收集各平台數據
        platforms = [
            ('Twitter', self.search_twitter),
            ('YouTube', self.search_youtube),
            ('Facebook', self.search_facebook_public),
            ('Instagram', self.search_instagram_public)
        ]
        
        for platform_name, search_func in platforms:
            logger.info(f"Collecting data from {platform_name}...")
            try:
                platform_data = search_func(max_results_per_platform)
                all_data.extend(platform_data)
                logger.info(f"Successfully collected {len(platform_data)} items from {platform_name}")
            except Exception as e:
                logger.error(f"Failed to collect data from {platform_name}: {e}")
        
        # 轉換為DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            
            # 保存數據
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"social_media_data_{timestamp}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            logger.info(f"Collected total {len(df)} items from all platforms")
            logger.info(f"Data saved to {filename}")
            
            # 顯示平台分布
            platform_counts = df['platform'].value_counts()
            logger.info("Platform distribution:")
            for platform, count in platform_counts.items():
                logger.info(f"  {platform}: {count} items")
                
            return df
        else:
            logger.warning("No data collected from any platform")
            return pd.DataFrame()

def main():
    """主函數"""
    crawler = SocialMediaCrawler()
    
    # 收集數據
    df = crawler.collect_all_platforms(max_results_per_platform=50)
    
    if not df.empty:
        print(f"\n✅ 成功收集 {len(df)} 筆社群媒體數據")
        print("\n📊 平台分布:")
        print(df['platform'].value_counts())
        
        print("\n📝 數據樣本:")
        print(df[['platform', 'content']].head())
    else:
        print("❌ 未收集到任何數據")

if __name__ == "__main__":
    main()
