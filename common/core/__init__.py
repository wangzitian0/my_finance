#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core system components for the common library.

This module provides the fundamental infrastructure components:
- DirectoryManager: SSOT directory path management  
- ConfigManager: Unified configuration system
- StorageManager: Backend abstraction for local/cloud storage
- Compatibility layer for legacy imports

Issue #184: Core library restructuring
"""

from .directory_manager import (
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
from .config_manager import (
    ConfigManager,
    ConfigSchema,
    ConfigType,
    config_manager,
    get_company_list,
    get_config,
    get_data_source_config,
    get_llm_config,
    reload_configs,
)
from .storage_manager import (
    LocalFilesystemBackend,
    StorageBackendInterface,
    StorageManager,
    create_storage_manager_from_config,
)

# Compatibility layer imports will be added after migration
try:
    from .compatibility import *
except ImportError:
    # Compatibility module will be created during migration
    pass

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
    # Configuration management
    "ConfigManager",
    "ConfigType",
    "ConfigSchema", 
    "config_manager",
    "get_config",
    "get_company_list",
    "get_llm_config",
    "get_data_source_config",
    "reload_configs",
    # Storage management
    "StorageManager",
    "StorageBackendInterface",
    "LocalFilesystemBackend", 
    "create_storage_manager_from_config",
]