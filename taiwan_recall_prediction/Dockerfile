# 使用官方Python 3.9 slim映像作為基礎
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=Asia/Taipei

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    unzip \
    gnupg \
    fonts-liberation \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-noto-cjk \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxss1 \
    libgconf-2-4 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安裝Chrome瀏覽器 (用於Selenium) - 簡化版本，不安裝Chrome以加快建構
# 如果需要Selenium功能，可以取消註解以下行
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
#     && echo "deb [arch=amd64] [signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
#     && apt-get update \
#     && apt-get install -y google-chrome-stable \
#     && rm -rf /var/lib/apt/lists/*

# 複製requirements.txt並安裝Python依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 建立資料目錄
RUN mkdir -p /app/data /app/logs /app/output

# 設定權限
RUN chmod +x *.py

# 暴露Streamlit預設端口
EXPOSE 8501

# 建立啟動腳本
RUN echo '#!/bin/bash\n\
echo "🗳️ 台灣罷免預測分析系統 - Docker版本"\n\
echo "================================"\n\
\n\
# 檢查是否有現有資料\n\
if [ ! -f "/app/data/analysis_complete.flag" ]; then\n\
    echo "📊 首次執行，開始資料收集與分析..."\n\
    \n\
    echo "🕷️ 執行PTT爬蟲..."\n\
    python ptt_crawler.py\n\
    \n\
    echo "🕷️ 執行Dcard爬蟲..."\n\
    python dcard_crawler.py\n\
    \n\
    echo "😊 執行情緒分析..."\n\
    python sentiment_analyzer.py\n\
    \n\
    echo "🎯 執行MECE分析..."\n\
    python mece_analyzer.py\n\
    \n\
    # 標記分析完成\n\
    touch /app/data/analysis_complete.flag\n\
    echo "✅ 初始分析完成！"\n\
else\n\
    echo "📊 發現現有分析資料，直接啟動Dashboard"\n\
fi\n\
\n\
echo "🌐 啟動Streamlit Dashboard..."\n\
echo "Dashboard將在 http://localhost:8501 開啟"\n\
streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8501\n\
' > /app/start.sh && chmod +x /app/start.sh

# 預設命令
CMD ["/app/start.sh"]
