#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Retry Failed Downloads Utility

This script identifies failed downloads and retries them using the appropriate spider.
Supports both yfinance and SEC Edgar data sources.
"""

import os
import sys
import argparse
import subprocess
import tempfile
import yaml
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path to import common modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.metadata_manager import MetadataManager


def get_base_data_dir():
    """Get the base data directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "data" / "original"


def create_temp_config(source, ticker, failed_downloads):
    """Create a temporary config file for retrying failed downloads."""
    if source == "yfinance":
        # Create yfinance config
        config = {
            "source": "yfinance",
            "tickers": [ticker],
            "data_periods": []
        }
        
        # Extract unique data periods from failed downloads
        periods_set = set()
        for failure in failed_downloads:
            config_info = failure.get("config_info", {})
            period = config_info.get("period")
            interval = config_info.get("interval")
            oid = config_info.get("oid")
            data_type = failure.get("data_type")
            
            if all([period, interval, oid or data_type]):
                period_key = (oid or data_type, period, interval)
                periods_set.add(period_key)
        
        for oid, period, interval in periods_set:
            config["data_periods"].append({
                "oid": oid,
                "period": period,
                "interval": interval
            })
    
    elif source == "sec-edgar":
        # Create SEC Edgar config
        config = {
            "source": "sec-edgar",
            "tickers": [ticker],
            "count": 8,
            "email": "ZitianSG (wangzitian0@gmail.com)",
            "file_types": []
        }
        
        # Extract unique filing types from failed downloads
        filing_types = set()
        for failure in failed_downloads:
            config_info = failure.get("config_info", {})
            filing_type = config_info.get("filing_type")
            data_type = failure.get("data_type")
            
            if filing_type:
                filing_types.add(filing_type)
            elif data_type:
                filing_types.add(data_type.upper())
        
        config["file_types"] = list(filing_types)
    
    else:
        raise ValueError(f"Unsupported source: {source}")
    
    return config


def retry_failed_downloads(metadata_manager, source=None, ticker=None, dry_run=False):
    """Retry failed downloads for specified source/ticker or all."""
    base_dir = Path(metadata_manager.base_data_dir)
    if not base_dir.exists():
        print("No data directory found.")
        return
    
    retry_count = 0
    
    # Collect all failed downloads to retry
    retries_to_perform = []
    
    if source and ticker:
        # Retry for specific ticker
        failures = metadata_manager.get_failed_downloads(source, ticker)
        if failures:
            retries_to_perform.append((source, ticker, failures))
    elif source:
        # Retry for all tickers in a source
        source_dir = base_dir / source
        if not source_dir.exists():
            print(f"Source '{source}' not found.")
            return
        
        for ticker_dir in source_dir.iterdir():
            if ticker_dir.is_dir():
                ticker_name = ticker_dir.name
                failures = metadata_manager.get_failed_downloads(source, ticker_name)
                if failures:
                    retries_to_perform.append((source, ticker_name, failures))
    else:
        # Retry all failures
        for source_dir in base_dir.iterdir():
            if source_dir.is_dir():
                source_name = source_dir.name
                for ticker_dir in source_dir.iterdir():
                    if ticker_dir.is_dir():
                        ticker_name = ticker_dir.name
                        failures = metadata_manager.get_failed_downloads(source_name, ticker_name)
                        if failures:
                            retries_to_perform.append((source_name, ticker_name, failures))
    
    if not retries_to_perform:
        print("✓ No failed downloads found to retry.")
        return
    
    print(f"Found {len(retries_to_perform)} ticker(s) with failed downloads to retry.")
    
    for source_name, ticker_name, failures in retries_to_perform:
        print(f"\n🔄 Retrying {len(failures)} failed downloads for {source_name}/{ticker_name}")
        
        if dry_run:
            print("  DRY RUN - would retry:")
            for failure in failures:
                print(f"    - {failure['data_type']}: {failure.get('error_message', 'Unknown error')}")
            continue
        
        try:
            # Create temporary config file
            config = create_temp_config(source_name, ticker_name, failures)
            
            # Write config to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
                yaml.dump(config, temp_file, default_flow_style=False)
                temp_config_path = temp_file.name
            
            # Determine which spider to run
            if source_name == "yfinance":
                spider_path = Path(__file__).parent.parent / "spider" / "yfinance_spider.py"
            elif source_name == "sec-edgar":
                spider_path = Path(__file__).parent.parent / "spider" / "sec_edgar_spider.py"
            else:
                print(f"  ❌ Unknown source: {source_name}")
                continue
            
            # Run the spider
            print(f"  Running spider: {spider_path}")
            print(f"  Config: {temp_config_path}")
            
            result = subprocess.run([
                sys.executable, str(spider_path), temp_config_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ Successfully retried downloads for {source_name}/{ticker_name}")
                retry_count += len(failures)
            else:
                print(f"  ❌ Failed to retry downloads for {source_name}/{ticker_name}")
                print(f"  Error: {result.stderr}")
            
            # Clean up temporary file
            os.unlink(temp_config_path)
            
        except Exception as e:
            print(f"  ❌ Error retrying {source_name}/{ticker_name}: {e}")
    
    print(f"\n✓ Retry process completed. Attempted to retry {retry_count} failed downloads.")


def main():
    parser = argparse.ArgumentParser(description="Retry failed downloads")
    parser.add_argument("--source", "-s", help="Source name (e.g., 'yfinance', 'sec-edgar')")
    parser.add_argument("--ticker", "-t", help="Ticker symbol")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be retried without actually running")
    
    args = parser.parse_args()
    
    base_data_dir = get_base_data_dir()
    metadata_manager = MetadataManager(str(base_data_dir))
    
    retry_failed_downloads(metadata_manager, args.source, args.ticker, args.dry_run)


if __name__ == "__main__":
    main()