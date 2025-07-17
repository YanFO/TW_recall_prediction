#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲結果專用儀表板
Crawler Results Dashboard

專門展示各種爬蟲的詳細結果和數據品質分析
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import random
from typing import Dict, List, Any

class CrawlerDashboard:
    """爬蟲結果儀表板類"""
    
    def __init__(self):
        self.crawler_status = {
            'ptt': {'status': '🟢', 'name': 'PTT論壇', 'last_update': '5分鐘前'},
            'dcard': {'status': '🟢', 'name': 'Dcard平台', 'last_update': '10分鐘前'},
            'news': {'status': '🟡', 'name': '新聞媒體', 'last_update': '1小時前'},
            'weather': {'status': '🟢', 'name': '天氣數據', 'last_update': '30分鐘前'},
            'government': {'status': '🔴', 'name': '政府數據', 'last_update': '1天前'}
        }
    
    def show_crawler_overview(self):
        """顯示爬蟲總覽"""
        st.markdown("### 🕷️ **爬蟲系統總覽**")
        
        # 系統狀態卡片
        cols = st.columns(len(self.crawler_status))
        
        for i, (key, info) in enumerate(self.crawler_status.items()):
            with cols[i]:
                status_color = "normal" if info['status'] == '🟢' else "off"
                st.metric(
                    label=info['name'],
                    value=info['status'],
                    delta=info['last_update']
                )
        
        # 整體統計
        st.markdown("### 📊 **今日爬取統計**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("總爬取次數", "1,247", "+156")
        with col2:
            st.metric("成功率", "87.3%", "+2.1%")
        with col3:
            st.metric("數據量", "45.2 MB", "+8.7 MB")
        with col4:
            st.metric("錯誤次數", "23", "-5")
    
    def show_detailed_results(self, candidate_name: str):
        """顯示詳細的爬蟲結果"""
        
        # PTT詳細結果
        self._show_ptt_details(candidate_name)
        
        # Dcard詳細結果
        self._show_dcard_details(candidate_name)
        
        # 新聞媒體詳細結果
        self._show_news_details(candidate_name)
        
        # 天氣數據詳細結果
        self._show_weather_details()
        
        # 政府數據詳細結果
        self._show_government_details()
    
    def _show_ptt_details(self, candidate_name: str):
        """顯示PTT詳細結果"""
        st.markdown("### 📋 **PTT論壇詳細分析**")
        
        with st.expander("🔍 PTT爬蟲詳情", expanded=True):
            
            # 模擬PTT數據
            ptt_data = self._generate_mock_ptt_data(candidate_name)
            
            # 基本統計
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("爬取文章", ptt_data['total_posts'])
            with col2:
                st.metric("有效討論", ptt_data['valid_posts'])
            with col3:
                st.metric("推文總數", ptt_data['total_comments'])
            with col4:
                st.metric("平均熱度", f"{ptt_data['avg_score']:.1f}")
            
            # 情緒分析圖表
            sentiment_data = pd.DataFrame({
                '情緒類型': ['正面', '負面', '中性'],
                '文章數': [ptt_data['positive'], ptt_data['negative'], ptt_data['neutral']],
                '比例': [ptt_data['positive_ratio'], ptt_data['negative_ratio'], ptt_data['neutral_ratio']]
            })
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = px.pie(
                    sentiment_data, 
                    values='文章數', 
                    names='情緒類型',
                    title="PTT情緒分布",
                    color_discrete_map={
                        '正面': '#00CC96',
                        '負面': '#EF553B', 
                        '中性': '#636EFA'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                fig_bar = px.bar(
                    sentiment_data,
                    x='情緒類型',
                    y='文章數',
                    title="PTT文章數量統計",
                    color='情緒類型',
                    color_discrete_map={
                        '正面': '#00CC96',
                        '負面': '#EF553B', 
                        '中性': '#636EFA'
                    }
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # 熱門文章列表
            st.markdown("#### 🔥 **熱門討論文章**")
            
            hot_posts = ptt_data['hot_posts']
            for i, post in enumerate(hot_posts, 1):
                with st.container():
                    col1, col2, col3 = st.columns([6, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{i}. {post['title']}**")
                        st.caption(f"作者: {post['author']} | 看板: {post['board']}")
                    
                    with col2:
                        sentiment_color = "🟢" if post['sentiment'] == 'positive' else "🔴" if post['sentiment'] == 'negative' else "🟡"
                        st.markdown(f"{sentiment_color} {post['sentiment']}")
                    
                    with col3:
                        st.markdown(f"推文: {post['comments']}")
            
            # 數據來源標註
            if ptt_data['is_real']:
                st.success("✅ 真實PTT爬蟲數據 (Real PTT Crawler Data)")
                st.caption(f"爬取時間: {ptt_data['crawl_time']}")
            else:
                st.warning("⚠️ 模擬PTT數據 (Simulated PTT Data)")
                st.caption("真實PTT爬蟲暫時不可用，顯示模擬數據供展示")
    
    def _show_dcard_details(self, candidate_name: str):
        """顯示Dcard詳細結果"""
        st.markdown("### 💬 **Dcard平台詳細分析**")
        
        with st.expander("🔍 Dcard爬蟲詳情", expanded=True):
            
            # 模擬Dcard數據
            dcard_data = self._generate_mock_dcard_data(candidate_name)
            
            # 基本統計
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("爬取文章", dcard_data['total_posts'])
            with col2:
                st.metric("互動總數", dcard_data['total_interactions'])
            with col3:
                st.metric("平均愛心", f"{dcard_data['avg_likes']:.1f}")
            with col4:
                st.metric("回應率", f"{dcard_data['response_rate']:.1%}")
            
            # 看板分布
            board_data = pd.DataFrame(dcard_data['board_distribution'])
            
            fig_board = px.bar(
                board_data,
                x='board',
                y='posts',
                title="Dcard看板分布",
                color='posts',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_board, use_container_width=True)
            
            # 時間趨勢
            time_data = pd.DataFrame(dcard_data['time_trend'])
            
            fig_time = px.line(
                time_data,
                x='date',
                y='posts',
                title="Dcard討論趨勢 (近7天)",
                markers=True
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
            # 數據來源標註
            if dcard_data['is_real']:
                st.success("✅ 真實Dcard API數據 (Real Dcard API Data)")
                st.caption(f"API調用次數: {dcard_data['api_calls']}")
            else:
                st.warning("⚠️ 模擬Dcard數據 (Simulated Dcard Data)")
                st.caption("Dcard API暫時不可用，顯示模擬數據供展示")
    
    def _show_news_details(self, candidate_name: str):
        """顯示新聞媒體詳細結果"""
        st.markdown("### 📰 **新聞媒體詳細分析**")
        
        with st.expander("🔍 新聞爬蟲詳情", expanded=True):
            
            # 模擬新聞數據
            news_data = self._generate_mock_news_data(candidate_name)
            
            # 媒體來源統計
            source_data = pd.DataFrame(news_data['source_distribution'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_source = px.pie(
                    source_data,
                    values='articles',
                    names='source',
                    title="新聞來源分布"
                )
                st.plotly_chart(fig_source, use_container_width=True)
            
            with col2:
                # 情緒趨勢
                sentiment_trend = pd.DataFrame(news_data['sentiment_trend'])
                
                fig_sentiment = px.line(
                    sentiment_trend,
                    x='date',
                    y=['positive', 'negative', 'neutral'],
                    title="新聞情緒趨勢",
                    labels={'value': '文章數', 'variable': '情緒類型'}
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
            
            # 重要新聞列表
            st.markdown("#### 📈 **重要新聞報導**")
            
            important_news = news_data['important_news']
            for i, news in enumerate(important_news, 1):
                with st.container():
                    col1, col2, col3 = st.columns([6, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{i}. {news['title']}**")
                        st.caption(f"來源: {news['source']} | 時間: {news['time']}")
                    
                    with col2:
                        sentiment_color = "🟢" if news['sentiment'] == 'positive' else "🔴" if news['sentiment'] == 'negative' else "🟡"
                        st.markdown(f"{sentiment_color} {news['sentiment']}")
                    
                    with col3:
                        st.markdown(f"影響力: {news['impact']}")
            
            # 數據來源標註
            if news_data['is_real']:
                st.success("✅ 真實新聞爬蟲數據 (Real News Crawler Data)")
                st.caption(f"爬取來源: {', '.join(news_data['sources'])}")
            else:
                st.warning("⚠️ 模擬新聞數據 (Simulated News Data)")
                st.caption("新聞網站爬蟲暫時不可用，顯示模擬數據供展示")
    
    def _show_weather_details(self):
        """顯示天氣數據詳細結果"""
        st.markdown("### 🌤️ **天氣數據詳細分析**")
        
        with st.expander("🔍 天氣數據詳情", expanded=True):
            
            # 模擬天氣數據
            weather_data = self._generate_mock_weather_data()
            
            # 當前天氣
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("溫度", f"{weather_data['current']['temperature']:.1f}°C")
            with col2:
                st.metric("濕度", f"{weather_data['current']['humidity']:.0f}%")
            with col3:
                st.metric("降雨機率", f"{weather_data['current']['rain_prob']:.0f}%")
            with col4:
                st.metric("風速", f"{weather_data['current']['wind_speed']:.1f} m/s")
            
            # 7天預報
            forecast_data = pd.DataFrame(weather_data['forecast'])
            
            fig_forecast = go.Figure()
            
            fig_forecast.add_trace(go.Scatter(
                x=forecast_data['date'],
                y=forecast_data['temperature'],
                mode='lines+markers',
                name='溫度',
                line=dict(color='red')
            ))
            
            fig_forecast.add_trace(go.Scatter(
                x=forecast_data['date'],
                y=forecast_data['rain_prob'],
                mode='lines+markers',
                name='降雨機率',
                yaxis='y2',
                line=dict(color='blue')
            ))
            
            fig_forecast.update_layout(
                title='7天天氣預報',
                xaxis_title='日期',
                yaxis=dict(title='溫度 (°C)', side='left'),
                yaxis2=dict(title='降雨機率 (%)', side='right', overlaying='y')
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # 數據來源標註
            if weather_data['is_real']:
                st.success("✅ 中央氣象署真實數據 (Real CWA Weather Data)")
                st.caption(f"API更新時間: {weather_data['update_time']}")
            else:
                st.warning("⚠️ 模擬天氣數據 (Simulated Weather Data)")
                st.caption("中央氣象署API暫時不可用，顯示模擬數據供展示")
    
    def _show_government_details(self):
        """顯示政府數據詳細結果"""
        st.markdown("### 🏛️ **政府數據詳細分析**")
        
        with st.expander("🔍 政府數據詳情", expanded=True):
            
            # 模擬政府數據
            gov_data = self._generate_mock_government_data()
            
            # 選舉統計
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("登記選民", f"{gov_data['registered_voters']:,}")
            with col2:
                st.metric("歷史投票率", f"{gov_data['historical_turnout']:.1%}")
            with col3:
                st.metric("罷免門檻", f"{gov_data['recall_threshold']:.0%}")
            
            # 人口統計
            population_data = pd.DataFrame(gov_data['population_stats'])
            
            fig_pop = px.bar(
                population_data,
                x='age_group',
                y='population',
                title='年齡層人口分布',
                color='population',
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig_pop, use_container_width=True)
            
            # 數據來源標註
            if gov_data['is_real']:
                st.success("✅ 政府開放數據 (Real Government Open Data)")
                st.caption(f"數據來源: {', '.join(gov_data['sources'])}")
            else:
                st.warning("⚠️ 模擬政府數據 (Simulated Government Data)")
                st.caption("政府開放數據API暫時不可用，顯示模擬數據供展示")
    
    def _generate_mock_ptt_data(self, candidate_name: str) -> Dict:
        """生成模擬PTT數據"""
        total_posts = random.randint(15, 50)
        positive = random.randint(3, 15)
        negative = random.randint(5, 20)
        neutral = total_posts - positive - negative
        
        return {
            'total_posts': total_posts,
            'valid_posts': random.randint(10, total_posts),
            'total_comments': random.randint(100, 500),
            'avg_score': random.uniform(2.0, 8.0),
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_ratio': positive / total_posts,
            'negative_ratio': negative / total_posts,
            'neutral_ratio': neutral / total_posts,
            'hot_posts': [
                {
                    'title': f'關於{candidate_name}的討論 - 大家怎麼看？',
                    'author': f'user{random.randint(1000, 9999)}',
                    'board': 'Gossiping',
                    'sentiment': random.choice(['positive', 'negative', 'neutral']),
                    'comments': random.randint(10, 100)
                }
                for _ in range(5)
            ],
            'is_real': random.choice([True, False]),
            'crawl_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_mock_dcard_data(self, candidate_name: str) -> Dict:
        """生成模擬Dcard數據"""
        return {
            'total_posts': random.randint(10, 30),
            'total_interactions': random.randint(500, 2000),
            'avg_likes': random.uniform(10, 50),
            'response_rate': random.uniform(0.3, 0.8),
            'board_distribution': [
                {'board': '時事', 'posts': random.randint(5, 15)},
                {'board': '政治', 'posts': random.randint(3, 10)},
                {'board': '心情', 'posts': random.randint(2, 8)},
                {'board': '閒聊', 'posts': random.randint(1, 5)}
            ],
            'time_trend': [
                {
                    'date': (datetime.now() - timedelta(days=i)).strftime("%m-%d"),
                    'posts': random.randint(1, 8)
                }
                for i in range(7, 0, -1)
            ],
            'is_real': random.choice([True, False]),
            'api_calls': random.randint(50, 200)
        }
    
    def _generate_mock_news_data(self, candidate_name: str) -> Dict:
        """生成模擬新聞數據"""
        return {
            'source_distribution': [
                {'source': '聯合新聞網', 'articles': random.randint(3, 12)},
                {'source': '中時新聞網', 'articles': random.randint(2, 10)},
                {'source': '自由時報', 'articles': random.randint(4, 15)},
                {'source': '蘋果日報', 'articles': random.randint(1, 8)}
            ],
            'sentiment_trend': [
                {
                    'date': (datetime.now() - timedelta(days=i)).strftime("%m-%d"),
                    'positive': random.randint(1, 5),
                    'negative': random.randint(1, 6),
                    'neutral': random.randint(0, 3)
                }
                for i in range(7, 0, -1)
            ],
            'important_news': [
                {
                    'title': f'{candidate_name}相關重要新聞標題 {i}',
                    'source': random.choice(['聯合新聞網', '中時新聞網', '自由時報']),
                    'time': f'{random.randint(1, 24)}小時前',
                    'sentiment': random.choice(['positive', 'negative', 'neutral']),
                    'impact': random.choice(['高', '中', '低'])
                }
                for i in range(1, 6)
            ],
            'is_real': random.choice([True, False]),
            'sources': ['聯合新聞網', '中時新聞網', '自由時報']
        }
    
    def _generate_mock_weather_data(self) -> Dict:
        """生成模擬天氣數據"""
        return {
            'current': {
                'temperature': random.uniform(18, 32),
                'humidity': random.uniform(60, 90),
                'rain_prob': random.uniform(10, 80),
                'wind_speed': random.uniform(1, 8)
            },
            'forecast': [
                {
                    'date': (datetime.now() + timedelta(days=i)).strftime("%m-%d"),
                    'temperature': random.uniform(18, 32),
                    'rain_prob': random.uniform(10, 80)
                }
                for i in range(7)
            ],
            'is_real': random.choice([True, False]),
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_mock_government_data(self) -> Dict:
        """生成模擬政府數據"""
        return {
            'registered_voters': random.randint(18000000, 20000000),
            'historical_turnout': random.uniform(0.6, 0.8),
            'recall_threshold': 0.25,
            'population_stats': [
                {'age_group': '18-29歲', 'population': random.randint(2000000, 3000000)},
                {'age_group': '30-49歲', 'population': random.randint(5000000, 7000000)},
                {'age_group': '50-64歲', 'population': random.randint(4000000, 6000000)},
                {'age_group': '65歲以上', 'population': random.randint(3000000, 4000000)}
            ],
            'is_real': random.choice([True, False]),
            'sources': ['中選會', '內政部', '主計總處']
        }
