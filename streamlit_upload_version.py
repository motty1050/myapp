"""
都道府県別高齢化率可視化アプリ - ファイルアップロード版
Streamlitを使用した日本の高齢化率の地域差分析
実際の政府統計データ（住民基本台帳人口移動報告書）をアップロード対応
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile
import os

# ページ設定
st.set_page_config(
    page_title="日本の高齢化率分析 - アップロード版",
    page_icon="👴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
# タイトル
st.title("🧓 日本の高齢化率分析ツール（2015-2024年）")
st.markdown("### 実データアップロード対応版")

def get_region(prefecture):
    """都道府県を地域に分類（正式な8地域区分）"""
    # 都道府県名から県・府・都・道を除去して比較
    pref_clean = prefecture.replace('県', '').replace('府', '').replace('都', '').replace('道', '')
    
    regions = {
        "北海道": ["北海道"],
        "東北": ["青森", "岩手", "宮城", "秋田", "山形", "福島"],
        "関東": ["茨城", "栃木", "群馬", "埼玉", "千葉", "東京", "神奈川"],
        "中部": ["新潟", "富山", "石川", "福井", "山梨", "長野", "岐阜", "静岡", "愛知"],
        "近畿": ["三重", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山"],
        "中国": ["鳥取", "島根", "岡山", "広島", "山口"],
        "四国": ["徳島", "香川", "愛媛", "高知"],
        "九州": ["福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"]
    }
    
    for region, prefs in regions.items():
        if pref_clean in prefs:
            return region
    return "その他"

def load_uploaded_files(uploaded_files):
    """
    アップロードされたExcelファイルを処理して統合データフレームを作成
    """
    all_data = []
    
    for uploaded_file in uploaded_files:
        try:
            # ファイル名から年を抽出
            filename = uploaded_file.name
            st.write(f"📁 処理中: {filename}")
            
            # 年の抽出（複数パターンに対応）
            year = None
            if filename.startswith("15"):
                year = 2015
            elif filename.startswith("16"):
                year = 2016
            elif filename.startswith("17"):
                year = 2017
            elif filename.startswith("18"):
                year = 2018
            elif filename.startswith("19"):
                year = 2019
            elif filename.startswith("20"):
                year = 2020
            elif filename.startswith("21"):
                year = 2021
            elif filename.startswith("22"):
                year = 2022
            elif filename.startswith("23"):
                year = 2023
            elif filename.startswith("24"):
                year = 2024
            else:
                # ファイル名から年を推測
                for y in range(2015, 2025):
                    if str(y) in filename or str(y-2000) in filename:
                        year = y
                        break
            
            if year is None:
                st.warning(f"⚠️ {filename}: 年が特定できません（スキップ）")
                continue
            
            # Excelファイルを読み込み
            try:
                # 複数のシートを試行
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                st.write(f"利用可能なシート: {sheet_names}")
                
                df = None
                for sheet_name in sheet_names:
                    try:
                        # ヘッダー行を自動検出
                        for header_row in [0, 1, 2]:
                            test_df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header_row)
                            if len(test_df) > 10:  # 十分なデータがある場合
                                df = test_df
                                st.write(f"✅ シート '{sheet_name}' (ヘッダー行: {header_row}) を使用")
                                break
                        if df is not None:
                            break
                    except Exception as e:
                        continue
                
                if df is not None:
                    # データクリーニングと標準化
                    processed_df = clean_and_standardize_data(df, year, filename)
                    if processed_df is not None and not processed_df.empty:
                        all_data.append(processed_df)
                        st.success(f"✅ {year}年のデータを正常に処理しました（{len(processed_df)}行）")
                    else:
                        st.warning(f"⚠️ {filename}: データの処理に失敗しました")
                else:
                    st.error(f"❌ {filename}: 読み込み可能なシートが見つかりません")
            
            except Exception as e:
                st.error(f"❌ {filename}: ファイル読み込みエラー - {str(e)}")
                continue
                
        except Exception as e:
            st.error(f"❌ ファイル処理エラー: {str(e)}")
            continue
    
    if all_data:
        # 全データを結合
        combined_data = pd.concat(all_data, ignore_index=True)
        st.success(f"🎉 {len(all_data)}ファイルのデータを統合しました（総計{len(combined_data)}行）")
        return combined_data
    else:
        st.error("❌ アップロードされたファイルの処理に失敗しました")
        return None

def clean_and_standardize_data(df, year, filename):
    """
    データのクリーニングと標準化
    """
    try:
        st.write(f"📊 {filename} - 原データ形状: {df.shape}")
        
        # 空行や不要行を除去
        df = df.dropna(how='all')
        
        # データフレームの内容を確認
        st.write("列名一覧:", list(df.columns)[:10])  # 最初の10列のみ表示
        
        # 都道府県名を含む列を特定
        prefecture_col = None
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ['都道府県', 'prefecture', '地域', '自治体', '団体']):
                prefecture_col = col
                st.write(f"都道府県列として '{col}' を使用")
                break
        
        if prefecture_col is None:
            # 最初の列を都道府県として仮定
            prefecture_col = df.columns[0]
            st.write(f"都道府県列として最初の列 '{prefecture_col}' を使用")
        
        # 人口関連列を特定
        population_cols = []
        age_cols = []
        
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ['人口', 'population', '総数', 'total']) and not any(exclude in col_str for exclude in ['65歳', '高齢']):
                population_cols.append(col)
            elif any(keyword in col_str for keyword in ['65歳以上', '65歳～', '高齢者', 'elderly', 'aged']):
                age_cols.append(col)
        
        st.write(f"人口列候補: {population_cols[:3]}")  # 最初の3つのみ表示
        st.write(f"高齢者人口列候補: {age_cols[:3]}")
        
        # 基本データフレーム作成
        result_df = pd.DataFrame()
        result_df['都道府県'] = df[prefecture_col]
        result_df['年'] = year
        
        # 人口データの処理
        if population_cols:
            result_df['総人口'] = pd.to_numeric(df[population_cols[0]], errors='coerce')
        else:
            # サンプルデータ（実際のデータが見つからない場合）
            st.warning("⚠️ 総人口データが見つかりません。サンプルデータを使用します。")
            result_df['総人口'] = np.random.randint(500000, 13000000, len(df))
        
        # 高齢者人口データの処理
        if age_cols:
            result_df['65歳以上人口'] = pd.to_numeric(df[age_cols[0]], errors='coerce')
        else:
            # サンプルデータ（実際のデータが見つからない場合）
            st.warning("⚠️ 65歳以上人口データが見つかりません。推定値を使用します。")
            result_df['65歳以上人口'] = result_df['総人口'] * np.random.uniform(0.20, 0.35, len(df))
        
        # 高齢化率計算
        result_df['高齢化率'] = (result_df['65歳以上人口'] / result_df['総人口'] * 100).round(2)
        
        # 都道府県名の標準化（県・府・都・道を残す）
        result_df['都道府県'] = result_df['都道府県'].astype(str)
        # 不要な文字列を除去（但し、都道府県は保持）
        result_df['都道府県'] = result_df['都道府県'].str.strip()
        result_df['都道府県'] = result_df['都道府県'].str.replace(r'^\d+\.?\s*', '', regex=True)  # 先頭の数字を除去
        result_df['都道府県'] = result_df['都道府県'].str.replace('計', '')  # 「計」を除去
        
        # 地域分類を追加
        result_df['地域'] = result_df['都道府県'].apply(get_region)
        
        # 不正なデータを除去
        result_df = result_df[result_df['都道府県'].notna()]
        result_df = result_df[result_df['都道府県'] != 'nan']
        result_df = result_df[result_df['都道府県'] != '']
        result_df = result_df[~result_df['都道府県'].str.contains('全国|合計|総計', na=False)]  # 全国計などを除去
        result_df = result_df[result_df['総人口'] > 0]
        result_df = result_df[result_df['高齢化率'] >= 0]
        result_df = result_df[result_df['高齢化率'] <= 100]
        
        # 正式な都道府県名のリストで検証
        valid_prefectures = [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
        ]
        
        # 都道府県名の修正を試行
        for i, pref in result_df['都道府県'].items():
            if pref not in valid_prefectures:
                # 部分一致で正しい都道府県名を探す
                for valid_pref in valid_prefectures:
                    if any(part in pref for part in [valid_pref.replace('県', ''), valid_pref.replace('府', ''), valid_pref.replace('都', ''), valid_pref.replace('道', '')]):
                        result_df.loc[i, '都道府県'] = valid_pref
                        break
        
        # 有効な都道府県のみを保持
        result_df = result_df[result_df['都道府県'].isin(valid_prefectures)]
        
        # 47都道府県に限定（合計行などを除去）
        if len(result_df) > 47:
            result_df = result_df.head(47)
        
        st.write(f"処理後データ形状: {result_df.shape}")
        return result_df
        
    except Exception as e:
        st.error(f"データクリーニングエラー: {str(e)}")
        return None

@st.cache_data
def load_sample_data():
    """サンプルデータを生成（実際の統計データの代替）"""
    prefectures = [
        "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
        "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
        "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
        "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
        "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
        "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
        "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
    ]
    
    years = list(range(2015, 2025))  # 2015-2024年のデータ
    data = []
    
    # 都道府県ごとの基準高齢化率を設定（2015年現実的な値）
    base_rates = {
        "秋田県": 33.0, "高知県": 32.5, "島根県": 32.0, "山口県": 31.8,
        "徳島県": 31.5, "和歌山県": 31.2, "鳥取県": 31.0, "愛媛県": 30.8,
        "岩手県": 30.5, "山形県": 30.3, "青森県": 30.0, "佐賀県": 29.8,
        "長崎県": 29.5, "熊本県": 29.3, "大分県": 29.0, "宮崎県": 28.8,
        "鹿児島県": 28.5, "北海道": 28.2, "福島県": 28.0, "新潟県": 27.8,
        "群馬県": 27.5, "富山県": 27.3, "石川県": 27.0, "福井県": 26.8,
        "長野県": 26.5, "岐阜県": 26.3, "静岡県": 26.0, "三重県": 25.8,
        "栃木県": 25.5, "茨城県": 25.3, "山梨県": 25.0, "香川県": 24.8,
        "広島県": 24.5, "岡山県": 24.3, "京都府": 24.0, "兵庫県": 23.8,
        "宮城県": 23.5, "福岡県": 23.3, "滋賀県": 23.0, "奈良県": 22.8,
        "大阪府": 22.5, "千葉県": 22.3, "愛知県": 22.0, "神奈川県": 21.8,
        "埼玉県": 21.5, "東京都": 21.0, "沖縄県": 20.0
    }
    
    for pref in prefectures:
        base_rate = base_rates.get(pref, 27.0)
        for year in years:
            # 年次増加率（現実的な高齢化進行を反映）
            year_factor = (year - 2015) * 0.6  # 年間約0.6%ずつ増加
            # ランダムノイズ
            noise = np.random.normal(0, 0.5)
            rate = base_rate + year_factor + noise
            
            # 総人口（現実的な規模）
            if pref == "東京都":
                total_pop = np.random.randint(13000000, 14000000)
            elif pref in ["神奈川県", "大阪府"]:
                total_pop = np.random.randint(8000000, 10000000)
            elif pref in ["愛知県", "埼玉県", "千葉県"]:
                total_pop = np.random.randint(5000000, 8000000)
            elif pref in ["北海道", "兵庫県", "福岡県"]:
                total_pop = np.random.randint(3000000, 6000000)
            else:
                total_pop = np.random.randint(500000, 3000000)
            
            elderly_pop = int(total_pop * rate / 100)
            
            data.append({
                "都道府県": pref,
                "年": year,
                "総人口": total_pop,
                "65歳以上人口": elderly_pop,
                "高齢化率": round(rate, 1),
                "地域": get_region(pref)
            })
    
    return pd.DataFrame(data)

# メインアプリケーション
st.sidebar.header("🔧 分析オプション")

# データソース選択
data_source = st.sidebar.radio(
    "データソースを選択",
    ["Excelファイルアップロード", "サンプルデータ"],
    index=0,
    help="実際の政府統計データをアップロードするか、検証用サンプルデータを使用"
)

df = None

if data_source == "Excelファイルアップロード":
    st.sidebar.markdown("### 📁 ファイルアップロード")
    uploaded_files = st.sidebar.file_uploader(
        "Excelファイルを選択（複数年対応）",
        type=['xls', 'xlsx'],
        accept_multiple_files=True,
        help="住民基本台帳人口移動報告書のExcelファイルをアップロードしてください"
    )
    
    if uploaded_files:
        with st.sidebar:
            st.write("🔄 ファイル処理中...")
            df = load_uploaded_files(uploaded_files)
    else:
        st.info("📋 政府統計データ（住民基本台帳人口移動報告書）のExcelファイルをアップロードしてください。")
        st.markdown("""
        **対応ファイル例:**
        - 1502stnen.xls (2015年)
        - 1602stnen.xls (2016年)  
        - 2102stnen.xlsx (2021年)
        - 24stnen.xlsx (2024年)
        
        **データソース:** 総務省統計局 e-Stat
        """)

else:
    st.sidebar.write("🎲 サンプルデータを読み込み中...")
    df = load_sample_data()

# データが読み込まれた場合のみ処理を続行
if df is not None and not df.empty:
    # 年範囲選択（データに応じて動的に調整）
    available_years = sorted(df["年"].unique())
    year_range = st.sidebar.slider(
        "年範囲を選択",
        min_value=min(available_years),
        max_value=max(available_years),
        value=(min(available_years), max(available_years)),
        step=1
    )

    # 都道府県選択（高齢化率順でソート）
    selected_prefs = st.sidebar.multiselect(
        "特定都道府県を選択（空白で全て）",
        options=sorted(df["都道府県"].unique()),
        default=[]
    )

    # 地域選択（地域列が存在する場合）
    if "地域" in df.columns:
        selected_regions = st.sidebar.multiselect(
            "地域を選択（空白で全て）",
            options=sorted(df["地域"].unique()),
            default=[]
        )
    else:
        selected_regions = []

    # データフィルタリング
    filtered_df = df[
        (df["年"] >= year_range[0]) & 
        (df["年"] <= year_range[1])
    ]

    if selected_prefs:
        filtered_df = filtered_df[filtered_df["都道府県"].isin(selected_prefs)]

    if selected_regions and "地域" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["地域"].isin(selected_regions)]

    # メイン分析
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "分析対象都道府県数",
            len(filtered_df["都道府県"].unique()),
            delta=None
        )

    with col2:
        if len(filtered_df) > 0:
            latest_year_data = filtered_df[filtered_df['年'] == year_range[1]]
            earliest_year_data = filtered_df[filtered_df['年'] == year_range[0]]
            
            if len(latest_year_data) > 0 and len(earliest_year_data) > 0:
                latest_avg = latest_year_data['高齢化率'].mean()
                earliest_avg = earliest_year_data['高齢化率'].mean()
                delta = latest_avg - earliest_avg
                
                st.metric(
                    "平均高齢化率（最新年）",
                    f"{latest_avg:.1f}%",
                    delta=f"{delta:.1f}%"
                )
            else:
                st.metric("平均高齢化率", "データなし")
        else:
            st.metric("平均高齢化率", "データなし")

    with col3:
        if len(filtered_df) > 0:
            st.metric(
                "総データ件数",
                f"{len(filtered_df):,}件",
                delta=None
            )

    # 可視化セクション
    st.header("📊 データ可視化")

    # データが存在する場合のみ可視化を実行
    if len(filtered_df) > 0:
        # タブで分析を分割
        tab1, tab2, tab3, tab4 = st.tabs(["📈 時系列推移", "🗾 地域比較", "📊 ランキング", "🔍 詳細分析"])

        with tab1:
            st.subheader("都道府県別高齢化率の時系列推移")
            
            # インタラクティブな線グラフ
            fig = px.line(
                filtered_df,
                x="年",
                y="高齢化率",
                color="都道府県",
                title="都道府県別高齢化率の推移",
                hover_data=["地域"] if "地域" in filtered_df.columns else None,
                height=600
            )
            
            fig.update_layout(
                xaxis_title="年",
                yaxis_title="高齢化率 (%)",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 地域別平均推移（地域列が存在する場合のみ）
            if "地域" in filtered_df.columns:
                st.subheader("地域別平均高齢化率の推移")
                
                region_avg = filtered_df.groupby(["年", "地域"])["高齢化率"].mean().reset_index()
                
                fig2 = px.line(
                    region_avg,
                    x="年",
                    y="高齢化率",
                    color="地域",
                    title="地域別平均高齢化率の推移",
                    markers=True,
                    height=500
                )
                
                st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            st.subheader("地域間格差の分析")
            
            if "地域" in filtered_df.columns:
                # 箱ひげ図
                fig3 = px.box(
                    filtered_df,
                    x="地域",
                    y="高齢化率",
                    title="地域別高齢化率の分布",
                    height=500
                )
                
                fig3.update_xaxes(tickangle=45)
                st.plotly_chart(fig3, use_container_width=True)
                
                # ヒートマップ（年×地域）
                st.subheader("年×地域ヒートマップ")
                
                heatmap_data = filtered_df.groupby(["年", "地域"])["高齢化率"].mean().unstack()
                
                fig4 = px.imshow(
                    heatmap_data.T,
                    title="年別地域別平均高齢化率",
                    color_continuous_scale="YlOrRd",
                    height=400
                )
                
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("地域情報が利用できません。実データでは地域分析が可能です。")

        with tab3:
            st.subheader("高齢化率ランキング")
            
            # 最新年のランキング
            latest_year = year_range[1]
            latest_data = filtered_df[filtered_df["年"] == latest_year].sort_values("高齢化率", ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{latest_year}年 高齢化率上位10都道府県**")
                if "地域" in latest_data.columns:
                    top_10 = latest_data.head(10)[["都道府県", "高齢化率", "地域"]]
                else:
                    top_10 = latest_data.head(10)[["都道府県", "高齢化率"]]
                st.dataframe(top_10.reset_index(drop=True), use_container_width=True)
            
            with col2:
                st.write(f"**{latest_year}年 高齢化率下位10都道府県**")
                if "地域" in latest_data.columns:
                    bottom_10 = latest_data.tail(10)[["都道府県", "高齢化率", "地域"]]
                else:
                    bottom_10 = latest_data.tail(10)[["都道府県", "高齢化率"]]
                st.dataframe(bottom_10.reset_index(drop=True), use_container_width=True)
            
            # 棒グラフ
            fig5 = px.bar(
                latest_data.head(15),
                x="高齢化率",
                y="都道府県",
                color="地域" if "地域" in latest_data.columns else None,
                title=f"{latest_year}年 高齢化率上位15都道府県",
                orientation="h",
                height=600
            )
            
            fig5.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig5, use_container_width=True)

        with tab4:
            st.subheader("詳細統計分析")
            
            # 変化率分析
            change_analysis = []
            for pref in filtered_df["都道府県"].unique():
                pref_data = filtered_df[filtered_df["都道府県"] == pref].sort_values("年")
                if len(pref_data) >= 2:
                    start_rate = pref_data.iloc[0]["高齢化率"]
                    end_rate = pref_data.iloc[-1]["高齢化率"]
                    change = end_rate - start_rate
                    change_rate = (change / start_rate) * 100 if start_rate > 0 else 0
                    
                    change_analysis.append({
                        "都道府県": pref,
                        "地域": pref_data.iloc[0]["地域"] if "地域" in pref_data.columns else "不明",
                        f"{year_range[0]}年": start_rate,
                        f"{year_range[1]}年": end_rate,
                        "増加ポイント": round(change, 1),
                        "増加率": round(change_rate, 1)
                    })
            
            if change_analysis:  # データが存在する場合のみ処理
                change_df = pd.DataFrame(change_analysis).sort_values("増加ポイント", ascending=False)
                
                st.write("**期間中の高齢化率変化分析**")
                st.dataframe(change_df, use_container_width=True)
                
                # 変化率の可視化
                # sizeパラメータには正の値のみ使用するため、絶対値を使用
                change_df_for_plot = change_df.copy()
                change_df_for_plot['増加率_絶対値'] = abs(change_df_for_plot['増加率'])
                
                fig6 = px.scatter(
                    change_df_for_plot,
                    x=f"{year_range[0]}年",
                    y="増加ポイント",
                    color="地域" if "地域" in change_df_for_plot.columns else None,
                    size="増加率_絶対値",
                    hover_data=["都道府県", "増加率"],
                    title="高齢化率の変化パターン",
                    height=500
                )
                
                st.plotly_chart(fig6, use_container_width=True)
            else:
                st.info("変化分析のためのデータが不足しています。")
            
            # 統計サマリー
            st.subheader("統計サマリー")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("最高高齢化率", f"{filtered_df['高齢化率'].max():.1f}%")
            
            with col2:
                st.metric("最低高齢化率", f"{filtered_df['高齢化率'].min():.1f}%")
            
            with col3:
                st.metric("標準偏差", f"{filtered_df['高齢化率'].std():.1f}")
            
            with col4:
                st.metric("格差（最大-最小）", f"{filtered_df['高齢化率'].max() - filtered_df['高齢化率'].min():.1f}%")

        # データダウンロード
        st.header("📥 データダウンロード")

        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df_to_csv(filtered_df)

        st.download_button(
            label="📊 フィルタリング済みデータをCSVでダウンロード",
            data=csv,
            file_name=f'aging_rate_data_{year_range[0]}_{year_range[1]}.csv',
            mime='text/csv',
        )
    else:
        st.warning("⚠️ フィルター条件に一致するデータがありません。")

else:
    if data_source == "Excelファイルアップロード":
        st.info("👆 サイドバーからExcelファイルをアップロードしてください。")
    else:
        st.error("❌ データの読み込みに失敗しました。")

# フッター
st.markdown("---")
st.markdown(f"""
**データについて**: 
- 実際の政府統計データ: 総務省「住民基本台帳人口移動報告書」
- サンプルデータ: 現実的な傾向を反映したデモ用データ

**ファイル形式**: 政府統計データ（e-Stat）Excel形式 (.xls/.xlsx)

**開発**: CUDA画像分類システム - 高齢化率分析拡張機能  
**バージョン**: ファイルアップロード対応版
""")
