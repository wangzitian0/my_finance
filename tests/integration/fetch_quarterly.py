# get_data/fetch_quarterly.py

import sqlite3
from datetime import datetime

import yfinance as yf

from common import can_fetch, get_db_path, update_fetch_time


def fetch_quarterly_balance(ticker_symbol: str, cooldown_minutes=60):
    """
    拉取 ticker.quarterly_balance_sheet -> quarterly_balance_sheet 表.
    带冷却. 返回 (ticker, dimension, message).
    """
    dimension = "Q_BALANCE"
    if not can_fetch(ticker_symbol, dimension, cooldown_minutes):
        msg = f"Skip {ticker_symbol} {dimension}, in cooldown."
        return (ticker_symbol, dimension, msg)

    ticker = yf.Ticker(ticker_symbol)
    df = ticker.quarterly_balance_sheet
    if df.empty:
        msg = f"No quarterly_balance_sheet for {ticker_symbol}"
        return (ticker_symbol, dimension, msg)

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # quarterly_balance_sheet 的 DF： 行=项目，列=日期
    df_t = df.T  # 行=日期, 列=项目
    insert_sql = """
    INSERT OR REPLACE INTO quarterly_balance_sheet
    (ticker, statement_date, item_name, value)
    VALUES (?, ?, ?, ?)
    """

    row_count = 0
    for date_idx, row_series in df_t.iterrows():
        # date_idx 可能是Timestamp
        date_str = str(date_idx.date()) if hasattr(date_idx, "date") else str(date_idx)
        for item_name, val in row_series.items():
            real_val = float(val) if val is not None else None
            cursor.execute(insert_sql, (ticker_symbol, date_str, item_name, real_val))
            row_count += 1

    conn.commit()
    conn.close()

    update_fetch_time(ticker_symbol, dimension)

    msg = f"Fetched {row_count} quarterly_balance rows for {ticker_symbol}"
    return (ticker_symbol, dimension, msg)
