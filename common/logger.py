# common/logger.py
"""
Legacy Logger Module (MOVED)
This file has been moved to common/system/logging.py (Issue #284)

For backward compatibility, this file re-exports all functionality from the new location.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "common.logger is deprecated. Use 'from common.system import setup_logger' instead. "
    "This module will be removed in version 4.0.0",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all functionality from new location
from .system.logging import (
    DefaultRequestLogIDFilter,
    StreamToLogger,
    setup_legacy_logger,
    setup_logger,
)


# Legacy compatibility function
def setup_logger(job_id, date_str=None):
    """Legacy compatibility wrapper for setup_logger."""
    from .system.logging import setup_logger as new_setup_logger

    return new_setup_logger(job_id=job_id, date_str=date_str)


__all__ = [
    "DefaultRequestLogIDFilter",
    "StreamToLogger",
    "setup_logger",
]
