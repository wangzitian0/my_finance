#!/usr/bin/env python3
"""
Centralized ETL Configuration Loader
Unified management of all ETL configuration reading, supporting three orthogonal dimensions: Stock Lists × Data Sources × Scenarios

Design Principles:
- Centralization: All ETL configurations are read through this module
- Orthogonality: Three dimensions configured independently, combined dynamically at runtime
- Simplicity: Flattened naming convention, intuitive and clear
- Caching: Avoid repeated reads, improve performance
- Validation: Configuration validity checking and error handling
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

# Add common to path
sys.path.insert(0, str(Path(__file__).parent))
from core.directory_manager import directory_manager


@dataclass
class StockListConfig:
    """Stock List Configuration"""

    name: str
    description: str
    tickers: List[str]
    companies: Dict[str, Dict[str, str]]  # ticker -> {name, cik, sector, ...}
    tier: str  # f2, m7, n100, v3k
    max_size_mb: int

    @property
    def count(self) -> int:
        return len(self.tickers)


@dataclass
class DataSourceConfig:
    """Data Source Configuration"""

    name: str
    description: str
    enabled: bool
    api_config: Dict[str, Any]
    rate_limits: Dict[str, Any]
    data_types: List[str]
    output_format: Dict[str, Any]


@dataclass
class ScenarioConfig:
    """Scenario Configuration"""

    name: str
    description: str
    data_sources: List[str]  # Available data source list
    processing_mode: str  # 'full', 'incremental', 'test'
    output_formats: List[str]
    quality_thresholds: Dict[str, float]
    resource_limits: Dict[str, Any]
    optimizations: Dict[str, Any]


@dataclass
class RuntimeETLConfig:
    """Runtime Combined ETL Configuration"""

    stock_list: StockListConfig
    data_sources: Dict[str, DataSourceConfig]  # name -> config
    scenario: ScenarioConfig

    # Runtime information
    combination: str  # f2_yfinance+sec_edgar_development
    generated_at: str

    @property
    def ticker_count(self) -> int:
        return self.stock_list.count

    @property
    def enabled_sources(self) -> List[str]:
        return [name for name, config in self.data_sources.items() if config.enabled]


class ETLConfigLoader:
    """Centralized ETL Configuration Loader"""

    def __init__(self):
        self.directory_manager = directory_manager
        self.config_root = self.directory_manager.get_config_path()
        self.etl_config_dir = self.config_root / "etl"

        # Ensure config directory exists
        self.etl_config_dir.mkdir(exist_ok=True)

        # Configuration cache
        self._cache = {}

        # Map old config names to new file names
        self._stock_list_mapping = {
            "f2": "stock_f2.yml",
            "m7": "stock_m7.yml",
            "n100": "stock_n100.yml",
            "v3k": "stock_v3k.yml",
        }

        self._data_source_mapping = {
            "yfinance": "source_yfinance.yml",
            "sec_edgar": "source_sec_edgar.yml",
        }

        self._scenario_mapping = {
            "development": "scenario_dev.yml",
            "production": "scenario_prod.yml",
        }

    def list_available_configs(self) -> Dict[str, List[str]]:
        """List all available configurations"""
        return {
            "stock_lists": list(self._stock_list_mapping.keys()),
            "data_sources": list(self._data_source_mapping.keys()),
            "scenarios": list(self._scenario_mapping.keys()),
        }

    def load_stock_list(self, name: str) -> StockListConfig:
        """Load stock list configuration"""
        cache_key = f"stock_{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if name not in self._stock_list_mapping:
            raise ValueError(
                f"Unknown stock list: {name}. Available: {list(self._stock_list_mapping.keys())}"
            )

        file_path = self.etl_config_dir / self._stock_list_mapping[name]
        config_data = self._load_yaml(file_path)

        # Parse company information, generate tickers list
        companies = config_data.get("companies", {})
        tickers = list(companies.keys())

        config = StockListConfig(
            name=name,
            description=config_data.get("description", ""),
            tickers=tickers,
            companies=companies,
            tier=config_data.get("tier", name),
            max_size_mb=config_data.get("max_size_mb", 100),
        )

        self._cache[cache_key] = config
        return config

    def load_data_source(self, name: str) -> DataSourceConfig:
        """Load data source configuration"""
        cache_key = f"source_{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if name not in self._data_source_mapping:
            raise ValueError(
                f"Unknown data source: {name}. Available: {list(self._data_source_mapping.keys())}"
            )

        file_path = self.etl_config_dir / self._data_source_mapping[name]
        config_data = self._load_yaml(file_path)

        config = DataSourceConfig(
            name=name,
            description=config_data.get("description", ""),
            enabled=config_data.get("enabled", True),
            api_config=config_data.get("api_config", {}),
            rate_limits=config_data.get("rate_limits", {}),
            data_types=config_data.get("data_types", []),
            output_format=config_data.get("output_format", {}),
        )

        self._cache[cache_key] = config
        return config

    def load_scenario(self, name: str) -> ScenarioConfig:
        """Load scenario configuration"""
        cache_key = f"scenario_{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if name not in self._scenario_mapping:
            raise ValueError(
                f"Unknown scenario: {name}. Available: {list(self._scenario_mapping.keys())}"
            )

        file_path = self.etl_config_dir / self._scenario_mapping[name]
        config_data = self._load_yaml(file_path)

        config = ScenarioConfig(
            name=name,
            description=config_data.get("description", ""),
            data_sources=config_data.get("data_sources", []),
            processing_mode=config_data.get("processing_mode", "full"),
            output_formats=config_data.get("output_formats", ["json"]),
            quality_thresholds=config_data.get("quality_thresholds", {}),
            resource_limits=config_data.get("resource_limits", {}),
            optimizations=config_data.get("optimizations", {}),
        )

        self._cache[cache_key] = config
        return config

    def build_runtime_config(
        self, stock_list: str, data_sources: List[str], scenario: str
    ) -> RuntimeETLConfig:
        """
        Combine orthogonal configurations to generate runtime configuration

        Args:
            stock_list: Stock list name (f2, m7, n100, v3k)
            data_sources: Data source list ['yfinance', 'sec_edgar']
            scenario: Scenario name ('development', 'production')

        Returns:
            Runtime ETL configuration
        """
        # Load configuration for each dimension
        stocks = self.load_stock_list(stock_list)
        sources = {name: self.load_data_source(name) for name in data_sources}
        scene = self.load_scenario(scenario)

        # Validate data sources are available in scenario
        available_sources = set(scene.data_sources)
        requested_sources = set(data_sources)
        if not requested_sources.issubset(available_sources):
            missing = requested_sources - available_sources
            raise ValueError(
                f"Data sources {missing} not available in scenario '{scenario}'. Available: {available_sources}"
            )

        # Generate combination identifier
        combination = f"{stock_list}_{'+'.join(data_sources)}_{scenario}"

        return RuntimeETLConfig(
            stock_list=stocks,
            data_sources=sources,
            scenario=scene,
            combination=combination,
            generated_at="runtime",
        )

    def get_legacy_config_mapping(self) -> Dict[str, str]:
        """Get mapping between old and new config files for migration"""
        return {
            # Stock Lists
            "common/config/stock_lists/f2.yml": "common/config/etl/stock_f2.yml",
            "common/config/stock_lists/m7.yml": "common/config/etl/stock_m7.yml",
            "common/config/stock_lists/n100.yml": "common/config/etl/stock_n100.yml",
            "common/config/stock_lists/v3k.yml": "common/config/etl/stock_v3k.yml",
            # Data Sources
            "common/config/data_sources/yfinance.yml": "common/config/etl/source_yfinance.yml",
            "common/config/data_sources/sec_edgar.yml": "common/config/etl/source_sec_edgar.yml",
            # Scenarios
            "common/config/scenarios/development.yml": "common/config/etl/scenario_dev.yml",
            "common/config/scenarios/production.yml": "common/config/etl/scenario_prod.yml",
        }

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file"""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file does not exist: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing error {file_path}: {e}")
        except Exception as e:
            raise ValueError(f"Configuration file read error {file_path}: {e}")

    def clear_cache(self):
        """Clear cache"""
        self._cache.clear()

    def validate_config_files(self) -> List[str]:
        """Validate that all configuration files exist and have correct format"""
        errors = []

        all_files = {}
        all_files.update({k: self.etl_config_dir / v for k, v in self._stock_list_mapping.items()})
        all_files.update({k: self.etl_config_dir / v for k, v in self._data_source_mapping.items()})
        all_files.update({k: self.etl_config_dir / v for k, v in self._scenario_mapping.items()})

        for name, file_path in all_files.items():
            try:
                self._load_yaml(file_path)
            except Exception as e:
                errors.append(f"{name}: {e}")

        return errors


# Global instance
etl_loader = ETLConfigLoader()


# Convenience functions
def load_stock_list(name: str) -> StockListConfig:
    """Load stock list configuration"""
    return etl_loader.load_stock_list(name)


def load_data_source(name: str) -> DataSourceConfig:
    """Load data source configuration"""
    return etl_loader.load_data_source(name)


def load_scenario(name: str) -> ScenarioConfig:
    """Load scenario configuration"""
    return etl_loader.load_scenario(name)


def build_etl_config(stock_list: str, data_sources: List[str], scenario: str) -> RuntimeETLConfig:
    """Build runtime ETL configuration"""
    return etl_loader.build_runtime_config(stock_list, data_sources, scenario)


def list_available_configs() -> Dict[str, List[str]]:
    """List all available configurations"""
    return etl_loader.list_available_configs()
