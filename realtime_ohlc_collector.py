import pybitflyer
import pandas as pd
from datetime import datetime, timezone, timedelta
import time
import os

# --- 設定 ---
PRODUCT_CODE = "BTC_JPY"
# APIのレート制限を考慮し、データ取得間隔を2秒に設定します。
FETCH_INTERVAL_SECONDS = 2
OHLC_FILEPATH = "ohlc_1min_realtime.csv"
RAW_TICKS_FILEPATH = "raw_ticks_backup.csv"
OHLC_HEADER = ['timestamp', 'open', 'high', 'low', 'close']
TICK_HEADER = ['timestamp', 'best_ask', 'best_bid', 'ltp']

def initialize_csv(filepath, header):
    """ファイルが存在しない場合にヘッダーを書き込む"""
    if not os.path.exists(filepath):
        pd.DataFrame(columns=header).to_csv(filepath, index=False)
        print(f"'{filepath}' を作成し、ヘッダーを書き込みました。")

def main():
    """
    リアルタイムでティックデータを取得し、1分足のOHLCを生成してCSVに追記する。
    """
    api = pybitflyer.API()
    
    initialize_csv(OHLC_FILEPATH, OHLC_HEADER)
    initialize_csv(RAW_TICKS_FILEPATH, TICK_HEADER)
    
    print("リアルタイムデータ収集・処理を開始します...")
    print(f"データ取得間隔: {FETCH_INTERVAL_SECONDS}秒 | OHLC出力ファイル: {OHLC_FILEPATH}")
    print("Ctrl+Cでスクリプトを安全に停止します。")
    
    try:
        while True:
            ticks_buffer = []
            
            # 現在の処理対象となる「分」の開始時刻と終了時刻を決定
            now_utc = datetime.now(timezone.utc)
            current_minute_start = now_utc.replace(second=0, microsecond=0)
            next_minute_start = current_minute_start + timedelta(minutes=1)
            
            print(f"\n{current_minute_start.strftime('%Y-%m-%d %H:%M')} のデータ収集を開始...")
            
            # --- 次の1分になるまで、ティックデータを収集 ---
            while datetime.now(timezone.utc) < next_minute_start:
                loop_start_time = time.time()
                try:
                    ticker = api.ticker(product_code=PRODUCT_CODE)
                    ticks_buffer.append({key: ticker.get(key) for key in TICK_HEADER})
                    print(f"  取得: LTP = {ticker['ltp']}", end='\r', flush=True)
                except Exception as e:
                    print(f"\nAPIエラー: {e}")
                
                elapsed_time = time.time() - loop_start_time
                time.sleep(max(0, FETCH_INTERVAL_SECONDS - elapsed_time))

            # --- 1分経過したので、収集したデータを処理 ---
            if not ticks_buffer:
                print("\n  この1分間に取得できたデータはありませんでした。")
                continue

            print(f"\n  集計処理中 ({len(ticks_buffer)}件)...")
            
            # ティックデータをDataFrameに変換
            df_ticks = pd.DataFrame(ticks_buffer)
            
            # 生データをバックアップファイルに追記
            df_ticks.to_csv(RAW_TICKS_FILEPATH, mode='a', header=False, index=False)

            # OHLCを計算
            df_ticks['timestamp'] = pd.to_datetime(df_ticks['timestamp'], format='ISO8601')
            ltp = df_ticks['ltp'].astype(float)
            
            ohlc_data = pd.DataFrame([{
                'timestamp': current_minute_start.strftime('%Y-%m-%d %H:%M:%S'),
                'open': ltp.iloc[0],
                'high': ltp.max(),
                'low': ltp.min(),
                'close': ltp.iloc[-1]
            }])
            
            # 計算したOHLCをファイルに追記
            ohlc_data.to_csv(OHLC_FILEPATH, mode='a', header=False, index=False)
            print("  OHLCデータを保存しました。")

    except KeyboardInterrupt:
        print("\n\nスクリプトを停止します。")
    except Exception as e:
        print(f"\n予期せぬエラーで停止しました: {e}")

if __name__ == "__main__":
    main() 