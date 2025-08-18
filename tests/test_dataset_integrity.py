#!/usr/bin/env python3
"""
Unit tests for dataset integrity verification (Issue #91)
Tests the 100-ticker dataset preparation and validation
"""

import json
import sys
import unittest
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml

    from common.build_tracker import BuildTracker
    from ETL.tests.test_config import DatasetTier, TestConfigManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Some dependencies may be missing, running with limited functionality")


class TestDatasetIntegrity(unittest.TestCase):
    """Test dataset integrity and completeness."""

    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = TestConfigManager()
        self.data_dir = Path("data")

    def test_n100_configuration_integrity(self):
        """Test N100 configuration has correct structure."""
        tier = DatasetTier("n100")
        config = self.config_manager.get_config(tier)
        yaml_config = self.config_manager.load_yaml_config(tier)

        # Basic structure validation
        self.assertEqual(yaml_config["dataset_name"], "nasdaq100")
        self.assertEqual(yaml_config["cli_alias"], "n100")
        self.assertEqual(yaml_config["tier"], 3)
        self.assertEqual(yaml_config["ticker_count"], 100)

        # Company data validation
        companies = yaml_config["companies"]
        self.assertEqual(len(companies), 100)

        # Check a few key companies are present
        key_companies = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
        for ticker in key_companies:
            self.assertIn(ticker, companies)
            self.assertIn("name", companies[ticker])
            self.assertIn("market_cap", companies[ticker])

    def test_data_sources_configuration(self):
        """Test data sources are properly configured."""
        tier = DatasetTier("n100")
        yaml_config = self.config_manager.load_yaml_config(tier)

        data_sources = yaml_config["data_sources"]

        # YFinance should be enabled
        self.assertTrue(data_sources["yfinance"]["enabled"])
        self.assertEqual(data_sources["yfinance"]["stage_config"], "stage_00_original_yfinance.yml")

        # SEC Edgar should be enabled (Issue #91 requirement)
        self.assertTrue(data_sources["sec_edgar"]["enabled"])
        self.assertEqual(
            data_sources["sec_edgar"]["stage_config"], "stage_00_original_sec_edgar.yml"
        )

        # Expected files counts
        expected_files = yaml_config["expected_files"]
        self.assertEqual(expected_files["yfinance"], 300)
        self.assertEqual(expected_files["sec_edgar"], 300)

    def test_build_system_functionality(self):
        """Test the build system can handle N100 dataset."""
        # Check if we have a recent build
        latest_build = BuildTracker.get_latest_build()

        if latest_build:
            status = latest_build.get_build_status()

            # Basic build validation
            self.assertIn("build_id", status)
            self.assertIn("status", status)
            self.assertIn("configuration", status)

            # Enhanced status validation (Issue #91)
            self.assertIn("dataset_summary", status)
            self.assertIn("build_info", status)
            self.assertIn("directory_structure", status)

            dataset_summary = status["dataset_summary"]
            self.assertIn("yfinance_files", dataset_summary)
            self.assertIn("sec_edgar_files", dataset_summary)
            self.assertIn("dcf_reports", dataset_summary)
            self.assertIn("total_files", dataset_summary)
            self.assertIn("companies_processed", dataset_summary)

    def test_directory_structure_exists(self):
        """Test expected directory structure exists."""
        expected_dirs = ["data/config", "data/stage_99_build", "common"]

        for dir_path in expected_dirs:
            self.assertTrue(Path(dir_path).exists(), f"Directory {dir_path} should exist")

    def test_configuration_files_exist(self):
        """Test all tier configuration files exist."""
        expected_configs = [
            "data/config/list_fast_2.yml",
            "data/config/list_magnificent_7.yml",
            "data/config/list_nasdaq_100.yml",
            "data/config/list_vti_3500.yml",
        ]

        for config_path in expected_configs:
            self.assertTrue(Path(config_path).exists(), f"Config file {config_path} should exist")

    def test_build_manifest_structure(self):
        """Test build manifest has expected structure."""
        latest_build = BuildTracker.get_latest_build()

        if latest_build:
            manifest_path = latest_build.build_path / "BUILD_MANIFEST.json"
            self.assertTrue(manifest_path.exists())

            with open(manifest_path) as f:
                manifest = json.load(f)

            # Required manifest sections
            required_sections = [
                "build_info",
                "stages",
                "data_partitions",
                "real_outputs",
                "statistics",
            ]

            for section in required_sections:
                self.assertIn(section, manifest)

            # Check stages structure
            stages = manifest["stages"]
            expected_stages = [
                "stage_01_extract",
                "stage_02_transform",
                "stage_03_load",
                "stage_04_analysis",
                "stage_05_reporting",
            ]

            for stage in expected_stages:
                self.assertIn(stage, stages)
                self.assertIn("status", stages[stage])

    def test_tier_system_completeness(self):
        """Test all tiers are properly configured."""
        tier_names = ["f2", "m7", "n100", "v3k"]

        for tier_name in tier_names:
            try:
                tier = DatasetTier(tier_name)
                config = self.config_manager.get_config(tier)
                yaml_config = self.config_manager.load_yaml_config(tier)

                # Basic validation
                self.assertIsNotNone(config)
                self.assertIsNotNone(yaml_config)
                self.assertIn("dataset_name", yaml_config)
                self.assertIn("companies", yaml_config)

            except Exception as e:
                self.fail(f"Tier {tier_name} configuration failed: {e}")


class TestN100SpecificRequirements(unittest.TestCase):
    """Test specific requirements for Issue #91."""

    def test_100_ticker_count(self):
        """Test N100 has exactly 100 tickers."""
        tier = DatasetTier("n100")
        yaml_config = TestConfigManager().load_yaml_config(tier)

        companies = yaml_config["companies"]
        self.assertEqual(len(companies), 100, "N100 should have exactly 100 companies")

    def test_sec_and_yahoo_integration(self):
        """Test both SEC and Yahoo Finance are enabled for N100."""
        tier = DatasetTier("n100")
        yaml_config = TestConfigManager().load_yaml_config(tier)

        data_sources = yaml_config["data_sources"]

        # Both sources should be enabled
        self.assertTrue(data_sources["yfinance"]["enabled"])
        self.assertTrue(data_sources["sec_edgar"]["enabled"])

    def test_comprehensive_reporting_available(self):
        """Test comprehensive reporting functionality is available."""
        # Test that BuildTracker can provide comprehensive status
        latest_build = BuildTracker.get_latest_build()

        if latest_build:
            status = latest_build.get_build_status()

            # Should have enhanced status info per Issue #91
            required_fields = ["dataset_summary", "build_info", "directory_structure"]

            for field in required_fields:
                self.assertIn(field, status, f"Status should include {field}")

    def test_pixi_commands_available(self):
        """Test that required pixi commands are configured."""
        import subprocess

        # Test that N100 build command exists
        result = subprocess.run(["pixi", "task", "list"], capture_output=True, text=True)

        task_output = result.stdout
        self.assertIn("build-n100", task_output)
        self.assertIn("data-status", task_output)


if __name__ == "__main__":
    unittest.main()
