#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common module for shared utilities and configurations.
This module provides centralized access to common functionality used across the entire project.

Issue #122: Five-Layer Data Architecture Implementation
- Unified directory management with SSOT principles
- Storage backend abstraction for cloud migration  
- Comprehensive configuration management system
- Legacy path mapping for backward compatibility
- DRY architecture eliminating hardcoded paths

Key Components:
- DirectoryManager: SSOT directory path management
- ConfigManager: Unified configuration loading and validation
- StorageManager: Backend abstraction for local/cloud storage
- DataLayer enum: Five-layer data architecture implementation
"""

# Import core components for easy access
from .directory_manager import (
    DirectoryManager,
    DataLayer,
    StorageBackend,
    directory_manager,
    get_data_path,
    get_config_path,
    get_build_path,
    get_source_path,
    ensure_data_structure
)

from .config_manager import (
    ConfigManager,
    ConfigType,
    ConfigSchema,
    config_manager,
    get_config,
    get_company_list,
    get_llm_config,
    get_data_source_config,
    reload_configs
)

from .storage_backends import (
    StorageManager,
    StorageBackendInterface,
    LocalFilesystemBackend,
    create_storage_manager_from_config
)

# Legacy imports for backward compatibility
from .data_access import data_access
from .build_tracker import BuildTracker
from .utils import *
from .logger import setup_logger

# Version information
__version__ = "2.0.0"
__version_info__ = (2, 0, 0)

# Compatibility layer for gradual migration
def get_legacy_data_path(*args, **kwargs):
    """
    Legacy compatibility function.
    Redirects to new directory manager system.
    """
    import warnings
    warnings.warn(
        "get_legacy_data_path is deprecated. Use get_data_path with DataLayer enum instead.",
        DeprecationWarning,
        stacklevel=2
    )
    if args and isinstance(args[0], str):
        # Try to map legacy path to new system
        legacy_path = args[0]
        layer = directory_manager.map_legacy_path(legacy_path)
        if layer:
            return get_data_path(layer, *args[1:], **kwargs)
    return data_access.get_data_path(*args, **kwargs)

__all__ = [
    # Core directory management
    'DirectoryManager', 'DataLayer', 'StorageBackend', 'directory_manager',
    'get_data_path', 'get_config_path', 'get_build_path', 'get_source_path', 
    'ensure_data_structure',
    
    # Configuration management
    'ConfigManager', 'ConfigType', 'ConfigSchema', 'config_manager',
    'get_config', 'get_company_list', 'get_llm_config', 'get_data_source_config',
    'reload_configs',
    
    # Storage backends
    'StorageManager', 'StorageBackendInterface', 'LocalFilesystemBackend',
    'create_storage_manager_from_config',
    
    # Legacy compatibility
    'data_access', 'BuildTracker', 'setup_logger', 'get_legacy_data_path',
    
    # Version info
    '__version__', '__version_info__'
]
