#!/usr/bin/env python3
"""
Test suite for the unified directory manager system.
Tests the SSOT directory management, five-layer architecture, and storage backend abstraction.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from common.directory_manager import (
    DataLayer,
    DirectoryManager,
    StorageBackend,
    get_build_path,
    get_config_path,
    get_data_path,
    get_source_path,
)


class TestDataLayer:
    """Test DataLayer enum"""

    def test_data_layer_values(self):
        """Test that DataLayer enum has correct values"""
        assert DataLayer.RAW_DATA.value == "stage_00_raw"
        assert DataLayer.DAILY_DELTA.value == "stage_01_daily_delta"
        assert DataLayer.DAILY_INDEX.value == "stage_02_daily_index"
        assert DataLayer.GRAPH_RAG.value == "stage_03_graph_rag"
        assert DataLayer.QUERY_RESULTS.value == "stage_04_query_results"


class TestDirectoryManager:
    """Test DirectoryManager class"""

    @pytest.fixture
    def temp_project_root(self):
        """Create temporary project root for testing"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        # Create basic structure
        (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
        (project_root / "build_data").mkdir(parents=True, exist_ok=True)

        yield project_root

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def directory_manager(self, temp_project_root):
        """Create DirectoryManager instance for testing"""
        return DirectoryManager(root_path=temp_project_root)

    def test_initialization(self, directory_manager, temp_project_root):
        """Test DirectoryManager initialization"""
        assert directory_manager.root_path == temp_project_root
        assert directory_manager.backend == StorageBackend.LOCAL_FS
        assert directory_manager.config is not None

    def test_get_data_root(self, directory_manager):
        """Test get_data_root method"""
        data_root = directory_manager.get_data_root()
        assert data_root.name == "build_data"
        assert data_root.is_absolute()

    def test_get_layer_path(self, directory_manager):
        """Test get_layer_path method"""
        raw_path = directory_manager.get_layer_path(DataLayer.RAW_DATA)
        assert raw_path.name == "stage_00_raw"

        # Test with partition
        partitioned_path = directory_manager.get_layer_path(DataLayer.RAW_DATA, "20250821")
        assert partitioned_path.parts[-1] == "20250821"
        assert partitioned_path.parts[-2] == "stage_00_raw"

    def test_get_subdir_path(self, directory_manager):
        """Test get_subdir_path method"""
        sec_path = directory_manager.get_subdir_path(DataLayer.RAW_DATA, "sec-edgar")
        assert sec_path.parts[-1] == "sec-edgar"
        assert sec_path.parts[-2] == "stage_00_raw"

        # Test with partition
        partitioned_sec_path = directory_manager.get_subdir_path(
            DataLayer.RAW_DATA, "sec-edgar", "20250821"
        )
        assert partitioned_sec_path.parts[-1] == "sec-edgar"
        assert partitioned_sec_path.parts[-2] == "20250821"
        assert partitioned_sec_path.parts[-3] == "stage_00_raw"

    def test_get_config_path(self, directory_manager):
        """Test get_config_path method"""
        config_path = directory_manager.get_config_path()
        assert config_path.parts[-2:] == ("common", "config")

    def test_get_llm_config_path(self, directory_manager):
        """Test get_llm_config_path method"""
        llm_config_dir = directory_manager.get_llm_config_path()
        assert llm_config_dir.parts[-3:] == ("config", "llm", "configs")
        assert llm_config_dir.parts[-1] == "configs"

        # Test with specific config name
        specific_config = directory_manager.get_llm_config_path("deepseek_fast.yml")
        assert specific_config.name == "deepseek_fast.yml"
        assert specific_config.parent.name == "configs"

    def test_get_build_path(self, directory_manager):
        """Test get_build_path method"""
        # Test default build path
        build_path = directory_manager.get_build_path()
        assert "stage_04_query_results" in str(build_path)

        # Test with timestamp
        timestamped_path = directory_manager.get_build_path("20250821_120000")
        assert timestamped_path.name == "build_20250821_120000"

        # Test with branch
        branch_path = directory_manager.get_build_path(branch="feature-test")
        assert "stage_04_query_results_feature-test" in str(branch_path)

    def test_get_source_path(self, directory_manager):
        """Test get_source_path method"""
        # Test basic source path
        sec_path = directory_manager.get_source_path("sec-edgar")
        assert sec_path.parts[-1] == "sec-edgar"
        assert sec_path.parts[-2] == "stage_00_raw"

        # Test with different layer
        processed_path = directory_manager.get_source_path("sec-edgar", DataLayer.DAILY_INDEX)
        assert processed_path.parts[-1] == "sec-edgar"
        assert processed_path.parts[-2] == "stage_02_daily_index"

        # Test with date partition
        dated_path = directory_manager.get_source_path("sec-edgar", date_partition="20250821")
        assert dated_path.parts[-1] == "20250821"
        assert dated_path.parts[-2] == "sec-edgar"

        # Test with ticker
        ticker_path = directory_manager.get_source_path("sec-edgar", ticker="AAPL")
        assert ticker_path.parts[-1] == "AAPL"
        assert ticker_path.parts[-2] == "sec-edgar"

        # Test with both date and ticker
        full_path = directory_manager.get_source_path(
            "sec-edgar", date_partition="20250821", ticker="AAPL"
        )
        assert full_path.parts[-1] == "AAPL"
        assert full_path.parts[-2] == "20250821"
        assert full_path.parts[-3] == "sec-edgar"

    def test_map_legacy_path(self, directory_manager):
        """Test legacy path mapping"""
        # Test legacy stage mapping
        assert directory_manager.map_legacy_path("stage_00_original") == DataLayer.RAW_DATA
        assert directory_manager.map_legacy_path("stage_99_build") == DataLayer.QUERY_RESULTS

        # Test legacy layer mapping
        assert directory_manager.map_legacy_path("layer_01_raw") == DataLayer.RAW_DATA
        assert directory_manager.map_legacy_path("layer_05_results") == DataLayer.QUERY_RESULTS

        # Test build data mapping
        assert directory_manager.map_legacy_path("build_data") == DataLayer.QUERY_RESULTS
        assert directory_manager.map_legacy_path("data") == DataLayer.RAW_DATA

        # Test unknown path
        assert directory_manager.map_legacy_path("unknown_path") is None

    def test_ensure_directories(self, directory_manager):
        """Test directory creation"""
        directory_manager.ensure_directories()

        # Check that layer directories are created
        for layer in DataLayer:
            layer_path = directory_manager.get_layer_path(layer)
            assert layer_path.exists()

        # Check common directories
        logs_path = directory_manager.get_logs_path()
        temp_path = directory_manager.get_temp_path()
        cache_path = directory_manager.get_cache_path()

        # Note: These might not exist yet as they're created on demand
        # Just check the paths are correctly formed
        assert "logs" in str(logs_path)
        assert "temp" in str(temp_path)
        assert "cache" in str(cache_path)

    def test_get_storage_info(self, directory_manager):
        """Test storage information retrieval"""
        storage_info = directory_manager.get_storage_info()

        assert "backend" in storage_info
        assert "root_path" in storage_info
        assert "layers" in storage_info
        assert "common_paths" in storage_info

        # Check layer paths
        assert len(storage_info["layers"]) == len(DataLayer)
        for layer_name in storage_info["layers"]:
            assert hasattr(DataLayer, layer_name)

        # Check common paths
        common_paths = storage_info["common_paths"]
        assert "config" in common_paths
        assert "logs" in common_paths
        assert "temp" in common_paths
        assert "cache" in common_paths


class TestConvenienceFunctions:
    """Test convenience functions"""

    @pytest.fixture
    def temp_project_root(self):
        """Create temporary project root for testing"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        # Create basic structure
        (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
        (project_root / "build_data").mkdir(parents=True, exist_ok=True)

        yield project_root

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_data_path(self):
        """Test get_data_path convenience function"""
        with patch("common.directory_manager.directory_manager") as mock_dm:
            mock_dm.get_layer_path.return_value = Path("/mock/path")
            mock_dm.get_subdir_path.return_value = Path("/mock/path/subdir")

            # Test without subdir
            result = get_data_path(DataLayer.RAW_DATA)
            mock_dm.get_layer_path.assert_called_once_with(DataLayer.RAW_DATA, None)

            # Test with subdir
            mock_dm.reset_mock()
            result = get_data_path(DataLayer.RAW_DATA, "sec-edgar")
            mock_dm.get_subdir_path.assert_called_once_with(DataLayer.RAW_DATA, "sec-edgar", None)

    def test_get_config_path_function(self):
        """Test get_config_path convenience function"""
        with patch("common.directory_manager.directory_manager") as mock_dm:
            mock_dm.get_config_path.return_value = Path("/mock/config")

            result = get_config_path()
            mock_dm.get_config_path.assert_called_once()

    def test_get_build_path_function(self):
        """Test get_build_path convenience function"""
        with patch("common.directory_manager.directory_manager") as mock_dm:
            mock_dm.get_build_path.return_value = Path("/mock/build")

            result = get_build_path("20250821_120000", "feature-test")
            mock_dm.get_build_path.assert_called_once_with("20250821_120000", "feature-test")

    def test_get_source_path_function(self):
        """Test get_source_path convenience function"""
        with patch("common.directory_manager.directory_manager") as mock_dm:
            mock_dm.get_source_path.return_value = Path("/mock/source")

            result = get_source_path("sec-edgar", DataLayer.RAW_DATA, "20250821", "AAPL")
            mock_dm.get_source_path.assert_called_once_with(
                "sec-edgar", DataLayer.RAW_DATA, "20250821", "AAPL"
            )


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_nonexistent_config_file(self):
        """Test behavior when config file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Create directory manager without config file
            dm = DirectoryManager(root_path=project_root)

            # Should use default config
            assert dm.config is not None
            assert "storage" in dm.config
            assert "layers" in dm.config

    def test_invalid_layer_access(self):
        """Test accessing invalid layer configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            dm = DirectoryManager(root_path=project_root)

            # Should handle gracefully
            layer_path = dm.get_layer_path(DataLayer.RAW_DATA)
            assert layer_path is not None

    def test_backend_switching(self):
        """Test different storage backends"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Test local filesystem backend
            dm_local = DirectoryManager(root_path=project_root, backend=StorageBackend.LOCAL_FS)
            assert dm_local.backend == StorageBackend.LOCAL_FS

            # Test cloud backends (should not fail even if not implemented)
            dm_s3 = DirectoryManager(root_path=project_root, backend=StorageBackend.CLOUD_S3)
            assert dm_s3.backend == StorageBackend.CLOUD_S3


if __name__ == "__main__":
    pytest.main([__file__])
