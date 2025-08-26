#!/usr/bin/env python3
"""
Unified test configuration for all test tiers (test, M7, nasdaq100, vti).
Provides consistent configuration management across different test scenarios.
"""

import os

# Add common directory to path for DirectoryManager
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common.directory_manager import DirectoryManager


class DatasetTier(Enum):
    """Data tiers for testing strategy - Four-tier system"""

    F2 = "f2"    # Fast 2 companies (development testing)
    M7 = "m7"    # Magnificent 7 (standard/PR testing)
    N100 = "n100"  # NASDAQ 100 (validation testing)
    V3K = "v3k"    # VTI 3500+ (production testing)


@dataclass
class TestConfig:
    """Unified test configuration"""

    tier: DatasetTier
    config_file: str
    expected_tickers: list = field(default_factory=list)
    timeout_seconds: int = 300
    max_retries: int = 3
    data_sources: list = field(default_factory=lambda: ["yfinance"])
    enable_sec_edgar: bool = False
    enable_graph_rag: bool = False

    def __post_init__(self):
        """Set tier-specific defaults"""
        # Normalize legacy aliases
        tier_value = self.tier.value
        if tier_value == "test":
            tier_value = "f2"
        elif tier_value == "nasdaq100":
            tier_value = "n100"
        elif tier_value == "vti":
            tier_value = "v3k"

        if tier_value == "f2":
            self.expected_tickers = ["MSFT", "NVDA"]  # Fast 2
            self.timeout_seconds = 120  # 2 minutes
            self.enable_sec_edgar = False
            self.enable_graph_rag = False
        elif tier_value == "m7":
            self.expected_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
            self.timeout_seconds = 300  # 5 minutes
            self.enable_sec_edgar = True
            self.enable_graph_rag = True
        elif tier_value == "n100":
            self.timeout_seconds = 1800  # 30 minutes
            self.enable_sec_edgar = True
            self.enable_graph_rag = True
        elif tier_value == "v3k":
            self.timeout_seconds = 7200  # 2 hours
            self.enable_sec_edgar = False  # Too expensive
            self.enable_graph_rag = True


class TestConfigManager:
    """Manages test configurations for different dataset tiers"""

    CONFIG_MAP = {
        # Primary four-tier system
        DatasetTier.F2: TestConfig(tier=DatasetTier.F2, config_file="list_fast_2.yml"),
        DatasetTier.M7: TestConfig(tier=DatasetTier.M7, config_file="list_magnificent_7.yml"),
        DatasetTier.N100: TestConfig(tier=DatasetTier.N100, config_file="list_nasdaq_100.yml"),
        DatasetTier.V3K: TestConfig(tier=DatasetTier.V3K, config_file="list_vti_3500.yml"),
    }

    def __init__(self, base_path: str = None):
        if base_path is None:
            # Use DirectoryManager to get correct config path
            directory_manager = DirectoryManager()
            self.config_dir = directory_manager.get_config_path()
        else:
            self.base_path = Path(base_path)
            self.config_dir = self.base_path / "data" / "config"

    def get_config(self, tier: DatasetTier) -> TestConfig:
        """Get test configuration for specified tier"""
        return self.CONFIG_MAP[tier]

    def load_yaml_config(self, tier: DatasetTier) -> Dict[str, Any]:
        """Load YAML configuration file for tier"""
        config = self.get_config(tier)
        config_path = self.config_dir / config.config_file

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def get_expected_file_count(self, tier: DatasetTier) -> Dict[str, int]:
        """Get expected file counts for validation"""
        config = self.get_config(tier)

        if tier == DatasetTier.TEST:
            return {
                "yfinance_files": 1,  # Single AAPL file
                "sec_edgar_files": 0,
                "total_tickers": 1,
            }
        elif tier == DatasetTier.M7:
            return {
                "yfinance_files": 21,  # 7 tickers * 3 timeframes
                "sec_edgar_files": (
                    84 if config.enable_sec_edgar else 0
                ),  # 7 tickers * 12 filings avg
                "total_tickers": 7,
            }
        elif tier == DatasetTier.NASDAQ100:
            return {
                "yfinance_files": 300,  # 100+ tickers * 3 timeframes
                "sec_edgar_files": 0,  # Not enabled for NASDAQ100
                "total_tickers": 100,
            }
        elif tier == DatasetTier.VTI:
            return {
                "yfinance_files": 15000,  # ~5000 tickers * 3 timeframes
                "sec_edgar_files": 0,  # Too expensive
                "total_tickers": 5000,
            }

    def validate_config_files(self) -> Dict[DatasetTier, bool]:
        """Validate that all required config files exist"""
        results = {}

        for tier, config in self.CONFIG_MAP.items():
            config_path = self.config_dir / config.config_file
            results[tier] = config_path.exists()

        return results

    def get_data_paths(self, tier: DatasetTier) -> Dict[str, Path]:
        """Get data paths for specified tier"""
        base_data_path = self.base_path / "data"

        return {
            "extract": base_data_path / "stage_01_extract",
            "transform": base_data_path / "stage_02_transform",
            "load": base_data_path / "stage_03_load",
            "build": base_data_path / "build",
            "reports": base_data_path / "reports",
            "config": self.config_dir / self.get_config(tier).config_file,
        }


# Global instance for easy access
test_config_manager = TestConfigManager()


def get_test_config(tier_name: str) -> TestConfig:
    """Get test config by tier name (convenience function)"""
    tier = DatasetTier(tier_name)
    return test_config_manager.get_config(tier)


def validate_test_environment() -> Dict[str, Any]:
    """Validate test environment for all tiers"""
    manager = TestConfigManager()

    return {
        "config_files": manager.validate_config_files(),
        "base_path_exists": manager.base_path.exists(),
        "config_dir_exists": manager.config_dir.exists(),
        "data_structure": {
            "stage_01_extract": (manager.base_path / "data" / "stage_01_extract").exists(),
            "stage_02_transform": (manager.base_path / "data" / "stage_02_transform").exists(),
            "stage_03_load": (manager.base_path / "data" / "stage_03_load").exists(),
            "build": (manager.base_path / "data" / "build").exists(),
        },
    }
