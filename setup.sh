#!/bin/bash

# ML推論アプリ開発用スクリプト

echo "🚀 ML推論アプリの開発環境セットアップ"

# バックエンドのセットアップ
echo "📦 バックエンド（Django）のセットアップ..."
cd backend

# 仮想環境の作成（既に存在する場合はスキップ）
if [ ! -d "venv" ]; then
    echo "🐍 Python仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境の有効化
echo "🔄 仮想環境を有効化中..."
source venv/bin/activate

# 依存関係のインストール
echo "📥 Python依存関係をインストール中..."
pip install -r requirements.txt

# データベースマイグレーション
echo "🗃️ データベースマイグレーションを実行中..."
python manage.py makemigrations
python manage.py migrate

# サンプルデータの作成
echo "🌱 サンプルデータを作成中..."
python manage.py shell << EOF
from inference.models import MLApp

# サンプルMLアプリの作成
if not MLApp.objects.exists():
    MLApp.objects.create(
        name='画像分類モデル',
        description='画像をアップロードして分類します',
        endpoint='image-classification'
    )
    MLApp.objects.create(
        name='テキスト感情分析',
        description='テキストの感情を分析します',
        endpoint='sentiment-analysis'
    )
    MLApp.objects.create(
        name='数値予測モデル',
        description='数値データから予測を行います',
        endpoint='numerical-prediction'
    )
    print("サンプルMLアプリを作成しました")
else:
    print("MLアプリは既に存在します")
EOF

echo "✅ バックエンドのセットアップが完了しました"

# フロントエンドのセットアップ
echo "📦 フロントエンド（React）のセットアップ..."
cd ../frontend

# Node.jsとnpmの確認
if ! command -v npm &> /dev/null; then
    echo "❌ npm が見つかりません。Node.jsをインストールしてください。"
    echo "   Ubuntu/Debian: sudo apt install npm"
    echo "   macOS: brew install node"
    exit 1
fi

# 依存関係のインストール
echo "📥 Node.js依存関係をインストール中..."
npm install

echo "✅ フロントエンドのセットアップが完了しました"

cd ..

echo "🎉 セットアップが完了しました！"
echo ""
echo "🔧 開発サーバーの起動方法:"
echo "  バックエンド: cd backend && source venv/bin/activate && python manage.py runserver"
echo "  フロントエンド: cd frontend && npm start"
echo ""
echo "🌐 アクセスURL:"
echo "  フロントエンド: http://localhost:3000"
echo "  バックエンドAPI: http://localhost:8000/api/"
echo "  Django管理画面: http://localhost:8000/admin/"
