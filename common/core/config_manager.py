#!/usr/bin/env python3
"""
Unified Configuration Management System
Centralized configuration loading and management for the entire project.

This module implements SSOT principles for configuration management,
providing a unified interface to all configuration files and settings.

Features:
- Automatic configuration discovery and loading
- Environment-specific configuration overrides
- Configuration validation and schema checking
- Hot-reloading support for development
- Backward compatibility with existing config systems

Issue #184: Moved to core/ as part of library restructuring
"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .directory_manager import directory_manager


class ConfigType(Enum):
    """Configuration file types"""

    COMPANY_LISTS = "company_lists"
    DATA_SOURCES = "data_sources"
    LLM_CONFIGS = "llm_configs"
    DIRECTORY_STRUCTURE = "directory_structure"
    SEC_EDGAR = "sec_edgar"
    STAGE_CONFIGS = "stage_configs"

    # Make sure we have the exact values the tests expect
    @property
    def value(self):
        return self._value_


@dataclass
class ConfigSchema:
    """Configuration schema definition"""

    name: str
    path: str
    required: bool = True
    format: str = "yaml"  # yaml, json
    description: str = ""


class ConfigManager:
    """
    Unified configuration management system.

    Provides centralized access to all configuration files with:
    - Automatic discovery and loading
    - Schema validation
    - Environment overrides
    - Caching for performance
    """

    def __init__(self, config_root: Optional[Path] = None):
        """
        Initialize ConfigManager.

        Args:
            config_root: Root configuration directory. Defaults to common/config/
        """
        self.config_path = config_root or directory_manager.get_config_path()
        self.config_root = self.config_path  # Alias for backward compatibility
        self._config_cache = {}  # Match test expectations
        self._cache = self._config_cache  # Alias for internal use
        self._file_timestamps = {}  # For hot reload detection
        self._schemas = self._define_schemas()
        self._load_all_configs()

    def _define_schemas(self) -> Dict[str, ConfigSchema]:
        """Define configuration schemas for validation"""
        return {
            "directory_structure": ConfigSchema(
                name="directory_structure",
                path="directory_structure.yml",
                description="SSOT directory structure configuration",
            ),
            "magnificent_7": ConfigSchema(
                name="magnificent_7",
                path="list_magnificent_7.yml",
                description="Magnificent 7 companies configuration",
            ),
            "nasdaq_100": ConfigSchema(
                name="nasdaq_100",
                path="list_nasdaq_100.yml",
                description="NASDAQ 100 companies configuration",
            ),
            "fast_2": ConfigSchema(
                name="fast_2",
                path="list_fast_2.yml",
                description="Fast 2 companies for development testing",
            ),
            "vti_3500": ConfigSchema(
                name="vti_3500",
                path="list_vti_3500.yml",
                description="VTI 3500+ companies for production",
            ),
            "sec_edgar_nasdaq100": ConfigSchema(
                name="sec_edgar_nasdaq100",
                path="sec_edgar_nasdaq100.yml",
                description="SEC Edgar configuration for NASDAQ 100",
            ),
            "stage_00_original_sec_edgar": ConfigSchema(
                name="stage_00_original_sec_edgar",
                path="stage_00_original_sec_edgar.yml",
                description="Stage 0 SEC Edgar data source configuration",
            ),
            "stage_00_original_yfinance": ConfigSchema(
                name="stage_00_original_yfinance",
                path="stage_00_original_yfinance.yml",
                description="Stage 0 YFinance data source configuration",
            ),
            "stage_00_target_pre_pr": ConfigSchema(
                name="stage_00_target_pre_pr",
                path="stage_00_target_pre_pr.yml",
                description="Pre-PR target configuration",
            ),
        }

    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file with format detection"""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yml", ".yaml"]:
                    try:
                        result = yaml.safe_load(f) or {}
                    except yaml.YAMLError as e:
                        raise ValueError(f"Failed to parse YAML file {file_path}: {e}")
                elif file_path.suffix.lower() == ".json":
                    try:
                        result = json.load(f) or {}
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Failed to parse JSON file {file_path}: {e}")
                else:
                    raise ValueError(f"Unsupported config format: {file_path.suffix}")

                # Update file timestamp for hot reload detection
                self._file_timestamps[str(file_path)] = file_path.stat().st_mtime
                return result

        except (FileNotFoundError, ValueError):
            raise  # Re-raise expected exceptions
        except Exception as e:
            raise ValueError(f"Failed to load config {file_path}: {e}")

    def _load_all_configs(self):
        """Load all configuration files into cache"""
        self._cache.clear()

        # Load schema-defined configs (gracefully handle missing files)
        for schema_name, schema in self._schemas.items():
            config_path = self.config_root / schema.path
            try:
                self._cache[schema_name] = self._load_config_file(config_path)
            except FileNotFoundError:
                if schema.required:
                    print(f"Warning: Required config {schema_name} not found at {config_path}")
                self._cache[schema_name] = {}

        # Load LLM configs
        llm_config_dir = self.config_root / "llm" / "configs"
        if llm_config_dir.exists():
            self._cache["llm_configs"] = {}
            for config_file in llm_config_dir.glob("*.yml"):
                config_name = config_file.stem
                try:
                    self._cache["llm_configs"][config_name] = self._load_config_file(config_file)
                except (FileNotFoundError, ValueError):
                    self._cache["llm_configs"][config_name] = {}

    def get_config(self, config_name: str, reload: bool = False) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            config_name: Configuration name (e.g., 'magnificent_7', 'directory_structure', 'database')
            reload: Force reload from file

        Returns:
            Configuration dictionary
        """
        if reload or config_name not in self._cache:
            if config_name in self._schemas:
                config_path = self.config_root / self._schemas[config_name].path
                try:
                    self._cache[config_name] = self._load_config_file(config_path)
                except FileNotFoundError:
                    self._cache[config_name] = {}
            else:
                # For configs not in schema (like test configs), try direct filename
                config_path = self.config_path / f"{config_name}.yml"
                if not config_path.exists():
                    config_path = self.config_path / f"{config_name}.yaml"
                if not config_path.exists():
                    config_path = self.config_path / f"{config_name}.json"

                if config_path.exists():
                    try:
                        self._cache[config_name] = self._load_config_file(config_path)
                    except (FileNotFoundError, ValueError):
                        self._cache[config_name] = {}
                else:
                    self._cache[config_name] = {}

        return self._cache.get(config_name, {})

    def get_company_list(self, list_name: str) -> List[Dict[str, Any]]:
        """
        Get company list configuration.

        Args:
            list_name: List name ('magnificent_7', 'nasdaq_100', 'fast_2', 'vti_3500', 'test')

        Returns:
            List of company dictionaries with ticker, name, cik
        """
        # Use cache key for company lists
        cache_key = f"company_list_{list_name}"

        # Check if already cached
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Check if it's in predefined schemas
        if list_name in self._schemas:
            config = self.get_config(list_name)
            companies = config.get("companies", [])
            self._cache[cache_key] = companies
            return companies

        # For test files and dynamic files, try different locations
        possible_paths = [
            self.config_path / f"list_{list_name}.yml",
            self.config_path / "stock_lists" / f"{list_name}.yml",
            self.config_path / "stock_lists" / f"list_{list_name}.yml",
        ]

        for list_file_path in possible_paths:
            if list_file_path.exists():
                config = self._load_config_file(list_file_path)
                companies = config.get("companies", [])
                self._cache[cache_key] = companies
                return companies

        # If not found, raise FileNotFoundError as tests expect
        raise FileNotFoundError(f"Company list '{list_name}' not found")

    def get_llm_config(self, model_name: str = "default") -> Dict[str, Any]:
        """
        Get LLM configuration.

        Args:
            model_name: Model configuration name ('default', 'deepseek_fast', 'local_ollama')

        Returns:
            LLM configuration dictionary
        """
        llm_configs = self._cache.get("llm_configs", {})
        return llm_configs.get(model_name, {})

    def get_data_source_config(self, source: str, stage: str = "stage_00") -> Dict[str, Any]:
        """
        Get data source configuration.

        Args:
            source: Data source name ('sec_edgar', 'yfinance', 'test_source')
            stage: Stage identifier

        Returns:
            Data source configuration dictionary
        """
        # First try the schema-based approach
        config_key = f"{stage}_original_{source}"
        if config_key in self._schemas:
            return self.get_config(config_key)

        # For test configs and other sources, try data_sources directory
        ds_path = self.config_path / "data_sources" / f"{source}.yml"
        if not ds_path.exists():
            ds_path = self.config_path / "data_sources" / f"{source}.yaml"
        if not ds_path.exists():
            ds_path = self.config_path / "data_sources" / f"{source}.json"

        if ds_path.exists():
            return self._load_config_file(ds_path)

        return {}

    def get_directory_config(self) -> Dict[str, Any]:
        """Get directory structure configuration"""
        return self.get_config("directory_structure")

    def list_available_configs(self) -> List[str]:
        """List all available configuration names"""
        return list(self._schemas.keys()) + ["llm_configs"]

    def validate_config(self, config_name: str) -> bool:
        """
        Validate configuration against schema.

        Args:
            config_name: Configuration name to validate

        Returns:
            True if valid, False otherwise
        """
        if config_name not in self._schemas:
            return False

        config = self.get_config(config_name)
        schema = self._schemas[config_name]

        # Basic validation - config exists and is not empty
        if schema.required and not config:
            return False

        return True

    def reload_all(self):
        """Reload all configurations from disk"""
        self._load_all_configs()

    def reload_configs(self):
        """Reload all configurations (alias for reload_all for test compatibility)"""
        self._cache.clear()
        self._config_cache.clear()
        self._file_timestamps.clear()
        self._load_all_configs()

    def load_config(self, config_filename: str) -> Dict[str, Any]:
        """
        Load configuration file by filename (test-compatible API).

        Args:
            config_filename: Configuration filename (e.g., 'database.yml')

        Returns:
            Configuration dictionary
        """
        # Handle direct file access for tests
        config_path = self.config_path / config_filename

        # Check cache first
        if config_filename in self._config_cache:
            # Check if file has been modified
            if config_path.exists():
                current_mtime = config_path.stat().st_mtime
                cached_mtime = self._file_timestamps.get(str(config_path), 0)
                if current_mtime <= cached_mtime:
                    return self._config_cache[config_filename]

        # Load from file
        config_data = self._load_config_file(config_path)
        self._config_cache[config_filename] = config_data
        return config_data

    def load_dataset_config(self, dataset_name: str) -> Dict[str, Any]:
        """Load dataset configuration for testing compatibility"""
        return self.load_config(f"stock_lists/{dataset_name}.yml")

    def get_config_path(self, config_name: str) -> Optional[Path]:
        """
        Get full path to configuration file.

        Args:
            config_name: Configuration name

        Returns:
            Path to configuration file or None if not found
        """
        if config_name in self._schemas:
            return self.config_root / self._schemas[config_name].path
        return None

    def create_config_template(self, config_name: str, template_data: Dict[str, Any]) -> bool:
        """
        Create configuration file from template.

        Args:
            config_name: Configuration name
            template_data: Template data dictionary

        Returns:
            True if created successfully
        """
        config_path = self.get_config_path(config_name)
        if not config_path:
            return False

        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(template_data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error creating config template {config_name}: {e}")
            return False

    def update_config(self, config_name: str, updates: Dict[str, Any], merge: bool = True) -> bool:
        """
        Update configuration file.

        Args:
            config_name: Configuration name
            updates: Dictionary of updates to apply
            merge: If True, merge with existing config. If False, replace entirely.

        Returns:
            True if updated successfully
        """
        config_path = self.get_config_path(config_name)
        if not config_path:
            return False

        try:
            if merge:
                current_config = self.get_config(config_name)
                current_config.update(updates)
                final_config = current_config
            else:
                final_config = updates

            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(final_config, f, default_flow_style=False, sort_keys=False)

            # Update cache
            self._cache[config_name] = final_config
            return True
        except Exception as e:
            print(f"Error updating config {config_name}: {e}")
            return False


# Global configuration manager instance
config_manager = ConfigManager()


# Convenience functions for backward compatibility
def get_config(config_name: str) -> Dict[str, Any]:
    """Get configuration using global config manager"""
    return config_manager.get_config(config_name)


def get_company_list(list_name: str) -> List[Dict[str, Any]]:
    """Get company list using global config manager"""
    return config_manager.get_company_list(list_name)


def get_llm_config(model_name: str = "default") -> Dict[str, Any]:
    """Get LLM configuration using global config manager"""
    return config_manager.get_llm_config(model_name)


def get_data_source_config(source: str, stage: str = "stage_00") -> Dict[str, Any]:
    """Get data source configuration using global config manager"""
    return config_manager.get_data_source_config(source, stage)


def reload_configs():
    """Reload all configurations"""
    config_manager.reload_configs()
