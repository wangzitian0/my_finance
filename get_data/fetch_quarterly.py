# get_data/fetch_quarterly.py

import sqlite3
import yfinance as yf
from datetime import datetime
from get_data.common import get_db_path, can_fetch, update_fetch_time

DIMENSION = "Q_BALANCE"

def run_quarterly_balance(ticker_symbol: str):
    """
    拉取 ticker.quarterly_balance_sheet 并存到 quarterly_balance_sheet。
    避免1小时内重复。
    """
    if not can_fetch(ticker_symbol, DIMENSION, cooldown_minutes=60):
        print(f"[SKIP] {ticker_symbol}'s quarterly_balance: fetched within 1 hour.")
        return

    print(f"[INFO] Fetch quarterly_balance_sheet for {ticker_symbol}")
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.quarterly_balance_sheet
    if df.empty:
        print(f"[WARN] No quarterly_balance_sheet for {ticker_symbol}")
        return

    _save_quarterly_to_db(ticker_symbol, df, table_name="quarterly_balance_sheet")
    update_fetch_time(ticker_symbol, DIMENSION)

def _save_quarterly_to_db(ticker_symbol, df, table_name):
    """
    将行索引=财务项目，列索引=日期 的 df 转置后存入 table_name。
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    df_t = df.T  # 行=日期, 列=项目
    insert_sql = f"""
    INSERT OR REPLACE INTO {table_name}
    (ticker, statement_date, item_name, value)
    VALUES (?, ?, ?, ?)
    """
    row_count = 0

    for date_idx, row_series in df_t.iterrows():
        date_str = str(date_idx.date()) if hasattr(date_idx, "date") else str(date_idx)
        for item_name, val in row_series.items():
            # val 可能是 None, NaN 等
            if val is None:
                real_val = None
            else:
                try:
                    real_val = float(val)
                except:
                    real_val = None

            cursor.execute(insert_sql, (ticker_symbol, date_str, item_name, real_val))
            row_count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Insert/Updated {row_count} rows into {table_name} for {ticker_symbol}")

