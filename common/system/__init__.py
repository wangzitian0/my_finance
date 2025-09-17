#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Utilities Module
System-level utilities and monitoring components.

Consolidates system utilities for Issue #284 refactoring.
- logging.py: Unified logging system (from logger.py + utils/logging_setup.py)
- monitoring.py: System monitoring and performance tracking (from monitoring/)
- progress.py: Progress tracking utilities (from utils/progress_tracking.py)
"""

from .logging import (
    DefaultRequestLogIDFilter,
    StreamToLogger,
    setup_legacy_logger,
    setup_logger,
)
from .monitoring import (
    PerformanceTimer,
    SystemMonitor,
    get_monitoring_summary,
    get_system_metrics,
    start_system_monitoring,
    stop_system_monitoring,
)
from .progress import (
    ProgressTracker,
    create_progress_bar,
    get_global_progress_tracker,
)

__all__ = [
    # Logging
    "DefaultRequestLogIDFilter",
    "StreamToLogger",
    "setup_legacy_logger",
    "setup_logger",
    # Monitoring
    "SystemMonitor",
    "PerformanceTimer",
    "start_system_monitoring",
    "stop_system_monitoring",
    "get_system_metrics",
    "get_monitoring_summary",
    # Progress tracking
    "ProgressTracker",
    "create_progress_bar",
    "get_global_progress_tracker",
]
