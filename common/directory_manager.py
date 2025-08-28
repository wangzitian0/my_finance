#!/usr/bin/env python3
"""
SSOT (Single Source of Truth) Directory Management System
Centralized directory path management for the entire project.

This module implements DRY and SSOT principles for directory management,
ensuring that all data storage locations can be easily changed without
affecting the entire codebase.

Issue #122: Five-Layer Data Architecture Implementation
- stage_00_raw: Raw Data Layer - Immutable source data
- stage_01_daily_delta: Daily Delta Layer - Incremental changes
- stage_02_daily_index: Daily Index Layer - Vectors, entities, relationships
- stage_03_graph_rag: Graph RAG Layer - Unified knowledge base
- stage_04_query_results: Query Results Layer - Analysis and reports

Features:
- Backend abstraction (local_filesystem, aws_s3, gcp_gcs, azure_blob)
- Legacy path mapping for backward compatibility
- Unified interface replacing data_access.py functionality
- Storage optimization configurations per layer
- Performance targets: <100ms query response (Issue #122)
"""

import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None


class StorageBackend(Enum):
    """Supported storage backends"""

    LOCAL_FS = "local_filesystem"
    CLOUD_S3 = "aws_s3"
    CLOUD_GCS = "gcp_gcs"
    CLOUD_AZURE = "azure_blob"


class DataLayer(Enum):
    """Five-Layer Data Architecture (Issue #122)

    Maps to directory_structure.yml configuration for flexible storage backends.
    Uses stage-based naming for consistency with existing codebase.
    """

    RAW_DATA = "layer_01_raw"  # Layer 1 - Immutable source data
    DAILY_DELTA = "layer_02_delta"  # Layer 2 - Incremental changes
    DAILY_INDEX = "layer_03_index"  # Layer 3 - Vectors, entities, relationships
    GRAPH_RAG = "layer_04_rag"  # Layer 4 - Unified knowledge base
    QUERY_RESULTS = "layer_05_results"  # Layer 5 - Analysis and reports


class DirectoryManager:
    """
    SSOT for all directory paths in the project.

    This class centralizes all path management to support:
    - DRY principle: Define paths once, use everywhere
    - SSOT principle: Single configuration point for all paths
    - Future storage migration: Easy backend switching
    - Multi-environment support: dev, test, prod
    """

    def __init__(
        self, root_path: Optional[Path] = None, backend: StorageBackend = StorageBackend.LOCAL_FS
    ):
        self.root_path = root_path or Path(__file__).parent.parent
        self.backend = backend
        self._load_config()

    def _load_config(self):
        """Load directory configuration from YAML file"""
        config_path = self.root_path / "common" / "config" / "directory_structure.yml"
        if config_path.exists() and HAS_YAML:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()

    def _default_config(self) -> Dict:
        """Default directory structure configuration"""
        return {
            "storage": {"backend": "local_filesystem", "root_path": "build_data"},
            "layers": {
                "stage_00_raw": {
                    "description": "Raw Data Layer - Immutable source data",
                    "subdirs": ["sec-edgar", "yfinance", "manual", "reference"],
                },
                "stage_01_daily_delta": {
                    "description": "Daily Delta Layer - Incremental daily changes",
                    "subdirs": ["additions", "modifications", "deletions", "metadata"],
                },
                "stage_02_daily_index": {
                    "description": "Daily Index Layer - New embeddings, entities, relationships",
                    "subdirs": ["vectors", "entities", "relationships", "embeddings", "indices"],
                },
                "stage_03_graph_rag": {
                    "description": "Graph RAG Layer - Unified knowledge base",
                    "subdirs": ["graph_db", "vector_store", "cache", "snapshots"],
                },
                "stage_04_query_results": {
                    "description": "Query Results Layer - Query and analysis results",
                    "subdirs": [
                        "dcf_reports",
                        "analytics",
                        "exports",
                        "dashboards",
                        "api_responses",
                    ],
                },
            },
            "common": {"config": "common/config", "logs": "logs", "temp": "temp", "cache": "cache"},
            "legacy_mapping": {
                "stage_00_original": "stage_00_raw",
                "stage_01_extract": "stage_01_daily_delta",
                "stage_02_transform": "stage_02_daily_index",
                "stage_03_load": "stage_03_graph_rag",
                "stage_99_build": "stage_04_query_results",
                "layer_01_raw": "stage_00_raw",
                "layer_02_delta": "stage_01_daily_delta",
                "layer_03_index": "stage_02_daily_index",
                "layer_04_rag": "stage_03_graph_rag",
                "layer_05_results": "stage_04_query_results",
                "data/config": "common/config",
                "data": "build_data",
            },
        }

    def get_data_root(self) -> Path:
        """Get the root data directory"""
        return self.root_path / self.config["storage"]["root_path"]

    def get_layer_path(self, layer: DataLayer, partition: Optional[str] = None) -> Path:
        """
        Get path for a specific data layer

        Args:
            layer: Data layer enum
            partition: Optional partition (e.g., date, company)
        """
        base_path = self.get_data_root() / layer.value

        if partition:
            return base_path / partition
        return base_path

    def get_subdir_path(
        self, layer: DataLayer, subdir: str, partition: Optional[str] = None
    ) -> Path:
        """Get path for a subdirectory within a layer"""
        layer_path = self.get_layer_path(layer, partition)
        return layer_path / subdir

    def get_config_path(self) -> Path:
        """Get configuration directory path"""
        return self.root_path / self.config["common"]["config"]

    def get_llm_config_path(self, config_name: Optional[str] = None) -> Path:
        """Get path to LLM configuration files

        Args:
            config_name: Optional specific config file name (e.g., 'deepseek_fast.yml')

        Returns:
            Path to LLM config directory or specific config file
        """
        llm_config_dir = self.get_config_path() / "llm" / "configs"
        if config_name:
            return llm_config_dir / config_name
        return llm_config_dir

    def get_build_path(
        self, build_timestamp: Optional[str] = None, branch: Optional[str] = None
    ) -> Path:
        """Get build directory path for backward compatibility with data_access.py

        Args:
            build_timestamp: Specific build timestamp (YYYYMMDD_HHMMSS format)
            branch: Branch name for feature branch builds

        Returns:
            Path to build directory
        """
        results_layer = self.get_layer_path(DataLayer.QUERY_RESULTS)

        if branch and branch != "main":
            build_base = results_layer.parent / f"stage_04_query_results_{branch}"
        else:
            build_base = results_layer

        if build_timestamp:
            return build_base / f"build_{build_timestamp}"
        else:
            return build_base

    def get_source_path(
        self,
        source: str,
        layer: DataLayer = DataLayer.RAW_DATA,
        date_partition: Optional[str] = None,
        ticker: Optional[str] = None,
    ) -> Path:
        """Get source-specific directory path

        Args:
            source: Data source (yfinance, sec-edgar, etc.)
            layer: Data layer enum
            date_partition: Optional date partition
            ticker: Optional ticker symbol

        Returns:
            Path to source directory
        """
        layer_path = self.get_layer_path(layer)
        source_path = layer_path / source

        if date_partition:
            source_path = source_path / date_partition

        if ticker:
            source_path = source_path / ticker

        return source_path

    def get_logs_path(self) -> Path:
        """Get logs directory path"""
        return self.root_path / self.config["common"]["logs"]

    def get_temp_path(self) -> Path:
        """Get temporary directory path"""
        return self.root_path / self.config["common"]["temp"]

    def get_cache_path(self) -> Path:
        """Get cache directory path"""
        return self.root_path / self.config["common"]["cache"]

    def map_legacy_path(self, legacy_stage: str) -> Optional[DataLayer]:
        """Map legacy stage paths to new layer structure"""
        mapping = {
            "stage_00_original": DataLayer.RAW_DATA,
            "stage_01_extract": DataLayer.DAILY_DELTA,
            "stage_02_transform": DataLayer.DAILY_INDEX,
            "stage_03_load": DataLayer.GRAPH_RAG,
            "stage_99_build": DataLayer.QUERY_RESULTS,
            # Legacy layer names
            "layer_01_raw": DataLayer.RAW_DATA,
            "layer_02_delta": DataLayer.DAILY_DELTA,
            "layer_03_index": DataLayer.DAILY_INDEX,
            "layer_04_rag": DataLayer.GRAPH_RAG,
            "layer_05_results": DataLayer.QUERY_RESULTS,
            # Build data references
            "build_data": DataLayer.QUERY_RESULTS,
            "data": DataLayer.RAW_DATA,
        }
        return mapping.get(legacy_stage)

    def ensure_directories(self):
        """Create all necessary directories"""
        # Create all layer directories
        for layer in DataLayer:
            layer_path = self.get_layer_path(layer)
            layer_path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories for each layer
            layer_config = self.config["layers"].get(layer.value, {})
            for subdir in layer_config.get("subdirs", []):
                subdir_path = layer_path / subdir
                subdir_path.mkdir(parents=True, exist_ok=True)

        # Create common directories
        for common_dir in ["config", "logs", "temp", "cache"]:
            if common_dir == "config":
                # Config is already in common/config
                continue
            path = self.root_path / self.config["common"][common_dir]
            path.mkdir(parents=True, exist_ok=True)

    def migrate_legacy_data(self, dry_run: bool = True):
        """
        Migrate data from legacy stage structure to new layer structure

        Args:
            dry_run: If True, only show what would be migrated
        """
        migrations = []
        data_root = self.get_data_root()

        # Check for legacy directories
        legacy_mapping = self.config.get("legacy_mapping", {})
        for legacy_stage, new_stage in legacy_mapping.items():
            if "/" in legacy_stage:  # Skip config mappings like "data/config"
                continue
            legacy_path = data_root / legacy_stage
            if legacy_path.exists():
                new_layer_enum = self.map_legacy_path(legacy_stage)
                if new_layer_enum:
                    new_path = self.get_layer_path(new_layer_enum)
                    migrations.append((legacy_path, new_path))

        if dry_run:
            print("Migration Plan (DRY RUN):")
            for old_path, new_path in migrations:
                print(f"  {old_path} -> {new_path}")
            return migrations
        else:
            # Perform actual migration
            import shutil

            for old_path, new_path in migrations:
                if new_path.exists():
                    print(f"Warning: {new_path} already exists, skipping {old_path}")
                    continue
                print(f"Migrating: {old_path} -> {new_path}")
                shutil.move(str(old_path), str(new_path))
            return migrations

    def get_storage_info(self) -> Dict:
        """Get current storage configuration info"""
        return {
            "backend": self.backend.value,
            "root_path": str(self.get_data_root()),
            "layers": {layer.name: str(self.get_layer_path(layer)) for layer in DataLayer},
            "common_paths": {
                "config": str(self.get_config_path()),
                "logs": str(self.get_logs_path()),
                "temp": str(self.get_temp_path()),
                "cache": str(self.get_cache_path()),
            },
        }


# Global instance for project-wide use
directory_manager = DirectoryManager()


# Convenience functions for backward compatibility
def get_data_path(layer: DataLayer, subdir: str = None, partition: str = None) -> Path:
    """Get data path using SSOT directory manager"""
    if subdir:
        return directory_manager.get_subdir_path(layer, subdir, partition)
    return directory_manager.get_layer_path(layer, partition)


def get_config_path() -> Path:
    """Get config path using SSOT directory manager"""
    return directory_manager.get_config_path()


def get_llm_config_path(config_name: Optional[str] = None) -> Path:
    """Get LLM config path using SSOT directory manager"""
    return directory_manager.get_llm_config_path(config_name)


def get_build_path(build_timestamp: Optional[str] = None, branch: Optional[str] = None) -> Path:
    """Get build directory path using SSOT directory manager"""
    return directory_manager.get_build_path(build_timestamp, branch)


def get_source_path(
    source: str,
    layer: DataLayer = DataLayer.RAW_DATA,
    date_partition: Optional[str] = None,
    ticker: Optional[str] = None,
) -> Path:
    """Get source-specific directory path using SSOT directory manager"""
    return directory_manager.get_source_path(source, layer, date_partition, ticker)


def ensure_data_structure():
    """Ensure all data directories exist"""
    directory_manager.ensure_directories()
