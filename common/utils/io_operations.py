#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidated I/O operations and utilities.

This module consolidates various I/O utility functions from utils.py
and other modules into a centralized location.

Issue #184: Utility consolidation phase
"""

import os
import re
from datetime import datetime, timedelta

# Import pandas for timestamp handling if available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def suppress_third_party_logs():
    """
    Adjust the logging levels for third-party libraries (like requests/urllib3)
    so that only critical messages are printed to the console.
    """
    import logging

    logging.getLogger("requests").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def is_file_recent(filepath, hours=1):
    """
    Check if the timestamp in the filename is within the past 'hours' hours.
    Assumes the filename format: <ticker>_<source>_<oid>_<date_str>.json,
    where date_str is in the format %y%m%d-%H%M%S.
    """
    filename = os.path.basename(filepath)
    match = re.search(r"_(\d{6}-\d{6})\.json$", filename)
    if match:
        timestamp_str = match.group(1)
        try:
            file_dt = datetime.strptime(timestamp_str, "%y%m%d-%H%M%S")
            return (datetime.now() - file_dt) < timedelta(hours=hours)
        except Exception:
            return False
    return False


def sanitize_data(obj, logger):
    """
    Recursively traverse the object.
    For any dictionary key that is not of type str, int, float, bool, or None,
    convert it to a JSON-serializable format while preserving the data.
    Special handling for pandas Timestamp and datetime objects to preserve temporal data.
    """
    if isinstance(obj, dict):
        sanitized_dict = {}
        for key, value in obj.items():
            # Sanitize the key
            if isinstance(key, (str, int, float, bool)) or key is None:
                sanitized_key = key
            else:
                # Convert non-serializable keys to string representation
                if PANDAS_AVAILABLE and isinstance(key, pd.Timestamp):
                    # Preserve pandas Timestamp as ISO string
                    sanitized_key = key.isoformat()
                    logger.debug(f"Converted pandas Timestamp key {key} to {sanitized_key}")
                elif isinstance(key, datetime):
                    # Preserve datetime as ISO string
                    sanitized_key = key.isoformat()
                    logger.debug(f"Converted datetime key {key} to {sanitized_key}")
                else:
                    sanitized_key = str(key)
                    logger.warning(f"Converted non-serializable key {key} to string: {sanitized_key}")
            
            # Recursively sanitize the value
            sanitized_value = sanitize_data(value, logger)
            sanitized_dict[sanitized_key] = sanitized_value
        return sanitized_dict
    
    elif isinstance(obj, list):
        return [sanitize_data(item, logger) for item in obj]
    
    elif isinstance(obj, tuple):
        return tuple(sanitize_data(item, logger) for item in obj)
    
    elif isinstance(obj, set):
        return [sanitize_data(item, logger) for item in obj]  # Convert set to list
    
    elif PANDAS_AVAILABLE and isinstance(obj, pd.Timestamp):
        # Preserve pandas Timestamp data as ISO string
        iso_string = obj.isoformat()
        logger.debug(f"Converted pandas Timestamp {obj} to ISO string: {iso_string}")
        return iso_string
    
    elif isinstance(obj, datetime):
        # Preserve datetime data as ISO string
        iso_string = obj.isoformat()
        logger.debug(f"Converted datetime {obj} to ISO string: {iso_string}")
        return iso_string
    
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    
    else:
        # For any other non-serializable object, convert to string
        str_representation = str(obj)
        logger.warning(f"Converted non-serializable object {type(obj)} to string: {str_representation}")
        return str_representation