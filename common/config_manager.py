#!/usr/bin/env python3
"""
Unified Configuration Management System - SSOT for All Configuration Access
Centralized configuration loading and management for the entire project.

This module implements SSOT principles for configuration management,
providing a unified interface to all configuration files and settings.

SSOT UNIFICATION (Issue #185):
- Replaces config.py, config_loader.py, unified_config_loader.py
- Consolidates 5 overlapping configuration systems
- Maintains backward compatibility with deprecation warnings
- Provides migration path to DirectoryManager

Features:
- Automatic configuration discovery and loading
- Environment-specific configuration overrides
- Configuration validation and schema checking
- Hot-reloading support for development
- Backward compatibility with existing config systems
- Legacy system deprecation warnings
- Full tier-based configuration support
"""

import json
import os
import warnings
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
        self.config_root = config_root or directory_manager.get_config_path()
        self._cache = {}
        self._schemas = self._define_schemas()
        self._load_all_configs()

    def _define_schemas(self) -> Dict[str, ConfigSchema]:
        """Define comprehensive configuration schemas for validation"""
        return {
            # Directory and Infrastructure
            "directory_structure": ConfigSchema(
                name="directory_structure",
                path="directory_structure.yml",
                description="SSOT directory structure configuration",
            ),
            
            # Company Lists (Dataset Tiers)
            "magnificent_7": ConfigSchema(
                name="magnificent_7",
                path="list_magnificent_7.yml",
                description="Magnificent 7 companies configuration (M7 tier)",
            ),
            "nasdaq_100": ConfigSchema(
                name="nasdaq_100",
                path="list_nasdaq_100.yml",
                description="NASDAQ 100 companies configuration (N100 tier)",
            ),
            "fast_2": ConfigSchema(
                name="fast_2",
                path="list_fast_2.yml",
                description="Fast 2 companies for development testing (F2 tier)",
            ),
            "vti_3500": ConfigSchema(
                name="vti_3500",
                path="list_vti_3500.yml",
                description="VTI 3500+ companies for production (V3K tier)",
            ),
            
            # SEC Edgar Configurations
            "sec_edgar_f2": ConfigSchema(
                name="sec_edgar_f2",
                path="sec_edgar_f2.yml",
                description="SEC Edgar configuration for F2 tier",
            ),
            "sec_edgar_m7": ConfigSchema(
                name="sec_edgar_m7",
                path="sec_edgar_m7.yml", 
                description="SEC Edgar configuration for M7 tier",
            ),
            "sec_edgar_n100": ConfigSchema(
                name="sec_edgar_n100",
                path="sec_edgar_n100.yml",
                description="SEC Edgar configuration for N100 tier",
            ),
            "sec_edgar_v3k": ConfigSchema(
                name="sec_edgar_v3k",
                path="sec_edgar_v3k.yml",
                description="SEC Edgar configuration for V3K tier",
            ),
            
            # Stage Configurations
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
            
            # Common Config File
            "common_config": ConfigSchema(
                name="common_config",
                path="../common_config.yml",
                description="Legacy common configuration file",
                required=False,
            ),
        }

    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file with format detection"""
        if not file_path.exists():
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yml", ".yaml"]:
                    return yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == ".json":
                    return json.load(f) or {}
                else:
                    raise ValueError(f"Unsupported config format: {file_path.suffix}")
        except Exception as e:
            print(f"Warning: Failed to load config {file_path}: {e}")
            return {}

    def _load_all_configs(self):
        """Load all configuration files into cache"""
        self._cache.clear()

        # Load schema-defined configs
        for schema_name, schema in self._schemas.items():
            config_path = self.config_root / schema.path
            self._cache[schema_name] = self._load_config_file(config_path)

        # Load LLM configs
        llm_config_dir = self.config_root / "llm" / "configs"
        if llm_config_dir.exists():
            self._cache["llm_configs"] = {}
            for config_file in llm_config_dir.glob("*.yml"):
                config_name = config_file.stem
                self._cache["llm_configs"][config_name] = self._load_config_file(config_file)

    def get_config(self, config_name: str, reload: bool = False) -> Dict[str, Any]:
        """
        Get configuration by name.

        Args:
            config_name: Configuration name (e.g., 'magnificent_7', 'directory_structure')
            reload: Force reload from file

        Returns:
            Configuration dictionary
        """
        if reload or config_name not in self._cache:
            if config_name in self._schemas:
                config_path = self.config_root / self._schemas[config_name].path
                self._cache[config_name] = self._load_config_file(config_path)
            else:
                return {}

        return self._cache.get(config_name, {})

    def get_company_list(self, list_name: str) -> List[Dict[str, Any]]:
        """
        Get company list configuration.

        Args:
            list_name: List name ('magnificent_7', 'nasdaq_100', 'fast_2', 'vti_3500')

        Returns:
            List of company dictionaries with ticker, name, cik
        """
        config = self.get_config(list_name)
        return config.get("companies", [])

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
            source: Data source name ('sec_edgar', 'yfinance')
            stage: Stage identifier

        Returns:
            Data source configuration dictionary
        """
        config_key = f"{stage}_original_{source}"
        return self.get_config(config_key)

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

    # ============================================================================
    # TIER-BASED CONFIGURATION METHODS (Replaces config_loader.py)
    # ============================================================================

    def load_dataset_config(self, tier: str) -> Dict[str, Any]:
        """
        Load dataset configuration for given tier (f2, m7, n100, v3k)
        Replaces config_loader.load_dataset_config()
        """
        tier_config_map = {
            "f2": "fast_2",
            "m7": "magnificent_7", 
            "n100": "nasdaq_100",
            "v3k": "vti_3500",
        }
        
        config_name = tier_config_map.get(tier.lower())
        if not config_name:
            # Try direct tier name
            config_name = tier.lower()
            
        return self.get_config(config_name)

    def load_sec_edgar_config(self, tier: str) -> Dict[str, Any]:
        """
        Load SEC Edgar configuration for given tier
        Replaces config_loader.load_sec_edgar_config()
        """
        config_name = f"sec_edgar_{tier.lower()}"
        return self.get_config(config_name)

    def load_yfinance_config(self) -> Dict[str, Any]:
        """
        Load YFinance configuration
        Replaces config_loader.load_yfinance_config()
        """
        return self.get_config("stage_00_original_yfinance")

    def load_stage_config(self, stage_name: str) -> Dict[str, Any]:
        """
        Load stage configuration by name
        Replaces config_loader.load_stage_config()
        """
        config_name = f"stage_{stage_name}"
        return self.get_config(config_name)

    def get_available_tiers(self) -> List[str]:
        """
        Get list of available dataset tiers
        Replaces config_loader.get_available_tiers()
        """
        return ["f2", "m7", "n100", "v3k"]

    def config_exists(self, config_name: str) -> bool:
        """
        Check if configuration file exists
        Replaces config_loader.config_exists()
        """
        config_path = self.get_config_path(config_name)
        return config_path is not None and config_path.exists()

    # ============================================================================
    # UNIFIED DATASET CONFIGURATION METHODS (Replaces unified_config_loader.py)
    # ============================================================================

    def get_company_tickers(self, tier: str) -> List[str]:
        """
        Get list of ticker symbols for tier
        Replaces unified_config_loader.get_company_tickers()
        """
        config = self.load_dataset_config(tier)
        companies = config.get("companies", {})
        if isinstance(companies, list):
            # Handle legacy list format
            return [company.get("ticker", "") for company in companies if company.get("ticker")]
        elif isinstance(companies, dict):
            # Handle dict format
            return list(companies.keys())
        return []

    def get_company_info(self, tier: str, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get company information for specific ticker
        Replaces unified_config_loader.get_company_info()
        """
        config = self.load_dataset_config(tier)
        companies = config.get("companies", {})
        
        if isinstance(companies, dict):
            return companies.get(ticker)
        elif isinstance(companies, list):
            # Search in list format
            for company in companies:
                if company.get("ticker") == ticker:
                    return company
        return None

    def get_cik_mapping(self, tier: str) -> Dict[str, str]:
        """
        Get ticker to CIK mapping for SEC data retrieval
        Replaces unified_config_loader.get_cik_mapping()
        """
        config = self.load_dataset_config(tier)
        companies = config.get("companies", {})
        cik_mapping = {}
        
        if isinstance(companies, dict):
            for ticker, company_info in companies.items():
                if company_info and company_info.get("cik"):
                    # Normalize CIK format
                    cik_normalized = str(company_info["cik"]).zfill(10)
                    cik_mapping[ticker] = cik_normalized
        elif isinstance(companies, list):
            for company in companies:
                ticker = company.get("ticker")
                cik = company.get("cik")
                if ticker and cik:
                    cik_mapping[ticker] = str(cik).zfill(10)
                    
        return cik_mapping

    def is_sec_enabled(self, tier: str) -> bool:
        """
        Check if SEC Edgar data is enabled for tier
        Replaces unified_config_loader.is_sec_enabled()
        """
        config = self.load_dataset_config(tier)
        data_sources = config.get("data_sources", {})
        if "sec_edgar" in data_sources:
            return data_sources["sec_edgar"].get("enabled", False)
        return False

    def get_timeout_seconds(self, tier: str) -> int:
        """
        Get timeout setting for tier
        Replaces unified_config_loader.get_timeout_seconds()
        """
        config = self.load_dataset_config(tier)
        validation = config.get("validation", {})
        return validation.get("timeout_seconds", 300)  # Default 5 minutes

    def get_expected_file_counts(self, tier: str) -> Dict[str, int]:
        """
        Get expected file counts for validation
        Replaces unified_config_loader.get_expected_file_counts()
        """
        config = self.load_dataset_config(tier)
        return config.get("expected_files", {})

    def validate_tier_config(self, tier: str) -> bool:
        """
        Validate that configuration for tier is complete and valid
        Replaces unified_config_loader.validate_tier_config()
        """
        try:
            config = self.load_dataset_config(tier)
            if not config:
                return False
                
            companies = config.get("companies", {})
            if not companies:
                return False
                
            ticker_count = config.get("ticker_count", 0)
            actual_count = len(self.get_company_tickers(tier))
            if ticker_count != actual_count:
                return False
                
            return True
        except Exception:
            return False

    # ============================================================================
    # LEGACY COMMON CONFIG SUPPORT (Replaces config.py)
    # ============================================================================

    def load_common_config(self) -> Dict[str, Any]:
        """
        Load the common configuration from common_config.yml
        Replaces config.load_common_config()
        
        DEPRECATED: Use config_manager.get_config('common_config') instead
        """
        warnings.warn(
            "load_common_config() is deprecated. Use config_manager.get_config('common_config') instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_config("common_config")


# Global configuration manager instance
config_manager = ConfigManager()


# ============================================================================
# GLOBAL CONVENIENCE FUNCTIONS FOR BACKWARD COMPATIBILITY
# ============================================================================

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
    config_manager.reload_all()


# ============================================================================
# LEGACY SYSTEM COMPATIBILITY FUNCTIONS WITH DEPRECATION WARNINGS
# ============================================================================

# Replaces config.py functions
def load_common_config() -> Dict[str, Any]:
    """
    DEPRECATED: Load the common configuration from common_config.yml
    Use config_manager.get_config('common_config') instead
    """
    warnings.warn(
        "load_common_config() from config.py is deprecated. "
        "Use 'from common.config_manager import config_manager; config_manager.get_config('common_config')' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.load_common_config()


# Replaces config_loader.py functions  
def load_dataset_config(tier: str) -> Dict[str, Any]:
    """
    DEPRECATED: Load dataset configuration for given tier
    Use config_manager.load_dataset_config() instead
    """
    warnings.warn(
        "load_dataset_config() from config_loader.py is deprecated. "
        "Use 'from common.config_manager import config_manager; config_manager.load_dataset_config(tier)' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.load_dataset_config(tier)


def load_sec_edgar_config(tier: str) -> Dict[str, Any]:
    """
    DEPRECATED: Load SEC Edgar configuration for given tier
    Use config_manager.load_sec_edgar_config() instead
    """
    warnings.warn(
        "load_sec_edgar_config() from config_loader.py is deprecated. "
        "Use 'from common.config_manager import config_manager; config_manager.load_sec_edgar_config(tier)' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.load_sec_edgar_config(tier)


def load_yfinance_config() -> Dict[str, Any]:
    """
    DEPRECATED: Load YFinance configuration
    Use config_manager.load_yfinance_config() instead
    """
    warnings.warn(
        "load_yfinance_config() from config_loader.py is deprecated. "
        "Use 'from common.config_manager import config_manager; config_manager.load_yfinance_config()' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.load_yfinance_config()


# Replaces unified_config_loader.py functions
def load_tier_config(tier: str) -> Dict[str, Any]:
    """
    DEPRECATED: Load configuration for tier
    Use config_manager.load_dataset_config() instead
    """
    warnings.warn(
        "load_tier_config() from unified_config_loader.py is deprecated. "
        "Use 'from common.config_manager import config_manager; config_manager.load_dataset_config(tier)' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.load_dataset_config(tier)


def get_tier_tickers(tier: str) -> List[str]:
    """
    DEPRECATED: Get ticker list for tier
    Use config_manager.get_company_tickers() instead
    """
    warnings.warn(
        "get_tier_tickers() from unified_config_loader.py is deprecated. "
        "Use 'from common.config_manager import config_manager; config_manager.get_company_tickers(tier)' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.get_company_tickers(tier)


def get_tier_cik_mapping(tier: str) -> Dict[str, str]:
    """
    DEPRECATED: Get CIK mapping for tier
    Use config_manager.get_cik_mapping() instead
    """
    warnings.warn(
        "get_tier_cik_mapping() from unified_config_loader.py is deprecated. "
        "Use 'from common.config_manager import config_manager; config_manager.get_cik_mapping(tier)' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return config_manager.get_cik_mapping(tier)


# ============================================================================
# CLASS IMPORTS FOR COMPATIBILITY
# ============================================================================

# Allow imports like "from common.config_manager import ConfigLoader"
class ConfigLoader:
    """
    DEPRECATED: Legacy ConfigLoader class for backward compatibility
    Use ConfigManager instead
    """
    
    def __init__(self):
        warnings.warn(
            "ConfigLoader from config_loader.py is deprecated. "
            "Use 'from common.config_manager import config_manager' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._config_manager = config_manager
    
    def load_dataset_config(self, tier: str) -> Dict[str, Any]:
        return self._config_manager.load_dataset_config(tier)
    
    def load_sec_edgar_config(self, tier: str) -> Dict[str, Any]:
        return self._config_manager.load_sec_edgar_config(tier)
    
    def load_yfinance_config(self) -> Dict[str, Any]:
        return self._config_manager.load_yfinance_config()
    
    def get_available_tiers(self) -> List[str]:
        return self._config_manager.get_available_tiers()
    
    def config_exists(self, filename: str) -> bool:
        return self._config_manager.config_exists(filename)


class UnifiedConfigLoader:
    """
    DEPRECATED: Legacy UnifiedConfigLoader class for backward compatibility
    Use ConfigManager instead
    """
    
    def __init__(self, config_dir: Path = None):
        warnings.warn(
            "UnifiedConfigLoader from unified_config_loader.py is deprecated. "
            "Use 'from common.config_manager import config_manager' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._config_manager = config_manager
    
    def load_config(self, tier: str) -> Dict[str, Any]:
        return self._config_manager.load_dataset_config(tier)
    
    def get_company_tickers(self, tier: str) -> List[str]:
        return self._config_manager.get_company_tickers(tier)
    
    def get_cik_mapping(self, tier: str) -> Dict[str, str]:
        return self._config_manager.get_cik_mapping(tier)
    
    def is_sec_enabled(self, tier: str) -> bool:
        return self._config_manager.is_sec_enabled(tier)
    
    def validate_tier_config(self, tier: str) -> bool:
        return self._config_manager.validate_tier_config(tier)


# Global instances for backward compatibility
config_loader = ConfigLoader()
unified_config_loader = UnifiedConfigLoader()
