#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import yfinance as yf
from datetime import datetime

# 你可以根据实际情况修改下列参数
DB_FOLDER = "data"
DB_NAME   = "yfinance_data.db"
TABLE_NAME = "stock_price"


def get_db_path() -> str:
    """
    返回数据库的完整路径，默认放在 data/ 目录下。
    """
    # 确保 data 目录存在
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    return os.path.join(DB_FOLDER, DB_NAME)


def init_db_schema():
    """
    初始化数据库表结构，若不存在则创建。
    Schema 主要参考 yfinance 返回的常见字段：
    Date, Open, High, Low, Close, Adj Close, Volume, Dividends, Stock Splits
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # 建表语句，可以根据需要再加上索引或者其他字段
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        trade_date TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        adj_close REAL,
        volume INTEGER,
        dividends REAL,
        stock_splits REAL,
        UNIQUE(ticker, trade_date)
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()


def fetch_and_insert_data(ticker_symbol: str, period: str = "1y"):
    """
    从 yfinance 拉取某只股票的历史数据，并写入 SQLite 数据库。
    默认抓取过去一年的数据(period="1y")。
    你可以自行指定 start/end/interval 或替换为 download() 等。
    """
    # 拉取数据
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period)

    if df.empty:
        print(f"[WARN] No data fetched for {ticker_symbol}")
        return

    # df 通常包含: Open, High, Low, Close, Volume, Dividends, Stock Splits, Adj Close
    # 索引是日期 DateTimeIndex
    # 将索引转为列，便于后续插入
    df.reset_index(inplace=True)

    # 连接数据库
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    insert_sql = f"""
    INSERT OR REPLACE INTO {TABLE_NAME}
    (ticker, trade_date, open, high, low, close, adj_close, volume, dividends, stock_splits)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # 逐行插入数据库
    for _, row in df.iterrows():
        trade_date_str = row["Date"].strftime("%Y-%m-%d")  # 若要存日期型，可直接存字符串或做 datetime 处理
        data_tuple = (
            ticker_symbol,
            trade_date_str,
            row["Open"],
            row["High"],
            row["Low"],
            row["Close"],
            row.get("Adj Close", None),
            int(row["Volume"]) if not None else 0,
            float(row["Dividends"]),
            float(row["Stock Splits"])
        )
        cursor.execute(insert_sql, data_tuple)

    conn.commit()
    conn.close()
    print(f"[INFO] Insert/Update {len(df)} rows for ticker {ticker_symbol} into {TABLE_NAME}")


def main():
    """
    脚本入口：初始化数据库表结构，然后示例拉取一些股票数据写入数据库。
    你可以根据需求调用 fetch_and_insert_data 多次
    """
    print("[INFO] Initializing database schema...")
    init_db_schema()

    # 这里演示拉取 AAPL 一年数据
    tickers_to_fetch = ["AAPL"]
    for t in tickers_to_fetch:
        print(f"[INFO] Fetching data for {t} ...")
        fetch_and_insert_data(t, period="1y")

    print("[DONE] All done!")


if __name__ == "__main__":
    main()

