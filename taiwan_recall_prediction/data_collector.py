#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣罷免預測 - 數據收集模組
整合多平台API和政府數據源
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """統一數據收集器"""
    
    def __init__(self):
        """初始化數據收集器"""
        self.config = self.load_config()
        self.session = requests.Session()
        
    def load_config(self) -> Dict:
        """載入API配置"""
        config_file = 'config/api_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 創建默認配置
            default_config = {
                "facebook": {
                    "access_token": "YOUR_FACEBOOK_ACCESS_TOKEN",
                    "app_id": "YOUR_APP_ID",
                    "app_secret": "YOUR_APP_SECRET"
                },
                "instagram": {
                    "access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN",
                    "client_id": "YOUR_CLIENT_ID"
                },
                "youtube": {
                    "api_key": "YOUR_YOUTUBE_API_KEY"
                },
                "government": {
                    "labor_api": "https://data.gov.tw/api/v1/rest/datastore/",
                    "statistics_api": "https://statdb.dgbas.gov.tw/pxweb/api/v1/",
                    "interior_api": "https://data.moi.gov.tw/api/v1/"
                }
            }
            
            # 創建配置目錄
            os.makedirs('config', exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            logger.warning(f"已創建默認配置文件: {config_file}")
            logger.warning("請填入正確的API密鑰後重新運行")
            return default_config

    def collect_facebook_data(self, keywords: List[str], days: int = 7) -> pd.DataFrame:
        """收集Facebook數據"""
        logger.info("開始收集Facebook數據...")
        
        try:
            access_token = self.config['facebook']['access_token']
            if access_token == "YOUR_FACEBOOK_ACCESS_TOKEN":
                logger.warning("Facebook API未配置，返回模擬數據")
                return self.generate_mock_facebook_data(keywords, days)
            
            # Facebook Graph API調用
            base_url = "https://graph.facebook.com/v18.0"
            
            all_data = []
            for keyword in keywords:
                # 搜索公開貼文
                search_url = f"{base_url}/search"
                params = {
                    'q': keyword,
                    'type': 'post',
                    'access_token': access_token,
                    'fields': 'id,message,created_time,likes.summary(true),comments.summary(true),shares',
                    'limit': 100
                }
                
                response = self.session.get(search_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    for post in data.get('data', []):
                        all_data.append({
                            'platform': 'Facebook',
                            'keyword': keyword,
                            'post_id': post.get('id'),
                            'content': post.get('message', ''),
                            'created_time': post.get('created_time'),
                            'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                            'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                            'shares': post.get('shares', {}).get('count', 0)
                        })
                
                time.sleep(1)  # API限制
            
            return pd.DataFrame(all_data)
            
        except Exception as e:
            logger.error(f"Facebook數據收集失敗: {e}")
            return self.generate_mock_facebook_data(keywords, days)

    def collect_instagram_data(self, hashtags: List[str], days: int = 7) -> pd.DataFrame:
        """收集Instagram數據"""
        logger.info("開始收集Instagram數據...")
        
        try:
            access_token = self.config['instagram']['access_token']
            if access_token == "YOUR_INSTAGRAM_ACCESS_TOKEN":
                logger.warning("Instagram API未配置，返回模擬數據")
                return self.generate_mock_instagram_data(hashtags, days)
            
            # Instagram Basic Display API調用
            base_url = "https://graph.instagram.com"
            
            all_data = []
            for hashtag in hashtags:
                # 搜索標籤
                search_url = f"{base_url}/ig_hashtag_search"
                params = {
                    'user_id': 'USER_ID',  # 需要用戶授權
                    'q': hashtag,
                    'access_token': access_token
                }
                
                response = self.session.get(search_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    # 處理Instagram數據...
                    
                time.sleep(1)  # API限制
            
            return pd.DataFrame(all_data)
            
        except Exception as e:
            logger.error(f"Instagram數據收集失敗: {e}")
            return self.generate_mock_instagram_data(hashtags, days)

    def collect_youtube_data(self, keywords: List[str], days: int = 7) -> pd.DataFrame:
        """收集YouTube數據"""
        logger.info("開始收集YouTube數據...")
        
        try:
            api_key = self.config['youtube']['api_key']
            if api_key == "YOUR_YOUTUBE_API_KEY":
                logger.warning("YouTube API未配置，返回模擬數據")
                return self.generate_mock_youtube_data(keywords, days)
            
            # YouTube Data API v3調用
            base_url = "https://www.googleapis.com/youtube/v3"
            
            all_data = []
            for keyword in keywords:
                # 搜索影片
                search_url = f"{base_url}/search"
                params = {
                    'part': 'snippet',
                    'q': keyword,
                    'type': 'video',
                    'key': api_key,
                    'maxResults': 50,
                    'publishedAfter': (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
                }
                
                response = self.session.get(search_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        video_id = item['id']['videoId']
                        
                        # 獲取影片統計
                        stats_url = f"{base_url}/videos"
                        stats_params = {
                            'part': 'statistics',
                            'id': video_id,
                            'key': api_key
                        }
                        
                        stats_response = self.session.get(stats_url, params=stats_params)
                        stats_data = stats_response.json()
                        
                        statistics = stats_data.get('items', [{}])[0].get('statistics', {})
                        
                        all_data.append({
                            'platform': 'YouTube',
                            'keyword': keyword,
                            'video_id': video_id,
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'published_at': item['snippet']['publishedAt'],
                            'channel_title': item['snippet']['channelTitle'],
                            'view_count': int(statistics.get('viewCount', 0)),
                            'like_count': int(statistics.get('likeCount', 0)),
                            'comment_count': int(statistics.get('commentCount', 0))
                        })
                        
                        time.sleep(0.1)  # API限制
                
                time.sleep(1)  # API限制
            
            return pd.DataFrame(all_data)
            
        except Exception as e:
            logger.error(f"YouTube數據收集失敗: {e}")
            return self.generate_mock_youtube_data(keywords, days)

    def collect_government_data(self) -> Dict[str, pd.DataFrame]:
        """收集政府公開數據"""
        logger.info("開始收集政府數據...")
        
        government_data = {}
        
        try:
            # 勞動部數據 - 失業率
            unemployment_data = self.get_unemployment_data()
            government_data['unemployment'] = unemployment_data
            
            # 主計總處數據 - 物價指數
            price_data = self.get_price_index_data()
            government_data['price_index'] = price_data
            
            # 內政部數據 - 人口統計
            population_data = self.get_population_data()
            government_data['population'] = population_data
            
        except Exception as e:
            logger.error(f"政府數據收集失敗: {e}")
            government_data = self.generate_mock_government_data()
        
        return government_data

    def get_unemployment_data(self) -> pd.DataFrame:
        """獲取失業率數據"""
        # 模擬政府API調用
        mock_data = {
            'year': [2023, 2023, 2023, 2023],
            'month': [9, 10, 11, 12],
            'unemployment_rate': [3.4, 3.3, 3.2, 3.1],
            'youth_unemployment': [7.8, 7.6, 7.4, 7.2],
            'region': ['全國', '全國', '全國', '全國']
        }
        return pd.DataFrame(mock_data)

    def get_price_index_data(self) -> pd.DataFrame:
        """獲取物價指數數據"""
        mock_data = {
            'year': [2023, 2023, 2023, 2023],
            'month': [9, 10, 11, 12],
            'cpi': [105.2, 105.8, 106.1, 106.5],
            'housing_price_index': [112.3, 113.1, 113.8, 114.2]
        }
        return pd.DataFrame(mock_data)

    def get_population_data(self) -> pd.DataFrame:
        """獲取人口統計數據"""
        mock_data = {
            'region': ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市'],
            'population': [2602418, 4030954, 2268807, 2814327, 1873794, 2744691],
            'age_18_35': [0.28, 0.31, 0.33, 0.32, 0.29, 0.30],
            'age_36_55': [0.35, 0.34, 0.36, 0.35, 0.34, 0.33],
            'age_56_plus': [0.37, 0.35, 0.31, 0.33, 0.37, 0.37]
        }
        return pd.DataFrame(mock_data)

    def generate_mock_data(self, keywords: List[str], count: int = 10) -> List[Dict]:
        """生成通用模擬數據"""
        import random
        from datetime import datetime, timedelta

        mock_data = []
        platforms = ['Facebook', 'Instagram', 'YouTube', 'PTT']
        sentiments = ['positive', 'negative', 'neutral']

        for i in range(count):
            mock_data.append({
                'platform': random.choice(platforms),
                'content': f"關於{random.choice(keywords)}的討論內容 {i+1}",
                'sentiment': random.choice(sentiments),
                'sentiment_score': random.uniform(-1, 1),
                'likes': random.randint(0, 1000),
                'shares': random.randint(0, 100),
                'comments': random.randint(0, 200),
                'created_at': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                'keyword': random.choice(keywords)
            })

        return mock_data

    def generate_mock_facebook_data(self, keywords: List[str], days: int) -> pd.DataFrame:
        """生成模擬Facebook數據"""
        import random
        
        mock_data = []
        for keyword in keywords:
            for i in range(random.randint(10, 30)):
                mock_data.append({
                    'platform': 'Facebook',
                    'keyword': keyword,
                    'post_id': f'fb_{keyword}_{i}',
                    'content': f'關於{keyword}的討論內容...',
                    'created_time': (datetime.now() - timedelta(days=random.randint(0, days))).isoformat(),
                    'likes': random.randint(0, 500),
                    'comments': random.randint(0, 100),
                    'shares': random.randint(0, 50)
                })
        
        return pd.DataFrame(mock_data)

    def generate_mock_instagram_data(self, hashtags: List[str], days: int) -> pd.DataFrame:
        """生成模擬Instagram數據"""
        import random
        
        mock_data = []
        for hashtag in hashtags:
            for i in range(random.randint(5, 20)):
                mock_data.append({
                    'platform': 'Instagram',
                    'hashtag': hashtag,
                    'post_id': f'ig_{hashtag}_{i}',
                    'caption': f'#{hashtag} 相關內容...',
                    'created_time': (datetime.now() - timedelta(days=random.randint(0, days))).isoformat(),
                    'likes': random.randint(0, 1000),
                    'comments': random.randint(0, 200)
                })
        
        return pd.DataFrame(mock_data)

    def generate_mock_youtube_data(self, keywords: List[str], days: int) -> pd.DataFrame:
        """生成模擬YouTube數據"""
        import random
        
        mock_data = []
        for keyword in keywords:
            for i in range(random.randint(3, 15)):
                mock_data.append({
                    'platform': 'YouTube',
                    'keyword': keyword,
                    'video_id': f'yt_{keyword}_{i}',
                    'title': f'{keyword}相關影片標題',
                    'description': f'關於{keyword}的影片描述...',
                    'published_at': (datetime.now() - timedelta(days=random.randint(0, days))).isoformat(),
                    'channel_title': f'頻道_{i}',
                    'view_count': random.randint(100, 50000),
                    'like_count': random.randint(10, 2000),
                    'comment_count': random.randint(5, 500)
                })
        
        return pd.DataFrame(mock_data)

    def generate_mock_government_data(self) -> Dict[str, pd.DataFrame]:
        """生成模擬政府數據"""
        return {
            'unemployment': self.get_unemployment_data(),
            'price_index': self.get_price_index_data(),
            'population': self.get_population_data()
        }

    def save_collected_data(self, data: Dict[str, pd.DataFrame], timestamp: str = None):
        """保存收集的數據"""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 創建數據目錄
        data_dir = f'data/collected_{timestamp}'
        os.makedirs(data_dir, exist_ok=True)
        
        for data_type, df in data.items():
            if not df.empty:
                file_path = f'{data_dir}/{data_type}.csv'
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"已保存 {data_type} 數據到 {file_path}")

def main():
    """主要執行函數"""
    collector = DataCollector()
    
    # 定義收集參數
    keywords = ['罷免', '投票', '政治', '選舉']
    hashtags = ['台灣政治', '投票', '罷免']
    
    # 收集所有數據
    all_data = {}
    
    # 社群媒體數據
    all_data['facebook'] = collector.collect_facebook_data(keywords)
    all_data['instagram'] = collector.collect_instagram_data(hashtags)
    all_data['youtube'] = collector.collect_youtube_data(keywords)
    
    # 政府數據
    government_data = collector.collect_government_data()
    all_data.update(government_data)
    
    # 保存數據
    collector.save_collected_data(all_data)
    
    logger.info("數據收集完成！")

if __name__ == "__main__":
    main()
