#!/usr/bin/env python3
"""
Build System Integration Tests

Tests that verify:
- Logs go to correct `build_data/logs` location
- Artifact placement in `build_data/` structure
- p3 command integration with new paths
- Build system compatibility with DirectoryManager
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
    get_data_path,
)


class TestBuildSystemIntegration:
    """Test build system integration with DirectoryManager"""

    @pytest.fixture
    def build_project_structure(self):
        """Create realistic project structure for build testing"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        # Create full project structure
        directories = [
            "common/config",
            "build_data",
            "logs",
            "temp",
            "cache",
            "ETL",
            "dcf_engine",
            "graph_rag",
            "evaluation",
        ]

        for directory in directories:
            (project_root / directory).mkdir(parents=True, exist_ok=True)

        # Create mock p3 script
        p3_script = project_root / "p3"
        with open(p3_script, "w") as f:
            f.write(
                '''#!/usr/bin/env python3
"""Mock p3 script for testing"""
import sys
import json
from pathlib import Path

def main():
    # Mock p3 command behavior
    if len(sys.argv) < 2:
        print("Usage: p3 <command> [args...]")
        return
    
    command = sys.argv[1]
    
    if command == "env-status":
        print("Environment Status: OK")
    elif command == "build":
        scope = sys.argv[2] if len(sys.argv) > 2 else "f2"
        print(f"Building {scope} scope...")
        
        # Create build artifacts in correct locations
        from common.core.directory_manager import DirectoryManager
        dm = DirectoryManager(root_path=Path.cwd())
        
        # Create build artifacts
        build_path = dm.get_build_path(branch="test-build")
        build_path.mkdir(parents=True, exist_ok=True)
        
        (build_path / "dcf_reports").mkdir(exist_ok=True)
        with open(build_path / "dcf_reports" / f"build_{scope}.json", 'w') as f:
            json.dump({"scope": scope, "status": "success"}, f)
        
        print(f"Build completed: {build_path}")
    elif command == "e2e":
        scope = sys.argv[2] if len(sys.argv) > 2 else "f2"
        print(f"Running e2e tests for {scope}...")
        print("All tests passed!")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
'''
            )
        p3_script.chmod(0o755)

        # Create directory structure config
        config_content = {
            "storage": {"backend": "local_filesystem", "root_path": "build_data"},
            "layers": {
                "layer_01_raw": {"subdirs": ["sec-edgar", "yfinance"]},
                "layer_05_results": {"subdirs": ["dcf_reports", "analytics", "exports"]},
            },
            "common": {
                "config": "common/config",
                "logs": "build_data/logs",  # Important: logs go to build_data
                "temp": "temp",
                "cache": "cache",
            },
        }

        config_file = project_root / "common" / "config" / "directory_structure.yml"
        with open(config_file, "w") as f:
            yaml.dump(config_content, f)

        yield project_root
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_logs_location_integration(self, build_project_structure):
        """Test that logs go to correct build_data/logs location"""
        dm = DirectoryManager(root_path=build_project_structure)

        # Test logs path resolution
        logs_path = dm.get_logs_path()
        expected_logs = build_project_structure / "build_data" / "logs"
        assert logs_path == expected_logs

        # Test that logs directory is created in build_data
        dm.ensure_directories()
        assert logs_path.parent.name == "build_data"

        # Simulate log creation
        logs_path.mkdir(parents=True, exist_ok=True)
        test_log = logs_path / "test.log"
        with open(test_log, "w") as f:
            f.write("Test log entry")

        assert test_log.exists()
        assert "build_data" in str(test_log.parent)

    def test_artifact_placement_in_build_data(self, build_project_structure):
        """Test that build artifacts are correctly placed in build_data structure"""
        dm = DirectoryManager(root_path=build_project_structure)

        # Test build artifacts placement
        dm.ensure_directories()

        # Test DCF reports placement
        dcf_reports_path = dm.get_subdir_path(DataLayer.QUERY_RESULTS, "dcf_reports")
        expected_dcf = build_project_structure / "build_data" / "layer_05_results" / "dcf_reports"
        assert dcf_reports_path == expected_dcf

        # Create sample artifacts
        dcf_reports_path.mkdir(parents=True, exist_ok=True)
        sample_report = dcf_reports_path / "sample_dcf_report.json"
        with open(sample_report, "w") as f:
            f.write('{"company": "AAPL", "dcf_value": 150.0}')

        assert sample_report.exists()
        assert "build_data" in str(sample_report)
        assert "layer_05_results" in str(sample_report)

        # Test analytics placement
        analytics_path = dm.get_subdir_path(DataLayer.QUERY_RESULTS, "analytics")
        analytics_path.mkdir(parents=True, exist_ok=True)
        sample_analytics = analytics_path / "performance_metrics.json"
        with open(sample_analytics, "w") as f:
            f.write('{"accuracy": 0.85, "precision": 0.78}')

        assert sample_analytics.exists()
        assert "build_data" in str(sample_analytics)

    def test_p3_command_integration(self, build_project_structure):
        """Test p3 command integration with new directory structure"""
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(build_project_structure)

        try:
            # Add project root to Python path for imports
            import sys

            sys.path.insert(0, str(build_project_structure))

            # Test env-status command
            result = subprocess.run(
                ["python3", "./p3", "env-status"], capture_output=True, text=True, timeout=30
            )
            assert result.returncode == 0
            assert "Environment Status: OK" in result.stdout

            # Test build command with scope
            result = subprocess.run(
                ["python3", "./p3", "build", "f2"], capture_output=True, text=True, timeout=30
            )
            assert result.returncode == 0
            assert "Building f2 scope" in result.stdout
            assert "Build completed" in result.stdout

            # Verify build artifacts were created in correct location
            dm = DirectoryManager(root_path=build_project_structure)
            build_path = dm.get_build_path(branch="test-build")
            dcf_reports = build_path / "dcf_reports" / "build_f2.json"
            assert dcf_reports.exists()

            # Test e2e command
            result = subprocess.run(
                ["python3", "./p3", "e2e", "f2"], capture_output=True, text=True, timeout=30
            )
            assert result.returncode == 0
            assert "Running e2e tests for f2" in result.stdout

        finally:
            os.chdir(original_cwd)

    def test_build_path_creation_integration(self, build_project_structure):
        """Test build path creation with different scenarios"""
        dm = DirectoryManager(root_path=build_project_structure)

        # Test main branch build
        main_build = dm.get_build_path()
        main_build.mkdir(parents=True, exist_ok=True)
        assert main_build.exists()
        assert "build_data" in str(main_build)
        assert "layer_05_results" in str(main_build)

        # Test feature branch build
        feature_build = dm.get_build_path(branch="feature-test")
        feature_build.mkdir(parents=True, exist_ok=True)
        assert feature_build.exists()
        assert "layer_05_results_feature-test" in str(feature_build)

        # Test timestamped build
        timestamp = "20250828_150000"
        timestamped_build = dm.get_build_path(build_timestamp=timestamp)
        timestamped_build.mkdir(parents=True, exist_ok=True)
        assert timestamped_build.exists()
        assert f"build_{timestamp}" in str(timestamped_build)

    def test_data_flow_through_layers(self, build_project_structure):
        """Test data flow through the five-layer architecture"""
        dm = DirectoryManager(root_path=build_project_structure)
        dm.ensure_directories()

        # Simulate data flow from raw to results
        # Layer 1: Raw data input
        raw_data_path = dm.get_subdir_path(DataLayer.RAW_DATA, "sec-edgar")
        raw_data_path.mkdir(parents=True, exist_ok=True)
        raw_file = raw_data_path / "AAPL_10K_2024.xml"
        with open(raw_file, "w") as f:
            f.write("<SEC-DOCUMENT>Sample SEC filing</SEC-DOCUMENT>")

        # Layer 2: Daily delta
        delta_path = dm.get_subdir_path(DataLayer.DAILY_DELTA, "additions")
        delta_path.mkdir(parents=True, exist_ok=True)
        delta_file = delta_path / "new_filings_20250828.json"
        with open(delta_file, "w") as f:
            f.write('{"new_filings": ["AAPL_10K_2024.xml"]}')

        # Layer 3: Daily index
        index_path = dm.get_subdir_path(DataLayer.DAILY_INDEX, "embeddings")
        index_path.mkdir(parents=True, exist_ok=True)
        index_file = index_path / "AAPL_embeddings.npy"
        with open(index_file, "wb") as f:
            f.write(b"mock_embeddings_data")

        # Layer 4: Graph RAG
        rag_path = dm.get_subdir_path(DataLayer.GRAPH_RAG, "vector_store")
        rag_path.mkdir(parents=True, exist_ok=True)
        rag_file = rag_path / "knowledge_base.db"
        with open(rag_file, "w") as f:
            f.write("MOCK_VECTOR_DATABASE")

        # Layer 5: Query results
        results_path = dm.get_subdir_path(DataLayer.QUERY_RESULTS, "dcf_reports")
        results_path.mkdir(parents=True, exist_ok=True)
        results_file = results_path / "AAPL_dcf_analysis.json"
        with open(results_file, "w") as f:
            f.write('{"ticker": "AAPL", "dcf_value": 175.0, "recommendation": "BUY"}')

        # Verify all files exist in correct locations
        assert raw_file.exists()
        assert delta_file.exists()
        assert index_file.exists()
        assert rag_file.exists()
        assert results_file.exists()

        # Verify all are under build_data
        for file_path in [raw_file, delta_file, index_file, rag_file, results_file]:
            assert "build_data" in str(file_path)


class TestBuildSystemPerformance:
    """Performance tests for build system integration"""

    @pytest.fixture
    def performance_build_structure(self):
        """Create build structure for performance testing"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        (project_root / "common" / "config").mkdir(parents=True, exist_ok=True)
        (project_root / "build_data").mkdir(parents=True, exist_ok=True)

        yield project_root
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_large_build_artifact_handling(self, performance_build_structure):
        """Test handling of large build artifacts"""
        dm = DirectoryManager(root_path=performance_build_structure)
        dm.ensure_directories()

        # Create large build artifacts
        start_time = time.time()

        results_path = dm.get_subdir_path(DataLayer.QUERY_RESULTS, "dcf_reports")
        results_path.mkdir(parents=True, exist_ok=True)

        # Create multiple large files to simulate real build
        for i in range(100):
            large_file = results_path / f"large_report_{i:03d}.json"
            with open(large_file, "w") as f:
                # Create ~1KB files
                data = {"report_id": i, "data": "x" * 900}
                f.write(str(data))

        creation_time = time.time() - start_time

        # Performance check: should handle 100 files in < 5 seconds
        assert creation_time < 5.0, f"File creation too slow: {creation_time:.2f}s"

        # Verify all files created correctly
        assert len(list(results_path.glob("*.json"))) == 100

    def test_concurrent_build_operations(self, performance_build_structure):
        """Test concurrent build operations"""
        import queue
        import threading

        dm = DirectoryManager(root_path=performance_build_structure)
        dm.ensure_directories()

        results = queue.Queue()

        def create_build_artifacts(thread_id):
            try:
                # Each thread creates artifacts in different subdirs
                subdir = f"thread_{thread_id}"
                path = dm.get_subdir_path(DataLayer.QUERY_RESULTS, subdir)
                path.mkdir(parents=True, exist_ok=True)

                for i in range(10):
                    artifact = path / f"artifact_{i}.json"
                    with open(artifact, "w") as f:
                        f.write(f'{{"thread": {thread_id}, "artifact": {i}}}')

                results.put((thread_id, "success"))
            except Exception as e:
                results.put((thread_id, f"error: {e}"))

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_build_artifacts, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Check results
        success_count = 0
        while not results.empty():
            thread_id, result = results.get()
            assert result == "success", f"Thread {thread_id} failed: {result}"
            success_count += 1

        assert success_count == 5


class TestBuildSystemErrorHandling:
    """Error handling tests for build system integration"""

    def test_build_permission_errors(self):
        """Test handling of build permission errors"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            dm = DirectoryManager(root_path=project_root)

            # Create restricted directory
            restricted_build = project_root / "build_data" / "restricted"
            restricted_build.mkdir(parents=True)

            if os.name != "nt":  # Skip on Windows
                os.chmod(restricted_build, 0o000)

                # Should handle permission errors gracefully
                try:
                    test_file = restricted_build / "test.json"
                    with open(test_file, "w") as f:
                        f.write('{"test": "data"}')
                except PermissionError:
                    pass  # Expected

                # Restore permissions
                os.chmod(restricted_build, 0o755)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_disk_space_simulation(self):
        """Test handling of disk space issues (simulated)"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            dm = DirectoryManager(root_path=project_root)
            dm.ensure_directories()

            # Simulate disk space check
            build_path = dm.get_build_path()
            build_path.mkdir(parents=True, exist_ok=True)

            # Check available space
            statvfs = os.statvfs(build_path)
            available_bytes = statvfs.f_frsize * statvfs.f_bavail

            # Should have reasonable space available for testing
            assert available_bytes > 1024 * 1024  # At least 1MB

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_corrupted_build_artifacts(self):
        """Test handling of corrupted build artifacts"""
        temp_dir = tempfile.mkdtemp()
        project_root = Path(temp_dir)

        try:
            dm = DirectoryManager(root_path=project_root)
            dm.ensure_directories()

            # Create corrupted artifacts
            results_path = dm.get_subdir_path(DataLayer.QUERY_RESULTS, "dcf_reports")
            results_path.mkdir(parents=True, exist_ok=True)

            corrupted_file = results_path / "corrupted.json"
            with open(corrupted_file, "w") as f:
                f.write('{"invalid": json: content}')  # Invalid JSON

            # Should be able to detect the file exists even if corrupted
            assert corrupted_file.exists()

            # Application should handle JSON parsing errors gracefully
            try:
                import json

                with open(corrupted_file) as f:
                    json.load(f)
            except json.JSONDecodeError:
                pass  # Expected behavior

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
