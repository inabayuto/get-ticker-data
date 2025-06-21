# %%
import pandas as pd
from datetime import datetime, timedelta
import os
from plotly.graph_objs import *

# %% データディレクトリの設定
def get_data_dir():
    """データディレクトリのパスを取得する"""
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # データディレクトリのパスを構築
    data_dir = os.path.join(script_dir)
    return data_dir

# %% 特徴量エンジニアリング
def feature_engineering(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['time'] = df['timestamp'].dt.time

    # 移動平均線の算出
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()

    # ボリンジャーバンドの算出
    df['std'] = df['close'].rolling(window=20).std()
    df['upper_band'] = df['ma20'] + (df['std'] * 2)
    df['lower_band'] = df['ma20'] - (df['std'] * 2)
    return df

# %% チャートの描画
def plot_chart(df):
    
    trace1 = {
        'type': 'candlestick', 
        'x': df['timestamp'], 
        'yaxis': "y2",
        'low': df['low'], 
        'high': df['high'], 
        'open': df['open'], 
        'close': df['close']
    }
    trace2 = {
        'line': {'width': 1}, 
        'mode': 'lines', 
        'name': 'mean 20', 
        'type': 'scatter', 
        'x': df['timestamp'], 
        'y': df['ma20'], 
        'yaxis': 'y2', 
        'marker': {'color': '#E377C2'}
    }
    trace3 = {
        'line': {'width': 1}, 
        'mode': 'lines', 
        'name': 'upper band', 
        'type': 'scatter', 
        'x': df['timestamp'], 
        'y': df['upper_band'], 
        'yaxis': 'y2', 
        'marker': {'color': '#CCC'},
        'legendgroup': 'BB', 
    }
    trace4 = {
        'line': {'width': 1}, 
        'mode': 'lines', 
        'name': 'lower band', 
        'type': 'scatter', 
        'x': df['timestamp'], 
        'y': df['lower_band'], 
        'yaxis': 'y2', 
        'marker': {'color': '#CCC'},
        'legendgroup': 'BB', 
    }
    fig = Figure(data=[trace1, trace2, trace3, trace4])
    return fig.show()


# %% メイン処理
def main():
    # データディレクトリの設定
    DATA_DIR = get_data_dir()
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"データディレクトリが見つかりません: {DATA_DIR}\n現在の作業ディレクトリ: {os.getcwd()}")
    
    # データの読み込み
    data_path = os.path.join(DATA_DIR, "ohlc_1min_realtime.csv")
    df = pd.read_csv(data_path)
    df = feature_engineering(df)
    plot_chart(df)
    # データの確認
    return df

if __name__ == "__main__":
    main()


# %%
