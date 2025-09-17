#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common module for shared utilities and configurations.
This module provides centralized access to common functionality used across the entire project.

Issue #284: Simplified L1 directory structure with 5 essential L2 modules
- Optimized common module to 5 essential L2 sub-modules
- No scattered files in common root directory
- Clean organization with exactly 5 L2 modules

Simplified Modular Structure (5 L2 Modules):
- config/: ALL configuration management (includes etl/)
- io/: File I/O and storage operations
- data/: Data processing and validation
- system/: System utilities (logging, monitoring, progress)
- ml/: ML/AI utilities and templates

Legacy modules maintained for compatibility:
- core/: Core system components (legacy paths)
- build/: Build tracking and metadata management
- utils/: Utility modules (legacy paths)
- schemas/: Data schema definitions (legacy paths)
"""

# === 5 ESSENTIAL L2 MODULES ===

# Build and quality modules (maintained)
from .build.build_tracker import BuildTracker
from .build.metadata_manager import MetadataManager
from .build.quality_reporter import QualityReporter, setup_quality_reporter

# 1. Configuration Management (config/)
from .config.etl import (
    DataSourceConfig,
    ETLConfigLoader,
    RuntimeETLConfig,
    ScenarioConfig,
    StockListConfig,
    build_etl_config,
    etl_loader,
    list_available_configs,
    load_data_source,
    load_scenario,
    load_stock_list,
)

# Legacy core components (maintained for backward compatibility)
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

# 3. Data Processing and Validation (data/)
from .data import (
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
    check_data_completeness,
    convert_timestamps_to_iso,
    deep_merge_dicts,
    filter_companies_by_criteria,
    merge_company_lists,
    normalize_ticker_symbol,
    safe_json_serialize,
    validate_company_data,
    validate_company_list,
    validate_financial_data,
    validate_json_structure,
    validate_ticker_symbol,
)

# 2. I/O Operations (io/)
from .io import (
    DataLayer,
    DirectoryManager,
    LocalFilesystemBackend,
    StorageBackend,
    StorageBackendInterface,
    StorageManager,
    create_storage_manager_from_config,
    directory_manager,
    ensure_data_structure,
    get_build_path,
    get_config_path,
    get_data_path,
    get_source_path,
    is_file_recent,
    sanitize_data,
    suppress_third_party_logs,
)

# 5. ML/AI Utilities (ml/)
from .ml import (
    NUMPY_AVAILABLE,
    FallbackEmbeddings,
    FallbackLLM,
    FallbackRetrieval,
    PromptManager,
    PromptType,
    TemplateManager,
    get_dcf_valuation_prompt,
    get_financial_analysis_prompt,
    get_investment_recommendation_prompt,
    get_sec_filing_prompt,
    get_template,
    list_templates,
    prompt_manager,
    render_template,
    template_manager,
)

# 4. System Utilities (system/)
from .system import (
    DefaultRequestLogIDFilter,
    PerformanceTimer,
    ProgressTracker,
    StreamToLogger,
    SystemMonitor,
    create_progress_bar,
    get_global_progress_tracker,
    get_monitoring_summary,
    get_system_metrics,
    setup_legacy_logger,
    setup_logger,
    start_system_monitoring,
    stop_system_monitoring,
)

# Utility modules (legacy compatibility)
from .utils.id_generation import Snowflake, generate_snowflake_id, generate_snowflake_str

# === LEGACY MODULE COMPATIBILITY ===


# Legacy imports for backward compatibility
try:
    from .data_access import data_access
except ImportError:
    # Fallback if data_access is not available
    data_access = None

# Compatibility layer
from .core.compatibility import get_legacy_data_path

# Version information
__version__ = "3.0.0"  # Major version for 5-module restructuring
__version_info__ = (3, 0, 0)

__all__ = [
    # === 5 ESSENTIAL L2 MODULES ===
    # 1. Configuration Management (config/)
    "ETLConfigLoader",
    "RuntimeETLConfig",
    "ScenarioConfig",
    "StockListConfig",
    "DataSourceConfig",
    "build_etl_config",
    "etl_loader",
    "list_available_configs",
    "load_data_source",
    "load_scenario",
    "load_stock_list",
    # 2. I/O Operations (io/)
    "DirectoryManager",
    "DataLayer",
    "StorageBackend",
    "StorageManager",
    "StorageBackendInterface",
    "LocalFilesystemBackend",
    "create_storage_manager_from_config",
    "directory_manager",
    "get_data_path",
    "get_config_path",
    "get_build_path",
    "get_source_path",
    "ensure_data_structure",
    "is_file_recent",
    "sanitize_data",
    "suppress_third_party_logs",
    # 3. Data Processing and Validation (data/)
    "convert_timestamps_to_iso",
    "deep_merge_dicts",
    "filter_companies_by_criteria",
    "merge_company_lists",
    "normalize_ticker_symbol",
    "safe_json_serialize",
    "validate_company_data",
    "check_data_completeness",
    "validate_company_list",
    "validate_financial_data",
    "validate_json_structure",
    "validate_ticker_symbol",
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
    # 4. System Utilities (system/)
    "DefaultRequestLogIDFilter",
    "StreamToLogger",
    "setup_legacy_logger",
    "setup_logger",
    "SystemMonitor",
    "PerformanceTimer",
    "start_system_monitoring",
    "stop_system_monitoring",
    "get_system_metrics",
    "get_monitoring_summary",
    "ProgressTracker",
    "create_progress_bar",
    "get_global_progress_tracker",
    # 5. ML/AI Utilities (ml/)
    "FallbackEmbeddings",
    "FallbackLLM",
    "FallbackRetrieval",
    "NUMPY_AVAILABLE",
    "PromptManager",
    "PromptType",
    "prompt_manager",
    "get_financial_analysis_prompt",
    "get_dcf_valuation_prompt",
    "get_sec_filing_prompt",
    "get_investment_recommendation_prompt",
    "TemplateManager",
    "template_manager",
    "get_template",
    "render_template",
    "list_templates",
    # === LEGACY MODULE COMPATIBILITY ===
    # Legacy configuration management
    "ConfigManager",
    "ConfigType",
    "ConfigSchema",
    "config_manager",
    "get_config",
    "get_company_list",
    "get_llm_config",
    "get_data_source_config",
    "reload_configs",
    # Build and quality modules
    "BuildTracker",
    "QualityReporter",
    "setup_quality_reporter",
    "MetadataManager",
    # Utility modules (legacy)
    "Snowflake",
    "generate_snowflake_id",
    "generate_snowflake_str",
    # Legacy compatibility
    "data_access",
    "get_legacy_data_path",
    # Version info
    "__version__",
    "__version_info__",
]
