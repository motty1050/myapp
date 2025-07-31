# ML推論アプリケーション

Django + React を使用した機械学習推論アプリケーションです。

## プロジェクト構成

```
myapp/
├── backend/           # Django バックエンド
│   ├── backend/       # Django設定
│   ├── inference/     # ML推論アプリ
│   └── requirements.txt
├── frontend/          # React フロントエンド
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## セットアップ

### バックエンド (Django)

1. 仮想環境の作成・有効化
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

3. データベースマイグレーション
```bash
python manage.py makemigrations
python manage.py migrate
```

4. スーパーユーザーの作成（オプション）
```bash
python manage.py createsuperuser
```

5. 開発サーバーの起動
```bash
python manage.py runserver
```

### フロントエンド (React)

1. 依存関係のインストール
```bash
cd frontend
npm install
```

2. 開発サーバーの起動
```bash
npm start
```

## 使用方法

1. バックエンドサーバー: http://localhost:8000
2. フロントエンドアプリ: http://localhost:3000
3. Django管理画面: http://localhost:8000/admin

## API エンドポイント

- `GET /api/ml-apps/` - MLアプリ一覧取得
- `POST /api/ml-apps/{id}/predict/` - 推論実行
- `GET /api/logs/` - 推論ログ一覧取得

## 機能

- ✅ MLアプリの管理
- ✅ 推論の実行
- ✅ 推論ログの記録
- ✅ Reactフロントエンド
- ✅ REST API
- ✅ CORS対応
- ✅ Streamlit高齢化率分析アプリ
- ✅ 政府統計データ対応
- ✅ 日本語ローカライゼーション

## Streamlitアプリ

### 高齢化率分析アプリ

- `streamlit_aging_analysis.py` - メイン版（政府統計データ対応）
- `streamlit_upload_version.py` - ファイルアップロード版
- `streamlit_simple_analysis.py` - シンプル版

実行方法:

```bash
# メイン版
streamlit run streamlit_aging_analysis.py

# ファイルアップロード版
streamlit run streamlit_upload_version.py --server.port 8503
```

詳細は `README_streamlit.md` を参照してください。

## 今後の拡張予定

- [ ] 実際のMLモデルの統合
- [ ] ユーザー認証
- [ ] ファイルアップロード機能
- [ ] リアルタイム推論
- [ ] 推論結果の可視化
