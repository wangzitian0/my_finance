#!/usr/bin/env python3
"""
Storage Management and Backend Operations
Moved from core/storage_manager.py → io/storage.py (Issue #284)

Storage backend abstraction for local and cloud storage with unified API.
"""

# Import the existing storage manager functionality
from ..core.storage_manager import *

# Re-export all functionality for the new io module structure
__all__ = [
    "LocalFilesystemBackend",
    "StorageBackendInterface",
    "StorageManager",
    "create_storage_manager_from_config",
]
