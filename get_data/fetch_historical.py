# get_data/fetch_historical.py

import sqlite3
import yfinance as yf
from get_data.common import get_db_path, can_fetch, update_fetch_time

DIMENSION = "HISTORICAL"  # 表示拉取历史行情

def run(ticker_symbol: str, period="1y"):
    """
    拉取 ticker_symbol 的历史行情，并存储到 stock_price 表。
    如果 1 小时内拉取过，就跳过。
    """
    if not can_fetch(ticker_symbol, DIMENSION, cooldown_minutes=60):
        print(f"[SKIP] {ticker_symbol}'s historical: fetched within 1 hour.")
        return
    
    print(f"[INFO] Fetch historical data for {ticker_symbol}, period={period}")

    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period)
    if df.empty:
        print(f"[WARN] No historical data fetched for {ticker_symbol}")
        return

    df.reset_index(inplace=True)
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    insert_sql = """
    INSERT OR REPLACE INTO stock_price
    (ticker, trade_date, open, high, low, close, adj_close, volume, dividends, stock_splits)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            int(row.get("Volume", 0)),
            float(row.get("Dividends", 0.0)),
            float(row.get("Stock Splits", 0.0))
        )
        cursor.execute(insert_sql, data_tuple)
        row_count += 1

    conn.commit()
    conn.close()

    print(f"[INFO] Inserted/Updated {row_count} rows of historical for {ticker_symbol}")

    # 更新拉取时间
    update_fetch_time(ticker_symbol, DIMENSION)

