#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情緒分析模組 - 分析文本情緒傾向
"""

import pandas as pd
import numpy as np
import jieba
import re
from collections import Counter
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class SentimentAnalyzer:
    def __init__(self):
        # 載入情緒詞典
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        self.political_keywords = self._load_political_keywords()
        
    def _load_positive_words(self):
        """載入正面詞彙"""
        return {
            '支持', '贊成', '同意', '好', '棒', '讚', '優秀', '正確', '應該', '必要',
            '希望', '期待', '加油', '努力', '改善', '進步', '成功', '勝利', '正義',
            '民主', '自由', '公正', '透明', '負責', '誠實', '清廉', '有能力'
        }
    
    def _load_negative_words(self):
        """載入負面詞彙"""
        return {
            '反對', '不同意', '爛', '差', '糟', '噁心', '討厭', '憤怒', '生氣', '失望',
            '騙', '謊言', '貪污', '腐敗', '無能', '失職', '背叛', '欺騙', '虛偽',
            '獨裁', '專制', '壓迫', '不公', '黑箱', '暗盤', '買票', '作弊'
        }
    
    def _load_political_keywords(self):
        """載入政治相關關鍵詞"""
        return {
            'recall_related': ['罷免', '罷韓', '罷王', '罷免案', '連署', '投票'],
            'support': ['支持罷免', '同意罷免', '罷免成功'],
            'oppose': ['反對罷免', '不同意罷免', '罷免失敗'],
            'neutral': ['罷免投票', '罷免程序', '罷免規定']
        }
    
    def preprocess_text(self, text):
        """文本預處理"""
        if pd.isna(text) or text == '':
            return ''
        
        # 移除特殊字符，保留中文、英文、數字
        text = re.sub(r'[^\u4e00-\u9fff\w\s]', ' ', str(text))
        
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def analyze_sentiment_rule_based(self, text):
        """基於規則的情緒分析"""
        if not text:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        # 分詞
        words = list(jieba.cut(text))
        
        # 計算正負面詞彙數量
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # 計算情緒分數 (-1 到 1)
        total_words = len(words)
        if total_words == 0:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        score = (positive_count - negative_count) / total_words
        
        # 判斷情緒類別
        if score > 0.1:
            sentiment = 'positive'
        elif score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # 計算信心度
        confidence = min(abs(score) * 10, 1.0)
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def analyze_recall_stance(self, text):
        """分析對罷免的立場"""
        if not text:
            return {'stance': 'neutral', 'confidence': 0}
        
        text_lower = text.lower()
        
        # 支持罷免的關鍵詞
        support_patterns = [
            r'支持.*?罷免', r'同意.*?罷免', r'罷免.*?成功', r'一定要.*?罷免',
            r'罷免.*?通過', r'投.*?同意', r'罷免.*?支持'
        ]
        
        # 反對罷免的關鍵詞
        oppose_patterns = [
            r'反對.*?罷免', r'不同意.*?罷免', r'罷免.*?失敗', r'不要.*?罷免',
            r'罷免.*?不通過', r'投.*?不同意', r'罷免.*?反對'
        ]
        
        support_score = sum(len(re.findall(pattern, text)) for pattern in support_patterns)
        oppose_score = sum(len(re.findall(pattern, text)) for pattern in oppose_patterns)
        
        if support_score > oppose_score:
            stance = 'support_recall'
            confidence = min(support_score / (support_score + oppose_score + 1), 1.0)
        elif oppose_score > support_score:
            stance = 'oppose_recall'
            confidence = min(oppose_score / (support_score + oppose_score + 1), 1.0)
        else:
            stance = 'neutral'
            confidence = 0
        
        return {
            'stance': stance,
            'confidence': confidence,
            'support_signals': support_score,
            'oppose_signals': oppose_score
        }
    
    def analyze_dataframe(self, df, text_column='content'):
        """分析整個DataFrame的情緒"""
        results = []
        
        print(f"開始分析 {len(df)} 筆資料...")
        
        for idx, row in df.iterrows():
            text = self.preprocess_text(row[text_column])
            
            # 情緒分析
            sentiment_result = self.analyze_sentiment_rule_based(text)
            
            # 罷免立場分析
            stance_result = self.analyze_recall_stance(text)
            
            # 合併結果
            result = {
                'index': idx,
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['score'],
                'sentiment_confidence': sentiment_result['confidence'],
                'positive_words': sentiment_result['positive_words'],
                'negative_words': sentiment_result['negative_words'],
                'recall_stance': stance_result['stance'],
                'stance_confidence': stance_result['confidence'],
                'support_signals': stance_result['support_signals'],
                'oppose_signals': stance_result['oppose_signals']
            }
            
            results.append(result)
            
            if (idx + 1) % 50 == 0:
                print(f"已處理 {idx + 1} 筆資料...")
        
        return pd.DataFrame(results)
    
    def generate_summary_report(self, df, sentiment_df):
        """生成分析摘要報告"""
        report = {
            'total_posts': len(df),
            'analysis_time': datetime.now().isoformat(),
            'sentiment_distribution': sentiment_df['sentiment'].value_counts().to_dict(),
            'stance_distribution': sentiment_df['recall_stance'].value_counts().to_dict(),
            'average_sentiment_score': sentiment_df['sentiment_score'].mean(),
            'sentiment_by_source': {},
            'stance_by_source': {}
        }
        
        # 按來源分析
        if 'source' in df.columns:
            for source in df['source'].unique():
                source_mask = df['source'] == source
                source_sentiment = sentiment_df[source_mask]
                
                report['sentiment_by_source'][source] = {
                    'count': len(source_sentiment),
                    'sentiment_dist': source_sentiment['sentiment'].value_counts().to_dict(),
                    'stance_dist': source_sentiment['recall_stance'].value_counts().to_dict(),
                    'avg_sentiment': source_sentiment['sentiment_score'].mean()
                }
        
        return report
    
    def create_visualizations(self, df, sentiment_df, save_path='sentiment_analysis.png'):
        """創建視覺化圖表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 情緒分布
        sentiment_counts = sentiment_df['sentiment'].value_counts()
        axes[0, 0].pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('情緒分布')
        
        # 2. 罷免立場分布
        stance_counts = sentiment_df['recall_stance'].value_counts()
        axes[0, 1].pie(stance_counts.values, labels=stance_counts.index, autopct='%1.1f%%')
        axes[0, 1].set_title('罷免立場分布')
        
        # 3. 情緒分數分布
        axes[1, 0].hist(sentiment_df['sentiment_score'], bins=20, alpha=0.7)
        axes[1, 0].set_xlabel('情緒分數')
        axes[1, 0].set_ylabel('頻率')
        axes[1, 0].set_title('情緒分數分布')
        
        # 4. 按來源分析
        if 'source' in df.columns:
            source_sentiment = df.groupby('source').apply(
                lambda x: sentiment_df.loc[x.index]['sentiment_score'].mean()
            )
            axes[1, 1].bar(source_sentiment.index, source_sentiment.values)
            axes[1, 1].set_xlabel('資料來源')
            axes[1, 1].set_ylabel('平均情緒分數')
            axes[1, 1].set_title('各來源平均情緒分數')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"視覺化圖表已儲存至 {save_path}")

def main():
    """主要執行函數"""
    analyzer = SentimentAnalyzer()
    
    # 尋找最新的資料檔案
    import glob
    import os
    
    ptt_files = glob.glob("ptt_data_*.csv")
    dcard_files = glob.glob("dcard_data_*.csv")
    
    all_data = []
    
    # 載入PTT資料
    if ptt_files:
        latest_ptt = max(ptt_files, key=os.path.getctime)
        print(f"載入PTT資料: {latest_ptt}")
        ptt_df = pd.read_csv(latest_ptt)
        all_data.append(ptt_df)
    
    # 載入Dcard資料
    if dcard_files:
        latest_dcard = max(dcard_files, key=os.path.getctime)
        print(f"載入Dcard資料: {latest_dcard}")
        dcard_df = pd.read_csv(latest_dcard)
        all_data.append(dcard_df)
    
    if not all_data:
        print("找不到資料檔案，請先執行爬蟲程式")
        return
    
    # 合併資料
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"總共載入 {len(combined_df)} 筆資料")
    
    # 執行情緒分析
    sentiment_results = analyzer.analyze_dataframe(combined_df)
    
    # 合併結果
    final_df = pd.concat([combined_df.reset_index(drop=True), sentiment_results], axis=1)
    
    # 儲存結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"sentiment_analysis_results_{timestamp}.csv"
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"分析結果已儲存至 {output_file}")
    
    # 生成報告
    report = analyzer.generate_summary_report(combined_df, sentiment_results)
    
    print("\n=== 情緒分析摘要報告 ===")
    print(f"總文章數: {report['total_posts']}")
    print(f"情緒分布: {report['sentiment_distribution']}")
    print(f"罷免立場分布: {report['stance_distribution']}")
    print(f"平均情緒分數: {report['average_sentiment_score']:.3f}")
    
    # 創建視覺化
    analyzer.create_visualizations(combined_df, sentiment_results)
    
    return final_df, report

if __name__ == "__main__":
    main()
