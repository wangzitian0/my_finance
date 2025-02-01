# get_data/fetch_info.py

import json
import sqlite3
import yfinance as yf
from datetime import datetime

from common import (
    get_db_path,
    can_fetch,
    update_fetch_time,
)

def fetch_info(ticker_symbol: str, cooldown_minutes=60):
    """
    拉取 ticker.info, 存入 stock_info 表. 带冷却判断. 
    返回 (ticker, dimension, message).
    """
    dimension = "INFO"
    if not can_fetch(ticker_symbol, dimension, cooldown_minutes):
        msg = f"Skip {ticker_symbol} info, in cooldown."
        return (ticker_symbol, dimension, msg)

    ticker = yf.Ticker(ticker_symbol)
    info_dict = ticker.info
    if not info_dict:
        msg = f"No info for {ticker_symbol}"
        return (ticker_symbol, dimension, msg)

    info_json = json.dumps(info_dict, ensure_ascii=False)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    upsert_sql = """
    INSERT OR REPLACE INTO stock_info (ticker, info_json, last_update)
    VALUES (?, ?, ?)
    """
    cursor.execute(upsert_sql, (ticker_symbol, info_json, now_str))
    conn.commit()
    conn.close()

    update_fetch_time(ticker_symbol, dimension)

    msg = f"Fetched info for {ticker_symbol}"
    return (ticker_symbol, dimension, msg)

