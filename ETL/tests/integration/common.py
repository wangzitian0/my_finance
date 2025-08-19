import sqlite3
from datetime import datetime, timedelta

DB_FOLDER = "data"
DB_NAME = "yfinance_data.db"


def get_db_path():
    return f"{DB_FOLDER}/{DB_NAME}"


def ensure_common_tables():
    """
    Create common database tables:
    1) fetch_log: Record data fetch status
    2) stock_price: Store stock historical data
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Create fetch_log table
    create_fetch_log_sql = """
    CREATE TABLE IF NOT EXISTS fetch_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        dimension TEXT NOT NULL,
        last_fetch_time TEXT NOT NULL,
        last_success_time TEXT,
        success INTEGER NOT NULL DEFAULT 0,
        UNIQUE(ticker, dimension)
    )
    """
    cursor.execute(create_fetch_log_sql)

    # Create stock_price table
    create_stock_price_sql = """
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        trade_date TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        adj_close REAL,
        volume INTEGER,
        UNIQUE(ticker, trade_date)
    )
    """
    cursor.execute(create_stock_price_sql)

    conn.commit()
    conn.close()


def can_fetch(ticker: str, dimension: str, cooldown_minutes=60) -> bool:
    """
    1. If last fetch failed (success=0), must retry
    2. If last fetch succeeded, but data is stale (beyond cooldown time), allow fetch
    3. Otherwise don't fetch
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    sel_sql = """
    SELECT last_fetch_time, last_success_time, success FROM fetch_log
    WHERE ticker=? AND dimension=?
    """
    cursor.execute(sel_sql, (ticker, dimension))
    row = cursor.fetchone()
    conn.close()

    now = datetime.now()

    if not row:
        return True  # If no record exists, must fetch

    last_fetch_time, last_success_time, success = row
    last_fetch_dt = datetime.strptime(last_fetch_time, "%Y-%m-%d %H:%M:%S")

    # If last attempt failed, must retry
    if success == 0:
        return True

    # If succeeded, check if data is stale
    if last_success_time:
        last_success_dt = datetime.strptime(last_success_time, "%Y-%m-%d %H:%M:%S")
        if now - last_success_dt > timedelta(minutes=cooldown_minutes):
            return True

    return False


def update_fetch_time(ticker: str, dimension: str, success: bool):
    """
    Update in fetch_log:
    - `last_fetch_time` (always updated regardless of success)
    - `success=1` represents success, and record `last_success_time`
    - `success=0` represents failure, but keep `last_success_time` unchanged
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    if success:
        upsert_sql = """
        INSERT OR REPLACE INTO fetch_log (ticker, dimension, last_fetch_time, last_success_time, success)
        VALUES (?, ?, ?, ?, 1)
        """
        cursor.execute(upsert_sql, (ticker, dimension, now_str, now_str))
    else:
        upsert_sql = """
        INSERT OR REPLACE INTO fetch_log (ticker, dimension, last_fetch_time, success)
        VALUES (?, ?, ?, 0)
        """
        cursor.execute(upsert_sql, (ticker, dimension, now_str))

    conn.commit()
    conn.close()
