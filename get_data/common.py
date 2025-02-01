# get_data/common.py

import os
import sqlite3
from datetime import datetime, timedelta
import traceback

DB_FOLDER = "data"
DB_NAME = "yfinance_data.db"

def get_db_path() -> str:
    """
    返回数据库的完整路径，默认放在 data/ 目录下。
    """
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    return os.path.join(DB_FOLDER, DB_NAME)

def ensure_common_tables():
    """
    初始化与抓取过程相关的公共表:
    1) fetch_log: 记录上次拉取时间(控制冷却)
    2) fetch_attempt_log: 记录这次抓取是成功还是失败
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # fetch_log: 用于 cooldown 机制
    create_fetch_log_sql = """
    CREATE TABLE IF NOT EXISTS fetch_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        dimension TEXT NOT NULL,   -- 比如 'HISTORICAL_1d', 'INFO', 'Q_BALANCE' ...
        last_fetch_time TEXT NOT NULL,
        UNIQUE(ticker, dimension)
    )
    """
    cursor.execute(create_fetch_log_sql)

    # fetch_attempt_log: 记录本次请求是否成功
    create_attempt_log_sql = """
    CREATE TABLE IF NOT EXISTS fetch_attempt_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        dimension TEXT NOT NULL,
        attempt_time TEXT NOT NULL,
        success INTEGER NOT NULL,  -- 1=成功, 0=失败
        message TEXT
    )
    """
    cursor.execute(create_attempt_log_sql)

    conn.commit()
    conn.close()

def can_fetch(ticker: str, dimension: str, cooldown_minutes=60) -> bool:
    """
    查询 fetch_log 表, 看 ticker+dimension 是否在 cooldown 时间内(默认1小时).
    若上次拉取 < 1 小时前, 返回 True; 否则 False.
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    sel_sql = """
    SELECT last_fetch_time FROM fetch_log
    WHERE ticker=? AND dimension=?
    """
    cursor.execute(sel_sql, (ticker, dimension))
    row = cursor.fetchone()
    conn.close()

    if not row:
        # 从未拉取过, 可以拉
        return True

    last_str = row[0]
    last_dt = datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()

    # 如果 now - last_dt >= cooldown_minutes, 说明超过冷却期, 可以拉
    return (now - last_dt) >= timedelta(minutes=cooldown_minutes)

def update_fetch_time(ticker: str, dimension: str):
    """
    在 fetch_log 中更新/插入 last_fetch_time= now
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

def log_attempt(ticker: str, dimension: str, success: bool, message=""):
    """
    在 fetch_attempt_log 表记录一次抓取尝试结果.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    ins_sql = """
    INSERT INTO fetch_attempt_log (ticker, dimension, attempt_time, success, message)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(ins_sql, (ticker, dimension, now_str, int(success), message))
    conn.commit()
    conn.close()

def safe_call(func, *args, **kwargs):
    """
    封装一次安全调用, 如果 func 出错, log_attempt(success=0), 并返回 False;
    如果成功, log_attempt(success=1), 返回 True.
    要求func里要返回(ticker, dimension, message), 以便log.
    """
    try:
        ticker, dimension, msg = func(*args, **kwargs)
        # 成功
        log_attempt(ticker, dimension, True, msg)
        return True
    except Exception as e:
        # 失败
        err_msg = f"Exception: {repr(e)}\nTraceback: {traceback.format_exc()}"
        # 如果能从func参数中提取出ticker/dimension, 也可以手动指定
        # 这里假设func里抛出前不会返回(ticker, dimension, msg), 
        # 所以 dimension 就写个 "UNKNOWN"
        # 你也可以在 func 里捕获异常再抛出. 这里仅作示例.
        log_attempt("UNKNOWN", "UNKNOWN", False, err_msg)
        return False

