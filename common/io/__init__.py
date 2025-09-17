#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I/O Module - File I/O and Storage Operations
Unified interface for all file operations, directory management, and storage backends.

Issue #284: Consolidation of I/O operations into single module
- directory.py: Directory management (from core/directory_manager.py)
- storage.py: Storage backend operations (from core/storage_manager.py)
- files.py: File utilities (from utils/io_operations.py)
"""

# Directory management
from .directory import (
    DataLayer,
    DirectoryManager,
    StorageBackend,
    directory_manager,
    ensure_data_structure,
    get_build_path,
    get_config_path,
    get_data_path,
    get_source_path,
)

# File operations
from .files import (
    is_file_recent,
    sanitize_data,
    suppress_third_party_logs,
)

# Storage management
from .storage import (
    LocalFilesystemBackend,
    StorageBackendInterface,
    StorageManager,
    create_storage_manager_from_config,
)

__all__ = [
    # Directory management
    "DirectoryManager",
    "DataLayer",
    "StorageBackend",
    "directory_manager",
    "get_data_path",
    "get_config_path",
    "get_build_path",
    "get_source_path",
    "ensure_data_structure",
    # Storage management
    "StorageManager",
    "StorageBackendInterface",
    "LocalFilesystemBackend",
    "create_storage_manager_from_config",
    # File operations
    "is_file_recent",
    "sanitize_data",
    "suppress_third_party_logs",
]
