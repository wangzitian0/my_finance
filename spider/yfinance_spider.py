#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Suppress DeprecationWarnings from yfinance
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import json
import re
from datetime import datetime, timedelta
import yfinance as yf
import yaml
import logging  # Used in sanitize_data for logging warnings

from common.logger import setup_logger
from common.progress import create_progress_bar

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORIGINAL_DATA_DIR = os.path.join(BASE_DIR, "data", "original")


def is_file_recent(filepath, hours=1):
    """
    Check if the timestamp in the filename is within the past 'hours' hours.
    Assumes the filename format: <ticker>_<source>_<oid>_<date_str>.json,
    where date_str is in the format %y%m%d-%H%M%S.
    """
    filename = os.path.basename(filepath)
    match = re.search(r"_(\d{6}-\d{6})\.json$", filename)
    if match:
        timestamp_str = match.group(1)
        try:
            file_dt = datetime.strptime(timestamp_str, "%y%m%d-%H%M%S")
            if datetime.now() - file_dt < timedelta(hours=hours):
                return True
        except Exception:
            return False
    return False


def sanitize_data(obj, logger):
    """
    Recursively traverse the object.
    For any dictionary key that is not of type str, int, float, bool, or None,
    log a warning and convert that key to a string and set its value to None.
    """
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if not isinstance(k, (str, int, float, bool)) and k is not None:
                logger.warning(f"Key {k} (type {type(k)}) is not a valid JSON key type; converting key to string and setting its value to null")
                new_key = str(k)
                new_dict[new_key] = None  # Set value to null (None)
            else:
                new_key = k
                new_dict[new_key] = sanitize_data(v, logger)
        return new_dict
    elif isinstance(obj, list):
        return [sanitize_data(item, logger) for item in obj]
    else:
        return obj


def save_data(ticker, source, oid, data, logger):
    """
    Save the data as a JSON file with the filename format:
    <ticker>_<source>_<oid>_<date_str>.json
    The file is stored under data/original/<source>/<ticker>/.
    Before saving, the data is sanitized so that all dictionary keys are allowed.
    """
    date_str = datetime.now().strftime("%y%m%d-%H%M%S")
    filename = f"{ticker}_{source}_{oid}_{date_str}.json"
    ticker_dir = os.path.join(ORIGINAL_DATA_DIR, source, ticker)
    os.makedirs(ticker_dir, exist_ok=True)
    filepath = os.path.join(ticker_dir, filename)
    sanitized_data = sanitize_data(data, logger)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sanitized_data, f, ensure_ascii=False, indent=2, default=str)
    return filepath


def fetch_stock_data(ticker, period, interval):
    """
    Use yfinance to fetch various types of data for the given ticker.
    Data includes:
      - Basic info (info, fast_info)
      - Historical market data (history)
      - Dividends and splits
      - Earnings (annual and quarterly)
      - Balance sheet and cashflow
      - Recommendations and calendar info
      - Major holders and institutional holders
      - Sustainability data
      - Options data
      - News
    All yfinance calls are wrapped in a warnings context to ignore DeprecationWarnings.
    """
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            tkr = yf.Ticker(ticker)
        except Exception as e:
            raise Exception(f"yfinance Ticker initialization error for {ticker}: {e}")
        try:
            hist = tkr.history(period=period, interval=interval)
        except Exception as e:
            raise Exception(f"yfinance history fetching error for {ticker}: {e}")
    history_data = hist.to_dict(orient="list") if not hist.empty else {}

    def safe_get(attr, to_dict=False, orient="dict"):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                val = getattr(tkr, attr)
                if callable(val):
                    val = val()
            if attr == "fast_info":
                try:
                    return dict(val)
                except Exception:
                    return str(val)
            if to_dict:
                if hasattr(val, "empty") and not val.empty:
                    return val.to_dict(orient=orient)
                else:
                    return {} if orient == "dict" else []
            return val
        except Exception:
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
    """
    Run the job using the YAML configuration file.
    The configuration should contain:
      - tickers: list of ticker symbols
      - source: string for data source (e.g., "yfinance")
      - data_periods: list of dictionaries with keys: oid, period, interval
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tickers = config.get("tickers", [])
    source = config.get("source", "yfinance")
    data_periods = config.get("data_periods", [])

    for period_cfg in data_periods:
        oid = period_cfg.get("oid")
        period = period_cfg.get("period")
        interval = period_cfg.get("interval")

        job_id = f"{source}_{oid}"
        date_str = datetime.now().strftime("%y%m%d-%H%M%S")
        exe_id = f"{job_id}_{date_str}"

        logger = setup_logger(job_id, date_str)
        logger.info(f"Job started: exe_id={exe_id}")

        total = len(tickers)
        success = 0
        errors = 0
        skipped = 0

        progress_bar = create_progress_bar(total, description="Tickers Progress")
        for ticker in tickers:
            base_filename = f"{ticker}_{source}_{oid}_"
            ticker_dir = os.path.join(ORIGINAL_DATA_DIR, source, ticker)
            exists_recent = False
            if os.path.exists(ticker_dir):
                for fname in os.listdir(ticker_dir):
                    if fname.startswith(base_filename) and fname.endswith(".json"):
                        fpath = os.path.join(ticker_dir, fname)
                        if is_file_recent(fpath, hours=1):
                            exists_recent = True
                            break

            if exists_recent:
                skipped += 1
                success += 1
                logger.info(f"Ticker {ticker}: Data exists (skipped).")
            else:
                try:
                    logger.info(f"Fetching data for ticker: {ticker} (period={period}, interval={interval})")
                    data = fetch_stock_data(ticker, period, interval)
                    filepath = save_data(ticker, source, oid, data, logger)
                    success += 1
                    logger.info(f"Ticker {ticker}: Data saved at {filepath}")
                except Exception:
                    errors += 1
                    logger.exception(f"Ticker {ticker}: Error fetching data")
            progress_bar.update(1)
        progress_bar.close()

        logger.info(f"Job finished: exe_id={exe_id}")
        logger.info(f"Summary: Processed={total}, Success={success}, Skipped={skipped}, Errors={errors}")
        print(f"Job summary for {exe_id}: Processed={total}, Success={success}, Skipped={skipped}, Errors={errors}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python yfinance_spider.py <config_file_path>")
        exit(1)
    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        print(f"Config file {config_file} does not exist.")
        exit(1)
    run_job(config_file)
