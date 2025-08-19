# get_data/init_schema.py

import sqlite3

from common import get_db_path


def init_db_schema():
    """
    Establish or update main business tables:
      - stock_price: Market data
      - stock_info: Latest info
      - quarterly_balance_sheet: Quarterly financial example (expandable)
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # 1) Market data table
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

    # 2) Info table
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

    # 3) Quarterly financials (demo)
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
