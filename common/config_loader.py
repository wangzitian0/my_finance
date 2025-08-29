#!/usr/bin/env python3
"""
DEPRECATED: Unified Configuration Loader - Replaced by config_manager.py

Issue #185: Configuration SSOT Unification
- This module is deprecated in favor of config_manager.py
- All classes and functions redirect to config_manager with deprecation warnings
- Legacy imports will continue to work but will show deprecation warnings

Migration Guide:
OLD: from common.config_loader import config_loader; config_loader.load_dataset_config('m7')
NEW: from common.config_manager import config_manager; config_manager.load_dataset_config('m7')
"""

import os
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Add common to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.core.directory_manager import directory_manager


class ConfigLoader:
    """
    DEPRECATED: Unified configuration loader using common library

    This class is deprecated. Use config_manager.ConfigManager instead.
    """

    def __init__(self):
        warnings.warn(
            "ConfigLoader from common.config_loader is deprecated. "
            "Use 'from common.config_manager import config_manager' instead. "
            "This class will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.directory_manager = directory_manager
        self.config_dir = directory_manager.get_config_path()

    def load_dataset_config(self, tier: str) -> Dict[str, Any]:
        """Load dataset configuration for given tier (f2, m7, n100, v3k)"""
        # Map tier names to actual config file names
        tier_config_map = {
            "f2": "list_fast_2.yml",
            "m7": "list_magnificent_7.yml",
            "n100": "list_nasdaq_100.yml",
            "v3k": "list_vti_3500.yml",
        }

        config_file = tier_config_map.get(tier)
        if not config_file:
            # Fallback to pattern for unknown tiers
            config_file = f"list_{tier}.yml"

        return self._load_config_file(config_file)

    def load_sec_edgar_config(self, tier: str) -> Dict[str, Any]:
        """Load SEC Edgar configuration for given tier"""
        config_file = f"sec_edgar_{tier}.yml"
        return self._load_config_file(config_file)

    def load_yfinance_config(self) -> Dict[str, Any]:
        """Load YFinance configuration"""
        return self._load_config_file("stage_00_original_yfinance.yml")

    def load_stage_config(self, stage_name: str) -> Dict[str, Any]:
        """Load stage configuration by name"""
        config_file = f"stage_{stage_name}.yml"
        return self._load_config_file(config_file)

    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load a specific configuration file"""
        config_path = self.config_dir / filename

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filename}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading config {filename}: {e}")

    def get_available_tiers(self) -> list[str]:
        """Get list of available dataset tiers"""
        tiers = []
        for config_file in self.config_dir.glob("list_*.yml"):
            tier = config_file.stem.replace("list_", "")
            tiers.append(tier)
        return sorted(tiers)

    def get_config_path(self, filename: str) -> Path:
        """Get full path to a configuration file"""
        return self.config_dir / filename

    def config_exists(self, filename: str) -> bool:
        """Check if configuration file exists"""
        return (self.config_dir / filename).exists()


# Global instance for easy import (deprecated, redirects to config_manager)
config_loader = ConfigLoader()

# Add redirect to config_manager functionality
try:
    from .config_manager import config_manager

    # Override methods to redirect to config_manager
    def _redirect_load_dataset_config(tier: str) -> Dict[str, Any]:
        return config_manager.load_dataset_config(tier)

    def _redirect_load_sec_edgar_config(tier: str) -> Dict[str, Any]:
        return config_manager.load_sec_edgar_config(tier)

    def _redirect_load_yfinance_config() -> Dict[str, Any]:
        return config_manager.load_yfinance_config()

    def _redirect_get_available_tiers() -> list[str]:
        return config_manager.get_available_tiers()

    def _redirect_config_exists(filename: str) -> bool:
        return config_manager.config_exists(filename)

    # Monkey patch the global instance to redirect to config_manager
    config_loader.load_dataset_config = _redirect_load_dataset_config
    config_loader.load_sec_edgar_config = _redirect_load_sec_edgar_config
    config_loader.load_yfinance_config = _redirect_load_yfinance_config
    config_loader.get_available_tiers = _redirect_get_available_tiers
    config_loader.config_exists = _redirect_config_exists

except ImportError:
    # If config_manager not available, use legacy implementation
    pass
