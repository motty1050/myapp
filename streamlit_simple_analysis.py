"""
単一ファイル対応・高齢化率分析アプリ
実際のExcelファイルやサンプルデータの詳細分析に対応
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ページ設定
st.set_page_config(
    page_title="高齢化率分析 - シンプル版",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
st.title("📊 都道府県別高齢化率分析")
st.markdown("### シンプル分析版")

def get_region(prefecture):
    """都道府県を地域に分類"""
    regions = {
        "北海道": ["北海道"],
        "東北": ["青森", "岩手", "宮城", "秋田", "山形", "福島"],
        "関東": ["茨城", "栃木", "群馬", "埼玉", "千葉", "東京", "神奈川"],
        "中部": ["新潟", "富山", "石川", "福井", "山梨", "長野", "岐阜", "静岡", "愛知"],
        "関西": ["三重", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山"],
        "中国": ["鳥取", "島根", "岡山", "広島", "山口"],
        "四国": ["徳島", "香川", "愛媛", "高知"],
        "九州": ["福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"]
    }
    
    for region, prefs in regions.items():
        if prefecture in prefs:
            return region
    return "その他"

def load_and_analyze_file(uploaded_file):
    """
    アップロードされたExcelファイルを分析
    """
    try:
        st.write(f"📁 処理中: {uploaded_file.name}")
        
        # Excelファイルの内容を確認
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        st.write("### ファイル情報")
        st.write(f"**ファイル名**: {uploaded_file.name}")
        st.write(f"**シート数**: {len(sheet_names)}")
        st.write(f"**シート名**: {', '.join(sheet_names)}")
        
        # シート選択
        selected_sheet = st.selectbox(
            "分析するシートを選択:",
            sheet_names,
            index=0
        )
        
        # ヘッダー行選択
        header_row = st.selectbox(
            "ヘッダー行を選択:",
            [0, 1, 2, 3],
            index=1,
            help="0=1行目, 1=2行目..."
        )
        
        # データ読み込み
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, header=header_row)
        
        st.write("### データプレビュー")
        st.write(f"**データ形状**: {df.shape[0]}行 × {df.shape[1]}列")
        
        # 最初の10行を表示
        st.dataframe(df.head(10))
        
        st.write("### 列情報")
        cols_info = []
        for i, col in enumerate(df.columns):
            sample_values = df[col].dropna().head(3).tolist()
            cols_info.append({
                "列番号": i,
                "列名": str(col),
                "データ型": str(df[col].dtype),
                "非NULL数": df[col].count(),
                "サンプル値": str(sample_values)[:100]
            })
        
        cols_df = pd.DataFrame(cols_info)
        st.dataframe(cols_df)
        
        # 列選択
        st.write("### データ列の選択")
        
        col1, col2 = st.columns(2)
        
        with col1:
            prefecture_col = st.selectbox(
                "都道府県列を選択:",
                df.columns,
                index=0
            )
            
            population_col = st.selectbox(
                "総人口列を選択:",
                ["なし"] + list(df.columns),
                index=0
            )
        
        with col2:
            elderly_col = st.selectbox(
                "65歳以上人口列を選択:",
                ["なし"] + list(df.columns),
                index=0
            )
            
            aging_rate_col = st.selectbox(
                "高齢化率列を選択（あれば）:",
                ["なし"] + list(df.columns),
                index=0
            )
        
        if st.button("データを分析"):
            return analyze_data(df, prefecture_col, population_col, elderly_col, aging_rate_col)
        
        return None
        
    except Exception as e:
        st.error(f"ファイル読み込みエラー: {str(e)}")
        return None

def analyze_data(df, prefecture_col, population_col, elderly_col, aging_rate_col):
    """
    選択された列でデータを分析
    """
    try:
        # 基本データフレーム作成
        result_df = pd.DataFrame()
        result_df['都道府県'] = df[prefecture_col].astype(str)
        
        # 人口データの処理
        if population_col != "なし":
            result_df['総人口'] = pd.to_numeric(df[population_col], errors='coerce')
        else:
            st.warning("総人口データが指定されていません。サンプル値を使用します。")
            result_df['総人口'] = np.random.randint(500000, 13000000, len(df))
        
        # 高齢者人口データの処理
        if elderly_col != "なし":
            result_df['65歳以上人口'] = pd.to_numeric(df[elderly_col], errors='coerce')
        else:
            st.warning("65歳以上人口データが指定されていません。推定値を使用します。")
            result_df['65歳以上人口'] = result_df['総人口'] * np.random.uniform(0.20, 0.35, len(df))
        
        # 高齢化率の処理
        if aging_rate_col != "なし":
            result_df['高齢化率'] = pd.to_numeric(df[aging_rate_col], errors='coerce')
        else:
            result_df['高齢化率'] = (result_df['65歳以上人口'] / result_df['総人口'] * 100).round(2)
        
        # 都道府県名の標準化
        result_df['都道府県'] = result_df['都道府県'].str.replace('県', '').str.replace('府', '').str.replace('都', '').str.replace('道', '')
        
        # 地域分類を追加
        result_df['地域'] = result_df['都道府県'].apply(get_region)
        
        # データクリーニング
        result_df = result_df[result_df['都道府県'].notna()]
        result_df = result_df[result_df['都道府県'] != 'nan']
        result_df = result_df[result_df['総人口'] > 0]
        result_df = result_df[(result_df['高齢化率'] >= 0) & (result_df['高齢化率'] <= 100)]
        
        st.success(f"✅ {len(result_df)}件のデータを処理しました")
        
        return result_df
        
    except Exception as e:
        st.error(f"データ分析エラー: {str(e)}")
        return None

def create_sample_data():
    """
    現実的なサンプルデータを生成
    """
    prefectures = [
        "北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島",
        "茨城", "栃木", "群馬", "埼玉", "千葉", "東京", "神奈川",
        "新潟", "富山", "石川", "福井", "山梨", "長野", "岐阜",
        "静岡", "愛知", "三重", "滋賀", "京都", "大阪", "兵庫",
        "奈良", "和歌山", "鳥取", "島根", "岡山", "広島", "山口",
        "徳島", "香川", "愛媛", "高知", "福岡", "佐賀", "長崎",
        "熊本", "大分", "宮崎", "鹿児島", "沖縄"
    ]
    
    # 2024年の現実的な高齢化率
    aging_rates = {
        "秋田": 37.4, "高知": 36.3, "島根": 35.1, "山口": 34.7,
        "徳島": 34.4, "和歌山": 34.0, "鳥取": 33.8, "愛媛": 33.5,
        "岩手": 33.2, "山形": 32.9, "青森": 32.6, "佐賀": 32.3,
        "長崎": 32.0, "熊本": 31.7, "大分": 31.4, "宮崎": 31.1,
        "鹿児島": 30.8, "北海道": 30.5, "福島": 30.2, "新潟": 29.9,
        "群馬": 29.6, "富山": 29.3, "石川": 29.0, "福井": 28.7,
        "長野": 28.4, "岐阜": 28.1, "静岡": 27.8, "三重": 27.5,
        "栃木": 27.2, "茨城": 26.9, "山梨": 26.6, "香川": 26.3,
        "広島": 26.0, "岡山": 25.7, "京都": 25.4, "兵庫": 25.1,
        "宮城": 24.8, "福岡": 24.5, "滋賀": 24.2, "奈良": 23.9,
        "大阪": 23.6, "千葉": 23.3, "愛知": 23.0, "神奈川": 22.7,
        "埼玉": 22.4, "東京": 22.1, "沖縄": 21.8
    }
    
    data = []
    for pref in prefectures:
        aging_rate = aging_rates.get(pref, 25.0) + np.random.normal(0, 0.5)
        
        # 総人口（現実的な規模）
        if pref == "東京":
            total_pop = np.random.randint(13500000, 14000000)
        elif pref in ["神奈川", "大阪"]:
            total_pop = np.random.randint(8500000, 9500000)
        elif pref in ["愛知", "埼玉", "千葉"]:
            total_pop = np.random.randint(6000000, 7500000)
        elif pref in ["北海道", "兵庫", "福岡"]:
            total_pop = np.random.randint(4000000, 5500000)
        else:
            total_pop = np.random.randint(600000, 3000000)
        
        elderly_pop = int(total_pop * aging_rate / 100)
        
        data.append({
            "都道府県": pref,
            "総人口": total_pop,
            "65歳以上人口": elderly_pop,
            "高齢化率": round(aging_rate, 1),
            "地域": get_region(pref)
        })
    
    return pd.DataFrame(data)

# メインアプリケーション
st.sidebar.header("🔧 分析設定")

# データソース選択
data_source = st.sidebar.radio(
    "データソースを選択:",
    ["Excelファイル", "サンプルデータ"],
    index=1
)

df = None

if data_source == "Excelファイル":
    uploaded_file = st.sidebar.file_uploader(
        "Excelファイルを選択",
        type=['xls', 'xlsx'],
        help="住民基本台帳人口移動報告書や類似データ"
    )
    
    if uploaded_file is not None:
        df = load_and_analyze_file(uploaded_file)
    else:
        st.info("👆 サイドバーからExcelファイルをアップロードしてください。")

else:
    df = create_sample_data()
    st.success("✅ サンプルデータを読み込みました")

# データが存在する場合の分析
if df is not None and not df.empty:
    
    # データ概要
    st.header("📋 データ概要")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("都道府県数", len(df))
    
    with col2:
        st.metric("平均高齢化率", f"{df['高齢化率'].mean():.1f}%")
    
    with col3:
        st.metric("最高高齢化率", f"{df['高齢化率'].max():.1f}%")
    
    with col4:
        st.metric("最低高齢化率", f"{df['高齢化率'].min():.1f}%")
    
    # 可視化
    st.header("📊 可視化分析")
    
    tab1, tab2, tab3 = st.tabs(["📊 ランキング", "🗾 地域分析", "📈 分布分析"])
    
    with tab1:
        st.subheader("高齢化率ランキング")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**上位10都道府県**")
            top_10 = df.nlargest(10, '高齢化率')[['都道府県', '高齢化率', '地域']]
            st.dataframe(top_10.reset_index(drop=True), use_container_width=True)
        
        with col2:
            st.write("**下位10都道府県**")
            bottom_10 = df.nsmallest(10, '高齢化率')[['都道府県', '高齢化率', '地域']]
            st.dataframe(bottom_10.reset_index(drop=True), use_container_width=True)
        
        # 棒グラフ
        fig = px.bar(
            df.sort_values('高齢化率', ascending=True),
            x='高齢化率',
            y='都道府県',
            color='地域',
            title="都道府県別高齢化率",
            orientation='h',
            height=1200
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("地域別分析")
        
        # 地域別統計
        region_stats = df.groupby('地域')['高齢化率'].agg(['mean', 'std', 'min', 'max']).round(1)
        region_stats.columns = ['平均', '標準偏差', '最小', '最大']
        st.dataframe(region_stats)
        
        # 箱ひげ図
        fig2 = px.box(
            df,
            x='地域',
            y='高齢化率',
            title="地域別高齢化率の分布",
            height=500
        )
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)
        
        # 地域別平均
        region_avg = df.groupby('地域')['高齢化率'].mean().reset_index()
        fig3 = px.bar(
            region_avg,
            x='地域',
            y='高齢化率',
            title="地域別平均高齢化率",
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab3:
        st.subheader("分布分析")
        
        # ヒストグラム
        fig4 = px.histogram(
            df,
            x='高齢化率',
            nbins=20,
            title="高齢化率の分布",
            height=400
        )
        st.plotly_chart(fig4, use_container_width=True)
        
        # 散布図（人口 vs 高齢化率）
        fig5 = px.scatter(
            df,
            x='総人口',
            y='高齢化率',
            color='地域',
            size='65歳以上人口',
            hover_data=['都道府県'],
            title="総人口 vs 高齢化率",
            height=500
        )
        st.plotly_chart(fig5, use_container_width=True)
        
        # 統計サマリー
        st.subheader("統計サマリー")
        st.write(df[['総人口', '65歳以上人口', '高齢化率']].describe())
    
    # データテーブル
    st.header("📋 全データ")
    
    # フィルター
    selected_regions = st.multiselect(
        "地域でフィルター:",
        df['地域'].unique(),
        default=df['地域'].unique()
    )
    
    filtered_df = df[df['地域'].isin(selected_regions)]
    
    # ソート
    sort_by = st.selectbox(
        "並び替え:",
        ['高齢化率', '総人口', '65歳以上人口', '都道府県'],
        index=0
    )
    
    ascending = st.checkbox("昇順", value=False)
    
    sorted_df = filtered_df.sort_values(sort_by, ascending=ascending)
    
    st.dataframe(sorted_df, use_container_width=True)
    
    # ダウンロード
    st.header("📥 データダウンロード")
    
    csv = sorted_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 データをCSVでダウンロード",
        data=csv,
        file_name='aging_rate_analysis.csv',
        mime='text/csv'
    )

# フッター
st.markdown("---")
st.markdown("""
**このアプリについて**: 
都道府県別の高齢化率データを分析・可視化するツールです。
実際の政府統計データやサンプルデータに対応しています。

**開発**: CUDA画像分類システム - 高齢化率分析拡張機能
""")
