import sqlite3
from datetime import datetime, timedelta

DB_FOLDER = "data"
DB_NAME = "yfinance_data.db"


def get_db_path():
    return f"{DB_FOLDER}/{DB_NAME}"


def ensure_common_tables():
    """
    创建通用数据库表：
    1) fetch_log: 记录数据抓取状态
    2) stock_price: 存储股票历史数据
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # 创建 fetch_log 表
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

    # 创建 stock_price 表
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
    1. 如果上次拉取失败 (success=0)，必须重试
    2. 如果上次拉取成功，但数据过旧（超过冷却时间），允许拉取
    3. 否则不拉取
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
        return True  # 如果没有记录，必须拉取

    last_fetch_time, last_success_time, success = row
    last_fetch_dt = datetime.strptime(last_fetch_time, "%Y-%m-%d %H:%M:%S")

    # 如果上次失败，必须重试
    if success == 0:
        return True

    # 如果成功了，检查数据是否过旧
    if last_success_time:
        last_success_dt = datetime.strptime(last_success_time, "%Y-%m-%d %H:%M:%S")
        if now - last_success_dt > timedelta(minutes=cooldown_minutes):
            return True

    return False


def update_fetch_time(ticker: str, dimension: str, success: bool):
    """
    在 fetch_log 中更新:
    - `last_fetch_time` （无论成功与否都更新）
    - `success=1` 代表成功, 并记录 `last_success_time`
    - `success=0` 代表失败, 但保留 `last_success_time` 不变
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
