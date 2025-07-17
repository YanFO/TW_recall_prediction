#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲系統配置文件
Crawler System Configuration
"""

import os
from datetime import datetime

# 基本配置
BASE_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'request_delay': 1,  # 請求間隔（秒）
    'timeout': 10,
    'max_retries': 3
}

# 關鍵字配置
KEYWORDS = {
    'recall': ['罷免', '罷韓', '罷王', '罷柯', '罷免案', '投票', '連署'],
    'politics': ['政治', '選舉', '立委', '市長', '議員', '政黨'],
    'candidates': ['羅智強', '王鴻薇', '李彥秀', '徐巧芯', '賴士葆', '洪孟楷', '葉元之', '張智倫', '林德福', '廖先翔', '高虹安']
}

# PTT 配置
PTT_CONFIG = {
    'base_url': 'https://www.ptt.cc',
    'boards': ['Gossiping', 'HatePolitics', 'Politics', 'PublicIssue'],
    'pages_per_board': 5,
    'over18_confirm': True
}

# Dcard 配置
DCARD_CONFIG = {
    'base_url': 'https://www.dcard.tw',
    'api_base': 'https://www.dcard.tw/service/api/v2',
    'forums': ['politics', 'trending', 'boy-girl', 'whysoserious', 'talk'],
    'posts_per_forum': 50
}

# Mobile01 配置
MOBILE01_CONFIG = {
    'base_url': 'https://www.mobile01.com',
    'forums': {
        'politics': 376,  # 政治討論版
        'news': 1,        # 新聞討論版
        'life': 37        # 生活娛樂版
    },
    'pages_per_forum': 3
}

# Facebook 配置
FACEBOOK_CONFIG = {
    'graph_api_base': 'https://graph.facebook.com/v19.0',
    'access_token': os.getenv('FB_ACCESS_TOKEN', ''),  # 從環境變數讀取
    'pages': {
        'kmt': 'kmt.tw',
        'dpp': 'DemocraticProgressiveParty',
        'tpp': 'taiwanpeoplesparty'
    },
    'posts_limit': 25
}

# 資料庫配置
DATABASE_CONFIG = {
    'mongodb': {
        'host': 'localhost',
        'port': 27017,
        'database': 'recall_db',
        'collections': {
            'articles': 'recall_articles',
            'comments': 'recall_comments',
            'statistics': 'crawl_statistics'
        }
    },
    'sqlite': {
        'database': 'recall_data.db',
        'tables': {
            'articles': 'articles',
            'comments': 'comments',
            'statistics': 'statistics'
        }
    }
}

# 儲存配置
STORAGE_CONFIG = {
    'backup_enabled': True,
    'backup_formats': ['json', 'csv'],
    'backup_directory': 'backups',
    'max_backup_files': 10
}

# 日誌配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': f'crawler_{datetime.now().strftime("%Y%m%d")}.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# 情緒分析配置
SENTIMENT_CONFIG = {
    'positive_keywords': ['支持', '讚', '好', '棒', '優秀', '加油', '推', '贊成', '同意', '肯定', '厲害', '強'],
    'negative_keywords': ['反對', '爛', '差', '糟', '討厭', '垃圾', '失望', '不滿', '批評', '噓', '廢', '爛透'],
    'neutral_threshold': 0.1  # 情緒分數閾值
}

# 排程配置
SCHEDULE_CONFIG = {
    'enabled': False,
    'intervals': {
        'ptt': '*/30 * * * *',      # 每30分鐘
        'dcard': '0 */2 * * *',     # 每2小時
        'mobile01': '0 */4 * * *',  # 每4小時
        'facebook': '0 */6 * * *'   # 每6小時
    }
}

# API 限制配置
RATE_LIMITS = {
    'ptt': {
        'requests_per_minute': 30,
        'concurrent_requests': 3
    },
    'dcard': {
        'requests_per_minute': 60,
        'concurrent_requests': 5
    },
    'mobile01': {
        'requests_per_minute': 20,
        'concurrent_requests': 2
    },
    'facebook': {
        'requests_per_hour': 200,
        'concurrent_requests': 1
    }
}

# 輸出格式配置
OUTPUT_CONFIG = {
    'default_format': 'json',
    'include_metadata': True,
    'include_statistics': True,
    'compress_output': False
}

def get_config(section=None):
    """獲取配置"""
    if section:
        return globals().get(f'{section.upper()}_CONFIG', {})
    
    return {
        'base': BASE_CONFIG,
        'keywords': KEYWORDS,
        'ptt': PTT_CONFIG,
        'dcard': DCARD_CONFIG,
        'mobile01': MOBILE01_CONFIG,
        'facebook': FACEBOOK_CONFIG,
        'database': DATABASE_CONFIG,
        'storage': STORAGE_CONFIG,
        'logging': LOGGING_CONFIG,
        'sentiment': SENTIMENT_CONFIG,
        'schedule': SCHEDULE_CONFIG,
        'rate_limits': RATE_LIMITS,
        'output': OUTPUT_CONFIG
    }

def validate_config():
    """驗證配置"""
    errors = []
    
    # 檢查必要的環境變數
    if not FACEBOOK_CONFIG['access_token']:
        errors.append("Facebook access token not found in environment variables")
    
    # 檢查目錄是否存在
    backup_dir = STORAGE_CONFIG['backup_directory']
    if not os.path.exists(backup_dir):
        try:
            os.makedirs(backup_dir)
        except Exception as e:
            errors.append(f"Cannot create backup directory: {e}")
    
    return errors

if __name__ == "__main__":
    # 測試配置
    print("=== 爬蟲系統配置 ===")
    
    config = get_config()
    for section, settings in config.items():
        print(f"\n{section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    # 驗證配置
    errors = validate_config()
    if errors:
        print(f"\n配置錯誤:")
        for error in errors:
            print(f"  - {error}")
    else:
        print(f"\n✅ 配置驗證通過")
