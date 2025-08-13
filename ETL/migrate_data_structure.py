#!/usr/bin/env python3
"""
Data structure migration script for ETL pipeline reorganization.
Migrates from original/ structure to stage-based ETL structure.

Usage: pixi run python scripts/migrate_data_structure.py
"""

import json
import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DataMigrator:
    def __init__(self, base_path: str = "/Users/SP14016/zitian/my_finance/data"):
        self.base_path = Path(base_path)
        self.original_path = self.base_path / "original"
        self.stage_01_path = self.base_path / "stage_01_extract"
        self.backup_path = (
            self.base_path / "backup" / datetime.now().strftime("backup_%Y%m%d_%H%M%S")
        )

        # CIK to ticker mapping for M7 companies
        self.cik_to_ticker = {
            "0000320193": "AAPL",
            "0000789019": "MSFT",
            "0001018724": "AMZN",
            "0001652044": "GOOGL",
            "0001318605": "TSLA",
            "0001326801": "META",
            "0001065280": "NFLX",
        }

    def backup_original_data(self) -> bool:
        """Backup original data before migration"""
        try:
            logger.info(f"Creating backup at {self.backup_path}")
            self.backup_path.mkdir(parents=True, exist_ok=True)

            if self.original_path.exists():
                shutil.copytree(self.original_path, self.backup_path / "original")
                logger.info("Original data backed up successfully")

            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract date from filename in YYMMDD-HHMMSS format and convert to YYYYMMDD"""
        # Pattern: TICKER_source_type_YYMMDD-HHMMSS.json
        pattern = r"_(\d{6})-\d{6}\.json$"
        match = re.search(pattern, filename)
        if match:
            yymmdd = match.group(1)
            # Convert YY to YYYY (assume 20XX for now)
            yyyy = "20" + yymmdd[:2]
            mmdd = yymmdd[2:]
            return yyyy + mmdd
        return None

    def migrate_yfinance_data(self) -> bool:
        """Migrate yfinance data from original/yfinance to stage_01_extract/yfinance"""
        try:
            source_path = self.original_path / "yfinance"
            target_path = self.stage_01_path / "yfinance"

            if not source_path.exists():
                logger.warning("No yfinance data found to migrate")
                return True

            logger.info("Migrating yfinance data...")

            for ticker_dir in source_path.iterdir():
                if not ticker_dir.is_dir():
                    continue

                ticker = ticker_dir.name
                logger.info(f"Processing ticker: {ticker}")

                for file_path in ticker_dir.glob("*.json"):
                    # Extract date from filename
                    date_str = self.extract_date_from_filename(file_path.name)
                    if not date_str:
                        logger.warning(
                            f"Could not extract date from {file_path.name}, using today's date"
                        )
                        date_str = datetime.now().strftime("%Y%m%d")

                    # Create target directory structure
                    target_ticker_path = target_path / date_str / ticker
                    target_ticker_path.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    target_file = target_ticker_path / file_path.name
                    shutil.copy2(file_path, target_file)

                    logger.debug(f"Migrated: {file_path} -> {target_file}")

                # Copy README.md if exists
                readme_path = ticker_dir / "README.md"
                if readme_path.exists():
                    # Copy to most recent date partition
                    latest_date = max([d.name for d in target_path.glob("*/") if d.is_dir()])
                    target_readme = target_path / latest_date / ticker / "README.md"
                    shutil.copy2(readme_path, target_readme)

            logger.info("yfinance data migration completed")
            return True

        except Exception as e:
            logger.error(f"yfinance migration failed: {e}")
            return False

    def migrate_sec_edgar_data(self) -> bool:
        """Migrate SEC Edgar data from CIK-based to ticker-based structure"""
        try:
            source_path = self.original_path / "sec-edgar"
            target_path = self.stage_01_path / "sec_edgar"

            if not source_path.exists():
                logger.warning("No SEC Edgar data found to migrate")
                return True

            logger.info("Migrating SEC Edgar data...")

            for cik_dir in source_path.iterdir():
                if not cik_dir.is_dir():
                    continue

                cik = cik_dir.name
                ticker = self.cik_to_ticker.get(cik, f"CIK_{cik}")

                logger.info(f"Processing CIK {cik} -> {ticker}")

                # Process each filing type
                for filing_type_dir in cik_dir.iterdir():
                    if not filing_type_dir.is_dir():
                        continue

                    filing_type = filing_type_dir.name  # 10k, 10q, 8k

                    # Navigate through the nested CIK structure
                    nested_cik_path = (
                        filing_type_dir
                        / cik
                        / filing_type.upper().replace("K", "-K").replace("Q", "-Q")
                    )

                    if not nested_cik_path.exists():
                        logger.warning(f"Expected path not found: {nested_cik_path}")
                        continue

                    for file_path in nested_cik_path.glob("*.txt"):
                        # Use today's date as partition (SEC filings don't have extraction date in filename)
                        date_str = datetime.now().strftime("%Y%m%d")

                        # Create target directory structure
                        target_ticker_path = target_path / date_str / ticker
                        target_ticker_path.mkdir(parents=True, exist_ok=True)

                        # Create new filename: TICKER_sec_edgar_FILING_TYPE_TIMESTAMP.txt
                        timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
                        new_filename = (
                            f"{ticker}_sec_edgar_{filing_type}_{timestamp}_{file_path.name}"
                        )
                        target_file = target_ticker_path / new_filename

                        # Copy file
                        shutil.copy2(file_path, target_file)
                        logger.debug(f"Migrated: {file_path} -> {target_file}")

                # Create README.md for ticker
                date_str = datetime.now().strftime("%Y%m%d")
                readme_path = target_path / date_str / ticker / "README.md"
                readme_path.parent.mkdir(parents=True, exist_ok=True)

                with open(readme_path, "w") as f:
                    f.write(f"# {ticker} SEC Edgar Filings\n\n")
                    f.write(f"**CIK**: {cik}\n")
                    f.write(f"**Ticker**: {ticker}\n")
                    f.write(f"**Migration Date**: {datetime.now().isoformat()}\n\n")
                    f.write("## File Types\n")
                    f.write("- 10-K: Annual reports\n")
                    f.write("- 10-Q: Quarterly reports\n")
                    f.write("- 8-K: Current reports\n\n")
                    f.write("## Naming Convention\n")
                    f.write(
                        "Format: `TICKER_sec_edgar_FILING_TYPE_TIMESTAMP_ORIGINAL_FILENAME.txt`\n"
                    )

            logger.info("SEC Edgar data migration completed")
            return True

        except Exception as e:
            logger.error(f"SEC Edgar migration failed: {e}")
            return False

    def create_symlinks(self) -> bool:
        """Create 'latest' symlinks pointing to most recent partitions"""
        try:
            logger.info("Creating latest symlinks...")

            for source_dir in ["yfinance", "sec_edgar"]:
                stage_path = self.stage_01_path / source_dir

                if not stage_path.exists():
                    continue

                # Find most recent date partition
                date_dirs = [d for d in stage_path.iterdir() if d.is_dir() and d.name.isdigit()]
                if not date_dirs:
                    continue

                latest_date = max(date_dirs, key=lambda x: x.name)

                # Create symlink
                latest_link = stage_path / "latest"
                if latest_link.exists():
                    latest_link.unlink()

                latest_link.symlink_to(latest_date.name)
                logger.info(f"Created symlink: {latest_link} -> {latest_date.name}")

            return True

        except Exception as e:
            logger.error(f"Symlink creation failed: {e}")
            return False

    def validate_migration(self) -> bool:
        """Validate that migration completed successfully"""
        try:
            logger.info("Validating migration...")

            # Check that stage_01_extract has data
            yfinance_files = list(self.stage_01_path.rglob("*yfinance*.json"))
            sec_files = list(self.stage_01_path.rglob("*sec_edgar*.txt"))

            logger.info(f"Found {len(yfinance_files)} yfinance files")
            logger.info(f"Found {len(sec_files)} SEC Edgar files")

            # Check symlinks exist
            yf_latest = self.stage_01_path / "yfinance" / "latest"
            sec_latest = self.stage_01_path / "sec_edgar" / "latest"

            if yf_latest.exists():
                logger.info(f"yfinance latest symlink: {yf_latest} -> {yf_latest.readlink()}")

            if sec_latest.exists():
                logger.info(f"sec_edgar latest symlink: {sec_latest} -> {sec_latest.readlink()}")

            return len(yfinance_files) > 0 or len(sec_files) > 0

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def run_migration(self) -> bool:
        """Execute the complete migration process"""
        logger.info("Starting data structure migration...")

        steps = [
            ("Backup original data", self.backup_original_data),
            ("Migrate yfinance data", self.migrate_yfinance_data),
            ("Migrate SEC Edgar data", self.migrate_sec_edgar_data),
            ("Create symlinks", self.create_symlinks),
            ("Validate migration", self.validate_migration),
        ]

        for step_name, step_func in steps:
            logger.info(f"Step: {step_name}")
            if not step_func():
                logger.error(f"Migration failed at step: {step_name}")
                return False

        logger.info("Data structure migration completed successfully!")
        logger.info(f"Backup created at: {self.backup_path}")

        return True


def main():
    migrator = DataMigrator()
    success = migrator.run_migration()

    if success:
        logger.info("Migration completed successfully!")
        return 0
    else:
        logger.error("Migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
