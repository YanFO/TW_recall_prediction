#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECE分析模組 - 互斥且完全窮盡的分析框架
基於ChatGPT建議的完整MECE框架優化：
1. 投票率預測 (結構性因素、動機因素、社群媒體聲量)
2. 投票結果預測 (法規門檻、選民結構、情緒事件變數)
3. 7維度量化指標系統
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import jieba
from collections import Counter
import re
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, mean_squared_error
import joblib
import glob
import warnings
warnings.filterwarnings('ignore')

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class MECEAnalyzer:
    def __init__(self):
        self.demographic_keywords = self._load_demographic_keywords()
        self.issue_keywords = self._load_issue_keywords()
        self.quantitative_indicators = self._init_quantitative_indicators()
        self.recall_threshold = 0.25  # 25%同意門檻

    def _load_optimized_model(self):
        """載入優化後的模型"""
        try:
            # 尋找最新的優化模型文件
            model_files = glob.glob("optimized_model_*.joblib")
            if not model_files:
                print("未找到優化模型文件")
                return None

            # 選擇最新的模型文件
            latest_model_file = max(model_files, key=lambda x: x.split('_')[-1])

            # 載入模型包
            model_package = joblib.load(latest_model_file)

            print(f"成功載入優化模型: {latest_model_file}")
            return model_package['model']

        except Exception as e:
            print(f"載入優化模型失敗: {e}")
            return None
        
    def _init_quantitative_indicators(self):
        """初始化7維度量化指標系統"""
        return {
            'population_structure': {
                'eligible_voters': 0,
                'age_distribution': {},
                'geographic_distribution': {},
                'mobility_factor': 0  # 人口流動係數
            },
            'election_history': {
                'previous_turnout': 0,
                'previous_support_rate': 0,
                'historical_pattern': {}
            },
            'online_sentiment': {
                'discussion_volume': 0,
                'sentiment_ratio': 0,
                'trend_momentum': 0
            },
            'social_mobilization': {
                'post_engagement': 0,
                'community_activity': 0,
                'influencer_support': 0
            },
            'weather_factor': {
                'weather_score': 0,
                'precipitation_prob': 0,
                'temperature_comfort': 0
            },
            'event_impact': {
                'negative_keyword_spike': 0,
                'controversy_level': 0,
                'media_attention': 0
            },
            'political_mobilization': {
                'party_support': 0,
                'campaign_intensity': 0,
                'endorsement_count': 0
            }
        }

    def _load_demographic_keywords(self):
        """載入人口統計關鍵詞 - 擴展版本"""
        return {
            'age_groups': {
                'young': ['學生', '大學', '年輕', '新鮮人', '剛畢業', '20歲', '大一', '大二', '大三', '大四',
                         '青年', '年輕人', '新世代', '90後', '00後'],
                'middle': ['上班族', '工作', '職場', '30歲', '40歲', '中年', '家庭', '小孩', '父母',
                          '中壯年', '社會人士', '職業婦女'],
                'senior': ['退休', '老人', '長輩', '50歲', '60歲', '70歲', '阿公', '阿嬤', '銀髮族',
                          '資深', '年長者', '長者']
            },
            'regions': {
                'north': ['台北', '新北', '桃園', '新竹', '基隆', '宜蘭', '北部', '大台北'],
                'central': ['台中', '彰化', '南投', '雲林', '苗栗', '中部', '中台灣'],
                'south': ['台南', '高雄', '屏東', '嘉義', '南部', '南台灣'],
                'east': ['花蓮', '台東', '東部', '東台灣'],
                'islands': ['澎湖', '金門', '馬祖', '離島']
            },
            'occupation': {
                'student': ['學生', '大學生', '研究生', '博士生', '在學', '求學'],
                'professional': ['工程師', '醫師', '律師', '會計師', '老師', '教授', '專業人士'],
                'business': ['老闆', '創業', '自營', '商人', '業務', '企業主'],
                'labor': ['工人', '作業員', '司機', '服務業', '餐飲', '勞工'],
                'government': ['公務員', '軍人', '警察', '消防員', '公職', '軍公教']
            },
            'voting_motivation': {
                'high': ['一定要投', '必須投票', '責任', '義務', '關心政治', '公民責任'],
                'medium': ['可能會投', '看情況', '有空就去', '考慮中'],
                'low': ['不想投', '懶得投', '沒興趣', '無所謂', '不關心']
            }
        }
    
    def _load_issue_keywords(self):
        """載入議題關鍵詞 - 擴展版本"""
        return {
            'political_issues': {
                'governance': ['施政', '政策', '治理', '行政', '效率', '能力', '執政', '管理'],
                'corruption': ['貪污', '腐敗', '弊案', '黑金', '利益', '關說', '貪腐', '收賄'],
                'democracy': ['民主', '自由', '人權', '法治', '透明', '監督', '民主制度'],
                'economy': ['經濟', '就業', '薪資', '物價', '房價', '投資', '景氣', '失業']
            },
            'recall_reasons': {
                'performance': ['無能', '失職', '不適任', '表現差', '沒做事', '不稱職', '能力不足'],
                'scandal': ['醜聞', '爆料', '負面', '爭議', '問題', '風波', '事件'],
                'ideology': ['理念', '價值觀', '立場', '政治', '意識形態', '政治立場'],
                'representation': ['代表性', '民意', '選民', '承諾', '背叛', '民意代表', '選民意志']
            },
            'mobilization_keywords': {
                'support_mobilization': ['支持', '挺', '站出來', '團結', '一起', '加油', '努力'],
                'oppose_mobilization': ['反對', '抵制', '拒絕', '不要', '阻止', '反罷免'],
                'neutral_discussion': ['討論', '分析', '思考', '觀察', '了解', '關注']
            },
            'urgency_keywords': {
                'high_urgency': ['緊急', '重要', '關鍵', '決定性', '最後機會', '不能錯過'],
                'medium_urgency': ['需要', '應該', '建議', '希望', '期待'],
                'low_urgency': ['可以', '或許', '也許', '考慮', '看看']
            }
        }
    
    def classify_demographics(self, df, text_column='content'):
        """人口統計分類 (MECE: 年齡、地區、職業)"""
        results = []
        
        for idx, row in df.iterrows():
            text = str(row[text_column]).lower()
            
            # 年齡分類
            age_group = 'unknown'
            for group, keywords in self.demographic_keywords['age_groups'].items():
                if any(keyword in text for keyword in keywords):
                    age_group = group
                    break
            
            # 地區分類
            region = 'unknown'
            for reg, cities in self.demographic_keywords['regions'].items():
                if any(city in text for city in cities):
                    region = reg
                    break
            
            # 職業分類
            occupation = 'unknown'
            for occ, keywords in self.demographic_keywords['occupation'].items():
                if any(keyword in text for keyword in keywords):
                    occupation = occ
                    break
            
            results.append({
                'index': idx,
                'age_group': age_group,
                'region': region,
                'occupation': occupation
            })
        
        return pd.DataFrame(results)

    def predict_turnout_rate(self, df, sentiment_df, demo_df, weather_data=None):
        """預測投票率 - 基於MECE框架的三大因素"""

        # A. 結構性因素分析
        structural_factors = self._analyze_structural_factors(df, demo_df)

        # B. 動機因素分析
        motivation_factors = self._analyze_motivation_factors(df, sentiment_df)

        # C. 社群媒體聲量分析
        social_media_factors = self._analyze_social_media_factors(df, sentiment_df)

        # D. 天氣因素 (如果有資料)
        weather_impact = self._analyze_weather_impact(weather_data) if weather_data else 0.0

        # 綜合計算投票率預測
        base_turnout = 0.45  # 基礎投票率假設

        # 各因素權重
        structural_weight = 0.3
        motivation_weight = 0.4
        social_weight = 0.2
        weather_weight = 0.1

        predicted_turnout = (
            base_turnout +
            structural_factors * structural_weight +
            motivation_factors * motivation_weight +
            social_media_factors * social_weight +
            weather_impact * weather_weight
        )

        # 限制在合理範圍內
        predicted_turnout = max(0.1, min(0.9, predicted_turnout))

        return {
            'predicted_turnout_rate': predicted_turnout,
            'structural_score': structural_factors,
            'motivation_score': motivation_factors,
            'social_media_score': social_media_factors,
            'weather_impact': weather_impact,
            'confidence_level': self._calculate_turnout_confidence(df)
        }

    def _analyze_structural_factors(self, df, demo_df):
        """分析結構性因素 (人口與地理)"""
        factors = []

        # 地理便利性 (投開票所密度代理指標)
        region_distribution = demo_df['region'].value_counts(normalize=True)
        urban_ratio = region_distribution.get('north', 0) + region_distribution.get('central', 0)
        factors.append(urban_ratio * 0.1)  # 都市化程度提升投票率

        # 人口流動影響
        if 'source' in df.columns:
            local_discussion_ratio = len(df[df['source'] == 'PTT']) / len(df) if len(df) > 0 else 0
            factors.append(local_discussion_ratio * 0.05)

        return sum(factors)

    def _analyze_motivation_factors(self, df, sentiment_df):
        """分析動機因素"""
        factors = []

        # 政治動員程度
        if 'recall_stance' in sentiment_df.columns:
            stance_distribution = sentiment_df['recall_stance'].value_counts(normalize=True)
            polarization = 1 - max(stance_distribution) if len(stance_distribution) > 1 else 0
            factors.append(polarization * 0.15)  # 極化程度提升投票率

        # 議題熱度
        if 'sentiment_score' in sentiment_df.columns:
            avg_sentiment_intensity = abs(sentiment_df['sentiment_score'].mean())
            factors.append(avg_sentiment_intensity * 0.1)

        # 討論活躍度
        discussion_volume = len(df) / 1000  # 標準化討論量
        factors.append(min(discussion_volume, 0.1))

        return sum(factors)

    def _analyze_social_media_factors(self, df, sentiment_df):
        """分析社群媒體聲量"""
        factors = []

        # PTT vs Dcard 活躍度差異
        if 'source' in df.columns:
            source_counts = df['source'].value_counts()
            total_posts = len(df)
            if total_posts > 0:
                ptt_ratio = source_counts.get('PTT', 0) / total_posts
                dcard_ratio = source_counts.get('Dcard', 0) / total_posts
                platform_diversity = 1 - abs(ptt_ratio - dcard_ratio)
                factors.append(platform_diversity * 0.05)

        # 情緒強度變化
        if 'sentiment_score' in sentiment_df.columns and len(sentiment_df) > 1:
            sentiment_std = sentiment_df['sentiment_score'].std()
            factors.append(min(sentiment_std, 0.1))

        return sum(factors)

    def _analyze_weather_impact(self, weather_data):
        """分析天氣影響 (負面影響)"""
        if not weather_data:
            return 0.0

        impact = 0.0

        # 降雨機率影響
        if 'precipitation_prob' in weather_data:
            rain_impact = -weather_data['precipitation_prob'] * 0.001  # 每1%降雨機率減少0.1%投票率
            impact += rain_impact

        # 極端溫度影響
        if 'temperature' in weather_data:
            temp = weather_data['temperature']
            if temp < 10 or temp > 35:  # 極端溫度
                impact -= 0.02

        return impact

    def _calculate_turnout_confidence(self, df):
        """計算投票率預測信心度"""
        sample_size = len(df)

        if sample_size < 100:
            return 0.3
        elif sample_size < 500:
            return 0.6
        elif sample_size < 1000:
            return 0.8
        else:
            return 0.9

    def classify_issues(self, df, text_column='content'):
        """議題分類 (MECE: 政治議題、罷免原因)"""
        results = []
        
        for idx, row in df.iterrows():
            text = str(row[text_column]).lower()
            
            # 政治議題分類
            political_issues = []
            for issue, keywords in self.issue_keywords['political_issues'].items():
                if any(keyword in text for keyword in keywords):
                    political_issues.append(issue)
            
            # 罷免原因分類
            recall_reasons = []
            for reason, keywords in self.issue_keywords['recall_reasons'].items():
                if any(keyword in text for keyword in keywords):
                    recall_reasons.append(reason)
            
            results.append({
                'index': idx,
                'political_issues': ','.join(political_issues) if political_issues else 'none',
                'recall_reasons': ','.join(recall_reasons) if recall_reasons else 'none',
                'issue_count': len(political_issues) + len(recall_reasons)
            })
        
        return pd.DataFrame(results)
    
    def temporal_analysis(self, df, date_column='date'):
        """時間序列分析"""
        if date_column not in df.columns:
            print(f"找不到日期欄位 {date_column}")
            return pd.DataFrame()
        
        # 轉換日期格式
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.dropna(subset=[date_column])
        
        # 按日期分組
        daily_stats = df.groupby(df[date_column].dt.date).agg({
            'sentiment_score': ['mean', 'std', 'count'],
            'recall_stance': lambda x: (x == 'support_recall').sum() / len(x) if len(x) > 0 else 0
        }).round(3)
        
        daily_stats.columns = ['avg_sentiment', 'sentiment_std', 'post_count', 'support_ratio']
        
        return daily_stats.reset_index()

    def predict_recall_outcome(self, df, sentiment_df, demo_df, issue_df, turnout_prediction):
        """預測罷免結果 - 基於MECE框架的三大維度"""

        # A. 法規與門檻分析
        threshold_analysis = self._analyze_legal_threshold(turnout_prediction)

        # B. 選民結構分析
        voter_structure = self._analyze_voter_structure(demo_df, sentiment_df)

        # C. 情緒與事件變數分析
        emotional_events = self._analyze_emotional_events(df, sentiment_df, issue_df)

        # 綜合預測計算
        base_support_rate = 0.4  # 基礎支持率假設

        # 各因素權重
        threshold_weight = 0.3
        structure_weight = 0.4
        emotion_weight = 0.3

        predicted_support = (
            base_support_rate +
            threshold_analysis['threshold_effect'] * threshold_weight +
            voter_structure['structure_effect'] * structure_weight +
            emotional_events['emotion_effect'] * emotion_weight
        )

        # 限制在合理範圍內
        predicted_support = max(0.1, min(0.9, predicted_support))

        # 計算是否通過罷免
        turnout_rate = turnout_prediction['predicted_turnout_rate']
        support_votes_ratio = predicted_support * turnout_rate
        threshold_required = self.recall_threshold  # 25%

        will_pass = support_votes_ratio >= threshold_required

        return {
            'predicted_support_rate': predicted_support,
            'support_votes_ratio': support_votes_ratio,
            'legal_threshold': threshold_required,
            'prediction_result': '通過' if will_pass else '失敗',
            'pass_probability': min(support_votes_ratio / threshold_required, 1.0),
            'safety_margin': support_votes_ratio - threshold_required,
            'confidence_score': self._calculate_outcome_confidence(df, sentiment_df)
        }

    def _analyze_legal_threshold(self, turnout_prediction):
        """分析法規門檻影響"""
        turnout_rate = turnout_prediction['predicted_turnout_rate']

        # 投票率對門檻達成的影響
        if turnout_rate < 0.3:
            threshold_effect = -0.1  # 低投票率不利罷免
        elif turnout_rate > 0.6:
            threshold_effect = 0.05   # 高投票率有利罷免
        else:
            threshold_effect = 0.0

        return {
            'threshold_effect': threshold_effect,
            'turnout_impact': turnout_rate,
            'threshold_difficulty': self.recall_threshold / turnout_rate if turnout_rate > 0 else float('inf')
        }

    def _analyze_voter_structure(self, demo_df, sentiment_df):
        """分析選民結構"""
        structure_effects = []

        # 年齡結構影響
        if 'age_group' in demo_df.columns:
            age_dist = demo_df['age_group'].value_counts(normalize=True)
            young_ratio = age_dist.get('young', 0)
            senior_ratio = age_dist.get('senior', 0)

            # 年輕人通常更支持罷免
            age_effect = (young_ratio - senior_ratio) * 0.1
            structure_effects.append(age_effect)

        # 地區結構影響
        if 'region' in demo_df.columns:
            region_dist = demo_df['region'].value_counts(normalize=True)
            urban_ratio = region_dist.get('north', 0) + region_dist.get('central', 0)

            # 都市地區通常政治參與度較高
            region_effect = urban_ratio * 0.05
            structure_effects.append(region_effect)

        # 職業結構影響
        if 'occupation' in demo_df.columns:
            occ_dist = demo_df['occupation'].value_counts(normalize=True)
            professional_ratio = occ_dist.get('professional', 0)
            government_ratio = occ_dist.get('government', 0)

            # 專業人士vs公務員的對比
            occupation_effect = (professional_ratio - government_ratio) * 0.08
            structure_effects.append(occupation_effect)

        return {
            'structure_effect': sum(structure_effects),
            'age_factor': structure_effects[0] if len(structure_effects) > 0 else 0,
            'region_factor': structure_effects[1] if len(structure_effects) > 1 else 0,
            'occupation_factor': structure_effects[2] if len(structure_effects) > 2 else 0
        }

    def _analyze_emotional_events(self, df, sentiment_df, issue_df):
        """分析情緒與事件變數"""
        emotion_effects = []

        # 負面事件衝擊
        if 'recall_reasons' in issue_df.columns:
            scandal_mentions = issue_df['recall_reasons'].str.contains('scandal', na=False).sum()
            scandal_ratio = scandal_mentions / len(issue_df) if len(issue_df) > 0 else 0
            scandal_effect = scandal_ratio * 0.15
            emotion_effects.append(scandal_effect)

        # 情緒極化程度
        if 'sentiment_score' in sentiment_df.columns:
            sentiment_std = sentiment_df['sentiment_score'].std()
            polarization_effect = min(sentiment_std, 0.5) * 0.1
            emotion_effects.append(polarization_effect)

        # 討論熱度突增
        discussion_intensity = len(df) / 1000  # 標準化
        intensity_effect = min(discussion_intensity, 0.1)
        emotion_effects.append(intensity_effect)

        return {
            'emotion_effect': sum(emotion_effects),
            'scandal_impact': emotion_effects[0] if len(emotion_effects) > 0 else 0,
            'polarization_impact': emotion_effects[1] if len(emotion_effects) > 1 else 0,
            'intensity_impact': emotion_effects[2] if len(emotion_effects) > 2 else 0
        }

    def _calculate_outcome_confidence(self, df, sentiment_df):
        """計算結果預測信心度"""
        factors = []

        # 樣本大小
        sample_size = len(df)
        if sample_size > 1000:
            factors.append(0.3)
        elif sample_size > 500:
            factors.append(0.2)
        else:
            factors.append(0.1)

        # 立場分布均衡度
        if 'recall_stance' in sentiment_df.columns:
            stance_counts = sentiment_df['recall_stance'].value_counts()
            if len(stance_counts) > 1:
                balance = 1 - abs(stance_counts.iloc[0] - stance_counts.iloc[1]) / len(sentiment_df)
                factors.append(balance * 0.3)

        # 時間跨度 (如果有日期資料)
        if 'date' in df.columns:
            factors.append(0.2)  # 有時間序列資料增加信心度

        return min(sum(factors), 0.9)

    def create_prediction_features(self, df, sentiment_df, demo_df, issue_df):
        """創建預測特徵"""
        # 合併所有分析結果
        combined_df = df.copy()
        
        # 加入情緒分析結果
        for col in ['sentiment', 'sentiment_score', 'recall_stance', 'stance_confidence']:
            if col in sentiment_df.columns:
                combined_df[col] = sentiment_df[col]
        
        # 加入人口統計分類
        for col in ['age_group', 'region', 'occupation']:
            if col in demo_df.columns:
                combined_df[col] = demo_df[col]
        
        # 加入議題分類
        for col in ['political_issues', 'recall_reasons', 'issue_count']:
            if col in issue_df.columns:
                combined_df[col] = issue_df[col]
        
        # 創建特徵工程
        features = []
        
        for idx, row in combined_df.iterrows():
            feature_dict = {
                # 基礎特徵
                'sentiment_score': row.get('sentiment_score', 0),
                'stance_confidence': row.get('stance_confidence', 0),
                'issue_count': row.get('issue_count', 0),
                
                # 來源特徵
                'source_ptt': 1 if row.get('source') == 'PTT' else 0,
                'source_dcard': 1 if row.get('source') == 'Dcard' else 0,
                
                # 人口統計特徵
                'age_young': 1 if row.get('age_group') == 'young' else 0,
                'age_middle': 1 if row.get('age_group') == 'middle' else 0,
                'age_senior': 1 if row.get('age_group') == 'senior' else 0,
                
                'region_north': 1 if row.get('region') == 'north' else 0,
                'region_central': 1 if row.get('region') == 'central' else 0,
                'region_south': 1 if row.get('region') == 'south' else 0,
                
                # 議題特徵
                'issue_governance': 1 if 'governance' in str(row.get('political_issues', '')) else 0,
                'issue_corruption': 1 if 'corruption' in str(row.get('political_issues', '')) else 0,
                'issue_democracy': 1 if 'democracy' in str(row.get('political_issues', '')) else 0,
                
                # 目標變數
                'support_recall': 1 if row.get('recall_stance') == 'support_recall' else 0
            }
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def build_prediction_model(self, features_df):
        """建立預測模型"""
        # 準備特徵和目標變數
        feature_columns = [col for col in features_df.columns if col != 'support_recall']
        X = features_df[feature_columns]
        y = features_df['support_recall']
        
        # 分割訓練和測試集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 嘗試載入優化後的模型
        optimized_model = self._load_optimized_model()

        if optimized_model:
            model = optimized_model
            self.logger.info("使用優化後的模型進行預測")
        else:
            # 訓練隨機森林模型
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            self.logger.info("使用基礎模型進行預測")
        
        # 預測和評估
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 特徵重要性
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return {
            'model': model,
            'accuracy': accuracy,
            'feature_importance': feature_importance,
            'classification_report': classification_report(y_test, y_pred)
        }
    


    def predict_recall_outcome_ml(self, features_df, model_results):
        """機器學習預測罷免結果 (重新命名以避免衝突)"""
        model = model_results['model']

        # 計算支持率
        feature_columns = [col for col in features_df.columns if col != 'support_recall']
        X = features_df[feature_columns]

        # 預測概率 - 處理單類別情況
        proba = model.predict_proba(X)
        if proba.shape[1] == 1:
            # 只有一個類別，使用預測值作為支持率
            predictions = model.predict(X)
            support_probs = predictions.astype(float)
        else:
            # 有兩個類別，取支持類別的概率
            support_probs = proba[:, 1]

        # 計算整體支持率
        overall_support_rate = float(support_probs.mean())

        # 預測結果
        prediction = {
            'support_rate': overall_support_rate,
            'prediction': 'PASS' if overall_support_rate > 0.5 else 'FAIL',
            'confidence': float(abs(overall_support_rate - 0.5) * 2),
            'sample_size': int(len(features_df))
        }

        return prediction

    def create_mece_visualizations(self, df, sentiment_df, demo_df, issue_df):
        """創建MECE分析視覺化"""
        fig, axes = plt.subplots(3, 2, figsize=(16, 18))
        
        # 1. 年齡群組vs情緒
        age_sentiment = pd.merge(demo_df, sentiment_df, on='index')
        age_groups = age_sentiment.groupby('age_group')['sentiment_score'].mean()
        axes[0, 0].bar(age_groups.index, age_groups.values)
        axes[0, 0].set_title('各年齡群組平均情緒分數')
        axes[0, 0].set_ylabel('情緒分數')
        
        # 2. 地區vs罷免立場
        region_stance = pd.merge(demo_df, sentiment_df, on='index')
        stance_by_region = region_stance.groupby(['region', 'recall_stance']).size().unstack(fill_value=0)
        stance_by_region.plot(kind='bar', ax=axes[0, 1], stacked=True)
        axes[0, 1].set_title('各地區罷免立場分布')
        axes[0, 1].legend(title='立場')
        
        # 3. 職業vs情緒
        occ_sentiment = pd.merge(demo_df, sentiment_df, on='index')
        occ_groups = occ_sentiment.groupby('occupation')['sentiment_score'].mean()
        axes[1, 0].bar(occ_groups.index, occ_groups.values)
        axes[1, 0].set_title('各職業群組平均情緒分數')
        axes[1, 0].set_ylabel('情緒分數')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. 議題關注度
        issue_counts = issue_df['political_issues'].str.split(',').explode().value_counts()
        issue_counts = issue_counts[issue_counts.index != 'none'][:10]
        axes[1, 1].barh(issue_counts.index, issue_counts.values)
        axes[1, 1].set_title('政治議題關注度排名')
        axes[1, 1].set_xlabel('提及次數')
        
        # 5. 時間趨勢 (如果有日期資料)
        if 'date' in df.columns:
            temporal_data = self.temporal_analysis(pd.merge(df, sentiment_df, left_index=True, right_on='index'))
            if not temporal_data.empty:
                axes[2, 0].plot(temporal_data['date'], temporal_data['avg_sentiment'])
                axes[2, 0].set_title('情緒趨勢變化')
                axes[2, 0].set_ylabel('平均情緒分數')
                axes[2, 0].tick_params(axis='x', rotation=45)
        
        # 6. 來源vs立場
        if 'source' in df.columns:
            source_stance = pd.merge(df, sentiment_df, left_index=True, right_on='index')
            source_stance_dist = source_stance.groupby(['source', 'recall_stance']).size().unstack(fill_value=0)
            source_stance_dist.plot(kind='bar', ax=axes[2, 1])
            axes[2, 1].set_title('各資料來源罷免立場分布')
            axes[2, 1].legend(title='立場')
        
        plt.tight_layout()
        plt.savefig('mece_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """主要執行函數"""
    analyzer = MECEAnalyzer()
    
    # 載入最新的情緒分析結果
    import glob
    import os
    
    result_files = glob.glob("sentiment_analysis_results_*.csv")
    if not result_files:
        print("找不到情緒分析結果檔案，請先執行 sentiment_analyzer.py")
        return
    
    latest_file = max(result_files, key=os.path.getctime)
    print(f"載入分析結果: {latest_file}")
    
    df = pd.read_csv(latest_file)
    print(f"載入 {len(df)} 筆資料")
    
    # 分離原始資料和情緒分析結果
    sentiment_columns = ['sentiment', 'sentiment_score', 'sentiment_confidence', 
                        'recall_stance', 'stance_confidence']
    sentiment_df = df[['index'] + [col for col in sentiment_columns if col in df.columns]].copy()
    original_df = df.drop(columns=[col for col in sentiment_columns if col in df.columns])
    
    # 執行MECE分析
    print("執行人口統計分類...")
    demo_df = analyzer.classify_demographics(original_df)

    print("執行議題分類...")
    issue_df = analyzer.classify_issues(original_df)

    # 新增：投票率預測
    print("預測投票率...")
    turnout_prediction = analyzer.predict_turnout_rate(original_df, sentiment_df, demo_df)

    # 新增：罷免結果預測
    print("預測罷免結果...")
    outcome_prediction = analyzer.predict_recall_outcome(original_df, sentiment_df, demo_df, issue_df, turnout_prediction)

    print("創建預測特徵...")
    features_df = analyzer.create_prediction_features(original_df, sentiment_df, demo_df, issue_df)

    print("建立機器學習模型...")
    model_results = analyzer.build_prediction_model(features_df)

    print("機器學習預測...")
    ml_prediction = analyzer.predict_recall_outcome_ml(features_df, model_results)
    
    # 輸出結果
    print("\n" + "="*60)
    print("🎯 台灣罷免預測分析結果 (基於完整MECE框架)")
    print("="*60)

    print("\n📊 投票率預測:")
    print(f"  預測投票率: {turnout_prediction['predicted_turnout_rate']:.1%}")
    print(f"  結構性因素: {turnout_prediction['structural_score']:.3f}")
    print(f"  動機因素: {turnout_prediction['motivation_score']:.3f}")
    print(f"  社群媒體因素: {turnout_prediction['social_media_score']:.3f}")
    print(f"  信心度: {turnout_prediction['confidence_level']:.1%}")

    print("\n🗳️ 罷免結果預測:")
    print(f"  預測支持率: {outcome_prediction['predicted_support_rate']:.1%}")
    print(f"  支持票比例: {outcome_prediction['support_votes_ratio']:.1%}")
    print(f"  法定門檻: {outcome_prediction['legal_threshold']:.1%}")
    print(f"  預測結果: {'✅ 罷免通過' if outcome_prediction['prediction_result'] == '通過' else '❌ 罷免失敗'}")
    print(f"  通過機率: {outcome_prediction['pass_probability']:.1%}")
    print(f"  安全邊際: {outcome_prediction['safety_margin']:+.1%}")
    print(f"  信心度: {outcome_prediction['confidence_score']:.1%}")

    print("\n🤖 機器學習模型:")
    print(f"  模型準確率: {model_results['accuracy']:.1%}")
    print(f"  ML預測支持率: {ml_prediction['support_rate']:.1%}")
    print(f"  ML預測結果: {ml_prediction['prediction']}")
    print(f"  ML信心度: {ml_prediction['confidence']:.1%}")

    print("\n🔍 特徵重要性排名:")
    print(model_results['feature_importance'].head(10).to_string(index=False))
    
    # 儲存結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 儲存MECE分析結果
    mece_results = pd.concat([original_df, sentiment_df, demo_df, issue_df], axis=1)
    mece_results.to_csv(f"mece_analysis_results_{timestamp}.csv", index=False, encoding='utf-8-sig')
    
    # 儲存完整預測結果
    prediction_summary = {
        'analysis_time': datetime.now().isoformat(),
        'sample_size': int(len(original_df)),

        # 投票率預測
        'turnout_prediction': {
            'predicted_turnout': float(turnout_prediction['predicted_turnout_rate']),
            'structural_score': float(turnout_prediction['structural_score']),
            'motivation_score': float(turnout_prediction['motivation_score']),
            'social_media_score': float(turnout_prediction['social_media_score']),
            'confidence_level': float(turnout_prediction['confidence_level'])
        },

        # 罷免結果預測 (MECE框架)
        'outcome_prediction': {
            'predicted_support_rate': float(outcome_prediction['predicted_support_rate']),
            'support_votes_ratio': float(outcome_prediction['support_votes_ratio']),
            'legal_threshold': float(outcome_prediction['legal_threshold']),
            'prediction_result': str(outcome_prediction['prediction_result']),
            'pass_probability': float(outcome_prediction['pass_probability']),
            'safety_margin': float(outcome_prediction['safety_margin']),
            'confidence_score': float(outcome_prediction['confidence_score'])
        },

        # 機器學習預測
        'ml_prediction': {
            'model_accuracy': float(model_results['accuracy']),
            'predicted_support_rate': float(ml_prediction['support_rate']),
            'prediction': str(ml_prediction['prediction']),
            'confidence': float(ml_prediction['confidence'])
        },

        # 特徵重要性
        'feature_importance': [
            {
                'feature': str(row['feature']),
                'importance': float(row['importance'])
            }
            for _, row in model_results['feature_importance'].head(10).iterrows()
        ]
    }
    
    import json
    import numpy as np

    def convert_to_serializable(obj):
        """轉換為JSON可序列化的格式"""
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj

    # 轉換為可序列化格式
    serializable_summary = convert_to_serializable(prediction_summary)

    with open(f"prediction_results_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(serializable_summary, f, ensure_ascii=False, indent=2)
    
    # 創建視覺化
    analyzer.create_mece_visualizations(original_df, sentiment_df, demo_df, issue_df)
    
    print(f"\n💾 結果已儲存:")
    print(f"  📊 MECE分析結果: mece_analysis_results_{timestamp}.csv")
    print(f"  🎯 預測結果: prediction_results_{timestamp}.json")
    print(f"  📈 視覺化圖表: mece_analysis.png")

    print(f"\n🎉 分析完成！基於 {len(original_df)} 筆資料的完整MECE框架預測")

    return mece_results, prediction_summary

if __name__ == "__main__":
    main()
