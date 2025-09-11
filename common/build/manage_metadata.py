#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Metadata Management Utility

This script provides commands for managing download metadata including:
- Rebuilding metadata from existing files
- Retrying failed downloads
- Generating markdown indexes
- Cleaning up orphaned metadata
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import common modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.build.metadata_manager import MetadataManager


def get_base_data_dir():
    """Get the base data directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "data" / "original"


def list_sources_and_tickers(metadata_manager):
    """List all available sources and tickers."""
    base_dir = Path(metadata_manager.base_data_dir)
    if not base_dir.exists():
        print("No data directory found.")
        return

    print("Available sources and tickers:")
    for source_dir in base_dir.iterdir():
        if source_dir.is_dir():
            print(f"\n📁 {source_dir.name}:")
            ticker_dirs = [d for d in source_dir.iterdir() if d.is_dir()]
            if ticker_dirs:
                for ticker_dir in sorted(ticker_dirs):
                    metadata_path = ticker_dir / ".metadata.json"
                    if metadata_path.exists():
                        print(f"   ✓ {ticker_dir.name} (with metadata)")
                    else:
                        print(f"   ❌ {ticker_dir.name} (no metadata)")
            else:
                print("   (no tickers)")


def rebuild_metadata(metadata_manager, source=None, ticker=None):
    """Rebuild metadata from existing files."""
    base_dir = Path(metadata_manager.base_data_dir)
    if not base_dir.exists():
        print("No data directory found.")
        return

    if source and ticker:
        # Rebuild specific ticker
        print(f"Rebuilding metadata for {source}/{ticker}...")
        metadata_manager.rebuild_metadata_from_files(source, ticker)
        print(f"✓ Rebuilt metadata for {source}/{ticker}")
    elif source:
        # Rebuild all tickers for a source
        source_dir = base_dir / source
        if not source_dir.exists():
            print(f"Source '{source}' not found.")
            return

        print(f"Rebuilding metadata for all tickers in {source}...")
        for ticker_dir in source_dir.iterdir():
            if ticker_dir.is_dir():
                ticker = ticker_dir.name
                print(f"  Processing {ticker}...")
                metadata_manager.rebuild_metadata_from_files(source, ticker)
        print(f"✓ Rebuilt metadata for all tickers in {source}")
    else:
        # Rebuild all
        print("Rebuilding metadata for all sources and tickers...")
        for source_dir in base_dir.iterdir():
            if source_dir.is_dir():
                source = source_dir.name
                print(f"\n📁 Processing {source}...")
                for ticker_dir in source_dir.iterdir():
                    if ticker_dir.is_dir():
                        ticker = ticker_dir.name
                        print(f"  Processing {ticker}...")
                        metadata_manager.rebuild_metadata_from_files(source, ticker)
        print("✓ Rebuilt metadata for all sources and tickers")


def generate_indexes(metadata_manager, source=None, ticker=None):
    """Generate markdown indexes."""
    base_dir = Path(metadata_manager.base_data_dir)
    if not base_dir.exists():
        print("No data directory found.")
        return

    if source and ticker:
        # Generate index for specific ticker
        print(f"Generating index for {source}/{ticker}...")
        metadata_manager.generate_markdown_index(source, ticker)
        print(f"✓ Generated index for {source}/{ticker}")
    elif source:
        # Generate indexes for all tickers in a source
        source_dir = base_dir / source
        if not source_dir.exists():
            print(f"Source '{source}' not found.")
            return

        print(f"Generating indexes for all tickers in {source}...")
        for ticker_dir in source_dir.iterdir():
            if ticker_dir.is_dir():
                ticker = ticker_dir.name
                metadata_path = ticker_dir / ".metadata.json"
                if metadata_path.exists():
                    print(f"  Processing {ticker}...")
                    metadata_manager.generate_markdown_index(source, ticker)
        print(f"✓ Generated indexes for all tickers in {source}")
    else:
        # Generate all indexes
        print("Generating indexes for all sources and tickers...")
        for source_dir in base_dir.iterdir():
            if source_dir.is_dir():
                source = source_dir.name
                print(f"\n📁 Processing {source}...")
                for ticker_dir in source_dir.iterdir():
                    if ticker_dir.is_dir():
                        ticker = ticker_dir.name
                        metadata_path = ticker_dir / ".metadata.json"
                        if metadata_path.exists():
                            print(f"  Processing {ticker}...")
                            metadata_manager.generate_markdown_index(source, ticker)
        print("✓ Generated indexes for all sources and tickers")


def show_failed_downloads(metadata_manager, source=None, ticker=None):
    """Show failed download attempts."""
    base_dir = Path(metadata_manager.base_data_dir)
    if not base_dir.exists():
        print("No data directory found.")
        return

    total_failures = 0

    if source and ticker:
        # Show failures for specific ticker
        failures = metadata_manager.get_failed_downloads(source, ticker)
        if failures:
            print(f"\n❌ Failed downloads for {source}/{ticker}:")
            for failure in failures:
                print(
                    f"  - {failure['timestamp']}: {failure['data_type']} - {failure.get('error_message', 'Unknown error')}"
                )
            total_failures += len(failures)
    elif source:
        # Show failures for all tickers in a source
        source_dir = base_dir / source
        if not source_dir.exists():
            print(f"Source '{source}' not found.")
            return

        for ticker_dir in source_dir.iterdir():
            if ticker_dir.is_dir():
                ticker = ticker_dir.name
                failures = metadata_manager.get_failed_downloads(source, ticker)
                if failures:
                    print(f"\n❌ Failed downloads for {source}/{ticker}:")
                    for failure in failures:
                        print(
                            f"  - {failure['timestamp']}: {failure['data_type']} - {failure.get('error_message', 'Unknown error')}"
                        )
                    total_failures += len(failures)
    else:
        # Show all failures
        for source_dir in base_dir.iterdir():
            if source_dir.is_dir():
                source = source_dir.name
                for ticker_dir in source_dir.iterdir():
                    if ticker_dir.is_dir():
                        ticker = ticker_dir.name
                        failures = metadata_manager.get_failed_downloads(source, ticker)
                        if failures:
                            print(f"\n❌ Failed downloads for {source}/{ticker}:")
                            for failure in failures:
                                print(
                                    f"  - {failure['timestamp']}: {failure['data_type']} - {failure.get('error_message', 'Unknown error')}"
                                )
                            total_failures += len(failures)

    if total_failures == 0:
        print("✓ No failed downloads found.")
    else:
        print(f"\nTotal failed downloads: {total_failures}")


def cleanup_orphaned(metadata_manager, source=None, ticker=None):
    """Clean up orphaned metadata entries."""
    base_dir = Path(metadata_manager.base_data_dir)
    if not base_dir.exists():
        print("No data directory found.")
        return

    if source and ticker:
        # Clean specific ticker
        print(f"Cleaning orphaned metadata for {source}/{ticker}...")
        metadata_manager.cleanup_orphaned_metadata(source, ticker)
        print(f"✓ Cleaned orphaned metadata for {source}/{ticker}")
    elif source:
        # Clean all tickers for a source
        source_dir = base_dir / source
        if not source_dir.exists():
            print(f"Source '{source}' not found.")
            return

        print(f"Cleaning orphaned metadata for all tickers in {source}...")
        for ticker_dir in source_dir.iterdir():
            if ticker_dir.is_dir():
                ticker = ticker_dir.name
                metadata_path = ticker_dir / ".metadata.json"
                if metadata_path.exists():
                    print(f"  Processing {ticker}...")
                    metadata_manager.cleanup_orphaned_metadata(source, ticker)
        print(f"✓ Cleaned orphaned metadata for all tickers in {source}")
    else:
        # Clean all
        print("Cleaning orphaned metadata for all sources and tickers...")
        for source_dir in base_dir.iterdir():
            if source_dir.is_dir():
                source = source_dir.name
                print(f"\n📁 Processing {source}...")
                for ticker_dir in source_dir.iterdir():
                    if ticker_dir.is_dir():
                        ticker = ticker_dir.name
                        metadata_path = ticker_dir / ".metadata.json"
                        if metadata_path.exists():
                            print(f"  Processing {ticker}...")
                            metadata_manager.cleanup_orphaned_metadata(source, ticker)
        print("✓ Cleaned orphaned metadata for all sources and tickers")


def main():
    parser = argparse.ArgumentParser(description="Manage download metadata")
    parser.add_argument(
        "command",
        choices=["list", "rebuild", "index", "failures", "cleanup"],
        help="Command to execute",
    )
    parser.add_argument("--source", "-s", help="Source name (e.g., 'yfinance', 'sec-edgar')")
    parser.add_argument("--ticker", "-t", help="Ticker symbol")

    args = parser.parse_args()

    base_data_dir = get_base_data_dir()
    metadata_manager = MetadataManager(str(base_data_dir))

    if args.command == "list":
        list_sources_and_tickers(metadata_manager)
    elif args.command == "rebuild":
        rebuild_metadata(metadata_manager, args.source, args.ticker)
    elif args.command == "index":
        generate_indexes(metadata_manager, args.source, args.ticker)
    elif args.command == "failures":
        show_failed_downloads(metadata_manager, args.source, args.ticker)
    elif args.command == "cleanup":
        cleanup_orphaned(metadata_manager, args.source, args.ticker)


if __name__ == "__main__":
    main()
