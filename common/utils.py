import json
import os
import re
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml


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
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


# Data I/O Centralization Functions


def read_json_file(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Centralized JSON file reading with error handling.

    Args:
        file_path: Path to the JSON file
        default: Default value to return if file doesn't exist or has errors

    Returns:
        Parsed JSON data or default value
    """
    file_path = Path(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            return default
        raise
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise IOError(f"Error reading {file_path}: {e}")


def write_json_file(
    file_path: Union[str, Path], data: Any, ensure_dir: bool = True, indent: int = 2
) -> None:
    """
    Centralized JSON file writing with error handling.

    Args:
        file_path: Path to write the JSON file
        data: Data to serialize to JSON
        ensure_dir: Whether to create parent directories if they don't exist
        indent: JSON indentation for pretty printing
    """
    file_path = Path(file_path)

    if ensure_dir:
        ensure_path_exists(file_path.parent)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"Error writing JSON to {file_path}: {e}")


def read_yaml_file(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Centralized YAML file reading with error handling.

    Args:
        file_path: Path to the YAML file
        default: Default value to return if file doesn't exist or has errors

    Returns:
        Parsed YAML data or default value
    """
    file_path = Path(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        if default is not None:
            return default
        raise
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")
    except Exception as e:
        raise IOError(f"Error reading {file_path}: {e}")


def write_yaml_file(file_path: Union[str, Path], data: Any, ensure_dir: bool = True) -> None:
    """
    Centralized YAML file writing with error handling.

    Args:
        file_path: Path to write the YAML file
        data: Data to serialize to YAML
        ensure_dir: Whether to create parent directories if they don't exist
    """
    file_path = Path(file_path)

    if ensure_dir:
        ensure_path_exists(file_path.parent)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        raise IOError(f"Error writing YAML to {file_path}: {e}")


def read_text_file(
    file_path: Union[str, Path], default: str = None, encoding: str = "utf-8"
) -> str:
    """
    Centralized text file reading with error handling.

    Args:
        file_path: Path to the text file
        default: Default value to return if file doesn't exist
        encoding: File encoding (default: utf-8)

    Returns:
        File contents as string or default value
    """
    file_path = Path(file_path)

    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        if default is not None:
            return default
        raise
    except Exception as e:
        raise IOError(f"Error reading text file {file_path}: {e}")


def write_text_file(
    file_path: Union[str, Path], content: str, ensure_dir: bool = True, encoding: str = "utf-8"
) -> None:
    """
    Centralized text file writing with error handling.

    Args:
        file_path: Path to write the text file
        content: Text content to write
        ensure_dir: Whether to create parent directories if they don't exist
        encoding: File encoding (default: utf-8)
    """
    file_path = Path(file_path)

    if ensure_dir:
        ensure_path_exists(file_path.parent)

    try:
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Error writing text to {file_path}: {e}")


def list_files_by_pattern(
    directory: Union[str, Path], pattern: str = "*", recursive: bool = True
) -> list[Path]:
    """
    List files matching a pattern in a directory.

    Args:
        directory: Directory to search in
        pattern: Glob pattern to match (default: all files)
        recursive: Whether to search recursively (default: True)

    Returns:
        List of Path objects matching the pattern
    """
    directory = Path(directory)

    if not directory.exists():
        return []

    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def safe_file_operation(operation_func, *args, **kwargs):
    """
    Wrapper for safe file operations with consistent error handling.

    Args:
        operation_func: Function to execute (read_json_file, write_text_file, etc.)
        *args, **kwargs: Arguments to pass to the operation function

    Returns:
        Result of the operation or raises standardized exceptions
    """
    try:
        return operation_func(*args, **kwargs)
    except (FileNotFoundError, IOError, ValueError) as e:
        # Re-raise standardized exceptions
        raise e
    except Exception as e:
        # Wrap unexpected exceptions
        raise IOError(f"Unexpected error in file operation: {e}")


def get_file_info(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Get file information including size, modification time, etc.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information or None if file doesn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return None

    stat = file_path.stat()
    return {
        "path": str(file_path),
        "name": file_path.name,
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "suffix": file_path.suffix,
    }
