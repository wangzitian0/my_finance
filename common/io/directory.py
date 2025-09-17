#!/usr/bin/env python3
"""
Directory Management and Path Operations
Moved from core/directory_manager.py → io/directory.py (Issue #284)

SSOT (Single Source of Truth) Directory Management System
Centralized directory path management for the entire project.
"""

# Import the existing directory manager functionality
from ..core.directory_manager import *

# Re-export all functionality for the new io module structure
__all__ = [
    "DirectoryManager",
    "DataLayer",
    "StorageBackend",
    "directory_manager",
    "ensure_data_structure",
    "get_build_path",
    "get_config_path",
    "get_data_path",
    "get_source_path",
]
