# get_data/fetch_info.py

import json
import sqlite3
import yfinance as yf
from datetime import datetime
from get_data.common import get_db_path, can_fetch, update_fetch_time

DIMENSION = "INFO"

def run(ticker_symbol: str):
    """
    拉取并存储 ticker.info。若 1 小时内拉取过，则跳过。
    """
    if not can_fetch(ticker_symbol, DIMENSION, cooldown_minutes=60):
        print(f"[SKIP] {ticker_symbol}'s info: fetched within 1 hour.")
        return

    print(f"[INFO] Fetch info for {ticker_symbol}")

    ticker = yf.Ticker(ticker_symbol)
    info_dict = ticker.info
    if not info_dict:
        print(f"[WARN] No info data for {ticker_symbol}")
        return

    info_json = json.dumps(info_dict, ensure_ascii=False)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    insert_sql = """
    INSERT OR REPLACE INTO stock_info (ticker, info_json, last_update)
    VALUES (?, ?, ?)
    """
    cursor.execute(insert_sql, (ticker_symbol, info_json, now_str))
    conn.commit()
    conn.close()

    print(f"[INFO] Updated info for {ticker_symbol}")
    update_fetch_time(ticker_symbol, DIMENSION)

