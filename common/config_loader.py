#!/usr/bin/env python3
"""
Unified Configuration Loader
Centralized configuration management using common library for all config files.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Add common to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.directory_manager import DirectoryManager


class ConfigLoader:
    """Unified configuration loader using common library"""

    def __init__(self):
        self.directory_manager = DirectoryManager()
        self.config_dir = self.directory_manager.get_config_path()

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


# Global instance for easy import
config_loader = ConfigLoader()
