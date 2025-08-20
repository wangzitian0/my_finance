#!/usr/bin/env python3
"""
Please install lxml library first:
    pip install lxml

CIK numbers for the Magnificent 7 (7 major tech companies):
  - Apple (AAPL):       0000320193
  - Microsoft (MSFT):   0000789019
  - Amazon (AMZN):      0001018724
  - Alphabet (GOOGL):   0001652044
  - Facebook (FB, Meta):0001326801
  - Tesla (TSLA):       0001318605
  - Netflix (NFLX):     0001065280

It's recommended to use the above CIK numbers directly in configuration files instead of ticker symbols,
so the program will directly use CIK to query filings data, avoiding errors from internal conversion requests to /files/company_tickers.json.
"""

import warnings

try:
    from bs4 import XMLParsedAsHTMLWarning
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except ImportError:
    print("⚠️ Warning: beautifulsoup4 not available - some warnings may appear")

import json
import logging
import os
import time
from datetime import datetime, timedelta

import yaml
try:
    from secedgar import FilingType, filings
    SECEDGAR_AVAILABLE = True
    print("✅ secedgar import successful")
except ImportError as e:
    print(f"⚠️ secedgar not available: {e}")
    print("SEC Edgar collection will be skipped")
    FilingType = None
    filings = None
    SECEDGAR_AVAILABLE = False
from tqdm import tqdm

from common.metadata_manager import MetadataManager

# Set log output level to DEBUG
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Define base directory for saving data: data/stage_01_extract/sec_edgar/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGE_01_EXTRACT_DIR = os.path.join(BASE_DIR, "data", "stage_01_extract", "sec_edgar")
if not os.path.exists(STAGE_01_EXTRACT_DIR):
    os.makedirs(STAGE_01_EXTRACT_DIR)


def is_file_recent(filepath, hours=1):
    """
    Check if file was modified within the specified hours
    Parameters:
      filepath: file path
      hours: number of hours
    """
    if os.path.exists(filepath):
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        return datetime.now() - mtime < timedelta(hours=hours)
    return False


def run_job(config_path):
    """
    Main task: Load configuration from YAML config file, and process each CIK and filing type in sequence,
    directly calling secedgar.filings object's save() method to save filings data.
    Data will be saved in: data/stage_01_extract/sec_edgar/<date_partition>/<ticker>/ directory.
    Parameters:
      config_path: configuration file path
    """
    if not SECEDGAR_AVAILABLE:
        logging.warning("secedgar library not available - skipping SEC Edgar data collection")
        print("⚠️ SEC Edgar collection skipped - secedgar dependency not available")
        return
        
    logging.info(f"Loading configuration file: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Directly use CIK numbers (e.g. "0000320193")
    cik_list = config.get("tickers", [])
    count = config.get("count", 8)
    file_types = config.get("file_types", ["10K", "10Q", "13F", "8K"])
    email = config.get("email", "ZitianSG (wangzitian0@gmail.com)")

    # Initialize metadata manager
    metadata_manager = MetadataManager(STAGE_01_EXTRACT_DIR)

    total_tasks = len(cik_list) * len(file_types)
    logging.info(f"Starting to process tasks, total {total_tasks} tasks")
    pbar = tqdm(total=total_tasks, desc="Tickers Progress", unit="task")

    filing_type_map = {
        "10K": FilingType.FILING_10K,
        "10Q": FilingType.FILING_10Q,
        "13F": FilingType.FILING_13F,
        "8K": FilingType.FILING_8K,
    }

    for cik in cik_list:
        logging.info(f"Directly query using CIK: {cik}")
        # Map CIK to ticker for new directory structure
        cik_to_ticker = {
            "0000320193": "AAPL",
            "0000789019": "MSFT",
            "0001018724": "AMZN",
            "0001652044": "GOOGL",
            "0001318605": "TSLA",
            "0001326801": "META",
            "0001065280": "NFLX",
        }

        ticker = cik_to_ticker.get(cik, f"CIK_{cik}")
        date_partition = datetime.now().strftime("%Y%m%d")
        ticker_dir = os.path.join(STAGE_01_EXTRACT_DIR, date_partition, ticker)
        if not os.path.exists(ticker_dir):
            os.makedirs(ticker_dir)
        for ft in file_types:
            logging.info(f"开始处理 {cik} 的 {ft} filings")
            filing_type_enum = filing_type_map.get(ft)
            if filing_type_enum is None:
                logging.error(f"不支持的 filing 类型: {ft}，CIK: {cik}")
                pbar.update(1)
                continue

            # Create config info for this request
            config_info = {"filing_type": ft, "count": count, "email": email}

            # Check if recent data exists using metadata manager (check for 7 days for SEC filings)
            if metadata_manager.check_file_exists_recent(
                "sec_edgar", ticker, ft.lower(), config_info, hours=168
            ):  # 7 days
                logging.info(f"{ticker} ({cik}) {ft} filings: Recent data exists (skipped).")
            else:
                # All filings for a ticker go in the same directory
                output_dir = ticker_dir
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

            try:
                filings_obj = filings(
                    cik_lookup=cik,
                    filing_type=filing_type_enum,
                    count=count,
                    user_agent=email,
                )
                # Directly set cik_lookup internal mapping, avoiding calls to /files/company_tickers.json
                filings_obj.cik_lookup._lookup_dict = {cik: cik}
                filings_obj.save(output_dir)
                logging.info(f"Successfully saved {cik} {ft} filings to {output_dir}")

                # Update metadata for all downloaded files
                if os.path.exists(output_dir):
                    for filename in os.listdir(output_dir):
                        filepath = os.path.join(output_dir, filename)
                        if os.path.isfile(filepath):
                            metadata_manager.add_file_record(
                                "sec-edgar", cik, filepath, ft.lower(), config_info
                            )
                    metadata_manager.generate_markdown_index("sec-edgar", cik)

            except Exception as e:
                error_msg = str(e)
                metadata_manager.mark_download_failed(
                    "sec-edgar", cik, ft.lower(), config_info, error_msg
                )
                logging.exception(f"Error processing {cik} {ft} filings: {e}")
                logging.info(
                    "Please check access permissions for /files/company_tickers.json, if issues persist please manually download the file."
                )
            pbar.update(1)
            time.sleep(3)

    pbar.close()
    logging.info("All tasks processing completed")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        logging.error("Usage: python run_job.py <config_file_path>")
        sys.exit(1)
    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        logging.error(f"Configuration file {config_file} does not exist.")
        sys.exit(1)
    run_job(config_file)
