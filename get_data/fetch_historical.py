# get_data/fetch_historical.py

import sqlite3
import yfinance as yf
from datetime import datetime

from get_data.common import (
    get_db_path,
    can_fetch,
    update_fetch_time,
)

def fetch_historical(ticker_symbol: str, period="1y", interval="1d", cooldown_minutes=60):
    """
    拉取ticker_symbol指定 period + interval 的行情, 存入 stock_price 表.
    带1小时(或自定义)冷却检查. 
    如果过冷却期才能拉, 否则直接return, 不报错.
    
    返回 (ticker, dimension, message) 供 safe_call() 记录日志.
    """
    dimension = f"HISTORICAL_{interval}"

    # 冷却检查
    if not can_fetch(ticker_symbol, dimension, cooldown_minutes=cooldown_minutes):
        msg = f"Skip fetch {ticker_symbol}, dimension={dimension}, still in cooldown."
        return (ticker_symbol, dimension, msg)

    # 开始拉取
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period, interval=interval)

    if df.empty:
        msg = f"No data for {ticker_symbol}, {interval}, period={period}"
        return (ticker_symbol, dimension, msg)

    df.reset_index(inplace=True)
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    insert_sql = """
    INSERT OR REPLACE INTO stock_price
    (ticker, trade_date, open, high, low, close, adj_close, volume)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    row_count = 0
    for _, row in df.iterrows():
        trade_date = row["Date"].strftime("%Y-%m-%d")
        data_tuple = (
            ticker_symbol,
            trade_date,
            row.get("Open", None),
            row.get("High", None),
            row.get("Low", None),
            row.get("Close", None),
            row.get("Adj Close", None),
            int(row.get("Volume", 0))
        )
        cursor.execute(insert_sql, data_tuple)
        row_count += 1

    conn.commit()
    conn.close()

    # 更新 fetch_log
    update_fetch_time(ticker_symbol, dimension)

    msg = f"Fetched {row_count} rows for {ticker_symbol} {interval}, period={period}"
    return (ticker_symbol, dimension, msg)

