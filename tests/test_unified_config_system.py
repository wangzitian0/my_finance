#!/usr/bin/env python3
"""
Comprehensive test suite for unified configuration system.
Tests schema consistency, data integrity, and backward compatibility.
"""

import unittest
from pathlib import Path

from common.unified_config_loader import CompanyInfo, UnifiedConfigLoader
from ETL.tests.test_config import DatasetTier
from tests.config_schema_validator import ConfigSchemaValidator


class TestUnifiedConfigSystem(unittest.TestCase):
    """Test unified configuration system"""

    def setUp(self):
        """Set up test fixtures"""
        self.loader = UnifiedConfigLoader()
        self.validator = ConfigSchemaValidator()

    def test_schema_validation_all_configs(self):
        """Test that all configurations pass schema validation"""
        success = self.validator.validate_all_configs()
        self.assertTrue(success, f"Schema validation failed: {self.validator.errors}")

        # Print validation summary for debugging
        if self.validator.warnings:
            print("\nSchema validation warnings:")
            for warning in self.validator.warnings:
                print(f"  - {warning}")

    def test_unified_config_loading(self):
        """Test that all configurations can be loaded through unified loader"""
        tiers = [DatasetTier.F2, DatasetTier.M7, DatasetTier.N100, DatasetTier.V3K]

        for tier in tiers:
            with self.subTest(tier=tier):
                config = self.loader.load_config(tier)

                # Validate basic structure
                self.assertIsInstance(config.dataset_name, str)
                self.assertIsInstance(config.cli_alias, str)
                self.assertIsInstance(config.description, str)
                self.assertIsInstance(config.tier, int)
                self.assertIsInstance(config.tracked_in_git, bool)
                self.assertIsInstance(config.max_size_mb, int)
                self.assertIsInstance(config.ticker_count, int)
                self.assertIsInstance(config.last_updated, str)

                # Validate companies data
                self.assertIsInstance(config.companies, dict)
                self.assertGreater(len(config.companies), 0)

                # Check ticker count consistency
                self.assertEqual(config.ticker_count, len(config.companies))

                # Validate company info structure
                for ticker, company_info in config.companies.items():
                    self.assertIsInstance(company_info, CompanyInfo)
                    self.assertEqual(company_info.ticker, ticker)
                    self.assertIsInstance(company_info.name, str)
                    self.assertTrue(len(company_info.name) > 0)

    def test_tier_specific_validation(self):
        """Test tier-specific validation rules"""

        # Fast 2 - should reference M7 and have 2 companies
        f2_config = self.loader.load_config(DatasetTier.F2)
        self.assertEqual(len(f2_config.companies), 2)
        self.assertIsNotNone(f2_config.reference_config)
        self.assertIn("MSFT", f2_config.companies)
        self.assertIn("NVDA", f2_config.companies)

        # M7 - should have 7 technology companies
        m7_config = self.loader.load_config(DatasetTier.M7)
        self.assertEqual(len(m7_config.companies), 7)
        expected_m7_tickers = {"AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"}
        self.assertEqual(set(m7_config.companies.keys()), expected_m7_tickers)

        # N100 - should have 100+ companies
        n100_config = self.loader.load_config(DatasetTier.N100)
        self.assertGreaterEqual(len(n100_config.companies), 100)

        # VTI - should have 3000+ companies
        vti_config = self.loader.load_config(DatasetTier.V3K)
        self.assertGreaterEqual(len(vti_config.companies), 3000)

    def test_company_metadata_consistency(self):
        """Test that company metadata follows consistent patterns"""

        for tier in [DatasetTier.M7, DatasetTier.N100]:
            with self.subTest(tier=tier):
                config = self.loader.load_config(tier)

                for ticker, company_info in config.companies.items():
                    # CIK should be 10-digit string or None
                    if company_info.cik is not None:
                        self.assertIsInstance(company_info.cik, str)
                        self.assertEqual(len(company_info.cik), 10)
                        self.assertTrue(company_info.cik.isdigit())

                    # Market cap category should be valid if present
                    if company_info.market_cap_category:
                        valid_categories = {"mega", "large", "mid", "small"}
                        self.assertIn(company_info.market_cap_category, valid_categories)

                    # Sector can be empty string or None, but not invalid
                    if company_info.sector is not None:
                        self.assertIsInstance(company_info.sector, str)

    def test_sec_integration_readiness(self):
        """Test configurations are ready for SEC integration"""

        # M7 and N100 should have SEC enabled and CIK numbers
        for tier in [DatasetTier.M7, DatasetTier.N100]:
            with self.subTest(tier=tier):
                self.assertTrue(self.loader.is_sec_enabled(tier))

                cik_mapping = self.loader.get_cik_mapping(tier)
                self.assertGreater(len(cik_mapping), 0)

                # Validate CIK format
                for ticker, cik in cik_mapping.items():
                    self.assertEqual(len(cik), 10)
                    self.assertTrue(cik.isdigit())

    def test_backward_compatibility(self):
        """Test backward compatibility with legacy test config"""
        from ETL.tests.test_config import TestConfigManager

        legacy_manager = TestConfigManager()

        # Test that legacy manager still works
        for tier in [DatasetTier.F2, DatasetTier.M7, DatasetTier.N100, DatasetTier.V3K]:
            with self.subTest(tier=tier):
                legacy_config = legacy_manager.get_config(tier)
                unified_config = self.loader.load_config(tier)

                # Compare key properties - handle CLI alias mapping
                config_to_alias = {
                    "list_fast_2.yml": "fast",  # Fast 2 uses "fast" alias
                    "list_magnificent_7.yml": "m7",
                    "list_nasdaq_100.yml": "n100",
                    "list_vti_3500.yml": "v3k",
                }
                expected_alias = config_to_alias.get(legacy_config.config_file)
                if expected_alias:
                    self.assertEqual(expected_alias, unified_config.cli_alias)

                # Verify ticker lists match
                legacy_tickers = (
                    set(legacy_config.expected_tickers) if legacy_config.expected_tickers else set()
                )
                unified_tickers = set(unified_config.companies.keys())

                if legacy_tickers:  # Only compare if legacy has specific tickers
                    self.assertEqual(legacy_tickers, unified_tickers)

    def test_timeout_configuration(self):
        """Test timeout configurations are reasonable"""

        timeouts = {
            DatasetTier.F2: 120,  # 2 minutes
            DatasetTier.M7: 300,  # 5 minutes
            DatasetTier.N100: 1800,  # 30 minutes
            DatasetTier.V3K: 7200,  # 2 hours
        }

        for tier, expected_timeout in timeouts.items():
            with self.subTest(tier=tier):
                actual_timeout = self.loader.get_timeout_seconds(tier)
                self.assertEqual(actual_timeout, expected_timeout)

    def test_data_source_configuration(self):
        """Test data source configurations are valid"""

        for tier in [DatasetTier.F2, DatasetTier.M7, DatasetTier.N100, DatasetTier.V3K]:
            with self.subTest(tier=tier):
                config = self.loader.load_config(tier)

                # Should have data_sources section
                self.assertIsNotNone(config.data_sources)

                # Should have yfinance and sec_edgar
                self.assertIn("yfinance", config.data_sources)
                self.assertIn("sec_edgar", config.data_sources)

                # Each source should have enabled and stage_config
                for source_name, source_config in config.data_sources.items():
                    self.assertIn("enabled", source_config)
                    self.assertIn("stage_config", source_config)
                    self.assertIsInstance(source_config["enabled"], bool)
                    self.assertTrue(source_config["stage_config"].endswith(".yml"))

    def test_expected_file_counts(self):
        """Test expected file count configurations"""

        for tier in [DatasetTier.F2, DatasetTier.M7, DatasetTier.N100, DatasetTier.V3K]:
            with self.subTest(tier=tier):
                expected_files = self.loader.get_expected_file_counts(tier)

                # Should have counts for both data sources
                self.assertIn("yfinance", expected_files)
                self.assertIn("sec_edgar", expected_files)

                # Counts should be non-negative integers
                self.assertIsInstance(expected_files["yfinance"], int)
                self.assertIsInstance(expected_files["sec_edgar"], int)
                self.assertGreaterEqual(expected_files["yfinance"], 0)
                self.assertGreaterEqual(expected_files["sec_edgar"], 0)

                # Fast 2 should have no SEC files (disabled)
                if tier == DatasetTier.F2:
                    self.assertEqual(expected_files["sec_edgar"], 0)

    def test_configuration_file_existence(self):
        """Test all required configuration files exist"""

        required_files = [
            "list_fast_2.yml",
            "list_magnificent_7.yml",
            "list_nasdaq_100.yml",
            "list_vti_3500.yml",
        ]

        for config_file in required_files:
            with self.subTest(config_file=config_file):
                config_path = self.loader.config_dir / config_file
                self.assertTrue(config_path.exists(), f"Missing config file: {config_file}")

    def test_vti_weight_data(self):
        """Test VTI-specific weight data"""

        vti_config = self.loader.load_config(DatasetTier.V3K)

        # Find companies with weight data
        weighted_companies = [
            company for company in vti_config.companies.values() if company.weight is not None
        ]

        # Should have many companies with weights
        self.assertGreater(len(weighted_companies), 100)

        # Weight format should be valid
        for company in weighted_companies[:10]:  # Check first 10
            if company.weight:
                self.assertTrue(company.weight.endswith("%"))
                weight_val = float(company.weight.rstrip("%"))
                self.assertGreater(weight_val, 0.0)
                self.assertLessEqual(weight_val, 100.0)


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
