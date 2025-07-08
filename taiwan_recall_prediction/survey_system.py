#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣罷免預測 - 問卷調查系統
政治關心度與效能感量表
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from typing import Dict, List
import numpy as np

class SurveySystem:
    """問卷調查系統"""
    
    def __init__(self):
        """初始化問卷系統"""
        self.survey_data = []
        self.load_existing_data()
        
    def load_existing_data(self):
        """載入現有問卷數據"""
        survey_file = 'data/survey_responses.json'
        if os.path.exists(survey_file):
            with open(survey_file, 'r', encoding='utf-8') as f:
                self.survey_data = json.load(f)
    
    def save_survey_data(self):
        """保存問卷數據"""
        os.makedirs('data', exist_ok=True)
        survey_file = 'data/survey_responses.json'
        with open(survey_file, 'w', encoding='utf-8') as f:
            json.dump(self.survey_data, f, ensure_ascii=False, indent=2)
    
    def show_survey_interface(self):
        """顯示問卷調查界面"""
        st.title("📋 政治關心度與效能感調查")
        st.markdown("---")
        
        st.markdown("""
        ### 📝 調查說明
        
        本調查旨在了解民眾對政治事務的關心程度和政治效能感，
        所有回答將用於學術研究，完全匿名且保密。
        
        **預計填答時間**: 約5-8分鐘
        """)
        
        # 基本資料
        st.header("👤 基本資料")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age_group = st.selectbox(
                "年齡層",
                ["18-25歲", "26-35歲", "36-45歲", "46-55歲", "56-65歲", "65歲以上"]
            )
            
            education = st.selectbox(
                "教育程度",
                ["國中以下", "高中職", "專科", "大學", "研究所以上"]
            )
            
            occupation = st.selectbox(
                "職業類別",
                ["學生", "軍公教", "服務業", "製造業", "金融業", "資訊業", "自由業", "退休", "其他"]
            )
        
        with col2:
            region = st.selectbox(
                "居住地區",
                ["台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市", "其他縣市"]
            )
            
            income = st.selectbox(
                "家庭月收入",
                ["3萬以下", "3-5萬", "5-8萬", "8-12萬", "12-20萬", "20萬以上", "不願透露"]
            )
            
            political_party = st.selectbox(
                "政黨傾向",
                ["泛藍", "泛綠", "中間選民", "無特定傾向", "不願透露"]
            )
        
        # 政治關心度量表
        st.header("🧠 政治關心度量表")
        st.markdown("請根據您的實際情況，選擇最符合的選項（1=非常不同意，7=非常同意）")
        
        political_interest_questions = [
            "我經常關注政治新聞和時事",
            "我會主動了解政治人物的政見和表現",
            "我認為政治事務與我的生活息息相關",
            "我會與朋友或家人討論政治議題",
            "我會參與政治相關的活動或集會",
            "我認為每個公民都應該關心政治",
            "我會透過多種管道獲取政治資訊"
        ]
        
        political_interest_scores = []
        for i, question in enumerate(political_interest_questions):
            score = st.slider(
                f"Q{i+1}. {question}",
                min_value=1,
                max_value=7,
                value=4,
                key=f"political_interest_{i}"
            )
            political_interest_scores.append(score)
        
        # 政治效能感量表
        st.header("⚡ 政治效能感量表")
        
        st.subheader("🔹 內在政治效能感")
        st.markdown("評估您對自己政治能力的認知")
        
        internal_efficacy_questions = [
            "我認為自己有能力理解政治議題",
            "我有足夠的政治知識來做出明智的投票決定",
            "我能夠有效地表達自己的政治觀點",
            "我有信心參與政治討論",
            "我認為自己的政治判斷是正確的"
        ]
        
        internal_efficacy_scores = []
        for i, question in enumerate(internal_efficacy_questions):
            score = st.slider(
                f"IE{i+1}. {question}",
                min_value=1,
                max_value=7,
                value=4,
                key=f"internal_efficacy_{i}"
            )
            internal_efficacy_scores.append(score)
        
        st.subheader("🔹 外在政治效能感")
        st.markdown("評估您對政治體系回應性的認知")
        
        external_efficacy_questions = [
            "政府官員關心一般民眾的想法",
            "我的投票能夠影響政府的決策",
            "政治人物會履行競選承諾",
            "政府政策會考慮民眾的需求",
            "透過選舉可以改變政府的方向",
            "民眾的意見對政府決策有影響力"
        ]
        
        external_efficacy_scores = []
        for i, question in enumerate(external_efficacy_questions):
            score = st.slider(
                f"EE{i+1}. {question}",
                min_value=1,
                max_value=7,
                value=4,
                key=f"external_efficacy_{i}"
            )
            external_efficacy_scores.append(score)
        
        # 經濟動機相關問題
        st.header("💰 經濟動機評估")
        
        economic_motivation_questions = [
            "我會因為經濟政策表現而改變投票意向",
            "經濟狀況是我投票時的重要考量",
            "我認為政治決策會直接影響我的經濟狀況",
            "我會因為個人經濟利益而支持特定候選人",
            "經濟議題比其他政治議題更重要"
        ]
        
        economic_motivation_scores = []
        for i, question in enumerate(economic_motivation_questions):
            score = st.slider(
                f"EM{i+1}. {question}",
                min_value=1,
                max_value=7,
                value=4,
                key=f"economic_motivation_{i}"
            )
            economic_motivation_scores.append(score)
        
        # 罷免相關態度
        st.header("🗳️ 罷免態度評估")
        
        recall_attitude_questions = [
            "我認為罷免是民主制度的重要機制",
            "如果政治人物表現不佳，應該被罷免",
            "我會參與罷免投票",
            "我會鼓勵他人參與罷免投票",
            "罷免投票是公民的權利和義務"
        ]
        
        recall_attitude_scores = []
        for i, question in enumerate(recall_attitude_questions):
            score = st.slider(
                f"RA{i+1}. {question}",
                min_value=1,
                max_value=7,
                value=4,
                key=f"recall_attitude_{i}"
            )
            recall_attitude_scores.append(score)
        
        # 提交問卷
        st.markdown("---")
        
        if st.button("📤 提交問卷", type="primary"):
            # 計算各維度分數
            political_interest_avg = np.mean(political_interest_scores)
            internal_efficacy_avg = np.mean(internal_efficacy_scores)
            external_efficacy_avg = np.mean(external_efficacy_scores)
            economic_motivation_avg = np.mean(economic_motivation_scores)
            recall_attitude_avg = np.mean(recall_attitude_scores)
            
            # 創建回應記錄
            response = {
                "timestamp": datetime.now().isoformat(),
                "demographics": {
                    "age_group": age_group,
                    "education": education,
                    "occupation": occupation,
                    "region": region,
                    "income": income,
                    "political_party": political_party
                },
                "scores": {
                    "political_interest": {
                        "individual_scores": political_interest_scores,
                        "average": political_interest_avg
                    },
                    "internal_efficacy": {
                        "individual_scores": internal_efficacy_scores,
                        "average": internal_efficacy_avg
                    },
                    "external_efficacy": {
                        "individual_scores": external_efficacy_scores,
                        "average": external_efficacy_avg
                    },
                    "economic_motivation": {
                        "individual_scores": economic_motivation_scores,
                        "average": economic_motivation_avg
                    },
                    "recall_attitude": {
                        "individual_scores": recall_attitude_scores,
                        "average": recall_attitude_avg
                    }
                }
            }
            
            # 保存回應
            self.survey_data.append(response)
            self.save_survey_data()
            
            # 顯示結果
            st.success("✅ 問卷提交成功！感謝您的參與！")
            
            # 顯示個人結果
            st.header("📊 您的調查結果")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("政治關心度", f"{political_interest_avg:.2f}/7")
                st.metric("內在政治效能感", f"{internal_efficacy_avg:.2f}/7")
            
            with col2:
                st.metric("外在政治效能感", f"{external_efficacy_avg:.2f}/7")
                st.metric("經濟動機", f"{economic_motivation_avg:.2f}/7")
            
            with col3:
                st.metric("罷免態度", f"{recall_attitude_avg:.2f}/7")
            
            # 提供解釋
            st.markdown("### 📈 結果解釋")
            
            if political_interest_avg >= 5.5:
                st.success("🔥 您對政治事務非常關心")
            elif political_interest_avg >= 4:
                st.info("👍 您對政治事務有一定程度的關心")
            else:
                st.warning("💤 您對政治事務關心程度較低")
            
            if (internal_efficacy_avg + external_efficacy_avg) / 2 >= 5:
                st.success("💪 您具有較高的政治效能感")
            elif (internal_efficacy_avg + external_efficacy_avg) / 2 >= 4:
                st.info("👌 您具有中等程度的政治效能感")
            else:
                st.warning("😔 您的政治效能感較低")
    
    def show_survey_analytics(self):
        """顯示問卷分析結果"""
        st.title("📈 問卷調查分析")
        st.markdown("---")
        
        if not self.survey_data:
            st.warning("目前沒有問卷數據")
            return
        
        # 基本統計
        st.header("📊 基本統計")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("總回應數", len(self.survey_data))
        
        with col2:
            # 計算平均政治關心度
            avg_interest = np.mean([
                response['scores']['political_interest']['average'] 
                for response in self.survey_data
            ])
            st.metric("平均政治關心度", f"{avg_interest:.2f}/7")
        
        with col3:
            # 計算平均政治效能感
            avg_efficacy = np.mean([
                (response['scores']['internal_efficacy']['average'] + 
                 response['scores']['external_efficacy']['average']) / 2
                for response in self.survey_data
            ])
            st.metric("平均政治效能感", f"{avg_efficacy:.2f}/7")
        
        # 人口統計分析
        st.header("👥 人口統計分析")
        
        # 轉換為DataFrame進行分析
        demographics_data = []
        scores_data = []
        
        for response in self.survey_data:
            demo = response['demographics'].copy()
            demo['timestamp'] = response['timestamp']
            demographics_data.append(demo)
            
            scores = {
                'timestamp': response['timestamp'],
                'political_interest': response['scores']['political_interest']['average'],
                'internal_efficacy': response['scores']['internal_efficacy']['average'],
                'external_efficacy': response['scores']['external_efficacy']['average'],
                'economic_motivation': response['scores']['economic_motivation']['average'],
                'recall_attitude': response['scores']['recall_attitude']['average']
            }
            scores_data.append(scores)
        
        df_demographics = pd.DataFrame(demographics_data)
        df_scores = pd.DataFrame(scores_data)
        
        # 年齡層分析
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("年齡層分布")
            age_counts = df_demographics['age_group'].value_counts()
            st.bar_chart(age_counts)
        
        with col2:
            st.subheader("地區分布")
            region_counts = df_demographics['region'].value_counts()
            st.bar_chart(region_counts)
        
        # 分數分析
        st.header("📈 分數分析")
        
        # 各維度平均分數
        st.subheader("各維度平均分數")
        
        avg_scores = {
            '政治關心度': df_scores['political_interest'].mean(),
            '內在政治效能感': df_scores['internal_efficacy'].mean(),
            '外在政治效能感': df_scores['external_efficacy'].mean(),
            '經濟動機': df_scores['economic_motivation'].mean(),
            '罷免態度': df_scores['recall_attitude'].mean()
        }
        
        st.bar_chart(avg_scores)
        
        # 相關性分析
        st.subheader("維度間相關性")
        correlation_matrix = df_scores[['political_interest', 'internal_efficacy', 
                                       'external_efficacy', 'economic_motivation', 
                                       'recall_attitude']].corr()
        st.dataframe(correlation_matrix)

def main():
    """主要執行函數"""
    survey_system = SurveySystem()
    
    # 側邊欄選擇
    st.sidebar.title("📋 問卷系統")
    
    mode = st.sidebar.selectbox(
        "選擇模式",
        ["填寫問卷", "查看分析結果"]
    )
    
    if mode == "填寫問卷":
        survey_system.show_survey_interface()
    else:
        survey_system.show_survey_analytics()

if __name__ == "__main__":
    main()
