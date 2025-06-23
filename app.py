import streamlit as st
import pandas as pd
import os
from plot_stock_chart import get_data_dir, feature_engineering, plot_chart

# ページ設定
st.set_page_config(layout="wide")
st.title("BTC/USD リアルタイムOHLCチャート (1分足)")

# データファイルのパスを取得
try:
    DATA_DIR = get_data_dir()
    data_path = os.path.join(DATA_DIR, "ohlc_1min_realtime.csv")

    # ファイルの存在確認
    if not os.path.exists(data_path):
        st.error(f"データファイルが見つかりません: {data_path}")
        st.info("`realtime_ohlc_collector.py` を実行してデータを生成してください。")
    else:
        # データの読み込み
        df = pd.read_csv(data_path)

        # 特徴量エンジニアリング
        df_featured = feature_engineering(df.copy())

        # チャートの生成
        st.header("ローソク足チャート")
        fig = plot_chart(df_featured)
        st.plotly_chart(fig, use_container_width=True)

        # データテーブルの表示（オプション）
        st.header("データ詳細")
        if st.checkbox("生データを表示"):
            st.write("### 生データ (最新5件)")
            st.dataframe(df.tail())
        
        if st.checkbox("テクニカル指標付きデータを表示"):
            st.write("### テクニカル指標付きデータ (最新5件)")
            st.dataframe(df_featured.tail())

except FileNotFoundError as e:
    st.error(e)
except Exception as e:
    st.error(f"アプリケーションの実行中に予期せぬエラーが発生しました: {e}") 