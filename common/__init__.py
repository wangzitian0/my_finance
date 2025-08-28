#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common module for shared utilities and configurations.
This module provides centralized access to common functionality used across the entire project.

Issue #122: Five-Layer Data Architecture Implementation
Issue #184: Core library restructuring with focused components

- Unified directory management with SSOT principles
- Storage backend abstraction for cloud migration
- Comprehensive configuration management system
- Legacy path mapping for backward compatibility
- DRY architecture eliminating hardcoded paths

New Structure:
- core/: Core system components (DirectoryManager, ConfigManager, StorageManager)
- utils/: Organized utility modules (I/O, logging, data processing, etc.)
- systems/: Specialized system modules (BuildTracker, QualityReporter, etc.)
- tests/: Comprehensive test structure
"""

from .core.config_manager import (
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

# Core components
from .core.directory_manager import (
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
from .core.storage_manager import (
    LocalFilesystemBackend,
    StorageBackendInterface,
    StorageManager,
    create_storage_manager_from_config,
)

# System modules
from .systems.build_tracker import BuildTracker
from .systems.graph_rag_schema import (
    DEFAULT_EMBEDDING_CONFIG,
    MAGNIFICENT_7_CIKS,
    MAGNIFICENT_7_TICKERS,
    DCFValuationNode,
    DocumentChunkNode,
    DocumentType,
    GraphNodeSchema,
    GraphRAGQuery,
    GraphRAGResponse,
    GraphRelationship,
    QueryIntent,
    RelationshipType,
    SECFilingNode,
    SemanticSearchResult,
    StockNode,
    VectorEmbeddingConfig,
)
from .systems.metadata_manager import MetadataManager
from .systems.quality_reporter import QualityReporter, setup_quality_reporter
from .utils.data_processing import (
    convert_timestamps_to_iso,
    deep_merge_dicts,
    filter_companies_by_criteria,
    merge_company_lists,
    normalize_ticker_symbol,
    safe_json_serialize,
    validate_company_data,
)
from .utils.id_generation import Snowflake, generate_snowflake_id, generate_snowflake_str
from .utils.io_operations import is_file_recent, sanitize_data, suppress_third_party_logs

# Utility modules
from .utils.logging_setup import setup_logger
from .utils.progress_tracking import create_progress_bar, get_global_progress_tracker

# Legacy imports for backward compatibility
try:
    from .data_access import data_access
except ImportError:
    # Fallback if data_access is not available
    data_access = None

# Compatibility layer
from .core.compatibility import get_legacy_data_path

# Version information
__version__ = "2.1.0"  # Incremented for restructuring
__version_info__ = (2, 1, 0)

__all__ = [
    # Core directory management
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
    # Utility functions
    "setup_logger",
    "suppress_third_party_logs",
    "is_file_recent",
    "sanitize_data",
    "Snowflake",
    "generate_snowflake_id",
    "generate_snowflake_str",
    "create_progress_bar",
    "get_global_progress_tracker",
    "normalize_ticker_symbol",
    "validate_company_data",
    "merge_company_lists",
    "filter_companies_by_criteria",
    "convert_timestamps_to_iso",
    "safe_json_serialize",
    "deep_merge_dicts",
    # System modules
    "BuildTracker",
    "QualityReporter",
    "setup_quality_reporter",
    "MetadataManager",
    # Graph RAG schema
    "QueryIntent",
    "DocumentType",
    "VectorEmbeddingConfig",
    "GraphNodeSchema",
    "StockNode",
    "SECFilingNode",
    "DocumentChunkNode",
    "DCFValuationNode",
    "RelationshipType",
    "GraphRelationship",
    "SemanticSearchResult",
    "GraphRAGQuery",
    "GraphRAGResponse",
    "MAGNIFICENT_7_TICKERS",
    "MAGNIFICENT_7_CIKS",
    "DEFAULT_EMBEDDING_CONFIG",
    # Legacy compatibility
    "data_access",
    "get_legacy_data_path",
    # Version info
    "__version__",
    "__version_info__",
]
