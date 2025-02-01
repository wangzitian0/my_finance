# get_data/common.py

import os
import sqlite3
from datetime import datetime, timedelta

DB_FOLDER = "data"
DB_NAME = "yfinance_data.db"

def get_db_path() -> str:
    """返回数据库的完整路径，默认放在 data/ 目录下。"""
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    return os.path.join(DB_FOLDER, DB_NAME)

def ensure_fetch_log_table():
    """
    确保数据库中存在 fetch_log 表，用于记录 ticker + dimension 的最后拉取时间。
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS fetch_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        dimension TEXT NOT NULL,
        last_fetch_time TEXT NOT NULL,
        UNIQUE(ticker, dimension)
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()

def can_fetch(ticker: str, dimension: str, cooldown_minutes=60) -> bool:
    """
    检查 fetch_log 表，看某个 ticker + dimension 是否超过 cooldown_minutes 未拉取。
    如果距离上次拉取 < cooldown_minutes，则返回 False, 否则 True。
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    select_sql = """
    SELECT last_fetch_time 
    FROM fetch_log 
    WHERE ticker=? AND dimension=?
    """
    cursor.execute(select_sql, (ticker, dimension))
    row = cursor.fetchone()
    conn.close()

    if not row:
        # 从未拉取过，可以拉
        return True
    
    last_fetch_str = row[0]
    last_fetch_dt = datetime.strptime(last_fetch_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()

    if now - last_fetch_dt < timedelta(minutes=cooldown_minutes):
        # 上次拉取时间在指定冷却期内
        return False
    else:
        return True

def update_fetch_time(ticker: str, dimension: str):
    """
    成功拉取后，更新/插入最后拉取时间为当前时间。
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    upsert_sql = """
    INSERT OR REPLACE INTO fetch_log (ticker, dimension, last_fetch_time)
    VALUES (?, ?, ?)
    """
    cursor.execute(upsert_sql, (ticker, dimension, now_str))
    conn.commit()
    conn.close()

