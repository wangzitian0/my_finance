#!/usr/bin/env python3
"""
Progress Tracking and Reporting
Moved from utils/progress_tracking.py → system/progress.py (Issue #284)

Progress tracking utilities for long-running operations.
"""

# Import the existing progress tracking functionality
from ..utils.progress_tracking import *

# Re-export all functionality for the new system module structure
__all__ = [
    "create_progress_bar",
    "get_global_progress_tracker",
    "ProgressTracker",
]
