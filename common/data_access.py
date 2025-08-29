#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEPRECATED: Centralized data directory I/O operations for the my_finance system.

Issue #185: Configuration SSOT Unification
- This module is deprecated in favor of DirectoryManager SSOT system
- All functions redirect to DirectoryManager with deprecation warnings
- Legacy imports will continue to work but will show deprecation warnings

Migration Guide:
OLD: from common.data_access import data_access; data_access.get_stage_dir('stage_00_original')
NEW: from common.directory_manager import directory_manager, DataLayer; directory_manager.get_layer_path(DataLayer.RAW_DATA)

This module provides a unified interface for accessing all data directories and files.
"""

import os
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from .core.directory_manager import directory_manager


class DataAccess:
    """
    DEPRECATED: Centralized data access utility for consistent data directory operations.
    
    This class is deprecated. Use DirectoryManager instead for SSOT path management.
    All methods in this class now redirect to DirectoryManager with deprecation warnings.
    
    Migration:
        OLD: from common.data_access import DataAccess; data_access = DataAccess()
        NEW: from common.directory_manager import directory_manager
    """

    def __init__(self, base_dir: Optional[Union[str, Path]] = None):
        """
        Initialize DataAccess with optional base directory.

        Args:
            base_dir: Base directory for data access. Defaults to using DirectoryManager SSOT.
        """
        warnings.warn(
            "DataAccess class from common.data_access is deprecated. "
            "Use 'from common.directory_manager import directory_manager' instead. "
            "This class will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2
        )
        
        if base_dir is None:
            # Use DirectoryManager SSOT for data root
            self.base_dir = directory_manager.get_data_root()
        else:
            self.base_dir = Path(base_dir)

    # Stage directory access methods
    def get_stage_dir(self, stage: Union[str, int]) -> Path:
        """Get stage directory path."""
        if isinstance(stage, int):
            stage = f"stage_{stage:02d}_"
            if stage == "stage_00_":
                stage += "original"
            elif stage == "stage_01_":
                stage += "extract"
            elif stage == "stage_02_":
                stage += "transform"
            elif stage == "stage_03_":
                stage += "load"
            elif stage == "stage_99_":
                stage += "build"
        return self.base_dir / stage

    def get_original_dir(self) -> Path:
        """Get original data directory (stage_00_original)."""
        return self.get_stage_dir("stage_00_original")

    def get_extract_dir(self) -> Path:
        """Get extract directory (stage_01_extract)."""
        return self.get_stage_dir("stage_01_extract")

    def get_transform_dir(self) -> Path:
        """Get transform directory (stage_02_transform)."""
        return self.get_stage_dir("stage_02_transform")

    def get_load_dir(self) -> Path:
        """Get load directory (stage_03_load)."""
        return self.get_stage_dir("stage_03_load")

    def get_build_dir(
        self, build_timestamp: Optional[str] = None, branch: Optional[str] = None
    ) -> Path:
        """
        Get build directory path.

        Args:
            build_timestamp: Specific build timestamp (YYYYMMDD_HHMMSS format)
            branch: Branch name for feature branch builds

        Returns:
            Path to build directory
        """
        if branch and branch != "main":
            build_base = self.base_dir / f"stage_99_build_{branch}"
        else:
            build_base = self.base_dir / "stage_99_build"

        if build_timestamp:
            return build_base / f"build_{build_timestamp}"
        else:
            return build_base

    def get_release_dir(self, release_id: Optional[str] = None) -> Path:
        """
        Get release directory path.

        Args:
            release_id: Specific release ID (release_YYYYMMDD_HHMMSS_build_ID format)

        Returns:
            Path to release directory
        """
        release_base = self.base_dir / "release"
        if release_id:
            return release_base / release_id
        else:
            return release_base

    # Configuration directory access
    def get_config_dir(self) -> Path:
        """Get configuration directory path."""
        return directory_manager.get_config_path()

    def get_config_file(self, config_name: str) -> Path:
        """
        Get configuration file path.

        Args:
            config_name: Configuration file name (with or without .yml extension)

        Returns:
            Path to configuration file
        """
        if not config_name.endswith(".yml"):
            config_name += ".yml"
        return self.get_config_dir() / config_name

    # Log directory access
    def get_log_dir(self, job_id: Optional[str] = None) -> Path:
        """
        Get log directory path.

        Args:
            job_id: Specific job ID for job-specific logs

        Returns:
            Path to log directory
        """
        log_base = self.base_dir / "log"
        if job_id:
            return log_base / job_id
        else:
            return log_base

    def get_log_file(self, job_id: str, timestamp: Optional[str] = None) -> Path:
        """
        Get log file path.

        Args:
            job_id: Job ID for the log
            timestamp: Log timestamp (YYMMDD-HHMMSS format)

        Returns:
            Path to log file
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        return self.get_log_dir(job_id) / f"{timestamp}.txt"

    # Source-specific directory access
    def get_source_dir(
        self, source: str, stage: str = "stage_00_original", date_partition: Optional[str] = None
    ) -> Path:
        """
        Get source-specific directory path.

        Args:
            source: Data source (yfinance, sec_edgar, etc.)
            stage: Data stage directory
            date_partition: Optional date partition

        Returns:
            Path to source directory
        """
        stage_dir = self.get_stage_dir(stage)
        source_dir = stage_dir / source

        if date_partition:
            return source_dir / date_partition
        else:
            return source_dir

    def get_ticker_dir(
        self,
        source: str,
        ticker: str,
        stage: str = "stage_00_original",
        date_partition: Optional[str] = None,
    ) -> Path:
        """
        Get ticker-specific directory path.

        Args:
            source: Data source (yfinance, sec_edgar, etc.)
            ticker: Stock ticker symbol
            stage: Data stage directory
            date_partition: Optional date partition

        Returns:
            Path to ticker directory
        """
        source_dir = self.get_source_dir(source, stage, date_partition)
        return source_dir / ticker

    # Latest build and release access
    def get_latest_build_link(self) -> Path:
        """Get path to latest build symlink."""
        return Path("common") / "latest_build"

    def get_latest_release_link(self) -> Path:
        """Get path to latest release symlink."""
        return self.get_release_dir() / "latest"

    # Utility methods for common operations
    def ensure_dir_exists(self, path: Path) -> Path:
        """
        Ensure directory exists, create if necessary.

        Args:
            path: Directory path to ensure exists

        Returns:
            Path object for the directory
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_latest_date_partition(self, source_dir: Path) -> Optional[str]:
        """
        Get the latest date partition from a source directory.

        Args:
            source_dir: Source directory to search

        Returns:
            Latest date partition string or None if not found
        """
        if not source_dir.exists():
            return None

        date_dirs = [
            d.name for d in source_dir.iterdir() if d.is_dir() and d.name.replace("_", "").isdigit()
        ]

        if date_dirs:
            return max(date_dirs)
        else:
            return None

    def list_builds(self, branch: Optional[str] = None) -> List[str]:
        """
        List available build directories.

        Args:
            branch: Branch name for feature branch builds

        Returns:
            List of build timestamp strings
        """
        build_base = self.get_build_dir(branch=branch)
        if not build_base.exists():
            return []

        builds = [
            d.name.replace("build_", "")
            for d in build_base.iterdir()
            if d.is_dir() and d.name.startswith("build_")
        ]

        return sorted(builds, reverse=True)  # Most recent first

    def list_releases(self) -> List[str]:
        """
        List available release directories.

        Returns:
            List of release ID strings
        """
        release_dir = self.get_release_dir()
        if not release_dir.exists():
            return []

        releases = [
            d.name for d in release_dir.iterdir() if d.is_dir() and d.name.startswith("release_")
        ]

        return sorted(releases, reverse=True)  # Most recent first


# Global instance for convenience
data_access = DataAccess()


# ============================================================================
# DEPRECATED: Convenience functions with deprecation warnings
# All functions redirect to DirectoryManager
# ============================================================================

def get_data_path(*args, **kwargs) -> Path:
    """
    DEPRECATED: Convenience function to get data paths using the global DataAccess instance.
    Use directory_manager.get_data_root() instead.
    """
    warnings.warn(
        "get_data_path() from common.data_access is deprecated. "
        "Use 'from common.directory_manager import directory_manager; directory_manager.get_data_root()' instead. "
        "This function will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    return data_access.base_dir.joinpath(*args)


def get_build_path(build_timestamp: Optional[str] = None, branch: Optional[str] = None) -> Path:
    """
    DEPRECATED: Convenience function to get build directory paths.
    Use directory_manager.get_build_path() instead.
    """
    warnings.warn(
        "get_build_path() from common.data_access is deprecated. "
        "Use 'from common.directory_manager import directory_manager; directory_manager.get_build_path()' instead. "
        "This function will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    return data_access.get_build_dir(build_timestamp, branch)


def get_config_path(config_name: str) -> Path:
    """
    DEPRECATED: Convenience function to get configuration file paths.
    Use directory_manager.get_config_path() instead.
    """
    warnings.warn(
        "get_config_path() from common.data_access is deprecated. "
        "Use 'from common.directory_manager import directory_manager; directory_manager.get_config_path()' instead. "
        "This function will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    return data_access.get_config_file(config_name)


def get_log_path(job_id: str, timestamp: Optional[str] = None) -> Path:
    """
    DEPRECATED: Convenience function to get log file paths.
    Use directory_manager.get_logs_path() instead.
    """
    warnings.warn(
        "get_log_path() from common.data_access is deprecated. "
        "Use 'from common.directory_manager import directory_manager; directory_manager.get_logs_path()' instead. "
        "This function will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    return data_access.get_log_file(job_id, timestamp)


def ensure_data_dir(*args, **kwargs) -> Path:
    """
    DEPRECATED: Convenience function to ensure data directory exists.
    Use directory_manager.ensure_directories() instead.
    """
    warnings.warn(
        "ensure_data_dir() from common.data_access is deprecated. "
        "Use 'from common.directory_manager import directory_manager; directory_manager.ensure_directories()' instead. "
        "This function will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    path = get_data_path(*args, **kwargs)
    return data_access.ensure_dir_exists(path)
