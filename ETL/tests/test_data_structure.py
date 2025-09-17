#!/usr/bin/env python3
"""
Unit tests for the new ETL data structure.
Tests directory structure, file naming conventions, and data flow.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from common.build.build_tracker import BuildTracker
from ETL.tests.test_config import DatasetTier, TestConfigManager


class TestDataStructure:
    """Test suite for ETL data structure"""

    def test_stage_directories_exist(self):
        """Test that all ETL stage directories exist"""
        base_path = Path("/Users/SP14016/zitian/my_finance/data")

        expected_dirs = [
            base_path / "stage_01_extract",
            base_path / "stage_02_transform",
            base_path / "stage_03_load",
            base_path / "build",
            base_path / "config",
        ]

        for dir_path in expected_dirs:
            assert dir_path.exists(), f"Directory {dir_path} should exist"

    def test_extract_stage_structure(self):
        """Test stage_01_extract directory structure"""
        extract_path = Path("/Users/SP14016/zitian/my_finance/data/stage_01_extract")

        # Should have yfinance and sec_edgar subdirectories
        expected_sources = ["yfinance", "sec_edgar"]

        for source in expected_sources:
            source_path = extract_path / source
            assert source_path.exists(), f"Source directory {source} should exist"

            # Should have latest symlink if data exists
            latest_link = source_path / "latest"
            if latest_link.exists():
                assert latest_link.is_symlink(), "Latest should be a symlink"
                assert (
                    latest_link.readlink().name.isdigit()
                ), "Latest should point to date partition"

    def test_config_manager_initialization(self):
        """Test that test config manager initializes correctly"""
        manager = TestConfigManager()

        # Test all tiers have configs
        for tier in DatasetTier:
            config = manager.get_config(tier)
            assert config.tier == tier
            assert config.config_file is not None
            assert config.timeout_seconds > 0

    def test_config_files_exist(self):
        """Test that all configuration files exist"""
        manager = TestConfigManager()
        results = manager.validate_config_files()

        # At least f2 and m7 configs should exist
        assert (
            results[DatasetTier.F2] or results[DatasetTier.M7]
        ), "At least one config file should exist for testing"

    def test_data_paths_accessible(self):
        """Test that data paths are accessible for each tier"""
        manager = TestConfigManager()

        for tier in [DatasetTier.F2, DatasetTier.M7]:  # Test main tiers
            paths = manager.get_data_paths(tier)

            # Extract and build paths should exist
            assert paths["extract"].exists(), f"Extract path should exist for {tier.value}"
            assert paths["build"].exists(), f"Build path should exist for {tier.value}"

    def test_build_tracker_initialization(self):
        """Test build tracker can be initialized"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = BuildTracker(base_path=temp_dir)

            # Should create build directory and manifest
            build_path = Path(temp_dir) / "build" / f"build_{tracker.build_id}"
            assert build_path.exists()

            # Should have stage logs and artifacts subdirectories
            assert (build_path / "stage_logs").exists()
            assert (build_path / "artifacts").exists()

    def test_filename_convention_yfinance(self):
        """Test yfinance filename convention"""
        # Pattern: TICKER_yfinance_OID_TIMESTAMP.json
        test_filename = "AAPL_yfinance_1y_1d_250810-120000.json"

        import re

        pattern = r"^[A-Z]+_yfinance_[a-zA-Z0-9_]+_\d{6}-\d{6}\.json$"
        assert re.match(pattern, test_filename), f"Filename {test_filename} should match pattern"

    def test_filename_convention_sec_edgar(self):
        """Test SEC Edgar filename convention"""
        # Pattern: TICKER_sec_edgar_FILING_TYPE_TIMESTAMP_ORIGINAL.txt
        test_filename = "AAPL_sec_edgar_10k_250810-120000_0000320193-24-000123.txt"

        import re

        pattern = r"^[A-Z]+_sec_edgar_[a-z0-9]+_\d{6}-\d{6}_.*\.txt$"
        assert re.match(pattern, test_filename), f"Filename {test_filename} should match pattern"

    def test_date_partition_format(self):
        """Test date partition format is YYYYMMDD"""
        today = datetime.now()
        expected_format = today.strftime("%Y%m%d")

        assert len(expected_format) == 8, "Date partition should be 8 digits"
        assert expected_format.isdigit(), "Date partition should be all digits"
        assert int(expected_format[:4]) >= 2025, "Year should be reasonable"


class TestDataMigration:
    """Test suite for data migration functionality"""

    def test_migration_script_exists(self):
        """Test that migration script exists and is executable"""
        script_path = Path("/Users/SP14016/zitian/my_finance/scripts/migrate_data_structure.py")
        assert script_path.exists(), "Migration script should exist"

        # Check if script has proper shebang
        with open(script_path, "r") as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!"), "Migration script should have shebang"

    def test_backup_created_during_migration(self):
        """Test that backup is created during migration"""
        backup_path = Path("/Users/SP14016/zitian/my_finance/data/backup")

        if backup_path.exists():
            # Check for backup directories
            backup_dirs = [
                d for d in backup_path.iterdir() if d.is_dir() and d.name.startswith("backup_")
            ]
            assert len(backup_dirs) > 0, "At least one backup should exist"


class TestConfigValidation:
    """Test configuration validation"""

    def test_validate_test_environment(self):
        """Test environment validation function"""
        from tests.test_config import validate_test_environment

        result = validate_test_environment()

        assert isinstance(result, dict), "Should return dict"
        assert "config_files" in result, "Should check config files"
        assert "data_structure" in result, "Should check data structure"
        assert result["base_path_exists"], "Base path should exist"

    def test_get_expected_file_counts(self):
        """Test expected file count calculation"""
        manager = TestConfigManager()

        test_counts = manager.get_expected_file_count(DatasetTier.TEST)
        assert test_counts["total_tickers"] == 1, "Test tier should have 1 ticker"

        m7_counts = manager.get_expected_file_count(DatasetTier.M7)
        assert m7_counts["total_tickers"] == 7, "M7 tier should have 7 tickers"
