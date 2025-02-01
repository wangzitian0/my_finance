# get_data/init_schema.py

import sqlite3
from get_data.common import get_db_path

def init_db_schema():
    """
    初始化数据库表结构：行情表、info表、以及季度财务相关表等。
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    create_price_table_sql = """
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        trade_date TEXT NOT NULL,
        open REAL, high REAL, low REAL, close REAL, adj_close REAL,
        volume INTEGER, dividends REAL, stock_splits REAL,
        UNIQUE(ticker, trade_date)
    )
    """
    cursor.execute(create_price_table_sql)

    create_info_table_sql = """
    CREATE TABLE IF NOT EXISTS stock_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        info_json TEXT NOT NULL,
        last_update TEXT NOT NULL,
        UNIQUE(ticker)
    )
    """
    cursor.execute(create_info_table_sql)

    create_q_balance_sql = """
    CREATE TABLE IF NOT EXISTS quarterly_balance_sheet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        statement_date TEXT NOT NULL,
        item_name TEXT NOT NULL,
        value REAL,
        UNIQUE(ticker, statement_date, item_name)
    )
    """
    cursor.execute(create_q_balance_sql)

    # 其它季度财务表例如 quarterly_cashflow, quarterly_financials, quarterly_earnings
    # 可以在这里一并建表
    # ...

    conn.commit()
    conn.close()


