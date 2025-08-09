# get_data/init_schema.py

import sqlite3

from common import get_db_path


def init_db_schema():
    """
    建立或更新主要业务表:
      - stock_price: 行情
      - stock_info: 最新info
      - quarterly_balance_sheet: 季度财务示例 (可扩展更多)
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # 1) 行情表
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        trade_date TEXT NOT NULL,
        open REAL, high REAL, low REAL, close REAL, adj_close REAL,
        volume INTEGER,
        UNIQUE(ticker, trade_date)
    )
    """
    )

    # 2) info表
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS stock_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        info_json TEXT NOT NULL,
        last_update TEXT NOT NULL,
        UNIQUE(ticker)
    )
    """
    )

    # 3) 季度财务 (演示)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS quarterly_balance_sheet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        statement_date TEXT NOT NULL,
        item_name TEXT NOT NULL,
        value REAL,
        UNIQUE(ticker, statement_date, item_name)
    )
    """
    )

    conn.commit()
    conn.close()
