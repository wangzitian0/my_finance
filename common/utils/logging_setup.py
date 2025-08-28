#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging setup and configuration utilities.

Migrated from logger.py with enhanced functionality and organization.

Issue #184: Utility consolidation - Logging setup
"""

import logging
import os
from datetime import datetime

from .id_generation import Snowflake

# Import removed to avoid circular dependency during restructuring
# Configuration can be passed as parameters instead


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
    name: str = None,
    level: int = logging.INFO,
    log_dir: str = None,
    build_id: str = None,
    use_file_handler: bool = True,
    use_console_handler: bool = True,
) -> logging.Logger:
    """
    Enhanced logger setup function with flexible configuration.

    Args:
        name: Logger name (defaults to root logger)
        level: Logging level
        log_dir: Directory for log files
        build_id: Build ID for log file naming
        use_file_handler: Whether to add file handler
        use_console_handler: Whether to add console handler

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(request_logid)s] - %(message)s"
    )

    # Add request log ID filter
    log_id_filter = DefaultRequestLogIDFilter()

    # Console handler
    if use_console_handler:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(log_id_filter)
        logger.addHandler(console_handler)

    # File handler
    if use_file_handler and log_dir:
        os.makedirs(log_dir, exist_ok=True)

        if build_id:
            log_filename = f"{build_id}.log"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"app_{timestamp}.log"

        log_file_path = os.path.join(log_dir, log_filename)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(log_id_filter)
        logger.addHandler(file_handler)

    return logger
