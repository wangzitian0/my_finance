#!/usr/bin/env python3
"""
Unified Directory Management System
Standardizes directory structure across all stages: stage_xx_yyyy/YYYYMMDD/TICKER/<file>.<type>
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class DirectoryManager:
    """
    Unified directory manager enforcing consistent structure across all stages.

    Standard Format: stage_xx_yyyy/YYYYMMDD/TICKER/<file>.<type>

    Examples:
    - stage_00_original/20250818/AAPL/AAPL_yfinance_daily.json
    - stage_01_extract/20250818/AAPL/AAPL_sec_edgar_10k_001.txt
    - stage_02_transform/20250818/AAPL/AAPL_cleaned_financials.json
    - stage_03_load/20250818/AAPL/AAPL_graph_nodes.json
    """

    # Stage definitions
    STAGES = {
        "stage_00_original": "Raw data collection (SEC Edgar, YFinance)",
        "stage_01_extract": "Extracted and parsed data",
        "stage_02_transform": "Cleaned and normalized data",
        "stage_03_load": "Graph nodes and embeddings",
        "stage_04_analysis": "DCF analysis results",
        "stage_05_reporting": "Final reports and visualizations",
        "stage_99_build": "Build artifacts and manifests",
    }

    # Data source types
    DATA_SOURCES = {
        "yfinance": "Yahoo Finance data",
        "sec_edgar": "SEC Edgar filings",
        "graph_nodes": "Neo4j graph nodes",
        "embeddings": "Vector embeddings",
        "dcf_results": "DCF calculation results",
    }

    def __init__(self, base_path: Union[str, Path] = "data"):
        """Initialize directory manager with base data path."""
        self.base_path = Path(base_path)

    def get_standard_path(
        self,
        stage: str,
        ticker: str,
        date_partition: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Get standardized path following stage_xx_yyyy/YYYYMMDD/TICKER/<file> format.

        Args:
            stage: Stage name (e.g., 'stage_00_original')
            ticker: Stock ticker (e.g., 'AAPL')
            date_partition: Date partition (e.g., '20250818'), defaults to today
            filename: Optional filename to append

        Returns:
            Path object following standard format
        """
        if date_partition is None:
            date_partition = datetime.now().strftime("%Y%m%d")

        path = self.base_path / stage / date_partition / ticker

        if filename:
            path = path / filename

        return path

    def create_directory_structure(
        self, stage: str, ticker: str, date_partition: Optional[str] = None
    ) -> Path:
        """
        Create standardized directory structure.

        Returns:
            Created directory path
        """
        path = self.get_standard_path(stage, ticker, date_partition)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def list_tickers_in_stage(self, stage: str, date_partition: Optional[str] = None) -> List[str]:
        """
        List all tickers in a given stage and date partition.

        Returns:
            List of ticker symbols
        """
        if date_partition is None:
            date_partition = datetime.now().strftime("%Y%m%d")

        stage_path = self.base_path / stage / date_partition

        if not stage_path.exists():
            return []

        return [d.name for d in stage_path.iterdir() if d.is_dir()]

    def get_files_for_ticker(
        self,
        stage: str,
        ticker: str,
        date_partition: Optional[str] = None,
        file_pattern: Optional[str] = None,
    ) -> List[Path]:
        """
        Get all files for a ticker in a stage.

        Args:
            stage: Stage name
            ticker: Stock ticker
            date_partition: Date partition, defaults to today
            file_pattern: Optional regex pattern to filter files

        Returns:
            List of file paths
        """
        ticker_path = self.get_standard_path(stage, ticker, date_partition)

        if not ticker_path.exists():
            return []

        files = [f for f in ticker_path.iterdir() if f.is_file()]

        if file_pattern:
            pattern = re.compile(file_pattern)
            files = [f for f in files if pattern.search(f.name)]

        return sorted(files)

    def migrate_legacy_structure(
        self, stage: str, legacy_path: Path, date_partition: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Migrate legacy directory structure to standard format.

        Args:
            stage: Target stage name
            legacy_path: Path to legacy directory structure
            date_partition: Target date partition, defaults to today

        Returns:
            Dictionary with migration statistics
        """
        if date_partition is None:
            date_partition = datetime.now().strftime("%Y%m%d")

        stats = {"files_moved": 0, "tickers_processed": 0, "errors": 0}

        if not legacy_path.exists():
            return stats

        # Process based on detected structure
        if self._is_ticker_based_structure(legacy_path):
            stats.update(self._migrate_ticker_based(stage, legacy_path, date_partition))
        elif self._is_date_based_structure(legacy_path):
            stats.update(self._migrate_date_based(stage, legacy_path, date_partition))
        else:
            # Try to detect and migrate mixed structures
            stats.update(self._migrate_mixed_structure(stage, legacy_path, date_partition))

        return stats

    def _is_ticker_based_structure(self, path: Path) -> bool:
        """Check if directory follows ticker-based structure (TICKER/files)."""
        if not path.exists():
            return False

        # Look for ticker-like directories (2-5 uppercase letters)
        ticker_pattern = re.compile(r"^[A-Z]{2,5}$")
        subdirs = [d for d in path.iterdir() if d.is_dir()]

        return len(subdirs) > 0 and any(ticker_pattern.match(d.name) for d in subdirs)

    def _is_date_based_structure(self, path: Path) -> bool:
        """Check if directory follows date-based structure (YYYYMMDD/files)."""
        if not path.exists():
            return False

        # Look for date-like directories
        date_pattern = re.compile(r"^\d{8}$")
        subdirs = [d for d in path.iterdir() if d.is_dir()]

        return len(subdirs) > 0 and any(date_pattern.match(d.name) for d in subdirs)

    def _migrate_ticker_based(
        self, stage: str, source_path: Path, date_partition: str
    ) -> Dict[str, int]:
        """Migrate ticker-based structure: TICKER/* -> stage/date/TICKER/*"""
        stats = {"files_moved": 0, "tickers_processed": 0, "errors": 0}

        for ticker_dir in source_path.iterdir():
            if not ticker_dir.is_dir():
                continue

            ticker = ticker_dir.name
            if not re.match(r"^[A-Z]{2,5}$", ticker):
                continue

            try:
                target_dir = self.create_directory_structure(stage, ticker, date_partition)

                for file_path in ticker_dir.iterdir():
                    if file_path.is_file():
                        target_file = target_dir / file_path.name
                        file_path.rename(target_file)
                        stats["files_moved"] += 1

                stats["tickers_processed"] += 1

            except Exception as e:
                print(f"Error migrating {ticker}: {e}")
                stats["errors"] += 1

        return stats

    def _migrate_date_based(
        self, stage: str, source_path: Path, date_partition: str
    ) -> Dict[str, int]:
        """Migrate date-based structure: YYYYMMDD/* -> stage/date/TICKER/*"""
        stats = {"files_moved": 0, "tickers_processed": 0, "errors": 0}

        # For date-based, we need to extract ticker from filenames
        for date_dir in source_path.iterdir():
            if not date_dir.is_dir():
                continue

            for file_path in date_dir.iterdir():
                if not file_path.is_file():
                    continue

                try:
                    # Extract ticker from filename (assume format: TICKER_*)
                    ticker_match = re.match(r"^([A-Z]{2,5})_", file_path.name)
                    if not ticker_match:
                        continue

                    ticker = ticker_match.group(1)
                    target_dir = self.create_directory_structure(stage, ticker, date_partition)
                    target_file = target_dir / file_path.name

                    file_path.rename(target_file)
                    stats["files_moved"] += 1

                except Exception as e:
                    print(f"Error migrating {file_path}: {e}")
                    stats["errors"] += 1

        # Count unique tickers processed
        tickers = set()
        stage_path = self.base_path / stage / date_partition
        if stage_path.exists():
            tickers = {d.name for d in stage_path.iterdir() if d.is_dir()}
        stats["tickers_processed"] = len(tickers)

        return stats

    def _migrate_mixed_structure(
        self, stage: str, source_path: Path, date_partition: str
    ) -> Dict[str, int]:
        """Handle mixed or complex legacy structures."""
        stats = {"files_moved": 0, "tickers_processed": 0, "errors": 0}

        # Walk through all files and try to extract ticker information
        for file_path in source_path.rglob("*"):
            if not file_path.is_file():
                continue

            try:
                # Multiple strategies to extract ticker
                ticker = None

                # Strategy 1: From filename
                ticker_match = re.match(r"^([A-Z]{2,5})_", file_path.name)
                if ticker_match:
                    ticker = ticker_match.group(1)

                # Strategy 2: From parent directory
                if not ticker and re.match(r"^[A-Z]{2,5}$", file_path.parent.name):
                    ticker = file_path.parent.name

                # Strategy 3: From path components
                if not ticker:
                    path_parts = file_path.parts
                    for part in path_parts:
                        if re.match(r"^[A-Z]{2,5}$", part):
                            ticker = part
                            break

                if ticker:
                    target_dir = self.create_directory_structure(stage, ticker, date_partition)
                    target_file = target_dir / file_path.name

                    # Avoid overwriting existing files
                    counter = 1
                    while target_file.exists():
                        name_parts = file_path.stem, counter, file_path.suffix
                        target_file = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        counter += 1

                    file_path.rename(target_file)
                    stats["files_moved"] += 1

            except Exception as e:
                print(f"Error migrating {file_path}: {e}")
                stats["errors"] += 1

        # Count unique tickers processed
        tickers = set()
        stage_path = self.base_path / stage / date_partition
        if stage_path.exists():
            tickers = {d.name for d in stage_path.iterdir() if d.is_dir()}
        stats["tickers_processed"] = len(tickers)

        return stats

    def validate_structure(
        self, stage: str, date_partition: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Validate directory structure compliance.

        Returns:
            Dictionary with validation results
        """
        if date_partition is None:
            date_partition = datetime.now().strftime("%Y%m%d")

        results = {
            "compliant": True,
            "stage": stage,
            "date_partition": date_partition,
            "tickers_found": 0,
            "files_found": 0,
            "issues": [],
        }

        stage_path = self.base_path / stage / date_partition

        if not stage_path.exists():
            results["compliant"] = False
            results["issues"].append(f"Stage path does not exist: {stage_path}")
            return results

        # Check ticker directories
        for ticker_dir in stage_path.iterdir():
            if not ticker_dir.is_dir():
                results["issues"].append(f"Non-directory found in stage: {ticker_dir}")
                continue

            # Validate ticker format
            if not re.match(r"^[A-Z]{2,5}$", ticker_dir.name):
                results["compliant"] = False
                results["issues"].append(f"Invalid ticker format: {ticker_dir.name}")
                continue

            results["tickers_found"] += 1

            # Count files in ticker directory
            files = [f for f in ticker_dir.iterdir() if f.is_file()]
            results["files_found"] += len(files)

            # Validate file naming (should start with ticker)
            for file_path in files:
                if not file_path.name.startswith(ticker_dir.name):
                    results["issues"].append(
                        f"File naming issue: {file_path} should start with {ticker_dir.name}"
                    )

        return results

    def get_structure_summary(self) -> Dict[str, any]:
        """
        Get summary of current directory structure across all stages.

        Returns:
            Dictionary with structure summary
        """
        summary = {"stages": {}, "total_files": 0, "total_tickers": set(), "date_partitions": set()}

        for stage in self.STAGES.keys():
            stage_path = self.base_path / stage

            if not stage_path.exists():
                continue

            stage_info = {"date_partitions": {}, "total_files": 0, "tickers": set()}

            # Process date partitions
            for date_dir in stage_path.iterdir():
                if not date_dir.is_dir() or not re.match(r"^\d{8}$", date_dir.name):
                    continue

                date_partition = date_dir.name
                summary["date_partitions"].add(date_partition)

                partition_info = {"tickers": {}, "total_files": 0}

                # Process ticker directories
                for ticker_dir in date_dir.iterdir():
                    if not ticker_dir.is_dir():
                        continue

                    ticker = ticker_dir.name
                    stage_info["tickers"].add(ticker)
                    summary["total_tickers"].add(ticker)

                    files = [f for f in ticker_dir.iterdir() if f.is_file()]
                    file_count = len(files)

                    partition_info["tickers"][ticker] = file_count
                    partition_info["total_files"] += file_count

                stage_info["date_partitions"][date_partition] = partition_info
                stage_info["total_files"] += partition_info["total_files"]

            summary["stages"][stage] = stage_info
            summary["total_files"] += stage_info["total_files"]

        # Convert sets to lists for JSON serialization
        summary["total_tickers"] = list(summary["total_tickers"])
        summary["date_partitions"] = list(summary["date_partitions"])

        for stage_info in summary["stages"].values():
            stage_info["tickers"] = list(stage_info["tickers"])

        return summary


def create_directory_manager(base_path: str = "data") -> DirectoryManager:
    """Factory function to create DirectoryManager instance."""
    return DirectoryManager(base_path)


if __name__ == "__main__":
    # Example usage and testing
    dm = DirectoryManager()

    # Print structure summary
    summary = dm.get_structure_summary()
    print("📁 Current Directory Structure Summary:")
    print(f"   Total Files: {summary['total_files']}")
    print(f"   Total Tickers: {len(summary['total_tickers'])}")
    print(f"   Date Partitions: {len(summary['date_partitions'])}")

    for stage, info in summary["stages"].items():
        if info["total_files"] > 0:
            print(f"\n📂 {stage}:")
            print(f"   Files: {info['total_files']}")
            print(f"   Tickers: {len(info['tickers'])}")
            print(f"   Partitions: {len(info['date_partitions'])}")
