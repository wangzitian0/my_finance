#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
from datetime import datetime, timedelta

import yaml

# Import config from neomodel and set database connection
from neomodel import config

config.DATABASE_URL = "bolt://neo4j:wangzitian0@localhost:7687"

# Use common module from project root directory, not in ETL directory
from common.logger import StreamToLogger, setup_logger
from common.progress import create_progress_bar
from common.snowflake import Snowflake
from common.utils import is_file_recent, sanitize_data, suppress_third_party_logs

# Optionally suppress third-party log messages (e.g. requests/urllib3)
suppress_third_party_logs()

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE_01_EXTRACT_DIR = os.path.join(BASE_DIR, "data", "stage_01_extract")

# Import models (ensure ETL is in PYTHONPATH)
from models import FastInfo, Info, PriceData, Recommendations, Stock, Sustainability


def import_json_file(file_path, logger):
    """
    Read a single JSON file and import data to Neo4j (via Neomodel models).
    Based on the ticker field in the JSON, first get or create a Stock node, then create Info, FastInfo, PriceData, Recommendations and Sustainability nodes, and establish relationships.
    """
    logger.info(f"Processing file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ticker = data.get("ticker")
    if not ticker:
        logger.error("Missing ticker field in JSON file.")
        return

    try:
        stock = Stock.nodes.get(ticker=ticker)
    except Stock.DoesNotExist:
        stock = Stock(
            ticker=ticker,
            period=data.get("period"),
            interval=data.get("interval"),
            fetched_at=datetime.fromisoformat(data.get("fetched_at")),
        )
        stock.save()

    # Process info node
    info_data = data.get("info")
    if info_data:
        info_node = Info(
            address1=info_data.get("address1"),
            city=info_data.get("city"),
            state=info_data.get("state"),
            zip=info_data.get("zip"),
            country=info_data.get("country"),
            phone=info_data.get("phone"),
            website=info_data.get("website"),
            industry=info_data.get("industry"),
            industryKey=info_data.get("industryKey"),
            industryDisp=info_data.get("industryDisp"),
            sector=info_data.get("sector"),
            sectorKey=info_data.get("sectorKey"),
            sectorDisp=info_data.get("sectorDisp"),
            longBusinessSummary=info_data.get("longBusinessSummary"),
            fullTimeEmployees=info_data.get("fullTimeEmployees"),
            companyOfficers=info_data.get("companyOfficers"),
        )
        info_node.save()
        stock.info.connect(info_node)

    # Process fast_info node
    fast_info_data = data.get("fast_info")
    if fast_info_data:
        fast_info_node = FastInfo(
            currency=fast_info_data.get("currency"),
            dayHigh=fast_info_data.get("dayHigh"),
            dayLow=fast_info_data.get("dayLow"),
            exchange=fast_info_data.get("exchange"),
            fiftyDayAverage=fast_info_data.get("fiftyDayAverage"),
            lastPrice=fast_info_data.get("lastPrice"),
            lastVolume=fast_info_data.get("lastVolume"),
        )
        fast_info_node.save()
        stock.fast_info.connect(fast_info_node)

    # Process recommendations node
    rec_data = data.get("recommendations")
    if rec_data:
        rec_node = Recommendations(
            period=rec_data.get("period"),
            strongBuy=rec_data.get("strongBuy"),
            buy=rec_data.get("buy"),
            hold=rec_data.get("hold"),
            sell=rec_data.get("sell"),
            strongSell=rec_data.get("strongSell"),
        )
        rec_node.save()
        stock.recommendations.connect(rec_node)

    # Process sustainability node
    sus_data = data.get("sustainability", {}).get("esgScores")
    if sus_data:
        sus_node = Sustainability(esgScores=sus_data)
        sus_node.save()
        stock.sustainability.connect(sus_node)

    # Process historical stock price data, assuming history section is a dictionary with arrays for each field
    history_data = data.get("history")
    if history_data:
        opens = history_data.get("Open", [])
        highs = history_data.get("High", [])
        lows = history_data.get("Low", [])
        closes = history_data.get("Close", [])
        volumes = history_data.get("Volume", [])
        # If there's a date field in JSON, it should be used; here using base date as example
        base_date = datetime(2025, 1, 1)
        count = min(len(opens), len(highs), len(lows), len(closes), len(volumes))
        for i in range(count):
            price_node = PriceData(
                date=base_date + timedelta(days=i),
                open=opens[i],
                high=highs[i],
                low=lows[i],
                close=closes[i],
                volume=volumes[i],
            )
            price_node.save()
            stock.prices.connect(price_node)

    logger.info(f"Imported data for ticker: {ticker}")


def import_all_json_files(source, tickers, logger):
    """
    For the given tickers list, read all JSON files from data/stage_00_original/<source>/<ticker> directories,
    and call import_json_file() to write data to Neo4j.
    """
    total_files = 0
    for ticker in tickers:
        # Use latest data from stage_01_extract
        latest_link = os.path.join(STAGE_01_EXTRACT_DIR, source, "latest")
        if os.path.exists(latest_link):
            ticker_dir = os.path.join(latest_link, ticker)
        else:
            # Fallback to most recent date partition
            source_dir = os.path.join(STAGE_01_EXTRACT_DIR, source)
            if os.path.exists(source_dir):
                date_dirs = [
                    d
                    for d in os.listdir(source_dir)
                    if os.path.isdir(os.path.join(source_dir, d)) and d.isdigit()
                ]
                if date_dirs:
                    latest_date = max(date_dirs)
                    ticker_dir = os.path.join(source_dir, latest_date, ticker)
                else:
                    ticker_dir = os.path.join(source_dir, ticker)  # fallback
            else:
                ticker_dir = os.path.join(STAGE_01_EXTRACT_DIR, source, ticker)
        if not os.path.isdir(ticker_dir):
            logger.warning(f"目录不存在：{ticker_dir}")
            continue
        files = [f for f in os.listdir(ticker_dir) if f.endswith(".json")]
        total_files += len(files)
    progress_bar = create_progress_bar(total_files, description="JSON Files")
    errors = 0
    for ticker in tickers:
        # Use latest data from stage_01_extract
        latest_link = os.path.join(STAGE_01_EXTRACT_DIR, source, "latest")
        if os.path.exists(latest_link):
            ticker_dir = os.path.join(latest_link, ticker)
        else:
            # Fallback to most recent date partition
            source_dir = os.path.join(STAGE_01_EXTRACT_DIR, source)
            if os.path.exists(source_dir):
                date_dirs = [
                    d
                    for d in os.listdir(source_dir)
                    if os.path.isdir(os.path.join(source_dir, d)) and d.isdigit()
                ]
                if date_dirs:
                    latest_date = max(date_dirs)
                    ticker_dir = os.path.join(source_dir, latest_date, ticker)
                else:
                    ticker_dir = os.path.join(source_dir, ticker)  # fallback
            else:
                ticker_dir = os.path.join(STAGE_01_EXTRACT_DIR, source, ticker)
        if not os.path.isdir(ticker_dir):
            continue
        for fname in os.listdir(ticker_dir):
            if fname.endswith(".json"):
                file_path = os.path.join(ticker_dir, fname)
                if is_file_recent(file_path, hours=1):
                    logger.info(f"File {file_path} is recent; skipped.")
                    progress_bar.update(1)
                    continue
                try:
                    import_json_file(file_path, logger)
                except Exception as e:
                    errors += 1
                    logger.exception(f"Error importing file {file_path}: {e}")
                progress_bar.update(1)
    progress_bar.close()
    logger.info(f"All JSON files imported. Total errors: {errors}")


def run_job(config_path):
    """
    Based on YAML configuration file (e.g. config.yml), read configuration and import JSON files from data/stage_00_original/<source>/<ticker>/ to Neo4j.
    Configuration file should contain:
      - tickers: list of ticker symbols
      - source: data source name (e.g. "yfinance")
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    tickers = config_data.get("tickers", [])
    source = config_data.get("source", "yfinance")

    job_id = f"{source}"
    date_str = datetime.now().strftime("%y%m%d-%H%M%S")
    exe_id = f"{job_id}_{date_str}"
    logger = setup_logger(job_id, date_str)
    logger.info(f"Job started: exe_id={exe_id}")

    sf = Snowflake(machine_id=1)
    total = len(tickers)
    processed = 0
    progress_bar = create_progress_bar(total, description="Tickers")
    for ticker in tickers:
        request_logid = sf.get_id()
        ticker_logger = logging.LoggerAdapter(logger, {"request_logid": request_logid})
        ticker_logger.info(f"Processing ticker: {ticker}")
        try:
            import_all_json_files(source, [ticker], ticker_logger)
        except Exception:
            ticker_logger.exception(f"Error processing ticker {ticker}")
        processed += 1
        progress_bar.update(1)
    progress_bar.close()

    logger.info(f"Job finished: exe_id={exe_id}, Processed {processed} tickers")
    print(f"Job summary: Processed {processed} tickers")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <config_file_path>")
        sys.exit(1)
    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        print(f"Config file {config_file} does not exist.")
        sys.exit(1)
    run_job(config_file)
