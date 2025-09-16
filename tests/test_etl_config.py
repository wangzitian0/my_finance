#!/usr/bin/env python3
"""
Unit tests for ETL configuration system
Test various functions of centralized configuration loader

Issue #278: ETL Configuration Centralization Tests
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from common.etl_loader import (
        DataSourceConfig,
        ETLConfigLoader,
        RuntimeETLConfig,
        ScenarioConfig,
        StockListConfig,
        build_etl_config,
        etl_loader,
        list_available_configs,
        load_data_source,
        load_scenario,
        load_stock_list,
    )
except ImportError as e:
    print(f"❌ Unable to import ETL configuration module: {e}")

    # If import fails, create an empty test class to avoid test runner failure
    class TestETLConfigImportFailure(unittest.TestCase):
        def test_import_failure(self):
            self.fail(f"ETL configuration module import failed: {e}")

    if __name__ == "__main__":
        unittest.main()
    else:
        # This allows test discovery mechanism to work normally
        pass


class TestETLConfigLoader(unittest.TestCase):
    """Test ETLConfigLoader class"""

    def setUp(self):
        """Set up test environment"""
        self.loader = ETLConfigLoader()

    def test_file_mappings(self):
        """Test file mapping configuration"""
        mappings = self.loader._stock_list_mapping
        expected_mappings = {
            "f2": "stock_f2.yml",
            "m7": "stock_m7.yml",
            "n100": "stock_n100.yml",
            "v3k": "stock_v3k.yml",
        }
        self.assertEqual(mappings, expected_mappings)

    def test_list_available_configs(self):
        """Test listing available configurations"""
        configs = self.loader.list_available_configs()

        self.assertIn("stock_lists", configs)
        self.assertIn("data_sources", configs)
        self.assertIn("scenarios", configs)

        self.assertEqual(set(configs["stock_lists"]), {"f2", "m7", "n100", "v3k"})
        self.assertEqual(set(configs["data_sources"]), {"yfinance", "sec_edgar"})
        self.assertEqual(set(configs["scenarios"]), {"development", "production"})

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
description: "Test stock list"
tier: "f2"
max_size_mb: 20
companies:
  MSFT:
    name: "Microsoft Corporation"
    sector: "Technology"
  NVDA:
    name: "NVIDIA Corporation"
    sector: "Technology"
""",
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_stock_list(self, mock_exists, mock_file):
        """Test loading stock list configuration"""
        config = self.loader.load_stock_list("f2")

        self.assertIsInstance(config, StockListConfig)
        self.assertEqual(config.name, "f2")
        self.assertEqual(config.tier, "f2")
        self.assertEqual(len(config.tickers), 2)
        self.assertIn("MSFT", config.tickers)
        self.assertIn("NVDA", config.tickers)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
description: "Yahoo Finance API"
enabled: true
data_types:
  - "historical_prices"
  - "financial_statements"
api_config:
  base_url: "https://query1.finance.yahoo.com"
  timeout_seconds: 30
rate_limits:
  requests_per_second: 2
output_format:
  file_extension: ".json"
""",
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_data_source(self, mock_exists, mock_file):
        """Test loading data source configuration"""
        config = self.loader.load_data_source("yfinance")

        self.assertIsInstance(config, DataSourceConfig)
        self.assertEqual(config.name, "yfinance")
        self.assertTrue(config.enabled)
        self.assertIn("historical_prices", config.data_types)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
description: "Development environment"
data_sources:
  - "yfinance"
  - "sec_edgar"
processing_mode: "test"
quality_thresholds:
  min_success_rate: 0.8
resource_limits:
  max_concurrent_requests: 5
optimizations:
  cache_enabled: true
""",
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_scenario(self, mock_exists, mock_file):
        """Test loading scenario configuration"""
        config = self.loader.load_scenario("development")

        self.assertIsInstance(config, ScenarioConfig)
        self.assertEqual(config.name, "development")
        self.assertEqual(config.processing_mode, "test")
        self.assertIn("yfinance", config.data_sources)

    def test_invalid_config_names(self):
        """Test invalid configuration names"""
        with self.assertRaises(ValueError):
            self.loader.load_stock_list("invalid")

        with self.assertRaises(ValueError):
            self.loader.load_data_source("invalid")

        with self.assertRaises(ValueError):
            self.loader.load_scenario("invalid")

    def test_cache_functionality(self):
        """Test cache functionality"""
        # Clear cache
        self.loader.clear_cache()
        self.assertEqual(len(self.loader._cache), 0)

    def test_legacy_config_mapping(self):
        """Test legacy config file mapping"""
        mapping = self.loader.get_legacy_config_mapping()

        # Check mapping contains all expected files
        self.assertIn("common/config/stock_lists/f2.yml", mapping)
        self.assertIn("common/config/etl/stock_f2.yml", mapping.values())


class TestRuntimeConfigBuilding(unittest.TestCase):
    """Test runtime configuration building"""

    def setUp(self):
        """Set up test environment"""
        # Mock configuration data
        self.mock_stock_config = """
description: "2-company subset"
tier: "f2"
max_size_mb: 20
companies:
  MSFT:
    name: "Microsoft Corporation"
    sector: "Technology"
  NVDA:
    name: "NVIDIA Corporation"
    sector: "Technology"
"""

        self.mock_yf_config = """
description: "Yahoo Finance API"
enabled: true
data_types:
  - "historical_prices"
api_config:
  base_url: "https://query1.finance.yahoo.com"
rate_limits:
  requests_per_second: 2
output_format:
  file_extension: ".json"
"""

        self.mock_scenario_config = """
description: "Development environment"
data_sources:
  - "yfinance"
  - "sec_edgar"
processing_mode: "test"
quality_thresholds:
  min_success_rate: 0.8
resource_limits:
  max_concurrent_requests: 5
optimizations:
  cache_enabled: true
"""

    @patch("pathlib.Path.exists", return_value=True)
    def test_build_runtime_config(self, mock_exists):
        """Test building runtime configuration"""
        with patch("builtins.open", mock_open()) as mock_file:
            # Set different file contents
            mock_file.side_effect = [
                mock_open(read_data=self.mock_stock_config).return_value,
                mock_open(read_data=self.mock_yf_config).return_value,
                mock_open(read_data=self.mock_scenario_config).return_value,
            ]

            loader = ETLConfigLoader()
            config = loader.build_runtime_config("f2", ["yfinance"], "development")

            self.assertIsInstance(config, RuntimeETLConfig)
            self.assertEqual(config.combination, "f2_yfinance_development")
            self.assertEqual(config.ticker_count, 2)
            self.assertIn("yfinance", config.enabled_sources)

    @patch("pathlib.Path.exists", return_value=True)
    def test_invalid_data_source_in_scenario(self, mock_exists):
        """Test unavailable data source in scenario"""
        # Modify scenario config to only allow yfinance
        limited_scenario = """
description: "Limited environment"
data_sources:
  - "yfinance"
processing_mode: "test"
"""

        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = [
                mock_open(read_data=self.mock_stock_config).return_value,
                mock_open(read_data=self.mock_yf_config).return_value,
                mock_open(read_data=limited_scenario).return_value,
            ]

            loader = ETLConfigLoader()

            # Trying to use unavailable data source should throw error
            with self.assertRaises(ValueError):
                loader.build_runtime_config("f2", ["yfinance", "sec_edgar"], "development")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    @patch("common.etl_loader.etl_loader")
    def test_convenience_functions(self, mock_loader):
        """Test convenience function calls"""
        # Mock return value
        mock_config = StockListConfig("f2", "test", ["MSFT"], {}, "f2", 20)
        mock_loader.load_stock_list.return_value = mock_config

        # Test convenience function
        result = load_stock_list("f2")

        # Verify call
        mock_loader.load_stock_list.assert_called_once_with("f2")
        self.assertEqual(result, mock_config)


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation"""

    def setUp(self):
        """Set up test environment"""
        self.loader = ETLConfigLoader()

    @patch("pathlib.Path.exists", return_value=False)
    def test_missing_config_files(self, mock_exists):
        """Test missing configuration files scenario"""
        errors = self.loader.validate_config_files()

        # Should return error for each configuration type
        self.assertTrue(len(errors) > 0)

    @patch("pathlib.Path.exists", return_value=True)
    @patch("builtins.open", mock_open(read_data="invalid: yaml: content: ["))
    def test_invalid_yaml_format(self, mock_exists):
        """Test invalid YAML format"""
        with self.assertRaises(ValueError):
            self.loader._load_yaml(Path("test.yml"))


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_list_available_configs_function(self):
        """Test list_available_configs function"""
        configs = list_available_configs()

        self.assertIsInstance(configs, dict)
        self.assertIn("stock_lists", configs)
        self.assertIn("data_sources", configs)
        self.assertIn("scenarios", configs)

    @patch("pathlib.Path.exists", return_value=True)
    def test_full_workflow_mock(self, mock_exists):
        """Test complete configuration loading workflow (mocked)"""
        mock_configs = {
            "stock_f2.yml": """
description: "F2 stocks"
tier: "f2"
companies:
  MSFT:
    name: "Microsoft Corporation"
""",
            "source_yfinance.yml": """
description: "Yahoo Finance"
enabled: true
data_types: ["historical_prices"]
api_config: {}
rate_limits: {}
output_format: {}
""",
            "scenario_dev.yml": """
description: "Development"
data_sources: ["yfinance"]
processing_mode: "test"
quality_thresholds: {}
resource_limits: {}
optimizations: {}
""",
        }

        def mock_open_func(file_path, *args, **kwargs):
            filename = file_path.name
            if filename in mock_configs:
                return mock_open(read_data=mock_configs[filename]).return_value
            raise FileNotFoundError()

        with patch("builtins.open", side_effect=mock_open_func):
            config = build_etl_config("f2", ["yfinance"], "development")

            self.assertIsInstance(config, RuntimeETLConfig)
            self.assertEqual(config.combination, "f2_yfinance_development")


if __name__ == "__main__":
    unittest.main(verbosity=2)
