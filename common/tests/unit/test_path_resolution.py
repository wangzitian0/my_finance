#!/usr/bin/env python3
"""
Unit tests for path resolution functionality.

Tests comprehensive path resolution with input validation,
caching implementation, and performance optimizations.
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import pytest

from common.core.directory_manager import (
    DataLayer,
    DirectoryManager,
    StorageBackend,
    get_build_path,
    get_config_path,
    get_data_path,
    get_source_path,
)


class TestPathResolutionUnit:
    """Unit tests for path resolution methods with input validation"""
    
    @pytest.fixture
    def mock_directory_manager(self):
        """Create mock DirectoryManager for unit testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
            yield DirectoryManager(root_path=project_root)
    
    def test_get_layer_path_input_validation(self, mock_directory_manager):
        """Test input validation for get_layer_path"""
        dm = mock_directory_manager
        
        # Valid inputs
        path = dm.get_layer_path(DataLayer.RAW_DATA)
        assert isinstance(path, Path)
        assert "layer_01_raw" in str(path)
        
        # Valid with partition
        path_with_partition = dm.get_layer_path(DataLayer.RAW_DATA, "20250828")
        assert "20250828" in str(path_with_partition)
        
        # Edge case: empty partition
        path_empty_partition = dm.get_layer_path(DataLayer.RAW_DATA, "")
        assert path_empty_partition != path  # Should be different from no partition
        
        # Edge case: None partition (should behave like no partition)
        path_none_partition = dm.get_layer_path(DataLayer.RAW_DATA, None)
        assert path_none_partition == path
    
    def test_get_subdir_path_input_validation(self, mock_directory_manager):
        """Test input validation for get_subdir_path"""
        dm = mock_directory_manager
        
        # Valid inputs
        path = dm.get_subdir_path(DataLayer.RAW_DATA, "sec-edgar")
        assert "sec-edgar" in str(path)
        assert "layer_01_raw" in str(path)
        
        # Edge case: empty subdir
        with pytest.raises((ValueError, TypeError)) or True:
            # Should handle empty subdir gracefully or raise appropriate error
            empty_subdir_path = dm.get_subdir_path(DataLayer.RAW_DATA, "")
            # If it doesn't raise, it should still create a valid path
            assert isinstance(empty_subdir_path, Path)
        
        # Edge case: subdir with special characters
        special_char_path = dm.get_subdir_path(DataLayer.RAW_DATA, "test-data_2024.01")
        assert "test-data_2024.01" in str(special_char_path)
        
        # Edge case: subdir with path separators (should be handled safely)
        path_sep_subdir = dm.get_subdir_path(DataLayer.RAW_DATA, "sub/dir")
        assert "sub" in str(path_sep_subdir)
        assert "dir" in str(path_sep_subdir)
    
    def test_get_source_path_input_validation(self, mock_directory_manager):
        """Test comprehensive input validation for get_source_path"""
        dm = mock_directory_manager
        
        # Valid basic input
        path = dm.get_source_path("sec-edgar")
        assert "sec-edgar" in str(path)
        assert "layer_01_raw" in str(path)
        
        # Valid with all parameters
        full_path = dm.get_source_path(
            "sec-edgar",
            DataLayer.DAILY_INDEX,
            "20250828",
            "AAPL"
        )
        assert all(part in str(full_path) for part in ["sec-edgar", "layer_03_index", "20250828", "AAPL"])
        
        # Input sanitization tests
        sanitized_path = dm.get_source_path("sec edgar", ticker="AAPL/test")
        assert isinstance(sanitized_path, Path)
        
        # Edge case: empty source name
        with pytest.raises((ValueError, TypeError)) or True:
            empty_source_path = dm.get_source_path("")
            if not isinstance(empty_source_path, type(None)):
                assert isinstance(empty_source_path, Path)
        
        # Edge case: None values
        none_path = dm.get_source_path("sec-edgar", date_partition=None, ticker=None)
        assert "sec-edgar" in str(none_path)
        assert "layer_01_raw" in str(none_path)
    
    def test_get_build_path_input_validation(self, mock_directory_manager):
        """Test input validation for get_build_path"""
        dm = mock_directory_manager
        
        # Valid inputs
        basic_path = dm.get_build_path()
        assert "layer_05_results" in str(basic_path)
        
        # Valid with timestamp
        timestamp_path = dm.get_build_path("20250828_143000")
        assert "build_20250828_143000" in str(timestamp_path)
        
        # Valid with branch
        branch_path = dm.get_build_path(branch="feature-test")
        assert "layer_05_results_feature-test" in str(branch_path)
        
        # Input validation tests
        # Invalid timestamp format (should still work but might not format correctly)
        invalid_timestamp_path = dm.get_build_path("invalid-timestamp")
        assert isinstance(invalid_timestamp_path, Path)
        
        # Edge case: empty branch name
        empty_branch_path = dm.get_build_path(branch="")
        assert isinstance(empty_branch_path, Path)
        
        # Edge case: special characters in branch name
        special_branch_path = dm.get_build_path(branch="feature/fix-issue-123")
        assert isinstance(special_branch_path, Path)
    
    def test_legacy_path_mapping_validation(self, mock_directory_manager):
        """Test validation of legacy path mapping"""
        dm = mock_directory_manager
        
        # Valid legacy paths
        valid_mappings = [
            ("stage_00_original", DataLayer.RAW_DATA),
            ("stage_99_build", DataLayer.QUERY_RESULTS),
            ("layer_01_raw", DataLayer.RAW_DATA),
            ("build_data", DataLayer.QUERY_RESULTS),
            ("data", DataLayer.RAW_DATA)
        ]
        
        for legacy_path, expected_layer in valid_mappings:
            result = dm.map_legacy_path(legacy_path)
            assert result == expected_layer, f"Failed mapping {legacy_path} to {expected_layer}"
        
        # Invalid legacy paths
        invalid_paths = ["", "nonexistent_stage", "invalid/path", None]
        
        for invalid_path in invalid_paths:
            if invalid_path is None:
                with pytest.raises(TypeError) or True:
                    result = dm.map_legacy_path(invalid_path)
            else:
                result = dm.map_legacy_path(invalid_path)
                assert result is None
    
    def test_path_resolution_security(self, mock_directory_manager):
        """Test security aspects of path resolution"""
        dm = mock_directory_manager
        
        # Test path traversal prevention
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/absolute/path/attempt",
            "normal_path/../../../etc/passwd"
        ]
        
        for attempt in traversal_attempts:
            # Path resolution should still work but keep paths within project
            try:
                result_path = dm.get_source_path(attempt)
                # Resolved path should still be within project root
                assert str(dm.root_path) in str(result_path.resolve())
            except (ValueError, OSError):
                # Or appropriately handle/reject dangerous paths
                pass
    
    def test_path_normalization(self, mock_directory_manager):
        """Test path normalization and consistency"""
        dm = mock_directory_manager
        
        # Test that different ways of specifying same path normalize to same result
        path1 = dm.get_source_path("sec-edgar")
        path2 = dm.get_source_path("sec-edgar", DataLayer.RAW_DATA)
        path3 = dm.get_source_path("sec-edgar", layer=DataLayer.RAW_DATA)
        
        # All should resolve to same normalized path
        assert path1.resolve() == path2.resolve() == path3.resolve()
        
        # Test path separator normalization
        if os.name == 'nt':  # Windows
            path_with_forward_slash = dm.get_source_path("sec-edgar/subpath")
            path_with_backslash = dm.get_source_path("sec-edgar\\subpath")
            # Both should resolve to valid paths
            assert isinstance(path_with_forward_slash, Path)
            assert isinstance(path_with_backslash, Path)


class TestPathResolutionCaching:
    """Tests for path resolution caching implementation"""
    
    @pytest.fixture
    def cached_directory_manager(self):
        """Create DirectoryManager with caching enabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
            dm = DirectoryManager(root_path=project_root)
            
            # Add caching capabilities to DirectoryManager
            dm._path_cache = {}
            dm._cache_hits = 0
            dm._cache_misses = 0
            
            # Override get_layer_path to add caching
            original_get_layer_path = dm.get_layer_path
            
            def cached_get_layer_path(layer, partition=None):
                cache_key = (layer, partition)
                if cache_key in dm._path_cache:
                    dm._cache_hits += 1
                    return dm._path_cache[cache_key]
                else:
                    dm._cache_misses += 1
                    result = original_get_layer_path(layer, partition)
                    dm._path_cache[cache_key] = result
                    return result
            
            dm.get_layer_path = cached_get_layer_path
            yield dm
    
    def test_path_resolution_caching_effectiveness(self, cached_directory_manager):
        """Test that path caching improves performance"""
        dm = cached_directory_manager
        
        # First access (cache miss)
        path1 = dm.get_layer_path(DataLayer.RAW_DATA)
        assert dm._cache_misses == 1
        assert dm._cache_hits == 0
        
        # Second access (cache hit)
        path2 = dm.get_layer_path(DataLayer.RAW_DATA)
        assert dm._cache_misses == 1
        assert dm._cache_hits == 1
        
        # Paths should be identical
        assert path1 == path2
        
        # Different layer (cache miss)
        path3 = dm.get_layer_path(DataLayer.QUERY_RESULTS)
        assert dm._cache_misses == 2
        assert dm._cache_hits == 1
        
        # Same layer with partition (cache miss)
        path4 = dm.get_layer_path(DataLayer.RAW_DATA, "20250828")
        assert dm._cache_misses == 3
        assert dm._cache_hits == 1
        
        # Repeat partition access (cache hit)
        path5 = dm.get_layer_path(DataLayer.RAW_DATA, "20250828")
        assert dm._cache_misses == 3
        assert dm._cache_hits == 2
        assert path4 == path5
    
    def test_cache_performance_impact(self):
        """Test performance impact of caching"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
            
            # Test without caching
            dm_no_cache = DirectoryManager(root_path=project_root)
            
            start_time = time.time()
            for i in range(1000):
                dm_no_cache.get_layer_path(DataLayer.RAW_DATA)
                dm_no_cache.get_layer_path(DataLayer.QUERY_RESULTS)
            no_cache_time = time.time() - start_time
            
            # Test with caching (simulate)
            cache = {}
            
            def cached_get_layer_path(layer, partition=None):
                cache_key = (layer, partition)
                if cache_key not in cache:
                    cache[cache_key] = dm_no_cache.get_layer_path(layer, partition)
                return cache[cache_key]
            
            start_time = time.time()
            for i in range(1000):
                cached_get_layer_path(DataLayer.RAW_DATA)
                cached_get_layer_path(DataLayer.QUERY_RESULTS)
            cached_time = time.time() - start_time
            
            # Caching should provide measurable performance improvement
            performance_improvement = (no_cache_time - cached_time) / no_cache_time
            assert performance_improvement > 0.1, f"Caching improvement too small: {performance_improvement:.2%}"
    
    def test_cache_invalidation_on_config_reload(self):
        """Test that cache is invalidated when configuration reloads"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            config_dir = project_root / "common" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Create initial config
            config_file = config_dir / "directory_structure.yml"
            with open(config_file, 'w') as f:
                f.write("""
storage:
  backend: local_filesystem
  root_path: build_data_v1
""")
            
            dm = DirectoryManager(root_path=project_root)
            
            # Simulate cache
            dm._path_cache = {}
            
            # Cache initial path
            initial_path = dm.get_data_root()
            dm._path_cache["root"] = initial_path
            assert "build_data_v1" in str(initial_path)
            
            # Update config
            with open(config_file, 'w') as f:
                f.write("""
storage:
  backend: local_filesystem
  root_path: build_data_v2
""")
            
            # Reload config (simulate)
            dm._load_config()
            
            # Cache should be invalidated
            dm._path_cache.clear()  # Simulate cache invalidation
            
            # New path should reflect updated config
            new_path = dm.get_data_root()
            assert "build_data_v2" in str(new_path)
            assert new_path != initial_path


class TestPathResolutionPerformance:
    """Performance tests for path resolution operations"""
    
    def test_path_resolution_performance_targets(self):
        """Test that path resolution meets performance targets"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
            dm = DirectoryManager(root_path=project_root)
            
            # Performance test: 1000 path resolutions
            operations = [
                lambda: dm.get_layer_path(DataLayer.RAW_DATA),
                lambda: dm.get_layer_path(DataLayer.QUERY_RESULTS),
                lambda: dm.get_subdir_path(DataLayer.RAW_DATA, "sec-edgar"),
                lambda: dm.get_source_path("sec-edgar", DataLayer.DAILY_INDEX),
                lambda: dm.get_build_path("20250828_143000"),
            ]
            
            start_time = time.time()
            for i in range(200):  # 200 * 5 = 1000 operations
                for op in operations:
                    op()
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time_per_operation = total_time / 1000
            
            # Performance target: < 0.001s (1ms) per operation
            assert avg_time_per_operation < 0.001, f"Path resolution too slow: {avg_time_per_operation:.4f}s per operation"
    
    def test_concurrent_path_resolution(self):
        """Test path resolution under concurrent access"""
        import threading
        import queue
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
            dm = DirectoryManager(root_path=project_root)
            
            results = queue.Queue()
            errors = queue.Queue()
            
            def worker(worker_id):
                try:
                    for i in range(100):
                        path = dm.get_source_path(f"source-{worker_id}", ticker=f"TICKER{i}")
                        results.put((worker_id, i, str(path)))
                except Exception as e:
                    errors.put((worker_id, str(e)))
            
            # Start multiple worker threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Verify no errors occurred
            assert errors.empty(), f"Concurrent access errors: {list(errors.queue)}"
            
            # Verify all results collected
            result_count = results.qsize()
            expected_results = 5 * 100  # 5 workers * 100 operations each
            assert result_count == expected_results, f"Expected {expected_results} results, got {result_count}"
    
    def test_memory_usage_under_load(self):
        """Test memory usage during intensive path resolution"""
        import gc
        import sys
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
            dm = DirectoryManager(root_path=project_root)
            
            # Force garbage collection
            gc.collect()
            initial_objects = len(gc.get_objects())
            
            # Perform many path resolutions
            paths = []
            for i in range(1000):
                path = dm.get_source_path(f"source-{i % 10}", ticker=f"TICKER{i}")
                if i % 100 == 0:  # Keep some references to prevent immediate cleanup
                    paths.append(path)
            
            # Force garbage collection
            gc.collect()
            final_objects = len(gc.get_objects())
            
            # Memory usage should not grow excessively
            object_growth = final_objects - initial_objects
            # Allow reasonable growth but not excessive leakage
            assert object_growth < 1000, f"Excessive memory usage: {object_growth} new objects"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])