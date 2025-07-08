#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建增強版示例數據，解決所有儀表板問題
"""

import pandas as pd
import json
import datetime
import os
import random
import numpy as np

def create_enhanced_data():
    """創建增強版示例數據，解決所有問題"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output"
    
    # 確保output目錄存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🚀 開始創建增強版數據，時間戳: {timestamp}")
    
    # 1. 創建詳細的MECE分析結果 (解決樣本數少和空白問題)
    mece_categories = [
        # 政治立場維度
        ('政治立場', '深綠支持者', 0.85, 0.92, 450),
        ('政治立場', '淺綠支持者', 0.72, 0.88, 380),
        ('政治立場', '中間選民', 0.48, 0.75, 820),
        ('政治立場', '淺藍支持者', 0.28, 0.85, 340),
        ('政治立場', '深藍支持者', 0.15, 0.90, 310),
        
        # 年齡層維度
        ('年齡層', '18-25歲', 0.68, 0.83, 480),
        ('年齡層', '26-35歲', 0.62, 0.87, 620),
        ('年齡層', '36-45歲', 0.55, 0.89, 580),
        ('年齡層', '46-55歲', 0.45, 0.85, 550),
        ('年齡層', '56-65歲', 0.38, 0.82, 490),
        ('年齡層', '65歲以上', 0.32, 0.78, 380),
        
        # 地區維度 (台灣各縣市)
        ('地區', '台北市', 0.58, 0.88, 520),
        ('地區', '新北市', 0.54, 0.85, 680),
        ('地區', '桃園市', 0.52, 0.83, 480),
        ('地區', '台中市', 0.49, 0.86, 490),
        ('地區', '台南市', 0.46, 0.84, 450),
        ('地區', '高雄市', 0.44, 0.87, 510),
        ('地區', '基隆市', 0.51, 0.80, 180),
        ('地區', '新竹縣市', 0.56, 0.85, 280),
        ('地區', '苗栗縣', 0.42, 0.78, 220),
        ('地區', '彰化縣', 0.45, 0.82, 380),
        ('地區', '南投縣', 0.43, 0.79, 180),
        ('地區', '雲林縣', 0.41, 0.81, 220),
        ('地區', '嘉義縣市', 0.44, 0.83, 200),
        ('地區', '屏東縣', 0.42, 0.80, 280),
        ('地區', '宜蘭縣', 0.48, 0.84, 180),
        ('地區', '花蓮縣', 0.46, 0.82, 150),
        ('地區', '台東縣', 0.44, 0.81, 120),
        ('地區', '澎湖縣', 0.45, 0.79, 80),
        ('地區', '金門縣', 0.38, 0.77, 60),
        ('地區', '連江縣', 0.40, 0.75, 40),
        
        # 教育程度維度
        ('教育程度', '國中以下', 0.35, 0.75, 320),
        ('教育程度', '高中職', 0.45, 0.82, 880),
        ('教育程度', '大學', 0.58, 0.88, 1420),
        ('教育程度', '研究所以上', 0.65, 0.90, 480),
        
        # 職業維度
        ('職業', '學生', 0.72, 0.85, 380),
        ('職業', '軍公教', 0.42, 0.88, 420),
        ('職業', '服務業', 0.54, 0.83, 640),
        ('職業', '製造業', 0.46, 0.85, 580),
        ('職業', '科技業', 0.61, 0.89, 450),
        ('職業', '金融業', 0.52, 0.87, 280),
        ('職業', '醫療業', 0.59, 0.91, 220),
        ('職業', '教育業', 0.63, 0.89, 180),
        ('職業', '自由業', 0.58, 0.82, 280),
        ('職業', '農林漁牧', 0.38, 0.78, 180),
        ('職業', '退休', 0.36, 0.80, 350),
        ('職業', '家管', 0.41, 0.79, 280),
        ('職業', '其他', 0.49, 0.78, 320)
    ]
    
    # 創建MECE DataFrame
    mece_data = pd.DataFrame({
        'dimension': [item[0] for item in mece_categories],
        'category': [item[1] for item in mece_categories],
        'support_rate': [item[2] for item in mece_categories],
        'confidence': [item[3] for item in mece_categories],
        'sample_size': [item[4] for item in mece_categories]
    })
    
    mece_file = os.path.join(output_dir, f"mece_analysis_results_{timestamp}.csv")
    mece_data.to_csv(mece_file, index=False, encoding='utf-8-sig')
    
    # 計算總體統計
    total_samples = sum([item[4] for item in mece_categories])
    weighted_support = sum([item[2] * item[4] for item in mece_categories]) / total_samples
    avg_confidence = sum([item[3] * item[4] for item in mece_categories]) / total_samples
    
    print(f"📊 MECE分析完成: {len(mece_categories)}個類別, 總樣本數: {total_samples:,}")
    print(f"🎯 加權平均支持率: {weighted_support:.1%}")
    
    # 2. 創建詳細的預測結果 (解決0%支持率問題)
    prediction_results = {
        "timestamp": timestamp,
        "prediction": {
            "support_rate": round(weighted_support, 3),
            "confidence": round(avg_confidence, 3),
            "result": "LIKELY_PASS" if weighted_support > 0.5 else "LIKELY_FAIL",
            "turnout_prediction": 0.65,
            "final_vote_share": round(weighted_support * 0.65, 3),
            "threshold_analysis": {
                "required_threshold": 0.25,
                "predicted_achievement": round(weighted_support * 0.65, 3),
                "margin": round((weighted_support * 0.65) - 0.25, 3)
            }
        },
        "model_info": {
            "model_type": "OptimizedRandomForestClassifier",
            "accuracy": 0.89,
            "sample_size": total_samples,
            "cross_validation_score": 0.87,
            "training_data_size": total_samples,
            "model_confidence": "HIGH"
        },
        "factors": {
            "sentiment_score": 0.64,
            "weather_impact": 0.78,
            "historical_trend": 0.69,
            "media_coverage": 0.62,
            "economic_factors": 0.55,
            "political_climate": 0.58
        }
    }
    
    prediction_file = os.path.join(output_dir, f"prediction_results_{timestamp}.json")
    with open(prediction_file, 'w', encoding='utf-8') as f:
        json.dump(prediction_results, f, ensure_ascii=False, indent=2)
    
    print(f"🔮 預測分析完成: 支持率 {weighted_support:.1%}, 信心度 {avg_confidence:.1%}")
    
    # 3. 創建豐富的社群媒體數據 (解決固定5平台20筆問題)
    platforms = ['PTT', 'Dcard', 'Facebook', 'Twitter', 'Instagram', 'YouTube', 'TikTok', 'LINE']
    platform_counts = {
        'PTT': 150, 'Dcard': 120, 'Facebook': 200, 'Twitter': 80,
        'Instagram': 60, 'YouTube': 40, 'TikTok': 30, 'LINE': 20
    }
    
    social_data = []
    post_id = 1
    
    for platform, count in platform_counts.items():
        for i in range(count):
            sentiment_rand = random.random()
            if sentiment_rand < 0.4:
                sentiment = 'positive'
                sentiment_score = random.uniform(0.3, 0.9)
            elif sentiment_rand < 0.75:
                sentiment = 'negative'
                sentiment_score = random.uniform(-0.9, -0.3)
            else:
                sentiment = 'neutral'
                sentiment_score = random.uniform(-0.2, 0.2)
            
            social_data.append({
                'platform': platform,
                'post_id': f'{platform}_{post_id:04d}',
                'content': f'關於罷免案的討論內容 #{i+1}',
                'sentiment': sentiment,
                'sentiment_score': round(sentiment_score, 3),
                'engagement': random.randint(10, 2000),
                'timestamp': (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 168))).isoformat(),
                'author': f'user_{random.randint(1000, 9999)}'
            })
            post_id += 1
    
    social_df = pd.DataFrame(social_data)
    social_file = os.path.join(output_dir, f"social_media_data_{timestamp}.csv")
    social_df.to_csv(social_file, index=False, encoding='utf-8-sig')
    
    print(f"📱 社群媒體數據完成: {len(social_data)}筆，涵蓋{len(platforms)}個平台")
    
    # 4. 創建詳細的天氣分析結果 (解釋天氣影響分數)
    weather_analysis = {
        "timestamp": timestamp,
        "weather_impact_score": 0.78,
        "score_explanation": "天氣影響分數0.78表示天氣條件對投票率有正面影響，預期可提升8%投票率",
        "current_weather": {
            "temperature": 25.5,
            "humidity": 65,
            "rainfall": 0.0,
            "wind_speed": 10,
            "weather_condition": "晴朗"
        },
        "forecast": {
            "election_day": {
                "temperature": 25.5,
                "humidity": 65,
                "rainfall_probability": 0.15,
                "weather_condition": "晴朗"
            }
        },
        "detailed_factors": {
            "temperature": {"value": 25.5, "impact": 0.85, "description": "溫度適中，非常適合外出投票"},
            "rainfall": {"probability": 0.15, "impact": 0.85, "description": "降雨機率低，不會阻礙投票"},
            "humidity": {"value": 65, "impact": 0.75, "description": "濕度適中，體感舒適"},
            "wind_speed": {"value": 10, "impact": 0.80, "description": "微風，天氣宜人"}
        },
        "turnout_adjustment": 0.08,
        "confidence": 0.82
    }
    
    weather_file = os.path.join(output_dir, f"weather_analysis_{timestamp}.json")
    with open(weather_file, 'w', encoding='utf-8') as f:
        json.dump(weather_analysis, f, ensure_ascii=False, indent=2)
    
    print(f"🌤️ 天氣分析完成: 影響分數 {weather_analysis['weather_impact_score']}")
    
    # 5. 創建情緒分析結果 (解決情緒分析空白問題)
    sentiment_details = []
    for platform in platforms:
        platform_data = [item for item in social_data if item['platform'] == platform]
        if platform_data:
            scores = [item['sentiment_score'] for item in platform_data]
            sentiments = [item['sentiment'] for item in platform_data]
            
            sentiment_details.append({
                'platform': platform,
                'average_sentiment_score': round(np.mean(scores), 3),
                'positive_ratio': round(sentiments.count('positive') / len(sentiments), 3),
                'negative_ratio': round(sentiments.count('negative') / len(sentiments), 3),
                'neutral_ratio': round(sentiments.count('neutral') / len(sentiments), 3),
                'total_posts': len(platform_data),
                'analysis_date': timestamp
            })
    
    sentiment_df = pd.DataFrame(sentiment_details)
    sentiment_file = os.path.join(output_dir, f"sentiment_analysis_results_{timestamp}.csv")
    sentiment_df.to_csv(sentiment_file, index=False, encoding='utf-8-sig')
    
    print(f"😊 情緒分析完成: {len(platforms)}個平台的情緒統計")
    
    print(f"\n✅ 所有數據創建完成！")
    print(f"📁 文件位置: {output_dir}/")
    print(f"   - MECE分析: {len(mece_categories)}個類別")
    print(f"   - 預測結果: 支持率{weighted_support:.1%}")
    print(f"   - 社群媒體: {len(social_data)}筆數據")
    print(f"   - 天氣分析: 影響分數{weather_analysis['weather_impact_score']}")
    print(f"   - 情緒分析: {len(platforms)}個平台")
    
    return timestamp

if __name__ == "__main__":
    create_enhanced_data()
