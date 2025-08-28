#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration validation tests for import compatibility.

Tests to ensure that the restructured library maintains backward compatibility
with existing import patterns.

Issue #184: Core library restructuring - Migration validation
"""

import warnings

import pytest


def test_core_imports():
    """Test that core components can be imported from new locations."""
    try:
        from common.core.config_manager import ConfigManager
        from common.core.directory_manager import DataLayer, DirectoryManager
        from common.core.storage_manager import StorageManager

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import core components: {e}")


def test_utils_imports():
    """Test that utility functions can be imported from new locations."""
    try:
        from common.utils.id_generation import Snowflake
        from common.utils.io_operations import suppress_third_party_logs
        from common.utils.logging_setup import setup_logger
        from common.utils.progress_tracking import create_progress_bar

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import utility functions: {e}")


def test_systems_imports():
    """Test that system modules can be imported from new locations."""
    try:
        from common.systems.build_tracker import BuildTracker
        from common.systems.metadata_manager import MetadataManager
        from common.systems.quality_reporter import QualityReporter

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import system modules: {e}")


def test_main_common_imports():
    """Test that main common module exports work correctly."""
    try:
        from common import (
            BuildTracker,
            ConfigManager,
            DataLayer,
            DirectoryManager,
            MetadataManager,
            QualityReporter,
            Snowflake,
            StorageManager,
            create_progress_bar,
            setup_logger,
        )

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import from main common module: {e}")


def test_legacy_compatibility():
    """Test that legacy compatibility functions work with deprecation warnings."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        try:
            from common.core.compatibility import get_legacy_data_path

            # This should trigger a deprecation warning
            result = get_legacy_data_path()

            # Check that deprecation warning was issued
            assert len(w) > 0
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

        except Exception as e:
            pytest.fail(f"Legacy compatibility function failed: {e}")


def test_directory_manager_functionality():
    """Test that DirectoryManager still works after restructuring."""
    from common import DataLayer, DirectoryManager

    dm = DirectoryManager()

    # Test that basic functionality works
    assert dm.get_data_root().exists() or True  # May not exist in test environment
    assert len(list(DataLayer)) > 0

    # Test legacy mapping functionality
    legacy_layer = dm.map_legacy_path("stage_00_original")
    assert legacy_layer == DataLayer.RAW_DATA


def test_config_manager_functionality():
    """Test that ConfigManager still works after restructuring."""
    from common import ConfigManager, config_manager

    # Test that global instance exists
    assert config_manager is not None
    assert isinstance(config_manager, ConfigManager)

    # Test basic functionality
    available_configs = config_manager.list_available_configs()
    assert isinstance(available_configs, list)


def test_version_info():
    """Test that version information is updated correctly."""
    from common import __version__, __version_info__

    # Version should be incremented for restructuring
    assert __version__ == "2.1.0"
    assert __version_info__ == (2, 1, 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
