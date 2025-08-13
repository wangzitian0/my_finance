#!/usr/bin/env python3
"""
Build tracking system for ETL pipeline executions.
Tracks every build execution with comprehensive manifests and logs.
"""

import json
import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BuildTracker:
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Use project root relative path
            project_root = Path(__file__).parent.parent
            base_path = project_root / "data"
        self.base_path = Path(base_path)
        self.build_base_path = self.base_path / "stage_99_build"
        self.build_base_path.mkdir(exist_ok=True)

        self.build_id = self._generate_build_id()
        self.build_path = self.build_base_path / f"build_{self.build_id}"
        self.build_path.mkdir(exist_ok=True)

        # Create subdirectories
        (self.build_path / "stage_logs").mkdir(exist_ok=True)
        (self.build_path / "artifacts").mkdir(exist_ok=True)

        self.manifest = {
            "build_info": {
                "build_id": self.build_id,
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "status": "in_progress",
                "configuration": None,
                "command": None,
            },
            "stages": {
                "stage_01_extract": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "file_count": 0,
                },
                "stage_02_transform": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "file_count": 0,
                },
                "stage_03_load": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "file_count": 0,
                },
                "stage_04_analysis": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "companies_analyzed": 0,
                },
                "stage_05_reporting": {
                    "status": "pending",
                    "start_time": None,
                    "end_time": None,
                    "artifacts": [],
                    "reports_generated": 0,
                },
            },
            "data_partitions": {
                "extract_partition": None,
                "transform_partition": None,
                "load_partition": None,
            },
            "real_outputs": {
                "yfinance_files": [],
                "sec_edgar_files": [],
                "dcf_reports": [],
                "graph_rag_outputs": [],
            },
            "statistics": {
                "files_processed": 0,
                "companies_processed": 0,
                "errors": [],
                "warnings": [],
            },
        }

    def _generate_build_id(self) -> str:
        """Generate unique build ID with timestamp"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def start_build(self, config_name: str, command: str) -> str:
        """Start a new build execution"""
        logger.info(f"Starting build {self.build_id} with config: {config_name}")

        self.manifest["build_info"]["configuration"] = config_name
        self.manifest["build_info"]["command"] = command

        self._save_manifest()
        self._update_latest_symlink()

        return self.build_id

    def start_stage(self, stage: str) -> None:
        """Mark a stage as started"""
        if stage not in self.manifest["stages"]:
            raise ValueError(f"Unknown stage: {stage}")

        logger.info(f"Starting stage: {stage}")
        self.manifest["stages"][stage]["status"] = "in_progress"
        self.manifest["stages"][stage]["start_time"] = datetime.now().isoformat()

        self._save_manifest()

    def complete_stage(
        self,
        stage: str,
        partition: Optional[str] = None,
        artifacts: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        """Mark a stage as completed with optional metadata"""
        if stage not in self.manifest["stages"]:
            raise ValueError(f"Unknown stage: {stage}")

        logger.info(f"Completing stage: {stage}")
        self.manifest["stages"][stage]["status"] = "completed"
        self.manifest["stages"][stage]["end_time"] = datetime.now().isoformat()

        if artifacts:
            self.manifest["stages"][stage]["artifacts"].extend(artifacts)

        # Update stage-specific metadata
        for key, value in kwargs.items():
            if key in self.manifest["stages"][stage]:
                self.manifest["stages"][stage][key] = value

        # Update partition info
        if partition:
            if stage == "stage_01_extract":
                self.manifest["data_partitions"]["extract_partition"] = partition
            elif stage == "stage_02_transform":
                self.manifest["data_partitions"]["transform_partition"] = partition
            elif stage == "stage_03_load":
                self.manifest["data_partitions"]["load_partition"] = partition

        self._save_manifest()

    def fail_stage(self, stage: str, error_message: str) -> None:
        """Mark a stage as failed"""
        if stage not in self.manifest["stages"]:
            raise ValueError(f"Unknown stage: {stage}")

        logger.error(f"Stage {stage} failed: {error_message}")
        self.manifest["stages"][stage]["status"] = "failed"
        self.manifest["stages"][stage]["end_time"] = datetime.now().isoformat()
        self.manifest["statistics"]["errors"].append(
            {"stage": stage, "error": error_message, "timestamp": datetime.now().isoformat()}
        )

        self._save_manifest()

    def add_warning(self, stage: str, warning_message: str) -> None:
        """Add a warning to the build"""
        logger.warning(f"Stage {stage} warning: {warning_message}")
        self.manifest["statistics"]["warnings"].append(
            {"stage": stage, "warning": warning_message, "timestamp": datetime.now().isoformat()}
        )

        self._save_manifest()

    def log_stage_output(self, stage: str, log_content: str) -> None:
        """Save stage execution logs"""
        log_file = self.build_path / "stage_logs" / f"{stage}.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}]\n")
            f.write(log_content)
            f.write("\n\n")

    def save_artifact(self, stage: str, artifact_name: str, content: Any) -> str:
        """Save build artifacts (configs, intermediate results, etc.)"""
        artifact_path = self.build_path / "artifacts" / f"{stage}_{artifact_name}"

        if isinstance(content, (dict, list)):
            with open(artifact_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
        elif isinstance(content, str):
            with open(artifact_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # Binary content
            with open(artifact_path, "wb") as f:
                f.write(content)

        # Add to manifest
        self.manifest["stages"][stage]["artifacts"].append(artifact_name)
        self._save_manifest()

        return str(artifact_path)

    def track_real_output(self, output_type: str, file_paths: List[str]) -> None:
        """Track real output files generated during build"""
        if output_type not in self.manifest["real_outputs"]:
            self.manifest["real_outputs"][output_type] = []

        # Add new files, avoiding duplicates
        for file_path in file_paths:
            if file_path not in self.manifest["real_outputs"][output_type]:
                self.manifest["real_outputs"][output_type].append(file_path)

        logger.info(f"Tracked {len(file_paths)} {output_type} files")
        self._save_manifest()

    def scan_and_track_outputs(self) -> None:
        """Scan filesystem for actual outputs and track them"""
        base_path = Path(self.base_path)

        # Track YFinance files
        yfinance_files = []
        yfinance_dir = base_path / "original" / "yfinance"
        if yfinance_dir.exists():
            for ticker_dir in yfinance_dir.iterdir():
                if ticker_dir.is_dir():
                    for json_file in ticker_dir.glob("*m7_daily*.json"):
                        yfinance_files.append(str(json_file.relative_to(base_path)))

        # Track SEC Edgar files
        sec_files = []
        sec_dir = base_path / "original" / "sec_edgar"
        if sec_dir.exists():
            for ticker_dir in sec_dir.iterdir():
                if ticker_dir.is_dir():
                    for json_file in ticker_dir.glob("*.json"):
                        sec_files.append(str(json_file.relative_to(base_path)))

        # Track DCF reports
        dcf_reports = []
        reports_dir = base_path / "reports"
        if reports_dir.exists():
            for report_file in reports_dir.glob("M7_DCF_Report_*.md"):
                dcf_reports.append(str(report_file.relative_to(base_path)))

        # Update manifest
        self.manifest["real_outputs"]["yfinance_files"] = yfinance_files
        self.manifest["real_outputs"]["sec_edgar_files"] = sec_files
        self.manifest["real_outputs"]["dcf_reports"] = dcf_reports

        # Update statistics
        self.manifest["statistics"]["files_processed"] = len(yfinance_files) + len(sec_files)

        logger.info(
            f"Scanned outputs: {len(yfinance_files)} YFinance, {len(sec_files)} SEC, {len(dcf_reports)} reports"
        )
        self._save_manifest()

    def complete_build(self, status: str = "completed") -> None:
        """Complete the build execution"""
        logger.info(f"Completing build {self.build_id} with status: {status}")

        self.manifest["build_info"]["status"] = status
        self.manifest["build_info"]["end_time"] = datetime.now().isoformat()

        self._save_manifest()
        self._generate_build_report()

    def _save_manifest(self) -> None:
        """Save the build manifest to file"""
        manifest_path = self.build_path / "BUILD_MANIFEST.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2)

    def _generate_build_report(self) -> None:
        """Generate human-readable build report"""
        report_path = self.build_path / "BUILD_MANIFEST.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Build Report: {self.build_id}\n\n")

            # Build Info
            f.write("## Build Information\n\n")
            f.write(f"- **Build ID**: {self.manifest['build_info']['build_id']}\n")
            f.write(f"- **Configuration**: {self.manifest['build_info']['configuration']}\n")
            f.write(f"- **Command**: `{self.manifest['build_info']['command']}`\n")
            f.write(f"- **Status**: {self.manifest['build_info']['status']}\n")
            f.write(f"- **Start Time**: {self.manifest['build_info']['start_time']}\n")
            f.write(f"- **End Time**: {self.manifest['build_info']['end_time']}\n\n")

            # Stage Information
            f.write("## ETL Stages\n\n")
            for stage, info in self.manifest["stages"].items():
                f.write(f"### {stage}\n\n")
                f.write(f"- **Status**: {info['status']}\n")
                f.write(f"- **Start Time**: {info['start_time']}\n")
                f.write(f"- **End Time**: {info['end_time']}\n")
                f.write(f"- **Artifacts**: {len(info['artifacts'])} files\n")

                if info["artifacts"]:
                    f.write("  - " + "\n  - ".join(info["artifacts"]) + "\n")
                f.write("\n")

            # Data Partitions
            f.write("## Data Partitions\n\n")
            for partition_type, partition_date in self.manifest["data_partitions"].items():
                if partition_date:
                    f.write(f"- **{partition_type}**: `{partition_date}`\n")
            f.write("\n")

            # Statistics
            f.write("## Statistics\n\n")
            f.write(f"- **Files Processed**: {self.manifest['statistics']['files_processed']}\n")
            f.write(f"- **Errors**: {len(self.manifest['statistics']['errors'])}\n")
            f.write(f"- **Warnings**: {len(self.manifest['statistics']['warnings'])}\n\n")

            # Errors
            if self.manifest["statistics"]["errors"]:
                f.write("### Errors\n\n")
                for error in self.manifest["statistics"]["errors"]:
                    f.write(f"- **{error['stage']}** ({error['timestamp']}): {error['error']}\n")
                f.write("\n")

            # Warnings
            if self.manifest["statistics"]["warnings"]:
                f.write("### Warnings\n\n")
                for warning in self.manifest["statistics"]["warnings"]:
                    f.write(
                        f"- **{warning['stage']}** ({warning['timestamp']}): {warning['warning']}\n"
                    )
                f.write("\n")

            # File Locations
            f.write("## File Locations\n\n")
            f.write(f"- **Build Directory**: `{self.build_path.relative_to(Path.cwd())}`\n")
            f.write(f"- **Stage Logs**: `{self.build_path.relative_to(Path.cwd())}/stage_logs/`\n")
            f.write(f"- **Artifacts**: `{self.build_path.relative_to(Path.cwd())}/artifacts/`\n\n")

            # Copy SEC DCF Integration Process documentation and add reference
            sec_doc_copied = self._copy_sec_dcf_documentation()
            if sec_doc_copied:
                f.write("## 📋 SEC DCF Integration Process\n\n")
                f.write("This build includes comprehensive documentation of how SEC filings are integrated into DCF analysis:\n\n")
                f.write("- **Documentation**: [`SEC_DCF_Integration_Process.md`](./SEC_DCF_Integration_Process.md)\n")
                f.write("- **Process Overview**: Detailed explanation of the ETL pipeline and semantic retrieval system\n")
                f.write("- **Build Integration**: Shows how SEC data flows through the system into final DCF reports\n\n")
            
            # Generated Information
            f.write("---\n")
            f.write(f"*Generated on {datetime.now().isoformat()}*\n")

    def _update_latest_symlink(self) -> None:
        """Update the 'latest' symlink to point to current build"""
        # Update latest in common/ directory (worktree-specific)
        project_root = Path(__file__).parent.parent
        common_latest = project_root / "common" / "latest_build"

        if common_latest.exists():
            common_latest.unlink()

        # Create relative symlink to the build
        relative_path = self.build_path.relative_to(project_root)
        common_latest.symlink_to(f"../{relative_path}")
        logger.debug(f"Updated latest build symlink: {common_latest} -> {relative_path}")

        # Note: We no longer create latest symlink in build directory per issue #58
        # Only use common/latest_build for worktree isolation

    @classmethod
    def get_latest_build(cls, base_path: str = None) -> Optional["BuildTracker"]:
        """Get the most recent build tracker"""
        if base_path is None:
            # Use project root relative path
            project_root = Path(__file__).parent.parent
            base_path = project_root / "data"
        else:
            project_root = Path(base_path).parent

        # Set up build base path
        build_base_path = Path(base_path) / "stage_99_build"

        # Use common/latest_build location only (worktree-specific per issue #58)
        common_latest = project_root / "common" / "latest_build"
        if not common_latest.exists():
            return None

        latest_build_path = common_latest.resolve()
        build_id = latest_build_path.name.replace("build_", "")

        # Create a tracker instance for the existing build
        tracker = cls.__new__(cls)
        tracker.base_path = Path(base_path)
        tracker.build_base_path = build_base_path
        tracker.build_id = build_id
        tracker.build_path = latest_build_path

        # Load existing manifest
        manifest_path = latest_build_path / "BUILD_MANIFEST.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                tracker.manifest = json.load(f)

        return tracker

    def get_build_status(self) -> Dict[str, Any]:
        """Get current build status summary"""
        return {
            "build_id": self.build_id,
            "status": self.manifest["build_info"]["status"],
            "configuration": self.manifest["build_info"]["configuration"],
            "stages_completed": sum(
                1 for stage in self.manifest["stages"].values() if stage["status"] == "completed"
            ),
            "total_stages": len(self.manifest["stages"]),
            "errors": len(self.manifest["statistics"]["errors"]),
            "warnings": len(self.manifest["statistics"]["warnings"])
        }

    def _copy_sec_dcf_documentation(self) -> bool:
        """Copy SEC DCF integration process documentation to build artifacts"""
        try:
            # Source documentation file
            project_root = Path(__file__).parent.parent
            source_doc = project_root / "docs" / "SEC_DCF_Integration_Process.md"
            
            if not source_doc.exists():
                logger.warning(f"SEC DCF integration documentation not found: {source_doc}")
                return False
            
            # Target location in build artifacts
            target_doc = self.build_path / "SEC_DCF_Integration_Process.md"
            
            # Copy the documentation
            shutil.copy2(source_doc, target_doc)
            
            logger.info(f"📋 Copied SEC DCF integration documentation to build: {target_doc}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy SEC DCF documentation: {e}")
            return False
