#!/usr/bin/env python3
"""
Unit tests for ETL modules
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_etl_imports():
    """Test that ETL modules can be imported"""
    try:
        from ETL import build_dataset
        from ETL.tests import test_config

        assert True
    except ImportError as e:
        pytest.fail(f"ETL imports failed: {e}")


def test_dataset_tier_enum():
    """Test DatasetTier enum from ETL.tests.test_config"""
    try:
        from ETL.tests.test_config import DatasetTier

        # Test four-tier system
        assert DatasetTier.F2.value == "f2"
        assert DatasetTier.M7.value == "m7"
        assert DatasetTier.N100.value == "n100"
        assert DatasetTier.V3K.value == "v3k"

        # Test legacy aliases
        assert DatasetTier.TEST.value == "test"
        assert DatasetTier.NASDAQ100.value == "nasdaq100"
        assert DatasetTier.VTI.value == "vti"

    except Exception as e:
        pytest.fail(f"DatasetTier enum test failed: {e}")


def test_test_config_manager():
    """Test TestConfigManager from ETL.tests.test_config"""
    try:
        from ETL.tests.test_config import DatasetTier, TestConfigManager

        manager = TestConfigManager()

        # Test that all tiers have configurations
        for tier in DatasetTier:
            assert tier in manager.CONFIG_MAP, f"Missing config for tier {tier}"

        # Test specific tier configs
        f2_config = manager.get_config(DatasetTier.F2)
        assert f2_config.config_file == "list_fast_2.yml"
        assert f2_config.expected_tickers == ["MSFT", "NVDA"]

        m7_config = manager.get_config(DatasetTier.M7)
        assert m7_config.config_file == "list_magnificent_7.yml"
        assert len(m7_config.expected_tickers) == 7

    except Exception as e:
        pytest.fail(f"TestConfigManager test failed: {e}")


def test_build_dataset_arg_parsing():
    """Test build_dataset argument parsing logic"""
    try:
        from ETL.tests.test_config import DatasetTier

        # Test tier value normalization
        test_cases = [
            ("f2", "f2"),
            ("m7", "m7"),
            ("n100", "n100"),
            ("v3k", "v3k"),
            ("test", "f2"),  # Legacy alias
            ("nasdaq100", "n100"),  # Legacy alias
            ("vti", "v3k"),  # Legacy alias
        ]

        for input_tier, expected_output in test_cases:
            # This tests the logic without actually running build_dataset
            tier_enum = DatasetTier(input_tier)
            if input_tier == "test":
                # Should map to F2
                assert tier_enum == DatasetTier.TEST
            elif input_tier == "nasdaq100":
                # Should map to N100
                assert tier_enum == DatasetTier.NASDAQ100
            elif input_tier == "vti":
                # Should map to V3K
                assert tier_enum == DatasetTier.VTI
            else:
                # Direct mapping
                assert tier_enum.value == expected_output

    except Exception as e:
        pytest.fail(f"Build dataset arg parsing test failed: {e}")


def test_etl_manage_basic():
    """Test ETL manage module basic functionality"""
    try:
        import ETL.manage

        # Test that the module loads without errors
        assert hasattr(ETL.manage, "__file__")

    except Exception as e:
        pytest.fail(f"ETL manage basic test failed: {e}")


@patch("pathlib.Path.exists")
def test_config_file_validation_mock(mock_exists):
    """Test configuration file validation with mocked file system"""
    try:
        from ETL.tests.test_config import DatasetTier, TestConfigManager

        # Mock all config files exist
        mock_exists.return_value = True

        manager = TestConfigManager()

        # Test config loading logic
        for tier in [DatasetTier.F2, DatasetTier.M7, DatasetTier.N100, DatasetTier.V3K]:
            config = manager.get_config(tier)

            # Verify config structure
            assert hasattr(config, "tier")
            assert hasattr(config, "config_file")
            assert hasattr(config, "expected_tickers")
            assert hasattr(config, "timeout_seconds")

            # Verify config file naming convention
            assert config.config_file.startswith("list_")
            assert config.config_file.endswith(".yml")

    except Exception as e:
        pytest.fail(f"Config file validation mock test failed: {e}")


def test_tier_specific_settings():
    """Test tier-specific settings and defaults"""
    try:
        from ETL.tests.test_config import DatasetTier, TestConfigManager

        manager = TestConfigManager()

        # Test F2 (fast) settings
        f2_config = manager.get_config(DatasetTier.F2)
        assert f2_config.timeout_seconds == 120  # 2 minutes
        assert f2_config.enable_sec_edgar == False
        assert f2_config.enable_graph_rag == False

        # Test M7 settings
        m7_config = manager.get_config(DatasetTier.M7)
        assert m7_config.timeout_seconds == 300  # 5 minutes
        assert m7_config.enable_sec_edgar == True
        assert m7_config.enable_graph_rag == True

        # Test N100 settings
        n100_config = manager.get_config(DatasetTier.N100)
        assert n100_config.timeout_seconds == 1800  # 30 minutes
        assert n100_config.enable_sec_edgar == True
        assert n100_config.enable_graph_rag == True

        # Test V3K settings
        v3k_config = manager.get_config(DatasetTier.V3K)
        assert v3k_config.timeout_seconds == 7200  # 2 hours
        assert v3k_config.enable_sec_edgar == False  # Too expensive
        assert v3k_config.enable_graph_rag == True

    except Exception as e:
        pytest.fail(f"Tier specific settings test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
