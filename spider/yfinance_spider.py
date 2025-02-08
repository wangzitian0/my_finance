#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
from datetime import datetime, timedelta
import yfinance as yf
import yaml

# 定义文件保存根目录：data/original/yfinance
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "original", "yfinance")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 判断文件是否最近抓取过（1小时内不重复抓取）
def is_file_recent(filepath, hours=1):
    if os.path.exists(filepath):
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        if datetime.now() - mtime < timedelta(hours=hours):
            return True
    return False

# 保存数据为 JSON 文件，文件名格式：yfinance_<ticker>_<oid>_<date>.json
# 并且每个股票的数据保存在 data/original/yfinance/<ticker>/ 目录下
def save_data(ticker, oid, data):
    ticker_dir = os.path.join(DATA_DIR, ticker)
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir)
    date_str = datetime.now().strftime("%y%m%d-%H%M")
    filename = f"yfinance_{ticker}_{oid}_{date_str}.json"
    filepath = os.path.join(ticker_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"保存数据：{filepath}")
    return filepath

# 拉取指定股票及数据周期的数据
def fetch_stock_data(ticker, period, interval):
    print(f"正在抓取 {ticker} (period={period}, interval={interval}) 数据...")
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    data = hist.to_dict(orient="list")
    result = {
        "ticker": ticker,
        "period": period,
        "interval": interval,
        "fetched_at": datetime.now().isoformat(),
        "data": data,
    }
    return result

# 根据配置文件抓取任务
def run_job(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tickers = config.get("tickers", [])
    data_periods = config.get("data_periods", [])

    for period_cfg in data_periods:
        oid = period_cfg.get("oid")
        period = period_cfg.get("period")
        interval = period_cfg.get("interval")

        for ticker in tickers:
            # 构造基础文件名前缀，用于检查该股票该周期是否在1小时内已抓取
            base_filename = f"yfinance_{ticker}_{oid}_"
            exists_recent = False
            ticker_dir = os.path.join(DATA_DIR, ticker)
            if os.path.exists(ticker_dir):
                for fname in os.listdir(ticker_dir):
                    if fname.startswith(base_filename) and fname.endswith(".json"):
                        fpath = os.path.join(ticker_dir, fname)
                        if is_file_recent(fpath, hours=1):
                            print(f"文件 {fname} 已存在且在1小时内抓取，跳过 {ticker} {oid} 数据。")
                            exists_recent = True
                            break
            if exists_recent:
                continue

            try:
                data = fetch_stock_data(ticker, period, interval)
                save_data(ticker, oid, data)
            except Exception as e:
                print(f"抓取 {ticker} {oid} 数据时出错: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python yfinance_spider.py <配置文件路径>")
        sys.exit(1)
    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        print(f"配置文件 {config_file} 不存在。")
        sys.exit(1)
    run_job(config_file)
