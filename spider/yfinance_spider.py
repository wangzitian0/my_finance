#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, timedelta
import yfinance as yf
import yaml

# 定义数据保存根目录：data/original/yfinance/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "original", "yfinance")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def is_file_recent(filepath, hours=1):
    """判断文件是否在过去 hours 小时内更新过"""
    if os.path.exists(filepath):
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        if datetime.now() - mtime < timedelta(hours=hours):
            return True
    return False


def save_data(ticker, oid, data):
    """
    保存数据为 JSON 文件，文件名格式：
      yfinance_<ticker>_<oid>_<date>.json
    并将文件保存在 data/original/yfinance/<ticker>/ 目录下
    """
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


def fetch_stock_data(ticker, period, interval):
    """
    使用 yfinance 抓取指定股票的各类数据，包括：
      - 基本信息（info、fast_info）
      - 历史行情（history）
      - 分红（dividends）和拆股（splits）
      - 年度和季度财报（earnings、quarterly_earnings）
      - 资产负债表（balance_sheet）和现金流（cashflow）
      - 分析师推荐（recommendations）和日历信息（calendar）
      - 大股东及机构持股信息（major_holders、institutional_holders）
      - 可持续性数据（sustainability）
      - 期权信息（options）
      - 新闻（news）
    """
    print(f"正在抓取 {ticker} (period={period}, interval={interval}) 数据...")
    tkr = yf.Ticker(ticker)

    # 历史行情
    hist = tkr.history(period=period, interval=interval)
    history_data = hist.to_dict(orient="list") if not hist.empty else {}

    def safe_get(attr, to_dict=False, orient="dict"):
        try:
            val = getattr(tkr, attr)
            if callable(val):
                val = val()
            # 如果是DataFrame/Series且非空，则转换成字典；否则返回空对象
            if to_dict:
                if hasattr(val, "empty") and not val.empty:
                    return val.to_dict(orient=orient)
                else:
                    return {} if orient == "dict" else []
            return val
        except Exception as e:
            return {} if orient == "dict" else []

    data = {
        "ticker": ticker,
        "period": period,
        "interval": interval,
        "fetched_at": datetime.now().isoformat(),
        "info": safe_get("info"),
        "fast_info": safe_get("fast_info"),
        "history": history_data,
        "dividends": safe_get("dividends", to_dict=True),
        "splits": safe_get("splits", to_dict=True),
        "earnings": safe_get("earnings", to_dict=True),
        "quarterly_earnings": safe_get("quarterly_earnings", to_dict=True),
        "balance_sheet": safe_get("balance_sheet", to_dict=True),
        "cashflow": safe_get("cashflow", to_dict=True),
        "recommendations": safe_get("recommendations", to_dict=True),
        "calendar": safe_get("calendar", to_dict=True),
        "major_holders": safe_get("major_holders", to_dict=True, orient="records"),
        "institutional_holders": safe_get("institutional_holders", to_dict=True, orient="records"),
        "sustainability": safe_get("sustainability", to_dict=True),
        "options": safe_get("options"),
        "news": safe_get("news", orient="list"),
    }
    return data


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
            # 构造基础文件名前缀，用于检查文件是否在1小时内已抓取
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
