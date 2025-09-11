#!/usr/bin/env python3
"""
Unit tests for build_tracker.py - Build Tracking System
Tests build execution tracking, stage management, and artifact generation.
"""

import json
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from common.build.build_tracker import BuildTracker
from common.core.directory_manager import DirectoryManager


@pytest.mark.build
class TestBuildTracker:
    """Test BuildTracker build execution tracking."""

    def test_initialization_with_custom_path(self):
        """Test tracker initialization with custom path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_path = Path(temp_dir) / "custom_build"
            tracker = BuildTracker(base_path=str(build_path))

            assert tracker.build_base_path == build_path
            assert tracker.build_path.exists()
            assert tracker.build_id is not None
            assert len(tracker.build_id) > 0

    def test_initialization_with_default_path(self):
        """Test tracker initialization with default path."""
        with patch.object(DirectoryManager, "get_data_root") as mock_get_root:
            with tempfile.TemporaryDirectory() as temp_dir:
                mock_get_root.return_value = Path(temp_dir)
                tracker = BuildTracker()

                assert tracker.build_base_path.exists()
                assert "stage_04_query_results" in str(tracker.build_base_path)

    def test_build_id_generation(self):
        """Test build ID generation format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = BuildTracker(base_path=str(Path(temp_dir) / "test_build"))
            build_id = tracker._generate_build_id()

            # Should be in format YYYYMMDD_HHMMSS
            assert len(build_id) == 15
            assert "_" in build_id

            # Verify it's a valid timestamp format
            datetime.strptime(build_id, "%Y%m%d_%H%M%S")

    def test_directory_structure_creation(self):
        """Test build directory structure is created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_path = Path(temp_dir) / "test_build"
            tracker = BuildTracker(base_path=str(build_path))

            # Check subdirectories exist
            assert (tracker.build_path / "stage_logs").exists()
            assert (tracker.build_path / "artifacts").exists()

    def test_manifest_initialization(self):
        """Test build manifest is properly initialized."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = BuildTracker(base_path=str(Path(temp_dir) / "test_build"))

            manifest = tracker.manifest

            # Check build_info structure
            assert "build_info" in manifest
            assert manifest["build_info"]["build_id"] == tracker.build_id
            assert manifest["build_info"]["status"] == "in_progress"
            assert manifest["build_info"]["start_time"] is not None

            # Check stages structure
            assert "stages" in manifest
            expected_stages = [
                "stage_01_extract",
                "stage_02_transform",
                "stage_03_load",
                "stage_04_analysis",
                "stage_05_reporting",
            ]

            for stage in expected_stages:
                assert stage in manifest["stages"]
                assert manifest["stages"][stage]["status"] == "pending"

            # Check other sections
            assert "data_partitions" in manifest
            assert "real_outputs" in manifest
            assert "statistics" in manifest


@pytest.mark.build
class TestBuildStageManagement:
    """Test build stage management operations."""

    @pytest.fixture
    def tracker(self):
        """Create tracker for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_path = Path(temp_dir) / "test_build"
            yield BuildTracker(base_path=str(build_path))

    def test_start_build(self, tracker):
        """Test build start process."""
        with patch.object(tracker, "_save_manifest") as mock_save:
            with patch.object(tracker, "_update_latest_symlink") as mock_symlink:
                build_id = tracker.start_build("test_config", "test command")

                assert build_id == tracker.build_id
                assert tracker.manifest["build_info"]["configuration"] == "test_config"
                assert tracker.manifest["build_info"]["command"] == "test command"

                mock_save.assert_called_once()
                mock_symlink.assert_called_once()

    def test_start_stage(self, tracker):
        """Test stage start process."""
        stage = "stage_01_extract"

        with patch.object(tracker, "_save_manifest") as mock_save:
            tracker.start_stage(stage)

            stage_info = tracker.manifest["stages"][stage]
            assert stage_info["status"] == "in_progress"
            assert stage_info["start_time"] is not None

            mock_save.assert_called_once()

    def test_start_invalid_stage(self, tracker):
        """Test starting invalid stage raises error."""
        with pytest.raises(ValueError, match="Unknown stage"):
            tracker.start_stage("invalid_stage")

    def test_complete_stage(self, tracker):
        """Test stage completion."""
        stage = "stage_01_extract"
        artifacts = ["artifact1.json", "artifact2.txt"]

        # Start stage first
        tracker.start_stage(stage)

        with patch.object(tracker, "_save_manifest") as mock_save:
            tracker.complete_stage(
                stage=stage, partition="20250101", artifacts=artifacts, file_count=10
            )

            stage_info = tracker.manifest["stages"][stage]
            assert stage_info["status"] == "completed"
            assert stage_info["end_time"] is not None
            assert artifacts[0] in stage_info["artifacts"]
            assert artifacts[1] in stage_info["artifacts"]
            assert stage_info["file_count"] == 10

            # Check partition update
            assert tracker.manifest["data_partitions"]["extract_partition"] == "20250101"

            mock_save.assert_called_once()

    def test_fail_stage(self, tracker):
        """Test stage failure handling."""
        stage = "stage_02_transform"
        error_message = "Transform failed"

        with patch.object(tracker, "_save_manifest") as mock_save:
            tracker.fail_stage(stage, error_message)

            stage_info = tracker.manifest["stages"][stage]
            assert stage_info["status"] == "failed"
            assert stage_info["end_time"] is not None

            # Check error recorded
            errors = tracker.manifest["statistics"]["errors"]
            assert len(errors) == 1
            assert errors[0]["stage"] == stage
            assert errors[0]["error"] == error_message

            mock_save.assert_called_once()

    def test_add_warning(self, tracker):
        """Test warning addition."""
        stage = "stage_03_load"
        warning_message = "Load warning"

        with patch.object(tracker, "_save_manifest") as mock_save:
            tracker.add_warning(stage, warning_message)

            warnings = tracker.manifest["statistics"]["warnings"]
            assert len(warnings) == 1
            assert warnings[0]["stage"] == stage
            assert warnings[0]["warning"] == warning_message

            mock_save.assert_called_once()


@pytest.mark.build
class TestBuildArtifactManagement:
    """Test build artifact management."""

    @pytest.fixture
    def tracker(self):
        """Create tracker for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_path = Path(temp_dir) / "test_build"
            yield BuildTracker(base_path=str(build_path))

    def test_log_stage_output(self, tracker):
        """Test stage output logging."""
        stage = "stage_01_extract"
        log_content = "Test log content\nMultiple lines\nWith data"

        tracker.log_stage_output(stage, log_content)

        log_file = tracker.build_path / "stage_logs" / f"{stage}.log"
        assert log_file.exists()

        # Check content was written
        content = log_file.read_text(encoding="utf-8")
        assert log_content in content
        assert datetime.now().strftime("%Y-%m-%d") in content  # Timestamp

    def test_save_artifact_json(self, tracker):
        """Test saving JSON artifact."""
        stage = "stage_02_transform"
        artifact_name = "config.json"
        content = {"key": "value", "numbers": [1, 2, 3]}

        with patch.object(tracker, "_save_manifest") as mock_save:
            artifact_path = tracker.save_artifact(stage, artifact_name, content)

            # Check file was created
            artifact_file = Path(artifact_path)
            assert artifact_file.exists()

            # Check content
            with open(artifact_file, "r", encoding="utf-8") as f:
                loaded_content = json.load(f)
            assert loaded_content == content

            # Check manifest updated
            assert artifact_name in tracker.manifest["stages"][stage]["artifacts"]

            mock_save.assert_called_once()

    def test_save_artifact_text(self, tracker):
        """Test saving text artifact."""
        stage = "stage_03_load"
        artifact_name = "log.txt"
        content = "Test text content\nWith multiple lines"

        with patch.object(tracker, "_save_manifest") as mock_save:
            artifact_path = tracker.save_artifact(stage, artifact_name, content)

            # Check file was created
            artifact_file = Path(artifact_path)
            assert artifact_file.exists()

            # Check content
            assert artifact_file.read_text(encoding="utf-8") == content

    def test_save_artifact_binary(self, tracker):
        """Test saving binary artifact."""
        stage = "stage_04_analysis"
        artifact_name = "data.bin"
        content = b"Binary data content"

        with patch.object(tracker, "_save_manifest") as mock_save:
            artifact_path = tracker.save_artifact(stage, artifact_name, content)

            # Check file was created
            artifact_file = Path(artifact_path)
            assert artifact_file.exists()

            # Check content
            assert artifact_file.read_bytes() == content


@pytest.mark.build
class TestBuildOutputTracking:
    """Test build output tracking and scanning."""

    @pytest.fixture
    def tracker_with_outputs(self):
        """Create tracker with mock output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_path = Path(temp_dir) / "test_build"
            tracker = BuildTracker(base_path=str(build_path))

            # Create mock output structure
            base_path = tracker.base_path

            # YFinance files
            yfinance_dir = base_path / "original" / "yfinance" / "AAPL"
            yfinance_dir.mkdir(parents=True, exist_ok=True)
            (yfinance_dir / "AAPL_m7_daily_20250101.json").write_text('{"test": "data"}')
            (yfinance_dir / "AAPL_m7_daily_20250102.json").write_text('{"test": "data"}')

            # SEC Edgar files
            sec_dir = base_path / "original" / "sec_edgar" / "MSFT"
            sec_dir.mkdir(parents=True, exist_ok=True)
            (sec_dir / "MSFT_10K_20240101.json").write_text('{"test": "sec_data"}')

            # DCF reports
            reports_dir = base_path / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            (reports_dir / "M7_DCF_Report_20250101.md").write_text("# DCF Report")

            yield tracker

    def test_track_real_output(self, tracker_with_outputs):
        """Test tracking real output files."""
        file_paths = ["file1.json", "file2.json", "file1.json"]  # Include duplicate

        with patch.object(tracker_with_outputs, "_save_manifest") as mock_save:
            tracker_with_outputs.track_real_output("yfinance_files", file_paths)

            outputs = tracker_with_outputs.manifest["real_outputs"]["yfinance_files"]
            assert len(outputs) == 2  # Duplicates removed
            assert "file1.json" in outputs
            assert "file2.json" in outputs

            mock_save.assert_called_once()

    def test_scan_and_track_outputs(self, tracker_with_outputs):
        """Test scanning filesystem for outputs."""
        with patch.object(tracker_with_outputs, "_save_manifest") as mock_save:
            tracker_with_outputs.scan_and_track_outputs()

            real_outputs = tracker_with_outputs.manifest["real_outputs"]

            # Check YFinance files found
            assert len(real_outputs["yfinance_files"]) == 2
            assert any(
                "AAPL_m7_daily_20250101.json" in path for path in real_outputs["yfinance_files"]
            )

            # Check SEC files found
            assert len(real_outputs["sec_edgar_files"]) == 1
            assert any("MSFT_10K_20240101.json" in path for path in real_outputs["sec_edgar_files"])

            # Check DCF reports found
            assert len(real_outputs["dcf_reports"]) == 1
            assert any("M7_DCF_Report_20250101.md" in path for path in real_outputs["dcf_reports"])

            # Check statistics updated
            assert (
                tracker_with_outputs.manifest["statistics"]["files_processed"] == 3
            )  # 2 yfinance + 1 sec

            mock_save.assert_called_once()


@pytest.mark.build
class TestBuildCompletion:
    """Test build completion and reporting."""

    @pytest.fixture
    def tracker(self):
        """Create tracker for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_path = Path(temp_dir) / "test_build"
            yield BuildTracker(base_path=str(build_path))

    def test_complete_build(self, tracker):
        """Test build completion process."""
        with patch.object(tracker, "_save_manifest") as mock_save:
            with patch.object(tracker, "_generate_build_report") as mock_report:
                tracker.complete_build("completed")

                assert tracker.manifest["build_info"]["status"] == "completed"
                assert tracker.manifest["build_info"]["end_time"] is not None

                mock_save.assert_called_once()
                mock_report.assert_called_once()

    def test_save_manifest(self, tracker):
        """Test manifest saving."""
        tracker._save_manifest()

        manifest_file = tracker.build_path / "BUILD_MANIFEST.json"
        assert manifest_file.exists()

        # Check content can be loaded
        with open(manifest_file, "r", encoding="utf-8") as f:
            loaded_manifest = json.load(f)

        assert loaded_manifest["build_info"]["build_id"] == tracker.build_id

    def test_generate_build_report(self, tracker):
        """Test build report generation."""
        # Set up some test data
        tracker.manifest["build_info"]["configuration"] = "test_config"
        tracker.manifest["build_info"]["command"] = "test command"
        tracker.manifest["build_info"]["end_time"] = datetime.now().isoformat()

        with patch.object(tracker, "_copy_sec_dcf_documentation", return_value=True):
            tracker._generate_build_report()

            report_file = tracker.build_path / "BUILD_MANIFEST.md"
            assert report_file.exists()

            content = report_file.read_text(encoding="utf-8")
            assert f"Build Report: {tracker.build_id}" in content
            assert "test_config" in content
            assert "test command" in content
            assert "SEC DCF Integration Process" in content

    def test_get_build_status(self, tracker):
        """Test build status summary."""
        # Complete some stages
        tracker.start_stage("stage_01_extract")
        tracker.complete_stage("stage_01_extract")
        tracker.fail_stage("stage_02_transform", "Test error")
        tracker.add_warning("stage_03_load", "Test warning")

        status = tracker.get_build_status()

        assert status["build_id"] == tracker.build_id
        assert status["stages_completed"] == 1
        assert status["total_stages"] == 5
        assert status["errors"] == 1
        assert status["warnings"] == 1

        # Check dataset summary
        assert "dataset_summary" in status
        assert "build_info" in status
        assert "directory_structure" in status

    def test_calculate_duration(self, tracker):
        """Test duration calculation."""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1, minutes=30, seconds=45)

        tracker.manifest["build_info"]["start_time"] = start_time.isoformat()
        tracker.manifest["build_info"]["end_time"] = end_time.isoformat()

        duration = tracker._calculate_duration()
        assert duration == "1h 30m 45s"

        # Test minutes only
        end_time = start_time + timedelta(minutes=5, seconds=30)
        tracker.manifest["build_info"]["end_time"] = end_time.isoformat()

        duration = tracker._calculate_duration()
        assert duration == "5m 30s"

        # Test seconds only
        end_time = start_time + timedelta(seconds=45)
        tracker.manifest["build_info"]["end_time"] = end_time.isoformat()

        duration = tracker._calculate_duration()
        assert duration == "45s"


@pytest.mark.build
class TestBuildTrackerClassMethods:
    """Test BuildTracker class methods."""

    def test_get_latest_build_exists(self):
        """Test getting latest build when it exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test build structure
            project_root = Path(temp_dir)
            common_dir = project_root / "common"
            common_dir.mkdir()

            data_dir = project_root / "data"
            build_dir = data_dir / "stage_99_build" / "build_20250101_120000"
            build_dir.mkdir(parents=True)

            # Create manifest
            manifest = {"build_info": {"build_id": "20250101_120000", "status": "completed"}}
            manifest_file = build_dir / "BUILD_MANIFEST.json"
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump(manifest, f)

            # Create symlink
            latest_link = common_dir / "latest_build"
            latest_link.symlink_to(build_dir)

            # Test retrieval
            with patch("common.build.build_tracker.Path.cwd", return_value=project_root):
                with patch(
                    "common.build.build_tracker.__file__",
                    str(project_root / "common" / "build" / "build_tracker.py"),
                ):
                    latest_tracker = BuildTracker.get_latest_build(base_path=str(data_dir))

                    assert latest_tracker is not None
                    assert latest_tracker.build_id == "20250101_120000"
                    assert latest_tracker.manifest["build_info"]["status"] == "completed"

    def test_get_latest_build_not_exists(self):
        """Test getting latest build when it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            data_dir = project_root / "data"

            with patch("common.build.build_tracker.Path.cwd", return_value=project_root):
                with patch(
                    "common.build.build_tracker.__file__",
                    str(project_root / "common" / "build" / "build_tracker.py"),
                ):
                    latest_tracker = BuildTracker.get_latest_build(base_path=str(data_dir))

                    assert latest_tracker is None


@pytest.mark.integration
class TestBuildTrackerIntegration:
    """Integration tests for BuildTracker."""

    def test_complete_build_workflow(self):
        """Test complete build tracking workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_path = Path(temp_dir) / "integration_test"
            tracker = BuildTracker(base_path=str(build_path))

            # Start build
            build_id = tracker.start_build("integration_config", "pytest integration")
            assert build_id == tracker.build_id

            # Execute stages
            stages = ["stage_01_extract", "stage_02_transform", "stage_03_load"]

            for i, stage in enumerate(stages):
                # Start stage
                tracker.start_stage(stage)
                assert tracker.manifest["stages"][stage]["status"] == "in_progress"

                # Log some output
                tracker.log_stage_output(stage, f"Processing stage {i+1}")

                # Save artifact
                artifact_path = tracker.save_artifact(stage, f"result_{i}.json", {"stage": i})
                assert Path(artifact_path).exists()

                # Complete stage
                tracker.complete_stage(stage, partition=f"2025010{i+1}", file_count=i * 10)
                assert tracker.manifest["stages"][stage]["status"] == "completed"

            # Add some warnings and errors
            tracker.add_warning("stage_04_analysis", "Analysis warning")
            tracker.fail_stage("stage_05_reporting", "Reporting failed")

            # Track some outputs
            tracker.track_real_output("test_files", ["file1.txt", "file2.txt"])

            # Complete build
            tracker.complete_build("completed_with_errors")

            # Verify final state
            status = tracker.get_build_status()
            assert status["status"] == "completed_with_errors"
            assert status["stages_completed"] == 3
            assert status["errors"] == 1
            assert status["warnings"] == 1

            # Verify files created
            assert (tracker.build_path / "BUILD_MANIFEST.json").exists()
            assert (tracker.build_path / "BUILD_MANIFEST.md").exists()
            assert (tracker.build_path / "stage_logs").exists()
            assert (tracker.build_path / "artifacts").exists()
