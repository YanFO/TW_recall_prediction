#!/bin/bash

# 台灣罷免預測分析系統 - Docker 快速啟動腳本

echo "🗳️ 台灣罷免預測分析系統 - Docker版本"
echo "========================================"

# 檢查Docker是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安裝，請先安裝Docker"
    echo "下載地址: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 檢查Docker Compose是否安裝
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安裝，請先安裝Docker Compose"
    exit 1
fi

# 建立必要目錄
echo "📁 建立必要目錄..."
mkdir -p data output logs

# 設定目錄權限
chmod 755 data output logs

echo "🔧 選擇啟動模式:"
echo "1. 完整版 (包含資料庫和定時任務)"
echo "2. 簡化版 (僅主要分析應用)"
echo "3. 僅Dashboard (使用現有資料)"
echo "4. 停止所有服務"
echo "5. 查看服務狀態"
echo "6. 查看日誌"

read -p "請選擇 (1-6): " choice

case $choice in
    1)
        echo "🚀 啟動完整版服務..."
        docker-compose up -d
        echo "✅ 服務啟動完成!"
        echo "📊 Dashboard: http://localhost:8501"
        echo "🗄️ PostgreSQL: localhost:5432"
        echo "🔴 Redis: localhost:6379"
        ;;
    2)
        echo "🚀 啟動簡化版服務..."
        docker-compose up -d recall-analyzer
        echo "✅ 服務啟動完成!"
        echo "📊 Dashboard: http://localhost:8501"
        ;;
    3)
        echo "🚀 僅啟動Dashboard..."
        docker-compose up -d recall-analyzer
        docker-compose exec recall-analyzer streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8501
        ;;
    4)
        echo "🛑 停止所有服務..."
        docker-compose down
        echo "✅ 所有服務已停止"
        ;;
    5)
        echo "📊 服務狀態:"
        docker-compose ps
        ;;
    6)
        echo "📋 選擇要查看的日誌:"
        echo "1. 主要應用"
        echo "2. 定時任務"
        echo "3. 資料庫"
        echo "4. Redis"
        read -p "請選擇 (1-4): " log_choice
        
        case $log_choice in
            1) docker-compose logs -f recall-analyzer ;;
            2) docker-compose logs -f scheduler ;;
            3) docker-compose logs -f postgres ;;
            4) docker-compose logs -f redis ;;
            *) echo "❌ 無效選擇" ;;
        esac
        ;;
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

# 顯示有用的命令
echo ""
echo "🔧 常用命令:"
echo "查看服務狀態: docker-compose ps"
echo "查看日誌: docker-compose logs -f [服務名]"
echo "進入容器: docker-compose exec recall-analyzer bash"
echo "停止服務: docker-compose down"
echo "重新建構: docker-compose build --no-cache"
echo "清理資料: docker-compose down -v"
