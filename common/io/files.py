#!/usr/bin/env python3
"""
File I/O Operations and Utilities
Moved from utils/io_operations.py → io/files.py (Issue #284)

File operation utilities and I/O helper functions.
"""

# Import the existing I/O operations functionality
from ..utils.io_operations import *

# Re-export all functionality for the new io module structure
__all__ = [
    "is_file_recent",
    "sanitize_data",
    "suppress_third_party_logs",
]
