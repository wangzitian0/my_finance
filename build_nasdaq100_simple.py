#!/usr/bin/env python3
"""
Simple NASDAQ100 builder - reuses existing data format like M7
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path


def build_nasdaq100():
    """Build NASDAQ100 dataset by copying/organizing existing data"""

    # NASDAQ100 tickers (first 20 for testing, similar to M7's 7)
    nasdaq100_sample = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "META",
        "TSLA",
        "NFLX",  # M7
        "NVDA",
        "ADBE",
        "AMD",
        "ABNB",
        "GOOG",
        "AEP",
        "AMGN",  # Additional
        "ADI",
        "ANSS",
        "AMAT",
        "APP",
        "ARM",
        "ASML",  # More
    ]

    print(f"🔧 Building NASDAQ100 sample dataset...")
    print(f"   Companies: {len(nasdaq100_sample)}")
    print(f"   Strategy: Use existing data with standardized naming")

    base_dir = Path("data/original/yfinance")
    processed = 0

    for ticker in nasdaq100_sample:
        ticker_dir = base_dir / ticker
        if ticker_dir.exists():
            # Find the most recent data file for this ticker
            json_files = list(ticker_dir.glob("*.json"))
            if json_files:
                # Use the most recent file
                latest_file = max(json_files, key=lambda f: f.stat().st_mtime)

                # Create standardized filename: TICKER_yfinance_1y_1d_TIMESTAMP.json
                timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
                new_name = f"{ticker}_yfinance_1y_1d_{timestamp}.json"

                # Copy with new name (simulating download with proper naming)
                target_path = ticker_dir / new_name
                if not target_path.exists():  # Avoid duplicates
                    shutil.copy2(latest_file, target_path)
                    print(f"  ✅ {ticker}: {new_name}")
                    processed += 1
                else:
                    print(f"  ⚪ {ticker}: Already has standardized data")
            else:
                print(f"  ❌ {ticker}: No data found")
        else:
            print(f"  ❌ {ticker}: Directory not found")

    # Create build report
    report = {
        "tier": "nasdaq100_sample",
        "build_timestamp": datetime.now().isoformat(),
        "companies_processed": processed,
        "total_companies": len(nasdaq100_sample),
        "data_format": "standardized_naming",
        "naming_pattern": "TICKER_yfinance_1y_1d_TIMESTAMP.json",
    }

    report_path = Path("data/build_report_nasdaq100_sample.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ NASDAQ100 sample built successfully!")
    print(f"   Processed: {processed}/{len(nasdaq100_sample)} companies")
    print(f"   Report: {report_path}")

    return processed > 0


if __name__ == "__main__":
    build_nasdaq100()
