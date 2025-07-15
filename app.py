#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣罷免預測系統 - Streamlit Cloud 部署版本
Taiwan Recall Prediction System - Streamlit Cloud Deployment
"""

import sys
import os

# 添加taiwan_recall_prediction目錄到Python路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'taiwan_recall_prediction'))

# 導入主應用
try:
    from taiwan_recall_prediction.dashboard import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    import streamlit as st
    st.error(f"導入錯誤: {e}")
    st.info("請確保所有依賴包都已正確安裝")
