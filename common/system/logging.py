# common/system/logging.py
"""
Unified logging system with PathManager integration.
Consolidates common/logger.py + utils/logging_setup.py for Issue #284.

Moved from common/logger.py → common/system/logging.py (Issue #284)
Consolidated with utils/logging_setup.py for unified logging system.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import from relative paths after consolidation
from ..utils.id_generation import Snowflake


class DefaultRequestLogIDFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "request_logid"):
            record.request_logid = "N/A"
        return True


class StreamToLogger(object):
    """
    Mock file stream object that redirects write content to logger.
    Used to capture stderr output from underlying libraries (e.g., third-party libraries) and write to log.
    """

    def __init__(self, logger, log_level=logging.ERROR):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def setup_logger(
    job_id: str = None,
    date_str: str = None,
    level: int = logging.INFO,
    log_dir: str = None,
    use_file_handler: bool = True,
    use_console_handler: bool = True,
) -> logging.Logger:
    """
    Enhanced logger setup function with flexible configuration.
    Consolidates functionality from logger.py and utils/logging_setup.py.

    Args:
        job_id: Job ID for log file naming (legacy compatibility)
        date_str: Date string for log file naming (legacy compatibility)
        level: Logging level
        log_dir: Directory for log files (overrides DirectoryManager if provided)
        use_file_handler: Whether to add file handler
        use_console_handler: Whether to add console handler

    Returns:
        Configured logger instance
    """
    # Import here to avoid circular dependency
    from ..core.config_manager import config_manager
    from ..core.directory_manager import directory_manager

    # Use SSOT config manager - fallback to defaults if no logging config
    try:
        directory_config = config_manager.get_config("directory_structure")
        log_conf = directory_config.get("logging", {})
    except Exception:
        log_conf = {}

    log_level = getattr(logging, log_conf.get("level", "INFO"))
    file_level = getattr(logging, log_conf.get("file_level", "INFO"))
    log_format = log_conf.get(
        "format", "%(asctime)s - %(levelname)s - [%(request_logid)s] - %(message)s"
    )

    # Override with function parameters if provided
    if level is not None:
        log_level = level

    if date_str is None:
        date_str = datetime.now().strftime("%y%m%d-%H%M%S")

    # Build log file path using DirectoryManager or provided log_dir
    if log_dir:
        log_base_dir = Path(log_dir)
    else:
        log_base_dir = directory_manager.get_logs_path()

    if job_id:
        log_dir_path = log_base_dir / job_id
        log_dir_path.mkdir(parents=True, exist_ok=True)
        log_file = log_dir_path / f"{date_str}.txt"
        logger_name = f"{job_id}_{date_str}"
    else:
        log_base_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_base_dir / f"app_{timestamp}.log"
        logger_name = f"app_{timestamp}"

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Disable propagation to prevent messages from outputting to root logger
    logger.propagate = False

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Add request log ID filter
    log_id_filter = DefaultRequestLogIDFilter()

    # Console handler
    if use_console_handler:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(log_id_filter)
        logger.addHandler(console_handler)

    # File handler
    if use_file_handler:
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(log_id_filter)
        logger.addHandler(file_handler)

    return logger


# Legacy compatibility functions
def setup_legacy_logger(job_id, date_str=None):
    """Legacy compatibility function for existing code."""
    return setup_logger(job_id=job_id, date_str=date_str)
