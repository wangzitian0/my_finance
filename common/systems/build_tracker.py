#!/usr/bin/env python3
"""
Build tracking system for ETL pipeline executions.
Tracks every build execution with comprehensive manifests and logs.

Issue #184: Moved to systems/ as part of library restructuring
Refactored from oversized module (857 lines) into focused components
"""

import json
import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.directory_manager import DataLayer, DirectoryManager

logger = logging.getLogger(__name__)

# Try to import quality reporter, handle gracefully if not available
try:
    from .quality_reporter import QUALITY_REPORTING_AVAILABLE, setup_quality_reporter
except ImportError:
    QUALITY_REPORTING_AVAILABLE = False

    def setup_quality_reporter(build_id: str, tier_name: str):
        return None


class BuildTracker:
    """
    Enhanced build tracking system with focused responsibilities.

    Responsibilities:
    - Track build execution lifecycle
    - Generate build manifests
    - Manage build artifacts
    - Coordinate with quality reporting
    """

    def __init__(self, base_path: str = None):
        # Use DirectoryManager for SSOT directory management
        self.directory_manager = DirectoryManager()

        if base_path is None:
            # Get build_data root path and add stage_04_query_results (maps stage_99_build)
            data_root = self.directory_manager.get_data_root()
            self.base_path = data_root
            self.build_base_path = data_root / "stage_04_query_results"
        else:
            self.base_path = Path(base_path).parent
            self.build_base_path = Path(base_path)
        self.build_base_path.mkdir(parents=True, exist_ok=True)

        self.build_id = self._generate_build_id()
        self.build_path = self.build_base_path / f"build_{self.build_id}"
        self.build_path.mkdir(exist_ok=True)

        # Create subdirectories
        (self.build_path / "stage_logs").mkdir(exist_ok=True)
        (self.build_path / "quality_reports").mkdir(exist_ok=True)
        (self.build_path / "artifacts").mkdir(exist_ok=True)

        # Initialize build manifest
        self.manifest = self._initialize_manifest()

        # Setup quality reporter if available
        self.quality_reporter = None
        if QUALITY_REPORTING_AVAILABLE:
            self.quality_reporter = setup_quality_reporter(self.build_id, "build")

        logger.info(f"BuildTracker initialized with build_id: {self.build_id}")

    def _generate_build_id(self) -> str:
        """Generate unique build ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"{timestamp}_{short_uuid}"

    def _initialize_manifest(self) -> Dict[str, Any]:
        """Initialize build manifest with basic information"""
        return {
            "build_id": self.build_id,
            "start_time": datetime.now().isoformat(),
            "build_path": str(self.build_path),
            "status": "started",
            "stages": {},
            "artifacts": {},
            "quality_metrics": {},
            "errors": [],
            "metadata": {
                "tracker_version": "2.0.0",
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                "working_directory": str(Path.cwd()),
            },
        }

    def start_stage(self, stage_name: str, stage_config: Dict[str, Any] = None) -> str:
        """
        Start tracking a new stage.

        Args:
            stage_name: Name of the stage
            stage_config: Configuration for the stage

        Returns:
            Stage ID for tracking
        """
        stage_id = f"{stage_name}_{datetime.now().strftime('%H%M%S')}"

        stage_info = {
            "stage_id": stage_id,
            "stage_name": stage_name,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "config": stage_config or {},
            "outputs": {},
            "metrics": {},
            "errors": [],
        }

        self.manifest["stages"][stage_id] = stage_info
        self._save_manifest()

        logger.info(f"Started stage: {stage_name} (ID: {stage_id})")
        return stage_id

    def complete_stage(
        self, stage_id: str, outputs: Dict[str, Any] = None, metrics: Dict[str, Any] = None
    ) -> None:
        """
        Mark a stage as completed.

        Args:
            stage_id: Stage ID returned from start_stage
            outputs: Stage outputs
            metrics: Stage performance metrics
        """
        if stage_id not in self.manifest["stages"]:
            logger.error(f"Stage ID {stage_id} not found")
            return

        stage_info = self.manifest["stages"][stage_id]
        stage_info.update(
            {
                "end_time": datetime.now().isoformat(),
                "status": "completed",
                "outputs": outputs or {},
                "metrics": metrics or {},
            }
        )

        # Calculate duration
        start_time = datetime.fromisoformat(stage_info["start_time"])
        end_time = datetime.fromisoformat(stage_info["end_time"])
        stage_info["duration_seconds"] = (end_time - start_time).total_seconds()

        self._save_manifest()
        logger.info(
            f"Completed stage: {stage_info['stage_name']} (Duration: {stage_info['duration_seconds']:.2f}s)"
        )

    def fail_stage(self, stage_id: str, error: str, error_details: Dict[str, Any] = None) -> None:
        """
        Mark a stage as failed.

        Args:
            stage_id: Stage ID
            error: Error message
            error_details: Additional error details
        """
        if stage_id not in self.manifest["stages"]:
            logger.error(f"Stage ID {stage_id} not found")
            return

        stage_info = self.manifest["stages"][stage_id]
        stage_info.update(
            {
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "error": error,
                "error_details": error_details or {},
            }
        )

        # Calculate duration
        start_time = datetime.fromisoformat(stage_info["start_time"])
        end_time = datetime.fromisoformat(stage_info["end_time"])
        stage_info["duration_seconds"] = (end_time - start_time).total_seconds()

        # Add to build-level errors
        self.manifest["errors"].append(
            {
                "stage_id": stage_id,
                "stage_name": stage_info["stage_name"],
                "error": error,
                "timestamp": stage_info["end_time"],
            }
        )

        self._save_manifest()
        logger.error(f"Failed stage: {stage_info['stage_name']} - {error}")

    def add_artifact(
        self,
        artifact_name: str,
        artifact_path: str,
        artifact_type: str = "file",
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        Register a build artifact.

        Args:
            artifact_name: Name of the artifact
            artifact_path: Path to the artifact
            artifact_type: Type of artifact (file, directory, url, etc.)
            metadata: Additional artifact metadata
        """
        artifact_info = {
            "name": artifact_name,
            "path": str(artifact_path),
            "type": artifact_type,
            "created_time": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        # Add file size if it's a file
        if artifact_type == "file" and Path(artifact_path).exists():
            artifact_info["size_bytes"] = Path(artifact_path).stat().st_size

        self.manifest["artifacts"][artifact_name] = artifact_info
        self._save_manifest()

        logger.info(f"Registered artifact: {artifact_name} at {artifact_path}")

    def update_quality_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update build-level quality metrics"""
        self.manifest["quality_metrics"].update(metrics)
        self._save_manifest()

    def complete_build(self, status: str = "completed") -> Dict[str, Any]:
        """
        Mark the entire build as completed.

        Args:
            status: Final build status (completed, failed, cancelled)

        Returns:
            Complete build manifest
        """
        self.manifest.update({"end_time": datetime.now().isoformat(), "status": status})

        # Calculate total duration
        start_time = datetime.fromisoformat(self.manifest["start_time"])
        end_time = datetime.fromisoformat(self.manifest["end_time"])
        self.manifest["total_duration_seconds"] = (end_time - start_time).total_seconds()

        # Generate summary statistics
        self.manifest["summary"] = self._generate_build_summary()

        self._save_manifest()

        logger.info(f"Build {self.build_id} completed with status: {status}")
        logger.info(f"Total duration: {self.manifest['total_duration_seconds']:.2f} seconds")

        return self.manifest

    def _generate_build_summary(self) -> Dict[str, Any]:
        """Generate build summary statistics"""
        stages = self.manifest["stages"]

        summary = {
            "total_stages": len(stages),
            "completed_stages": len([s for s in stages.values() if s["status"] == "completed"]),
            "failed_stages": len([s for s in stages.values() if s["status"] == "failed"]),
            "total_artifacts": len(self.manifest["artifacts"]),
            "total_errors": len(self.manifest["errors"]),
        }

        # Calculate average stage duration for completed stages
        completed_durations = [
            s["duration_seconds"]
            for s in stages.values()
            if s["status"] == "completed" and "duration_seconds" in s
        ]

        if completed_durations:
            summary["average_stage_duration"] = sum(completed_durations) / len(completed_durations)
            summary["longest_stage_duration"] = max(completed_durations)
            summary["shortest_stage_duration"] = min(completed_durations)

        return summary

    def _save_manifest(self) -> None:
        """Save the current manifest to disk"""
        manifest_path = self.build_path / "build_manifest.json"
        try:
            with open(manifest_path, "w") as f:
                json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")

    def get_build_info(self) -> Dict[str, Any]:
        """Get current build information"""
        return {
            "build_id": self.build_id,
            "build_path": str(self.build_path),
            "status": self.manifest["status"],
            "stage_count": len(self.manifest["stages"]),
            "artifact_count": len(self.manifest["artifacts"]),
            "error_count": len(self.manifest["errors"]),
        }

    def cleanup_build(self, keep_artifacts: bool = True) -> None:
        """
        Clean up build directory.

        Args:
            keep_artifacts: Whether to preserve artifacts
        """
        if keep_artifacts:
            # Only remove logs and temporary files
            logs_path = self.build_path / "stage_logs"
            if logs_path.exists():
                shutil.rmtree(logs_path)
        else:
            # Remove entire build directory
            if self.build_path.exists():
                shutil.rmtree(self.build_path)

        logger.info(f"Cleaned up build {self.build_id}")
