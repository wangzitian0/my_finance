#!/usr/bin/env python3
"""
Orthogonal Configuration System
Three independent dimensions: Stock Lists × Data Sources × Scenarios
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

# Add common to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.directory_manager import DirectoryManager


@dataclass
class StockList:
    """Stock list configuration"""

    name: str
    description: str
    tickers: List[str]
    companies: Dict[str, Dict[str, str]]  # ticker -> {name, cik, sector, ...}
    tier: str  # f2, m7, n100, v3k


@dataclass
class DataSource:
    """Data source configuration"""

    name: str
    description: str
    enabled: bool
    api_config: Dict[str, Any]
    rate_limits: Dict[str, Any]
    data_types: List[str]  # ['historical_prices', 'financials', 'filings']


@dataclass
class Scenario:
    """Scenario/stage configuration"""

    name: str
    description: str
    data_sources: List[str]  # Which data sources to use
    processing_mode: str  # 'full', 'incremental', 'test'
    output_formats: List[str]
    quality_thresholds: Dict[str, float]


class OrthogonalConfigLoader:
    """Dynamic configuration loader for orthogonal dimensions"""

    def __init__(self):
        self.directory_manager = DirectoryManager()
        self.config_root = self.directory_manager.get_config_path()

        self.stock_lists_dir = self.config_root / "stock_lists"
        self.data_sources_dir = self.config_root / "data_sources"
        self.scenarios_dir = self.config_root / "scenarios"

        # Ensure directories exist
        for dir_path in [self.stock_lists_dir, self.data_sources_dir, self.scenarios_dir]:
            dir_path.mkdir(exist_ok=True)

    def list_available_configs(self) -> Dict[str, List[str]]:
        """List all available configurations in each dimension"""
        return {
            "stock_lists": self._list_configs(self.stock_lists_dir),
            "data_sources": self._list_configs(self.data_sources_dir),
            "scenarios": self._list_configs(self.scenarios_dir),
        }

    def _list_configs(self, directory: Path) -> List[str]:
        """List configuration files in a directory"""
        if not directory.exists():
            return []
        return [f.stem for f in directory.glob("*.yml")]

    def load_stock_list(self, name: str) -> StockList:
        """Load stock list configuration - supports both orthogonal and legacy formats"""
        # Try orthogonal format first
        orthogonal_path = self.stock_lists_dir / f"{name}.yml"

        if orthogonal_path.exists():
            config = self._load_yaml(orthogonal_path)
            return StockList(
                name=name,
                description=config.get("description", ""),
                tickers=list(config.get("companies", {}).keys()),
                companies=config.get("companies", {}),
                tier=config.get("tier", name),
            )

        # Fallback to legacy format
        legacy_mapping = {
            "f2": "list_fast_2.yml",
            "m7": "list_magnificent_7.yml",
            "n100": "list_nasdaq_100.yml",
            "v3k": "list_vti_3500.yml",
        }

        legacy_file = legacy_mapping.get(name)
        if legacy_file:
            legacy_path = self.config_root / legacy_file
            if legacy_path.exists():
                config = self._load_yaml(legacy_path)

                # Handle legacy reference_config format (for F2)
                companies = {}
                if "reference_config" in config:
                    ref_config_path = self.config_root / config["reference_config"]
                    ref_config = self._load_yaml(ref_config_path)
                    selected = config.get("selected_companies", ["MSFT", "NVDA"])
                    all_companies = ref_config.get("companies", {})
                    for ticker in selected:
                        if ticker in all_companies:
                            companies[ticker] = all_companies[ticker]
                else:
                    companies = config.get("companies", {})

                return StockList(
                    name=name,
                    description=config.get("description", ""),
                    tickers=list(companies.keys()),
                    companies=companies,
                    tier=config.get("tier", name),
                )

        raise FileNotFoundError(f"Stock list configuration not found: {name}")

    def load_data_source(self, name: str) -> DataSource:
        """Load data source configuration - supports both orthogonal and legacy formats"""
        # Try orthogonal format first
        orthogonal_path = self.data_sources_dir / f"{name}.yml"

        if orthogonal_path.exists():
            config = self._load_yaml(orthogonal_path)
            return DataSource(
                name=name,
                description=config.get("description", ""),
                enabled=config.get("enabled", True),
                api_config=config.get("api_config", {}),
                rate_limits=config.get("rate_limits", {}),
                data_types=config.get("data_types", []),
            )

        # Fallback to legacy format
        legacy_mapping = {
            "yfinance": "stage_00_original_yfinance.yml",
            "sec_edgar": "stage_00_original_sec_edgar.yml",
        }

        legacy_file = legacy_mapping.get(name)
        if legacy_file:
            legacy_path = self.config_root / legacy_file
            if legacy_path.exists():
                config = self._load_yaml(legacy_path)

                # Convert legacy format to orthogonal format
                return DataSource(
                    name=name,
                    description=config.get("description", f"Legacy {name} configuration"),
                    enabled=True,  # Assume enabled in legacy
                    api_config=config,  # Use entire config as api_config
                    rate_limits=config.get("collection", {}),
                    data_types=config.get(
                        "filing_types",
                        (
                            list(config.get("periods", {}).keys())
                            if name == "yfinance"
                            else ["10K", "10Q", "8K"]
                        ),
                    ),
                )

        raise FileNotFoundError(f"Data source configuration not found: {name}")

    def load_scenario(self, name: str) -> Scenario:
        """Load scenario configuration"""
        config_path = self.scenarios_dir / f"{name}.yml"
        config = self._load_yaml(config_path)

        return Scenario(
            name=name,
            description=config.get("description", ""),
            data_sources=config.get("data_sources", []),
            processing_mode=config.get("processing_mode", "full"),
            output_formats=config.get("output_formats", ["json"]),
            quality_thresholds=config.get("quality_thresholds", {}),
        )

    def build_runtime_config(
        self, stock_list: str, data_sources: List[str], scenario: str
    ) -> Dict[str, Any]:
        """
        Dynamically build runtime configuration by combining orthogonal dimensions

        Args:
            stock_list: Name of stock list (f2, m7, n100, v3k)
            data_sources: List of data source names ['yfinance', 'sec_edgar']
            scenario: Scenario name ('development', 'testing', 'production')

        Returns:
            Combined runtime configuration
        """
        # Load each dimension
        stocks = self.load_stock_list(stock_list)
        sources = [self.load_data_source(src) for src in data_sources]
        scene = self.load_scenario(scenario)

        # Validate data sources are available in scenario
        available_sources = set(scene.data_sources)
        requested_sources = set(data_sources)
        if not requested_sources.issubset(available_sources):
            missing = requested_sources - available_sources
            raise ValueError(f"Data sources {missing} not available in scenario '{scenario}'")

        # Build combined configuration
        runtime_config = {
            "stock_list": {
                "name": stocks.name,
                "tickers": stocks.tickers,
                "companies": stocks.companies,
                "count": len(stocks.tickers),
            },
            "data_sources": {
                source.name: {
                    "enabled": source.enabled,
                    "config": source.api_config,
                    "rate_limits": source.rate_limits,
                    "data_types": source.data_types,
                }
                for source in sources
            },
            "scenario": {
                "name": scene.name,
                "processing_mode": scene.processing_mode,
                "output_formats": scene.output_formats,
                "quality_thresholds": scene.quality_thresholds,
            },
            "runtime_info": {
                "combination": f"{stock_list}_{'+'.join(data_sources)}_{scenario}",
                "generated_at": "runtime",
            },
        }

        return runtime_config

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration file"""
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}")


# Global instance
orthogonal_config = OrthogonalConfigLoader()
