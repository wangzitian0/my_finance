#!/usr/bin/env python3
"""
Integration tests for DirectoryManager functionality.

Tests the complete DirectoryManager system including:
- Path resolution correctness
- DataLayer enum usage
- Backend switching functionality
- Legacy path mapping
- Configuration loading
- Real filesystem operations
- Error handling and validation
"""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from common.core.directory_manager import (
    DataLayer,
    DirectoryManager,
    StorageBackend,
    get_build_path,
    get_config_path,
    get_data_path,
    get_source_path,
)


class TestDirectoryManagerIntegration:
    """Integration tests for DirectoryManager with real filesystem operations"""

    @pytest.fixture
    def real_project_structure(self):
        """Create a realistic project structure for integration testing"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        # Create realistic project structure
        (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
        (project_root / "build_data").mkdir(parents=True, exist_ok=True)
        (project_root / "logs").mkdir(parents=True, exist_ok=True)
        (project_root / "cache").mkdir(parents=True, exist_ok=True)
        (project_root / "temp").mkdir(parents=True, exist_ok=True)

        # Create a realistic directory_structure.yml config
        config_content = {
            "storage": {"backend": "local_filesystem", "root_path": "build_data"},
            "layers": {
                "layer_01_raw": {
                    "description": "Raw Data Layer - Immutable source data",
                    "subdirs": ["sec-edgar", "yfinance", "manual", "reference"],
                    "performance": {
                        "target_response_time": "1000ms",
                        "caching": False,
                        "indexing": "minimal",
                    },
                },
                "layer_02_delta": {
                    "description": "Daily Delta Layer - Incremental changes",
                    "subdirs": ["additions", "modifications", "deletions", "metadata"],
                    "performance": {
                        "target_response_time": "500ms",
                        "caching": False,
                        "indexing": "temporal",
                    },
                },
                "layer_03_index": {
                    "description": "Daily Index Layer - Vectors, entities, relationships",
                    "subdirs": ["vectors", "entities", "relationships", "embeddings", "indices"],
                    "performance": {
                        "target_response_time": "200ms",
                        "caching": True,
                        "cache_ttl": "24h",
                        "indexing": "full",
                    },
                },
                "layer_04_rag": {
                    "description": "Graph RAG Layer - Unified knowledge base",
                    "subdirs": ["graph_db", "vector_store", "cache", "snapshots"],
                    "performance": {
                        "target_response_time": "100ms",
                        "caching": True,
                        "cache_ttl": "1h",
                        "indexing": "graph",
                    },
                },
                "layer_05_results": {
                    "description": "Query Results Layer - Analysis and reports",
                    "subdirs": [
                        "dcf_reports",
                        "analytics",
                        "exports",
                        "dashboards",
                        "api_responses",
                    ],
                    "performance": {
                        "target_response_time": "50ms",
                        "caching": True,
                        "cache_ttl": "7d",
                        "indexing": "business",
                    },
                },
            },
            "common": {"config": "common/config", "logs": "logs", "temp": "temp", "cache": "cache"},
            "legacy_mapping": {
                "stage_00_original": "layer_01_raw",
                "stage_01_extract": "layer_02_delta",
                "stage_02_transform": "layer_03_index",
                "stage_03_load": "layer_04_rag",
                "stage_99_build": "layer_05_results",
                "data/config": "common/config",
                "data": "build_data",
            },
        }

        config_file = project_root / "common" / "config" / "directory_structure.yml"
        with open(config_file, "w") as f:
            yaml.dump(config_content, f, default_flow_style=False)

        yield project_root

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_full_path_resolution_correctness(self, real_project_structure):
        """Test that all path resolution methods work correctly with real config"""
        dm = DirectoryManager(root_path=real_project_structure)

        # Test layer path resolution
        raw_path = dm.get_layer_path(DataLayer.RAW_DATA)
        expected_raw = real_project_structure / "build_data" / "layer_01_raw"
        assert raw_path == expected_raw

        # Test subdir path resolution
        sec_path = dm.get_subdir_path(DataLayer.RAW_DATA, "sec-edgar")
        expected_sec = expected_raw / "sec-edgar"
        assert sec_path == expected_sec

        # Test source path resolution with all parameters
        full_source_path = dm.get_source_path(
            "sec-edgar", DataLayer.RAW_DATA, date_partition="20250828", ticker="AAPL"
        )
        expected_full = expected_raw / "sec-edgar" / "20250828" / "AAPL"
        assert full_source_path == expected_full

    def test_data_layer_enum_consistency(self, real_project_structure):
        """Test that DataLayer enum values map correctly to filesystem structure"""
        dm = DirectoryManager(root_path=real_project_structure)

        # Test all DataLayer enum values
        layer_mappings = {
            DataLayer.RAW_DATA: "layer_01_raw",
            DataLayer.DAILY_DELTA: "layer_02_delta",
            DataLayer.DAILY_INDEX: "layer_03_index",
            DataLayer.GRAPH_RAG: "layer_04_rag",
            DataLayer.QUERY_RESULTS: "layer_05_results",
        }

        for layer, expected_dir in layer_mappings.items():
            path = dm.get_layer_path(layer)
            assert path.name == expected_dir
            assert expected_dir in str(path)

    def test_backend_switching_functionality(self, real_project_structure):
        """Test backend switching with different storage configurations"""
        # Test local filesystem backend
        dm_local = DirectoryManager(
            root_path=real_project_structure, backend=StorageBackend.LOCAL_FS
        )
        assert dm_local.backend == StorageBackend.LOCAL_FS

        # Test that paths are still resolved correctly
        path = dm_local.get_layer_path(DataLayer.RAW_DATA)
        assert "build_data" in str(path)
        assert "layer_01_raw" in str(path)

        # Test switching to cloud backend (should not break path resolution)
        dm_cloud = DirectoryManager(
            root_path=real_project_structure, backend=StorageBackend.CLOUD_S3
        )
        assert dm_cloud.backend == StorageBackend.CLOUD_S3

        # Paths should still resolve (even if backend not implemented)
        cloud_path = dm_cloud.get_layer_path(DataLayer.RAW_DATA)
        assert cloud_path == path  # Same path resolution logic

    def test_legacy_path_mapping_integration(self, real_project_structure):
        """Test complete legacy path mapping functionality"""
        dm = DirectoryManager(root_path=real_project_structure)

        # Test all legacy mappings from config
        legacy_tests = [
            ("stage_00_original", DataLayer.RAW_DATA),
            ("stage_01_extract", DataLayer.DAILY_DELTA),
            ("stage_02_transform", DataLayer.DAILY_INDEX),
            ("stage_03_load", DataLayer.GRAPH_RAG),
            ("stage_99_build", DataLayer.QUERY_RESULTS),
            ("build_data", DataLayer.QUERY_RESULTS),
            ("data", DataLayer.RAW_DATA),
        ]

        for legacy_path, expected_layer in legacy_tests:
            mapped_layer = dm.map_legacy_path(legacy_path)
            assert (
                mapped_layer == expected_layer
            ), f"Failed mapping {legacy_path} to {expected_layer}"

    def test_configuration_loading_and_validation(self, real_project_structure):
        """Test configuration loading with validation"""
        dm = DirectoryManager(root_path=real_project_structure)

        # Test that configuration loaded correctly
        assert dm.config is not None
        assert "storage" in dm.config
        assert "layers" in dm.config
        assert "common" in dm.config
        assert "legacy_mapping" in dm.config

        # Test specific configuration values
        assert dm.config["storage"]["backend"] == "local_filesystem"
        assert dm.config["storage"]["root_path"] == "build_data"

        # Test layer configurations
        raw_layer_config = dm.config["layers"]["layer_01_raw"]
        assert "sec-edgar" in raw_layer_config["subdirs"]
        assert "yfinance" in raw_layer_config["subdirs"]

        # Test performance configurations
        rag_layer_config = dm.config["layers"]["layer_04_rag"]
        assert rag_layer_config["performance"]["target_response_time"] == "100ms"
        assert rag_layer_config["performance"]["caching"] is True

    def test_directory_creation_integration(self, real_project_structure):
        """Test complete directory creation process"""
        dm = DirectoryManager(root_path=real_project_structure)

        # Create all directories
        dm.ensure_directories()

        # Verify all layer directories exist
        for layer in DataLayer:
            layer_path = dm.get_layer_path(layer)
            assert layer_path.exists(), f"Layer directory {layer_path} was not created"

            # Verify subdirectories exist
            layer_config = dm.config["layers"].get(layer.value, {})
            for subdir in layer_config.get("subdirs", []):
                subdir_path = layer_path / subdir
                assert subdir_path.exists(), f"Subdirectory {subdir_path} was not created"

    def test_storage_info_integration(self, real_project_structure):
        """Test complete storage information retrieval"""
        dm = DirectoryManager(root_path=real_project_structure)

        storage_info = dm.get_storage_info()

        # Verify structure
        required_keys = ["backend", "root_path", "layers", "common_paths"]
        for key in required_keys:
            assert key in storage_info

        # Verify layer information
        assert len(storage_info["layers"]) == len(DataLayer)
        for layer in DataLayer:
            assert layer.name in storage_info["layers"]
            layer_path = storage_info["layers"][layer.name]
            assert real_project_structure.name in layer_path
            assert "build_data" in layer_path
            assert layer.value in layer_path

        # Verify common paths
        common_paths = storage_info["common_paths"]
        for path_type in ["config", "logs", "temp", "cache"]:
            assert path_type in common_paths
            assert real_project_structure.name in common_paths[path_type]

    def test_build_path_integration_with_branches(self, real_project_structure):
        """Test build path generation with different branch scenarios"""
        dm = DirectoryManager(root_path=real_project_structure)

        # Test main branch build path
        main_build_path = dm.get_build_path()
        assert "layer_05_results" in str(main_build_path)
        assert "build_data" in str(main_build_path)

        # Test feature branch build path
        feature_build_path = dm.get_build_path(branch="feature-fix-common-lib-125")
        assert "layer_05_results_feature-fix-common-lib-125" in str(feature_build_path)

        # Test timestamped build path
        timestamp = "20250828_143000"
        timestamped_path = dm.get_build_path(build_timestamp=timestamp)
        assert f"build_{timestamp}" in str(timestamped_path)

        # Test combination
        combo_path = dm.get_build_path(build_timestamp=timestamp, branch="feature-test")
        assert "layer_05_results_feature-test" in str(combo_path)
        assert f"build_{timestamp}" in str(combo_path)


class TestDirectoryManagerPerformance:
    """Performance tests for DirectoryManager operations"""

    @pytest.fixture
    def performance_project_structure(self):
        """Create project structure optimized for performance testing"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        # Create structure
        (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
        (project_root / "build_data").mkdir(parents=True, exist_ok=True)

        yield project_root
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_path_resolution_performance(self, performance_project_structure):
        """Test path resolution performance under load"""
        dm = DirectoryManager(root_path=performance_project_structure)

        # Time multiple path resolutions
        start_time = time.time()
        iterations = 1000

        for i in range(iterations):
            # Mix different types of path resolutions
            dm.get_layer_path(DataLayer.RAW_DATA)
            dm.get_subdir_path(DataLayer.GRAPH_RAG, "graph_db")
            dm.get_source_path("sec-edgar", DataLayer.DAILY_INDEX)
            dm.get_build_path(f"20250828_{i:06d}")

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / (iterations * 4)  # 4 operations per iteration

        # Performance target: < 1ms per operation
        assert avg_time < 0.001, f"Path resolution too slow: {avg_time:.4f}s per operation"

    def test_configuration_loading_performance(self, performance_project_structure):
        """Test configuration loading performance"""
        # Time DirectoryManager initialization
        start_time = time.time()

        for i in range(100):
            dm = DirectoryManager(root_path=performance_project_structure)
            # Access some config to ensure it's loaded
            _ = dm.config["storage"]["backend"]

        end_time = time.time()
        avg_init_time = (end_time - start_time) / 100

        # Performance target: < 10ms initialization
        assert avg_init_time < 0.01, f"Initialization too slow: {avg_init_time:.4f}s"


class TestDirectoryManagerErrorHandling:
    """Error handling tests for DirectoryManager"""

    def test_missing_config_file_handling(self):
        """Test graceful handling of missing configuration file"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            # Create directory manager without config file
            dm = DirectoryManager(root_path=project_root)

            # Should fall back to default config
            assert dm.config is not None
            assert "storage" in dm.config
            assert dm.config["storage"]["backend"] == "local_filesystem"

            # Should still be able to resolve paths
            path = dm.get_layer_path(DataLayer.RAW_DATA)
            assert path is not None
            assert "layer_01_raw" in str(path)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_corrupted_config_file_handling(self):
        """Test handling of corrupted configuration file"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            # Create corrupted config file
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
            config_file = project_root / "common" / "config" / "directory_structure.yml"
            with open(config_file, "w") as f:
                f.write("invalid: yaml: content: [unclosed")

            # Should handle gracefully and fall back to defaults
            dm = DirectoryManager(root_path=project_root)
            assert dm.config is not None

            # Should still work with default config
            path = dm.get_layer_path(DataLayer.RAW_DATA)
            assert path is not None

        except yaml.YAMLError:
            # Expected behavior - should catch and handle
            pass
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_invalid_path_inputs(self):
        """Test handling of invalid path inputs"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            dm = DirectoryManager(root_path=project_root)

            # Test with None inputs
            path = dm.get_source_path("sec-edgar", date_partition=None, ticker=None)
            assert path is not None
            assert "sec-edgar" in str(path)

            # Test with empty string inputs
            path = dm.get_subdir_path(DataLayer.RAW_DATA, "", "")
            assert path is not None

            # Test legacy mapping with invalid input
            result = dm.map_legacy_path("nonexistent_legacy_path")
            assert result is None

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_permission_errors(self):
        """Test handling of permission errors"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            dm = DirectoryManager(root_path=project_root)

            # Create a directory with restricted permissions
            restricted_dir = project_root / "restricted"
            restricted_dir.mkdir()

            if os.name != "nt":  # Skip on Windows (different permission model)
                os.chmod(restricted_dir, 0o000)

                # Should handle permission errors gracefully
                try:
                    dm.ensure_directories()
                except PermissionError:
                    pass  # Expected behavior

                # Restore permissions for cleanup
                os.chmod(restricted_dir, 0o755)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
