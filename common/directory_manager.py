#!/usr/bin/env python3
"""
SSOT (Single Source of Truth) Directory Management System
Centralized directory path management for the entire project.

This module implements DRY and SSOT principles for directory management,
ensuring that all data storage locations can be easily changed without
affecting the entire codebase.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import yaml


class StorageBackend(Enum):
    """Supported storage backends"""

    LOCAL_FS = "local_filesystem"
    CLOUD_S3 = "aws_s3"
    CLOUD_GCS = "gcp_gcs"
    CLOUD_AZURE = "azure_blob"


class DataLayer(Enum):
    """Five-Layer Data Architecture (Issue #122)"""

    RAW_DATA = "stage_00_raw"  # Raw Data Layer - Immutable source data
    DAILY_DELTA = "stage_01_daily_delta"  # Daily Delta Layer - Incremental changes
    DAILY_INDEX = "stage_02_daily_index"  # Daily Index Layer - New embeddings, entities, relationships
    GRAPH_RAG = "stage_03_graph_rag"  # Graph RAG Layer - Unified knowledge base (single source of truth)
    QUERY_RESULTS = "stage_04_query_results"  # Query Results Layer - Analysis and reports


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
        if config_path.exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()

    def _default_config(self) -> Dict:
        """Default directory structure configuration"""
        return {
            "storage": {"backend": "local_filesystem", "root_path": "data"},
            "layers": {
                "layer_01_raw": {
                    "description": "Immutable source data",
                    "subdirs": ["sec-edgar", "yfinance", "manual"],
                },
                "layer_02_delta": {
                    "description": "Daily incremental changes",
                    "subdirs": ["additions", "modifications", "deletions"],
                },
                "layer_03_index": {
                    "description": "New vectors, entities, relationships",
                    "subdirs": ["vectors", "entities", "relationships", "embeddings"],
                },
                "layer_04_rag": {
                    "description": "Unified knowledge base",
                    "subdirs": ["graph_db", "vector_store", "cache"],
                },
                "layer_05_results": {
                    "description": "Analysis and reports",
                    "subdirs": ["dcf_reports", "analytics", "exports"],
                },
            },
            "common": {"config": "common/config", "logs": "logs", "temp": "temp", "cache": "cache"},
            "legacy": {
                "stage_00_original": "layer_01_raw",
                "stage_01_extract": "layer_02_delta",
                "stage_02_transform": "layer_03_index",
                "stage_03_load": "layer_04_rag",
                "stage_99_build": "layer_05_results",
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
        for legacy_stage, new_layer in self.config["legacy_mapping"].items():
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


def ensure_data_structure():
    """Ensure all data directories exist"""
    directory_manager.ensure_directories()
