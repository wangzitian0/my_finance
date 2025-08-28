#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility modules for the common library.

This module provides organized utility functions:
- IOOperations: Consolidated I/O utilities
- LoggingSetup: Logging configuration
- DataProcessing: Data transformation utilities
- IDGeneration: ID systems (Snowflake)
- ProgressTracking: Progress and status tracking

Issue #184: Core library restructuring - Utility consolidation
"""

from .data_processing import (
    convert_timestamps_to_iso,
    deep_merge_dicts,
    extract_unique_values,
    filter_companies_by_criteria,
    group_by_field,
    merge_company_lists,
    normalize_ticker_symbol,
    safe_json_serialize,
    validate_company_data,
)
from .id_generation import Snowflake, generate_snowflake_id, generate_snowflake_str
from .io_operations import is_file_recent, sanitize_data, suppress_third_party_logs
from .logging_setup import setup_logger
from .progress_tracking import ProgressTracker, create_progress_bar, get_global_progress_tracker

__all__ = [
    # I/O operations
    "suppress_third_party_logs",
    "is_file_recent",
    "sanitize_data",
    # Logging setup
    "setup_logger",
    # Data processing utilities
    "normalize_ticker_symbol",
    "validate_company_data",
    "merge_company_lists",
    "filter_companies_by_criteria",
    "extract_unique_values",
    "group_by_field",
    "convert_timestamps_to_iso",
    "safe_json_serialize",
    "deep_merge_dicts",
    # ID generation
    "Snowflake",
    "generate_snowflake_id",
    "generate_snowflake_str",
    # Progress tracking
    "create_progress_bar",
    "ProgressTracker",
    "get_global_progress_tracker",
]
