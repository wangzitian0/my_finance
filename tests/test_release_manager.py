#!/usr/bin/env python3
"""
Unit tests for the Release Management System

Tests cover core functionality including:
- Release creation and validation
- Artifact collection
- Manifest generation
- Local release management
"""
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).parent.parent))

from scripts.release_manager import ReleaseManager


class TestReleaseManager(unittest.TestCase):
    """Test cases for ReleaseManager class."""

    def setUp(self):
        """Set up test environment with temporary directories."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_project_root = self.temp_dir / "test_project"
        self.test_project_root.mkdir()

        # Create test directory structure
        self.setup_test_directory_structure()

        # Initialize release manager with test project root
        self.release_manager = ReleaseManager(self.test_project_root)

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def setup_test_directory_structure(self):
        """Create a realistic test directory structure."""
        # Create data directory structure
        data_dir = self.test_project_root / "data"
        data_dir.mkdir()

        # Stage 99 build directory
        build_dir = data_dir / "stage_99_build" / "build_20250820_123000"
        build_dir.mkdir(parents=True)

        # Create test build manifest
        manifest_content = """# Build Manifest\n\nBuild ID: 20250820_123000\nStatus: Completed\n"""
        (build_dir / "BUILD_MANIFEST.md").write_text(manifest_content)
        (build_dir / "BUILD_MANIFEST.json").write_text(
            '{"build_id": "20250820_123000", "status": "completed"}'
        )

        # LLM responses directory
        llm_dir = data_dir / "llm" / "responses"
        llm_dir.mkdir(parents=True)
        (llm_dir / "dcf_en_AAPL_test.md").write_text("# DCF Analysis for AAPL\n\nTest content")
        (llm_dir / "dcf_zh_MSFT_test.md").write_text("# MSFT DCF 分析\n\n测试内容")

        # Quality reports directory
        quality_dir = data_dir / "quality_reports" / "20250820_123000"
        quality_dir.mkdir(parents=True)
        (quality_dir / "quality_summary.json").write_text('{"quality": "good", "errors": 0}')
        (quality_dir / "quality_summary.md").write_text("# Quality Report\n\nAll tests passed")

        # Semantic results directory
        semantic_dir = data_dir / "llm" / "semantic_results"
        semantic_dir.mkdir(parents=True)
        (semantic_dir / "retrieved_docs_test.json").write_text('{"documents": [], "query": "test"}')

        # Config directory
        config_dir = data_dir / "config"
        config_dir.mkdir()
        (config_dir / "test_config.yml").write_text("database:\n  host: localhost\n  port: 5432")

        # Releases directory
        releases_dir = self.test_project_root / "releases"
        releases_dir.mkdir()

    def test_get_latest_build(self):
        """Test finding the latest build directory."""
        latest_build = self.release_manager.get_latest_build()
        self.assertIsNotNone(latest_build)
        self.assertTrue(latest_build.name.startswith("build_"))
        self.assertEqual(latest_build.name, "build_20250820_123000")

    def test_get_latest_build_no_builds(self):
        """Test behavior when no build directories exist."""
        # Remove build directory
        build_dir = self.test_project_root / "data" / "stage_99_build"
        shutil.rmtree(build_dir)

        latest_build = self.release_manager.get_latest_build()
        self.assertIsNone(latest_build)

    def test_collect_release_artifacts(self):
        """Test artifact collection from build directory."""
        build_path = self.test_project_root / "data" / "stage_99_build" / "build_20250820_123000"
        artifacts = self.release_manager.collect_release_artifacts(build_path)

        # Check artifact categories
        expected_categories = [
            "reports",
            "manifests",
            "quality_reports",
            "llm_responses",
            "semantic_results",
            "configs",
        ]
        for category in expected_categories:
            self.assertIn(category, artifacts)

        # Check specific artifacts
        self.assertEqual(len(artifacts["manifests"]), 2)  # BUILD_MANIFEST.md and .json
        self.assertEqual(len(artifacts["llm_responses"]), 2)  # 2 DCF reports
        self.assertEqual(len(artifacts["quality_reports"]), 2)  # quality summary files
        self.assertEqual(len(artifacts["semantic_results"]), 1)  # 1 semantic result
        self.assertEqual(len(artifacts["configs"]), 1)  # 1 config file

    def test_generate_release_manifest(self):
        """Test release manifest generation."""
        build_path = self.test_project_root / "data" / "stage_99_build" / "build_20250820_123000"
        artifacts = self.release_manager.collect_release_artifacts(build_path)

        manifest = self.release_manager.generate_release_manifest(
            artifacts, "test_release", build_path
        )

        # Check manifest structure
        self.assertIn("release_info", manifest)
        self.assertIn("artifacts", manifest)
        self.assertIn("statistics", manifest)
        self.assertIn("validation", manifest)

        # Check release info
        self.assertEqual(manifest["release_info"]["release_id"], "test_release")
        self.assertIn("timestamp", manifest["release_info"])
        self.assertIn("my_finance_version", manifest["release_info"])

        # Check statistics
        self.assertGreater(manifest["statistics"]["total_files"], 0)
        self.assertGreater(manifest["statistics"]["total_size"], 0)

        # Check validation data
        self.assertIn("file_counts", manifest["validation"])

    def test_create_release_readme(self):
        """Test README creation for releases."""
        manifest = {
            "release_info": {
                "release_id": "test_release",
                "timestamp": "2025-08-20T12:30:00",
                "source_build": "/test/build/path",
                "my_finance_version": "abc123",
            },
            "statistics": {
                "total_files": 10,
                "total_size": 1024,
                "manifests": {"count": 2, "total_size": 100},
                "llm_responses": {"count": 5, "total_size": 500},
            },
        }

        readme_path = self.temp_dir / "test_readme.md"
        self.release_manager.create_release_readme(readme_path, manifest)

        self.assertTrue(readme_path.exists())
        content = readme_path.read_text()

        # Check content
        self.assertIn("My Finance Release test_release", content)
        self.assertIn("Generated on: 2025-08-20T12:30:00", content)
        self.assertIn("Total Files: 10", content)
        self.assertIn("Total Size: 1,024 bytes", content)

    @patch("scripts.release_manager.subprocess.run")
    def test_get_git_commit_hash(self, mock_subprocess):
        """Test git commit hash retrieval."""
        # Mock successful git command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456\n"
        mock_subprocess.return_value = mock_result

        commit_hash = self.release_manager.get_git_commit_hash()
        self.assertEqual(commit_hash, "abc123def456")

        # Mock failed git command
        mock_result.returncode = 1
        commit_hash = self.release_manager.get_git_commit_hash()
        self.assertEqual(commit_hash, "unknown")

    def test_create_release_success(self):
        """Test successful release creation."""
        release_id, manifest = self.release_manager.create_release("test_release")

        # Check release was created
        self.assertEqual(release_id, "test_release")
        self.assertIsInstance(manifest, dict)

        # Check release directory exists
        release_dir = self.test_project_root / "releases" / "release_test_release"
        self.assertTrue(release_dir.exists())

        # Check required files
        self.assertTrue((release_dir / "RELEASE_MANIFEST.json").exists())
        self.assertTrue((release_dir / "README.md").exists())

        # Check artifact directories
        self.assertTrue((release_dir / "manifests").exists())
        self.assertTrue((release_dir / "llm_responses").exists())
        self.assertTrue((release_dir / "configs").exists())

    def test_create_release_no_build(self):
        """Test release creation failure when no builds exist."""
        # Remove build directory
        build_dir = self.test_project_root / "data" / "stage_99_build"
        shutil.rmtree(build_dir)

        with self.assertRaises(ValueError) as context:
            self.release_manager.create_release("test_release")

        self.assertIn("No build directory found", str(context.exception))

    def test_list_releases(self):
        """Test listing available releases."""
        # Initially no releases
        releases = self.release_manager.list_releases()
        self.assertEqual(releases, [])

        # Create a test release
        self.release_manager.create_release("test_release_1")
        self.release_manager.create_release("test_release_2")

        # Check releases are listed
        releases = self.release_manager.list_releases()
        self.assertEqual(len(releases), 2)
        self.assertIn("test_release_1", releases)
        self.assertIn("test_release_2", releases)

        # Check sorted order (most recent first)
        self.assertEqual(releases[0], "test_release_2")
        self.assertEqual(releases[1], "test_release_1")

    def test_validate_release_success(self):
        """Test successful release validation."""
        # Create a release first
        release_id, _ = self.release_manager.create_release("test_release")

        # Validate it
        is_valid = self.release_manager.validate_release(release_id)
        self.assertTrue(is_valid)

    def test_validate_release_missing_directory(self):
        """Test validation failure for missing release directory."""
        is_valid = self.release_manager.validate_release("nonexistent_release")
        self.assertFalse(is_valid)

    def test_validate_release_missing_manifest(self):
        """Test validation failure for missing manifest file."""
        # Create release directory without manifest
        release_dir = self.test_project_root / "releases" / "release_invalid_release"
        release_dir.mkdir(parents=True)
        (release_dir / "README.md").write_text("Test README")

        is_valid = self.release_manager.validate_release("invalid_release")
        self.assertFalse(is_valid)

    def test_validate_release_file_count_mismatch(self):
        """Test validation failure for file count mismatches."""
        # Create a release first
        release_id, _ = self.release_manager.create_release("test_release")

        # Remove a file to cause count mismatch
        release_dir = self.test_project_root / "releases" / f"release_{release_id}"
        llm_dir = release_dir / "llm_responses"
        if llm_dir.exists():
            files = list(llm_dir.glob("*"))
            if files:
                files[0].unlink()

        # Validation should fail
        is_valid = self.release_manager.validate_release(release_id)
        self.assertFalse(is_valid)


class TestReleaseManagerIntegration(unittest.TestCase):
    """Integration tests for release manager workflow."""

    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_project_root = self.temp_dir / "integration_test"
        self.test_project_root.mkdir()

        # Create comprehensive test structure
        self.setup_comprehensive_test_structure()

        self.release_manager = ReleaseManager(self.test_project_root)

    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.temp_dir)

    def setup_comprehensive_test_structure(self):
        """Create comprehensive test structure for integration tests."""
        # Multiple builds
        data_dir = self.test_project_root / "data"

        # Build 1 (older)
        build1_dir = data_dir / "stage_99_build" / "build_20250820_120000"
        build1_dir.mkdir(parents=True)
        (build1_dir / "BUILD_MANIFEST.md").write_text("# Build 1")

        # Build 2 (newer)
        build2_dir = data_dir / "stage_99_build" / "build_20250820_130000"
        build2_dir.mkdir(parents=True)
        (build2_dir / "BUILD_MANIFEST.md").write_text("# Build 2")
        (build2_dir / "BUILD_MANIFEST.json").write_text('{"build_id": "20250820_130000"}')

        # Large number of artifacts
        responses_dir = data_dir / "llm" / "responses"
        responses_dir.mkdir(parents=True)

        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
        for ticker in tickers:
            (responses_dir / f"dcf_en_{ticker}_test.md").write_text(f"DCF for {ticker}")
            (responses_dir / f"dcf_zh_{ticker}_test.md").write_text(f"{ticker} DCF 分析")

        # Quality reports
        quality_dir = data_dir / "quality_reports" / "20250820_130000"
        quality_dir.mkdir(parents=True)
        for stage in ["extract", "transform", "load", "analysis"]:
            (quality_dir / f"stage_{stage}_report.json").write_text(
                f'{{"stage": "{stage}", "status": "completed"}}'
            )
            (quality_dir / f"stage_{stage}_report.md").write_text(
                f"# {stage.title()} Report\\n\\nCompleted successfully"
            )

        # Multiple config files
        config_dir = data_dir / "config"
        config_dir.mkdir()
        configs = ["database.yml", "llm.yml", "etl.yml", "security.yml"]
        for config in configs:
            (config_dir / config).write_text(f"# {config} configuration\\ntest: true")

        # Semantic results
        semantic_dir = data_dir / "llm" / "semantic_results"
        semantic_dir.mkdir(parents=True)
        for ticker in tickers[:3]:  # Just first 3
            (semantic_dir / f"retrieved_docs_{ticker}_test.json").write_text(
                f'{{"ticker": "{ticker}", "docs": []}}'
            )

    def test_end_to_end_release_workflow(self):
        """Test complete release workflow from creation to validation."""
        # Step 1: Create release
        release_id, manifest = self.release_manager.create_release("integration_test_release")

        # Verify release creation
        self.assertIsNotNone(release_id)
        self.assertIsInstance(manifest, dict)

        # Step 2: Verify release structure
        release_dir = self.test_project_root / "releases" / f"release_{release_id}"
        self.assertTrue(release_dir.exists())

        # Check all artifact categories are present
        expected_dirs = [
            "manifests",
            "llm_responses",
            "quality_reports",
            "configs",
            "semantic_results",
        ]
        for dir_name in expected_dirs:
            self.assertTrue((release_dir / dir_name).exists())

        # Step 3: Verify artifact counts
        llm_files = list((release_dir / "llm_responses").glob("*.md"))
        self.assertEqual(len(llm_files), 14)  # 7 tickers * 2 languages

        quality_files = list((release_dir / "quality_reports").glob("*"))
        self.assertEqual(len(quality_files), 8)  # 4 stages * 2 formats

        config_files = list((release_dir / "configs").glob("*.yml"))
        self.assertEqual(len(config_files), 4)  # 4 config files

        # Step 4: List releases
        releases = self.release_manager.list_releases()
        self.assertIn(release_id, releases)

        # Step 5: Validate release
        is_valid = self.release_manager.validate_release(release_id)
        self.assertTrue(is_valid)

        # Step 6: Verify manifest accuracy
        manifest_path = release_dir / "RELEASE_MANIFEST.json"
        with open(manifest_path) as f:
            saved_manifest = json.load(f)

        # Check manifest integrity
        self.assertEqual(saved_manifest["release_info"]["release_id"], release_id)
        self.assertGreater(saved_manifest["statistics"]["total_files"], 20)

        # Verify file counts in manifest match actual files
        for category in ["llm_responses", "quality_reports", "configs"]:
            expected_count = saved_manifest["validation"]["file_counts"][category]
            actual_count = len(list((release_dir / category).glob("*")))
            self.assertEqual(expected_count, actual_count, f"Count mismatch for {category}")

    def test_multiple_releases_management(self):
        """Test managing multiple releases."""
        # Create multiple releases
        release_ids = []
        for i in range(3):
            release_id, _ = self.release_manager.create_release(f"multi_test_release_{i}")
            release_ids.append(release_id)

        # List releases
        releases = self.release_manager.list_releases()
        self.assertEqual(len(releases), 3)

        # Verify all releases are valid
        for release_id in release_ids:
            self.assertTrue(self.release_manager.validate_release(release_id))

        # Check releases are sorted correctly (newest first)
        self.assertEqual(releases[0], "multi_test_release_2")
        self.assertEqual(releases[1], "multi_test_release_1")
        self.assertEqual(releases[2], "multi_test_release_0")

    def test_latest_build_selection(self):
        """Test that the latest build is correctly selected."""
        # Should pick the newer build (build_20250820_130000)
        latest_build = self.release_manager.get_latest_build()
        self.assertEqual(latest_build.name, "build_20250820_130000")

        # Create release and verify it uses the correct build
        release_id, manifest = self.release_manager.create_release("latest_build_test")
        self.assertIn("build_20250820_130000", manifest["release_info"]["source_build"])


class TestReleaseManagerErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def setUp(self):
        """Set up error handling test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_project_root = self.temp_dir / "error_test"
        self.test_project_root.mkdir()

        self.release_manager = ReleaseManager(self.test_project_root)

    def tearDown(self):
        """Clean up error handling test environment."""
        shutil.rmtree(self.temp_dir)

    def test_no_data_directory(self):
        """Test behavior when data directory doesn't exist."""
        latest_build = self.release_manager.get_latest_build()
        self.assertIsNone(latest_build)

        with self.assertRaises(ValueError):
            self.release_manager.create_release("no_data_test")

    def test_empty_artifacts(self):
        """Test release creation with minimal/empty artifacts."""
        # Create minimal structure
        build_dir = self.test_project_root / "data" / "stage_99_build" / "build_20250820_140000"
        build_dir.mkdir(parents=True)
        (build_dir / "BUILD_MANIFEST.md").write_text("# Minimal build")

        # Should still create release successfully
        release_id, manifest = self.release_manager.create_release("minimal_test")

        self.assertIsNotNone(release_id)
        self.assertEqual(manifest["statistics"]["total_files"], 1)  # Just the manifest

    def test_corrupted_manifest_validation(self):
        """Test validation with corrupted manifest files."""
        # Create release directory with corrupted manifest
        release_dir = self.test_project_root / "releases" / "release_corrupted_test"
        release_dir.mkdir(parents=True)

        # Create corrupted JSON
        (release_dir / "RELEASE_MANIFEST.json").write_text("invalid json content")
        (release_dir / "README.md").write_text("Valid README")

        is_valid = self.release_manager.validate_release("corrupted_test")
        self.assertFalse(is_valid)

    def test_permission_errors(self):
        """Test handling of permission errors."""
        # This test would be platform-specific and might not work in all environments
        # For now, we'll mock the scenario
        pass

    def test_large_file_handling(self):
        """Test handling of large files in releases."""
        # Create build with large file
        build_dir = self.test_project_root / "data" / "stage_99_build" / "build_20250820_150000"
        build_dir.mkdir(parents=True)
        (build_dir / "BUILD_MANIFEST.md").write_text("# Large file test")

        # Create large config file
        config_dir = self.test_project_root / "data" / "config"
        config_dir.mkdir(parents=True)
        large_content = "x" * 1024 * 1024  # 1MB file
        (config_dir / "large_config.yml").write_text(large_content)

        # Should handle large files without issues
        release_id, manifest = self.release_manager.create_release("large_file_test")

        self.assertIsNotNone(release_id)
        self.assertGreater(manifest["statistics"]["total_size"], 1024 * 1024)


if __name__ == "__main__":
    # Run tests with detailed output
    unittest.main(verbosity=2)
