#!/usr/bin/env python3
"""
Simplified unit tests for subtree migration components
Focuses on core DirectoryManager functionality and path management
"""

import os

# Add project root to path for imports
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestDirectoryManagerBasic(unittest.TestCase):
    """Test basic DirectoryManager SSOT functionality"""

    def test_directory_manager_initialization(self):
        """Test DirectoryManager initializes correctly"""
        from common.core.directory_manager import DirectoryManager, StorageBackend

        dm = DirectoryManager()
        self.assertEqual(dm.backend, StorageBackend.LOCAL_FS)
        self.assertIn("my_finance", str(dm.root_path))

    def test_data_root_path(self):
        """Test get_data_root returns correct path"""
        from common.core.directory_manager import DirectoryManager

        dm = DirectoryManager()
        data_root = dm.get_data_root()
        self.assertEqual(data_root.name, "build_data")
        self.assertIn("my_finance", str(data_root.parent))

    def test_layer_paths(self):
        """Test layer path generation"""
        from common.core.directory_manager import DataLayer, DirectoryManager

        dm = DirectoryManager()

        # Test basic layer path
        raw_path = dm.get_layer_path(DataLayer.RAW_DATA)
        self.assertIn("layer_01_raw", str(raw_path))

        # Test layer path with partition
        partitioned_path = dm.get_layer_path(DataLayer.DAILY_DELTA, "20250825")
        self.assertIn("layer_02_delta", str(partitioned_path))
        self.assertIn("20250825", str(partitioned_path))

    def test_config_path(self):
        """Test configuration path"""
        from common.core.directory_manager import DirectoryManager

        dm = DirectoryManager()
        config_path = dm.get_config_path()
        self.assertIn("common/config", str(config_path))

    def test_legacy_mapping(self):
        """Test legacy path mapping"""
        from common.core.directory_manager import DataLayer, DirectoryManager

        dm = DirectoryManager()

        # Test legacy stage mapping
        mapped_layer = dm.map_legacy_path("stage_01_extract")
        self.assertEqual(mapped_layer, DataLayer.DAILY_DELTA)

        mapped_layer = dm.map_legacy_path("stage_00_original")
        self.assertEqual(mapped_layer, DataLayer.RAW_DATA)

        # Test invalid legacy path
        mapped_layer = dm.map_legacy_path("invalid_stage")
        self.assertIsNone(mapped_layer)


class TestDataLayerArchitecture(unittest.TestCase):
    """Test Five-Layer Data Architecture implementation"""

    def test_data_layer_enum_completeness(self):
        """Test DataLayer enum has all required layers"""
        from common.core.directory_manager import DataLayer

        layers = [layer.value for layer in DataLayer]

        expected_layers = [
            "layer_01_raw",
            "layer_02_delta",
            "layer_03_index",
            "layer_04_rag",
            "layer_05_results",
        ]

        for expected in expected_layers:
            self.assertIn(expected, layers)

    def test_legacy_mapping_completeness(self):
        """Test legacy mapping covers all old stage names"""
        from common.core.directory_manager import DataLayer, DirectoryManager

        dm = DirectoryManager()

        legacy_stages = [
            "stage_00_original",
            "stage_01_extract",
            "stage_02_transform",
            "stage_03_load",
            "stage_99_build",
        ]

        for stage in legacy_stages:
            mapped = dm.map_legacy_path(stage)
            self.assertIsNotNone(mapped)
            self.assertIsInstance(mapped, DataLayer)


class TestConfigurationSchema(unittest.TestCase):
    """Test configuration schema consistency"""

    def test_f2_config_exists(self):
        """Test F2 configuration file exists"""
        from common.core.directory_manager import DirectoryManager

        dm = DirectoryManager()
        config_path = dm.get_config_path()
        f2_config = config_path / "list_fast_2.yml"
        self.assertTrue(f2_config.exists(), f"F2 config should exist at {f2_config}")

    def test_m7_config_exists(self):
        """Test M7 configuration file exists"""
        from common.core.directory_manager import DirectoryManager

        dm = DirectoryManager()
        config_path = dm.get_config_path()
        m7_config = config_path / "list_magnificent_7.yml"
        self.assertTrue(m7_config.exists(), f"M7 config should exist at {m7_config}")

    def test_directory_structure_config_exists(self):
        """Test directory structure config exists"""
        from common.core.directory_manager import DirectoryManager

        dm = DirectoryManager()
        config_path = dm.get_config_path()
        dir_config = config_path / "directory_structure.yml"
        self.assertTrue(
            dir_config.exists(), f"Directory structure config should exist at {dir_config}"
        )


class TestPathMigrationNoHardcoding(unittest.TestCase):
    """Test that hardcoded paths have been eliminated"""

    def test_build_tracker_import(self):
        """Test BuildTracker can be imported and uses DirectoryManager"""
        try:
            from common.build_tracker import BuildTracker

            # If import succeeds, check if it has DirectoryManager usage
            tracker = BuildTracker()
            self.assertTrue(hasattr(tracker, "directory_manager") or hasattr(tracker, "base_path"))
        except ImportError as e:
            self.fail(f"BuildTracker import failed: {e}")

    def test_yfinance_spider_has_directory_manager(self):
        """Test yfinance_spider uses DirectoryManager"""
        # Test this without importing yfinance to avoid numpy issues
        import subprocess
        import sys

        # Check if yfinance_spider.py contains DirectoryManager reference
        yfinance_file = project_root + "/ETL/yfinance_spider.py"
        with open(yfinance_file, "r") as f:
            content = f.read()
            self.assertIn("DirectoryManager", content)
            self.assertIn("directory_manager", content)


class TestSubtreeMigrationSuccess(unittest.TestCase):
    """Test that subtree migration was successful"""

    def test_build_data_directory_exists(self):
        """Test build_data directory exists (subtree)"""
        build_data_path = Path(project_root) / "build_data"
        self.assertTrue(
            build_data_path.exists(), "build_data directory should exist after subtree migration"
        )

    def test_no_data_submodule(self):
        """Test old data submodule no longer exists (quality_reports dir is OK)"""
        # Check that data directory doesn't contain submodule artifacts
        data_path = Path(project_root) / "data"
        if data_path.exists():
            # If data directory exists, it should only contain quality_reports
            contents = list(data_path.iterdir())
            for item in contents:
                self.assertIn(
                    "quality",
                    item.name.lower(),
                    f"data/ should only contain quality reports, found: {item.name}",
                )
        # The key test: build_data should be the main data storage now
        build_data_path = Path(project_root) / "build_data"
        self.assertTrue(
            build_data_path.exists(), "build_data (subtree) should be the main data storage"
        )

    def test_config_moved_to_common(self):
        """Test configuration moved from data/config to common/config"""
        old_config_path = Path(project_root) / "data" / "config"
        new_config_path = Path(project_root) / "common" / "config"

        # Old path should not exist
        self.assertFalse(old_config_path.exists(), "Old data/config should be removed")

        # New path should exist
        self.assertTrue(new_config_path.exists(), "New common/config should exist")


if __name__ == "__main__":
    unittest.main(verbosity=2)
