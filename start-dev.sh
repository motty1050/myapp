#!/bin/bash

# 開発サーバー起動スクリプト

echo "🚀 ML推論アプリの開発サーバーを起動します..."

# ターミナルウィンドウでバックエンドサーバーを起動
echo "📡 バックエンドサーバーを起動中..."
cd backend
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!
cd ..

# 少し待ってからフロントエンドサーバーを起動
echo "⏳ バックエンドサーバーの起動を待機中..."
sleep 3

echo "🎨 フロントエンドサーバーを起動中..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ 両方のサーバーが起動しました！"
echo ""
echo "🌐 アクセスURL:"
echo "  フロントエンド: http://localhost:3000"
echo "  バックエンドAPI: http://localhost:8000/api/"
echo "  Django管理画面: http://localhost:8000/admin/"
echo ""
echo "🛑 サーバーを停止するには Ctrl+C を押してください"

# シグナルハンドラーでプロセスを終了
trap 'echo "🛑 サーバーを停止中..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT

# 両方のプロセスが終了するまで待機
wait
