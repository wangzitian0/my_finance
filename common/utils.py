import os
import re
import warnings
from datetime import datetime, timedelta


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
    log a warning and convert that key to a string and set its value to None.
    """
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if not isinstance(k, (str, int, float, bool)) and k is not None:
                logger.warning(
                    f"Key {k} (type {type(k)}) is not a valid JSON key type; converting key to string and setting its value to null"
                )
                new_key = str(k)
                new_dict[new_key] = None  # Discard the value by setting it to null
            else:
                new_key = k
                new_dict[new_key] = sanitize_data(v, logger)
        return new_dict
    elif isinstance(obj, list):
        return [sanitize_data(item, logger) for item in obj]
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
        "common": project_root / "common"
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
