#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backward compatibility layer for the common library restructuring.

This module provides import redirection and legacy function support to ensure
that existing code continues to work after the restructuring.

Issue #184: Core library restructuring - Backward compatibility layer
"""

import warnings
from typing import Any, Dict, List, Optional

from ..systems.build_tracker import BuildTracker
from ..systems.metadata_manager import MetadataManager
from ..systems.quality_reporter import QualityReporter, setup_quality_reporter
from ..utils.id_generation import Snowflake, generate_snowflake_id, generate_snowflake_str

# Import from new locations for redirection
from ..utils.io_operations import is_file_recent, sanitize_data, suppress_third_party_logs
from ..utils.logging_setup import setup_logger
from ..utils.progress_tracking import create_progress_bar
from .config_manager import config_manager, get_company_list, get_config
from .directory_manager import directory_manager, get_config_path, get_data_path


def deprecation_warning(old_import: str, new_import: str):
    """Issue deprecation warning for old imports."""
    warnings.warn(
        f"{old_import} is deprecated. Use {new_import} instead.", DeprecationWarning, stacklevel=3
    )


# Legacy function redirections with deprecation warnings
def get_legacy_data_path(*args, **kwargs):
    """Legacy data path function with deprecation warning."""
    deprecation_warning("get_legacy_data_path", "get_data_path from common.core.directory_manager")
    return str(directory_manager.get_data_root())


def get_legacy_config(*args, **kwargs):
    """Legacy config function with deprecation warning."""
    deprecation_warning("get_legacy_config", "get_config from common.core.config_manager")
    if args:
        return get_config(args[0])
    return {}


# Legacy class aliases
class LegacyBuildTracker(BuildTracker):
    """Legacy BuildTracker with deprecation warning."""

    def __init__(self, *args, **kwargs):
        deprecation_warning("LegacyBuildTracker", "BuildTracker from common.systems.build_tracker")
        super().__init__(*args, **kwargs)


class LegacyQualityReporter(QualityReporter):
    """Legacy QualityReporter with deprecation warning."""

    def __init__(self, *args, **kwargs):
        deprecation_warning(
            "LegacyQualityReporter", "QualityReporter from common.systems.quality_reporter"
        )
        super().__init__(*args, **kwargs)


# Legacy utility function redirections
def legacy_suppress_third_party_logs():
    """Legacy utility function with redirection."""
    deprecation_warning(
        "legacy_suppress_third_party_logs",
        "suppress_third_party_logs from common.utils.io_operations",
    )
    return suppress_third_party_logs()


def legacy_setup_logger(*args, **kwargs):
    """Legacy logger setup with redirection."""
    deprecation_warning("legacy_setup_logger", "setup_logger from common.utils.logging_setup")
    return setup_logger(*args, **kwargs)


def legacy_create_progress_bar(*args, **kwargs):
    """Legacy progress bar creation with redirection."""
    deprecation_warning(
        "legacy_create_progress_bar", "create_progress_bar from common.utils.progress_tracking"
    )
    return create_progress_bar(*args, **kwargs)


# Export compatibility functions and classes
__all__ = [
    # Legacy functions
    "get_legacy_data_path",
    "get_legacy_config",
    "legacy_suppress_third_party_logs",
    "legacy_setup_logger",
    "legacy_create_progress_bar",
    # Legacy classes
    "LegacyBuildTracker",
    "LegacyQualityReporter",
    # Utility
    "deprecation_warning",
]
