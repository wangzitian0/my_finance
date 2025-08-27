import os
import re
import warnings
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
        new_dict = {}
        for k, v in obj.items():
            if not isinstance(k, (str, int, float, bool)) and k is not None:
                # Special handling for pandas Timestamp objects
                if PANDAS_AVAILABLE and isinstance(k, pd.Timestamp):
                    try:
                        # Convert pandas Timestamp to ISO format string
                        new_key = k.isoformat()
                        logger.debug(
                            f"Converted pandas Timestamp key {k} to ISO format: {new_key}"
                        )
                        new_dict[new_key] = sanitize_data(v, logger)
                        continue
                    except Exception as e:
                        logger.warning(
                            f"Failed to convert pandas Timestamp key {k} to ISO format: {e}. Using string representation."
                        )
                
                # Special handling for datetime objects
                elif isinstance(k, datetime):
                    try:
                        new_key = k.isoformat()
                        logger.debug(
                            f"Converted datetime key {k} to ISO format: {new_key}"
                        )
                        new_dict[new_key] = sanitize_data(v, logger)
                        continue
                    except Exception as e:
                        logger.warning(
                            f"Failed to convert datetime key {k} to ISO format: {e}. Using string representation."
                        )
                
                # For other unsupported key types, convert to string but preserve the value
                logger.info(
                    f"Key {k} (type {type(k)}) is not a native JSON key type; converting to string while preserving value"
                )
                new_key = str(k)
                new_dict[new_key] = sanitize_data(v, logger)
            else:
                new_key = k
                new_dict[new_key] = sanitize_data(v, logger)
        return new_dict
    elif isinstance(obj, list):
        return [sanitize_data(item, logger) for item in obj]
    else:
        # Handle pandas Timestamp and datetime objects in values as well
        if PANDAS_AVAILABLE and isinstance(obj, pd.Timestamp):
            try:
                return obj.isoformat()
            except Exception:
                return str(obj)
        elif isinstance(obj, datetime):
            try:
                return obj.isoformat()
            except Exception:
                return str(obj)
        else:
            return obj


def get_project_paths():
    """
    Get standardized project path structure for data directories.
    Returns a dictionary with commonly used paths for consistent access.
    """
    from pathlib import Path

    # Get project root directory
    project_root = Path(__file__).parent.parent
    data_root = project_root / "data"

    return {
        "project_root": project_root,
        "data_root": data_root,
        "stage_00_original": data_root / "stage_00_original",
        "stage_01_extract": data_root / "stage_01_extract",
        "stage_02_transform": data_root / "stage_02_transform",
        "stage_03_load": data_root / "stage_03_load",
        "stage_99_build": data_root / "stage_99_build",
        "sec_edgar_original": data_root / "stage_00_original" / "sec-edgar",
        "sec_edgar_extract": data_root / "stage_01_extract" / "sec_edgar",
        "yfinance_original": data_root / "stage_00_original" / "yfinance",
        "yfinance_extract": data_root / "stage_01_extract" / "yfinance",
        "embeddings": data_root / "stage_03_load" / "embeddings",
        "graph_nodes": data_root / "stage_03_load" / "graph_nodes",
        "dcf_results": data_root / "stage_03_load" / "dcf_results",
        "release": data_root / "release",
        "logs": data_root / "log",
        "config": data_root / "config",
        "common": project_root / "common",
    }


def get_current_build_dir():
    """
    Get the current build directory path using BuildTracker.
    Returns Path object or None if no current build exists.
    """
    try:
        from common.build_tracker import BuildTracker

        build_tracker = BuildTracker.get_latest_build()
        if build_tracker:
            return Path(build_tracker.build_path)
    except Exception:
        pass
    return None


def ensure_path_exists(path):
    """
    Ensure a directory path exists, creating it if necessary.
    Args:
        path: Path object or string path
    Returns:
        Path object of the created/existing directory
    """
    from pathlib import Path

    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
