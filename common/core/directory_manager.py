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

Issue #184: Moved to core/ as part of library restructuring
"""

import hashlib
import logging
import os
import subprocess
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

try:
    import yaml
except ImportError:
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
    Uses stage-based naming for consistency with existing codebase structure.
    """

    RAW_DATA = "stage_00_raw"  # Layer 0 - Immutable source data
    DAILY_DELTA = "stage_01_daily_delta"  # Layer 1 - Incremental changes
    DAILY_INDEX = "stage_02_daily_index"  # Layer 2 - Vectors, entities, relationships
    GRAPH_RAG = "stage_03_graph_rag"  # Layer 3 - Unified knowledge base
    QUERY_RESULTS = "stage_04_query_results"  # Layer 4 - Analysis and reports


class DirectoryManager:
    """
    SSOT for all directory paths in the project.

    This class centralizes all path management to support:
    - DRY principle: Define paths once, use everywhere
    - SSOT principle: Single configuration point for all paths
    - Future storage migration: Easy backend switching
    - Multi-environment support: dev, test, prod
    - Enhanced security: Input validation and path sanitization
    - Performance optimization: Caching and concurrent access
    """

    def __init__(
        self, root_path: Optional[Path] = None, backend: StorageBackend = StorageBackend.LOCAL_FS
    ):
        self.root_path = root_path or Path(__file__).parent.parent.parent
        self.backend = backend
        self._path_cache = {}
        self._cache_lock = threading.RLock()
        self._cache_hits = 0
        self._cache_misses = 0
        self.logger = logging.getLogger(__name__)
        self._load_config()

    def _load_config(self):
        """Load directory configuration from YAML file with error handling"""
        config_path = self.root_path / "common" / "config" / "directory_structure.yml"
        try:
            if yaml is None:
                self.logger.warning("PyYAML not available, using default configuration")
                self.config = self._default_config()
                return

            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f)
                    if not isinstance(self.config, dict):
                        raise ValueError("Configuration must be a dictionary")
                    self._validate_config()
            else:
                self.logger.warning(f"Config file not found: {config_path}, using defaults")
                self.config = self._default_config()
        except Exception as e:
            # Catch all exceptions to ensure graceful fallback
            self.logger.error(f"Error loading config: {e}, falling back to defaults")
            self.config = self._default_config()

        # Clear cache when config reloads
        with self._cache_lock:
            self._path_cache.clear()

    def _validate_config(self):
        """Validate configuration structure and content"""
        required_keys = ["storage", "layers", "common"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")

        # Validate storage configuration
        storage_config = self.config["storage"]
        if "backend" not in storage_config or "root_path" not in storage_config:
            raise ValueError("Storage configuration must have 'backend' and 'root_path'")

        # Validate backend type
        backend_value = storage_config["backend"]
        valid_backends = [backend.value for backend in StorageBackend]
        if backend_value not in valid_backends:
            self.logger.warning(f"Unknown backend '{backend_value}', using local_filesystem")
            storage_config["backend"] = "local_filesystem"

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
        Get path for a specific data layer with caching and validation

        Args:
            layer: Data layer enum
            partition: Optional partition (e.g., date, company)
        """
        # Input validation
        if not isinstance(layer, DataLayer):
            raise TypeError("layer must be a DataLayer enum")

        # Sanitize partition if provided
        if partition is not None:
            partition = self._sanitize_path_component(str(partition))

        # Check cache first
        cache_key = (layer, partition)
        with self._cache_lock:
            if cache_key in self._path_cache:
                self._cache_hits += 1
                return self._path_cache[cache_key]
            self._cache_misses += 1

        # Calculate path
        base_path = self.get_data_root() / layer.value

        if partition:
            result_path = base_path / partition
        else:
            result_path = base_path

        # Cache the result
        with self._cache_lock:
            self._path_cache[cache_key] = result_path

        return result_path

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

    def get_agents_local_path(self, agent_name: Optional[str] = None) -> Path:
        """Get agent local documentation path

        Args:
            agent_name: Specific agent name (e.g., 'hrbp-agent', 'agent-coordinator')
                       If None, returns base agents/local path

        Returns:
            Path to agent local directory
        """
        base_path = Path(self.config["agents"]["local"])
        if agent_name:
            return self.root_path / str(base_path).format(agent_name=agent_name)
        return self.root_path / base_path

    def get_agent_performance_path(self, agent_name: str) -> Path:
        """Get agent performance logs path"""
        performance_path = self.config["agents"]["performance"].format(agent_name=agent_name)
        return self.root_path / performance_path

    def get_agent_analysis_path(self, agent_name: str) -> Path:
        """Get agent analysis files path"""
        analysis_path = self.config["agents"]["analysis"].format(agent_name=agent_name)
        return self.root_path / analysis_path

    def get_agent_reports_path(self, agent_name: str) -> Path:
        """Get agent reports path"""
        reports_path = self.config["agents"]["reports"].format(agent_name=agent_name)
        return self.root_path / reports_path

    def get_agent_temp_path(self, agent_name: str) -> Path:
        """Get agent temporary files path"""
        temp_path = self.config["agents"]["temp"].format(agent_name=agent_name)
        return self.root_path / temp_path

    def get_agents_shared_path(self) -> Path:
        """Get shared agent coordination path"""
        return self.root_path / self.config["agents"]["shared"]

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

    def _sanitize_path_component(self, component: str) -> str:
        """Sanitize a path component for security and validity

        Args:
            component: Path component to sanitize

        Returns:
            Sanitized path component

        Raises:
            ValueError: If component contains dangerous sequences
        """
        if not component or not isinstance(component, str):
            raise ValueError("Path component must be a non-empty string")

        # Remove leading/trailing whitespace
        component = component.strip()

        # Check for dangerous patterns
        dangerous_patterns = ["..", "~", "$", "`", "|", ";", "&", ">", "<", "\x00"]
        for pattern in dangerous_patterns:
            if pattern in component:
                raise ValueError(f"Dangerous pattern '{pattern}' found in path component")

        # Don't allow absolute paths
        if os.path.isabs(component):
            raise ValueError("Absolute paths not allowed in path components")

        # Replace problematic characters (if needed)
        import re

        if not re.match(r"^[\w\-./]+$", component):
            self.logger.warning(f"Path component contains special characters: {component}")

        return component

    def _validate_path_within_root(self, path: Path) -> Path:
        """Validate that a path stays within the project root

        Args:
            path: Path to validate

        Returns:
            Validated path

        Raises:
            ValueError: If path traverses outside project root
        """
        try:
            resolved_path = path.resolve()
            root_resolved = self.root_path.resolve()

            # Check if the resolved path is within project root
            resolved_path.relative_to(root_resolved)
            return path

        except ValueError as e:
            raise ValueError(
                f"Path traversal detected: {path} resolves outside project root"
            ) from e

    def _secure_subprocess_run(
        self, args: List[str], timeout: int = 30, **kwargs
    ) -> subprocess.CompletedProcess:
        """Execute subprocess with security validation and timeout

        Args:
            args: Command arguments
            timeout: Maximum execution time in seconds
            **kwargs: Additional subprocess arguments

        Returns:
            CompletedProcess result

        Raises:
            ValueError: If arguments contain dangerous commands
            TimeoutError: If operation times out
            RuntimeError: If subprocess execution fails
        """
        # Validate arguments
        validated_args = self._validate_subprocess_args(args)

        # Set secure defaults
        secure_kwargs = {
            "timeout": min(timeout, 300),  # Max 5 minutes
            "check": False,  # Don't raise on non-zero exit
            "capture_output": True,
            "text": True,
            **kwargs,
        }

        try:
            self.logger.debug(f"Executing subprocess: {' '.join(validated_args)}")
            result = subprocess.run(validated_args, **secure_kwargs)
            return result
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(
                f"Command timed out after {timeout}s: {' '.join(validated_args)}"
            ) from e
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Subprocess execution failed: {e}") from e

    def _validate_subprocess_args(self, args: List[str]) -> List[str]:
        """Validate subprocess arguments for security

        Args:
            args: Command arguments to validate

        Returns:
            Validated arguments

        Raises:
            TypeError: If arguments are not properly typed
            ValueError: If dangerous commands are detected
        """
        if not isinstance(args, list):
            raise TypeError("Subprocess arguments must be a list")

        validated_args = []
        dangerous_commands = ["rm", "del", "format", "mkfs", "dd", "chmod 777", "sudo rm"]

        for arg in args:
            if not isinstance(arg, (str, Path)):
                raise TypeError(f"Invalid argument type: {type(arg)}")

            arg_str = str(arg)
            for dangerous_cmd in dangerous_commands:
                if dangerous_cmd in arg_str.lower():
                    raise ValueError(f"Dangerous command detected: {dangerous_cmd}")

            validated_args.append(arg_str)

        return validated_args

    def _calculate_directory_size(self, path: Path, timeout: int = 30) -> int:
        """Calculate directory size with timeout handling

        Args:
            path: Directory path to calculate size for
            timeout: Maximum time to spend calculating in seconds

        Returns:
            Total size in bytes

        Raises:
            TimeoutError: If calculation times out
        """
        if not path.exists():
            return 0

        result = {"size": 0, "error": None}

        def calculate():
            try:
                total_size = 0
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                        except (OSError, IOError):
                            # Skip files that can't be accessed
                            pass
                result["size"] = total_size
            except Exception as e:
                result["error"] = e

        thread = threading.Thread(target=calculate)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            raise TimeoutError(f"Directory size calculation timed out after {timeout}s")

        if result["error"]:
            raise result["error"]

        return result["size"]

    def get_cache_stats(self) -> Dict[str, int]:
        """Get caching performance statistics

        Returns:
            Dictionary with cache statistics
        """
        with self._cache_lock:
            total_requests = self._cache_hits + self._cache_misses
            hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "cached_items": len(self._path_cache),
            }

    def clear_cache(self):
        """Clear the path resolution cache"""
        with self._cache_lock:
            self._path_cache.clear()
            self._cache_hits = 0
            self._cache_misses = 0
            self.logger.info("Path cache cleared")

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


def get_agents_local_path(agent_name: Optional[str] = None) -> Path:
    """Get agent local documentation path using SSOT directory manager"""
    return directory_manager.get_agents_local_path(agent_name)


def get_agent_performance_path(agent_name: str) -> Path:
    """Get agent performance logs path using SSOT directory manager"""
    return directory_manager.get_agent_performance_path(agent_name)


def get_agent_analysis_path(agent_name: str) -> Path:
    """Get agent analysis files path using SSOT directory manager"""
    return directory_manager.get_agent_analysis_path(agent_name)


def get_agent_reports_path(agent_name: str) -> Path:
    """Get agent reports path using SSOT directory manager"""
    return directory_manager.get_agent_reports_path(agent_name)


def get_agent_temp_path(agent_name: str) -> Path:
    """Get agent temporary files path using SSOT directory manager"""
    return directory_manager.get_agent_temp_path(agent_name)


def get_agents_shared_path() -> Path:
    """Get shared agent coordination path using SSOT directory manager"""
    return directory_manager.get_agents_shared_path()


def ensure_data_structure():
    """Ensure all data directories exist"""
    directory_manager.ensure_directories()
