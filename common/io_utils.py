#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified I/O utilities for the my_finance system.
This module provides centralized JSON, YAML, and file I/O operations.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

# Configure logger
logger = logging.getLogger(__name__)


class IOUtils:
    """Centralized I/O operations for consistent file handling across the codebase."""

    @staticmethod
    def load_json(file_path: Union[str, Path], encoding: str = "utf-8") -> Any:
        """
        Load JSON data from a file.

        Args:
            file_path: Path to the JSON file
            encoding: File encoding (default: utf-8)

        Returns:
            Parsed JSON data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        try:
            with open(file_path, "r", encoding=encoding) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {file_path}: {e}")
            raise

    @staticmethod
    def save_json(
        data: Any,
        file_path: Union[str, Path],
        indent: int = 2,
        ensure_ascii: bool = False,
        encoding: str = "utf-8",
        create_parents: bool = True,
    ) -> None:
        """
        Save data to a JSON file.

        Args:
            data: Data to save
            file_path: Path to the JSON file
            indent: JSON indentation level (default: 2)
            ensure_ascii: Ensure ASCII encoding (default: False)
            encoding: File encoding (default: utf-8)
            create_parents: Create parent directories if they don't exist (default: True)

        Raises:
            TypeError: If data is not JSON serializable
        """
        file_path = Path(file_path)

        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, "w", encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
            logger.debug(f"Saved JSON to {file_path}")
        except TypeError as e:
            logger.error(f"Failed to serialize data to JSON: {e}")
            raise

    @staticmethod
    def load_yaml(file_path: Union[str, Path], encoding: str = "utf-8") -> Any:
        """
        Load YAML data from a file.

        Args:
            file_path: Path to the YAML file
            encoding: File encoding (default: utf-8)

        Returns:
            Parsed YAML data

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"YAML file not found: {file_path}")

        try:
            with open(file_path, "r", encoding=encoding) as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML from {file_path}: {e}")
            raise

    @staticmethod
    def save_yaml(
        data: Any,
        file_path: Union[str, Path],
        default_flow_style: bool = False,
        encoding: str = "utf-8",
        create_parents: bool = True,
    ) -> None:
        """
        Save data to a YAML file.

        Args:
            data: Data to save
            file_path: Path to the YAML file
            default_flow_style: Use flow style for collections (default: False)
            encoding: File encoding (default: utf-8)
            create_parents: Create parent directories if they don't exist (default: True)

        Raises:
            yaml.YAMLError: If data cannot be serialized to YAML
        """
        file_path = Path(file_path)

        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, "w", encoding=encoding) as f:
                yaml.safe_dump(data, f, default_flow_style=default_flow_style, allow_unicode=True)
            logger.debug(f"Saved YAML to {file_path}")
        except yaml.YAMLError as e:
            logger.error(f"Failed to serialize data to YAML: {e}")
            raise

    @staticmethod
    def read_text(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """
        Read text content from a file.

        Args:
            file_path: Path to the text file
            encoding: File encoding (default: utf-8)

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")

        with open(file_path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def write_text(
        content: str,
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        create_parents: bool = True,
    ) -> None:
        """
        Write text content to a file.

        Args:
            content: Text content to write
            file_path: Path to the text file
            encoding: File encoding (default: utf-8)
            create_parents: Create parent directories if they don't exist (default: True)
        """
        file_path = Path(file_path)

        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        logger.debug(f"Wrote text to {file_path}")

    @staticmethod
    def read_lines(
        file_path: Union[str, Path], encoding: str = "utf-8", strip: bool = True
    ) -> List[str]:
        """
        Read lines from a text file.

        Args:
            file_path: Path to the text file
            encoding: File encoding (default: utf-8)
            strip: Strip whitespace from lines (default: True)

        Returns:
            List of lines

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")

        with open(file_path, "r", encoding=encoding) as f:
            lines = f.readlines()
            if strip:
                lines = [line.strip() for line in lines]
            return lines

    @staticmethod
    def append_json_line(
        data: Dict[str, Any],
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        create_parents: bool = True,
    ) -> None:
        """
        Append a JSON object as a new line (JSONL format).

        Args:
            data: Data to append
            file_path: Path to the JSONL file
            encoding: File encoding (default: utf-8)
            create_parents: Create parent directories if they don't exist (default: True)
        """
        file_path = Path(file_path)

        if create_parents:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding=encoding) as f:
            f.write(json.dumps(data) + "\n")

    @staticmethod
    def read_json_lines(file_path: Union[str, Path], encoding: str = "utf-8") -> List[Dict[str, Any]]:
        """
        Read JSON lines from a JSONL file.

        Args:
            file_path: Path to the JSONL file
            encoding: File encoding (default: utf-8)

        Returns:
            List of parsed JSON objects

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {file_path}")

        data = []
        with open(file_path, "r", encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON line: {e}")
        return data

    @staticmethod
    def file_exists(file_path: Union[str, Path]) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()

    @staticmethod
    def ensure_directory(dir_path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            dir_path: Directory path

        Returns:
            Path object for the directory
        """
        dir_path = Path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path


# Global instance for convenience
io_utils = IOUtils()

# Convenience functions for common operations
load_json = io_utils.load_json
save_json = io_utils.save_json
load_yaml = io_utils.load_yaml
save_yaml = io_utils.save_yaml
read_text = io_utils.read_text
write_text = io_utils.write_text
read_lines = io_utils.read_lines
append_json_line = io_utils.append_json_line
read_json_lines = io_utils.read_json_lines
file_exists = io_utils.file_exists
ensure_directory = io_utils.ensure_directory