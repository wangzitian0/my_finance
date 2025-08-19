import sqlite3
from datetime import datetime

import yfinance as yf

from common import can_fetch, get_db_path, update_fetch_time


def fetch_historical(ticker_symbol: str, period="1y", interval="1d", cooldown_minutes=60):
    """
    1. First check `can_fetch()`, return if no need to fetch
    2. Call yfinance to get data
    3. If successful, update database and record success=1
    4. If failed, still update fetch_log but with success=0
    """
    dimension = f"HISTORICAL_{interval}"

    if not can_fetch(ticker_symbol, dimension, cooldown_minutes):
        msg = f"Skip fetch {ticker_symbol}, dimension={dimension}, still in cooldown."
        return (ticker_symbol, dimension, msg)

    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            msg = f"No data for {ticker_symbol}, {interval}, period={period}"
            update_fetch_time(ticker_symbol, dimension, success=False)
            return (ticker_symbol, dimension, msg)

        latest_trade_date = df.index[-1].strftime("%Y-%m-%d")

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
                int(row.get("Volume", 0)),
            )
            cursor.execute(insert_sql, data_tuple)
            row_count += 1

        conn.commit()
        conn.close()

        update_fetch_time(ticker_symbol, dimension, success=True)

        msg = f"Fetched {row_count} rows for {ticker_symbol} {interval}, period={period}"
        return (ticker_symbol, dimension, msg)

    except Exception as e:
        update_fetch_time(ticker_symbol, dimension, success=False)
        err_msg = f"Exception: {repr(e)}"
        return (ticker_symbol, dimension, err_msg)
