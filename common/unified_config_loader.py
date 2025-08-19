#!/usr/bin/env python3
"""
Unified Configuration Loader
Handles loading and processing of dataset configurations with unified schema.
Supports both direct company lists and reference-based configurations.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from ETL.tests.test_config import DatasetTier


@dataclass
class CompanyInfo:
    """Company information with standardized fields"""

    ticker: str
    name: str
    cik: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap_category: Optional[str] = None
    market_cap: Optional[Union[int, str]] = None
    weight: Optional[str] = None  # For VTI configurations


@dataclass
class UnifiedDatasetConfig:
    """Unified dataset configuration with standardized structure"""

    # Basic metadata
    dataset_name: str
    cli_alias: str
    description: str
    tier: int
    tracked_in_git: bool
    max_size_mb: int
    ticker_count: int
    last_updated: str

    # Company data
    companies: Dict[str, CompanyInfo]

    # Data source configuration
    data_source_info: Optional[Dict[str, Any]] = None
    data_sources: Optional[Dict[str, Any]] = None
    expected_files: Optional[Dict[str, int]] = None
    validation: Optional[Dict[str, Any]] = None

    # Reference information (for Fast 2 type configs)
    reference_config: Optional[str] = None
    selected_companies: Optional[List[str]] = None


class UnifiedConfigLoader:
    """Loads and processes unified dataset configurations"""

    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "data" / "config"

        self.config_dir = config_dir

        # Configuration file mapping
        self.config_files = {
            DatasetTier.F2: "list_fast_2.yml",
            DatasetTier.M7: "list_magnificent_7.yml",
            DatasetTier.N100: "list_nasdaq_100.yml",
            DatasetTier.V3K: "list_vti_3500.yml",
            # Legacy aliases
            DatasetTier.TEST: "list_fast_2.yml",
            DatasetTier.NASDAQ100: "list_nasdaq_100.yml",
            DatasetTier.VTI: "list_vti_3500.yml",
        }

    def load_config(self, tier: DatasetTier) -> UnifiedDatasetConfig:
        """Load unified configuration for specified tier"""
        config_file = self.config_files[tier]
        config_path = self.config_dir / config_file

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        return self._parse_config(raw_config, config_file)

    def _parse_config(self, raw_config: Dict[str, Any], config_file: str) -> UnifiedDatasetConfig:
        """Parse raw configuration into unified format"""

        # Extract basic metadata
        dataset_name = raw_config["dataset_name"]
        cli_alias = raw_config["cli_alias"]
        description = raw_config["description"]
        tier = raw_config["tier"]
        tracked_in_git = raw_config["tracked_in_git"]
        max_size_mb = raw_config["max_size_mb"]
        ticker_count = raw_config["ticker_count"]
        last_updated = raw_config["last_updated"]

        # Parse company data
        companies = self._parse_companies(raw_config)

        # Extract optional sections
        data_source_info = raw_config.get("data_source_info")
        data_sources = raw_config.get("data_sources")
        expected_files = raw_config.get("expected_files")
        validation = raw_config.get("validation")

        # Reference information for Fast 2 type configs
        reference_config = raw_config.get("reference_config")
        selected_companies = raw_config.get("selected_companies")

        return UnifiedDatasetConfig(
            dataset_name=dataset_name,
            cli_alias=cli_alias,
            description=description,
            tier=tier,
            tracked_in_git=tracked_in_git,
            max_size_mb=max_size_mb,
            ticker_count=ticker_count,
            last_updated=last_updated,
            companies=companies,
            data_source_info=data_source_info,
            data_sources=data_sources,
            expected_files=expected_files,
            validation=validation,
            reference_config=reference_config,
            selected_companies=selected_companies,
        )

    def _parse_companies(self, raw_config: Dict[str, Any]) -> Dict[str, CompanyInfo]:
        """Parse company data from configuration"""
        companies = {}

        if "companies" in raw_config:
            # Direct company list
            for ticker, company_data in raw_config["companies"].items():
                companies[ticker] = CompanyInfo(
                    ticker=ticker,
                    name=company_data["name"],
                    cik=company_data.get("cik"),
                    sector=company_data.get("sector"),
                    industry=company_data.get("industry"),
                    market_cap_category=company_data.get("market_cap_category"),
                    market_cap=company_data.get("market_cap"),
                    weight=company_data.get("weight"),
                )

        elif "reference_config" in raw_config and "selected_companies" in raw_config:
            # Reference-based configuration (Fast 2 style)
            reference_file = raw_config["reference_config"]
            selected_tickers = raw_config["selected_companies"]

            # Load reference configuration
            reference_path = self.config_dir / reference_file
            if reference_path.exists():
                with open(reference_path, "r", encoding="utf-8") as f:
                    reference_config = yaml.safe_load(f)

                # Extract selected companies from reference
                if "companies" in reference_config:
                    for ticker in selected_tickers:
                        if ticker in reference_config["companies"]:
                            company_data = reference_config["companies"][ticker]
                            companies[ticker] = CompanyInfo(
                                ticker=ticker,
                                name=company_data["name"],
                                cik=company_data.get("cik"),
                                sector=company_data.get("sector"),
                                industry=company_data.get("industry"),
                                market_cap_category=company_data.get("market_cap_category"),
                                market_cap=company_data.get("market_cap"),
                                weight=company_data.get("weight"),
                            )

        return companies

    def get_company_tickers(self, tier: DatasetTier) -> List[str]:
        """Get list of ticker symbols for tier"""
        config = self.load_config(tier)
        return list(config.companies.keys())

    def get_company_info(self, tier: DatasetTier, ticker: str) -> Optional[CompanyInfo]:
        """Get company information for specific ticker"""
        config = self.load_config(tier)
        return config.companies.get(ticker)

    def get_cik_mapping(self, tier: DatasetTier) -> Dict[str, str]:
        """Get ticker to CIK mapping for SEC data retrieval"""
        config = self.load_config(tier)
        cik_mapping = {}

        for ticker, company_info in config.companies.items():
            if company_info.cik:
                # Normalize CIK format
                cik_normalized = str(company_info.cik).zfill(10)
                cik_mapping[ticker] = cik_normalized

        return cik_mapping

    def is_sec_enabled(self, tier: DatasetTier) -> bool:
        """Check if SEC Edgar data is enabled for tier"""
        config = self.load_config(tier)
        if config.data_sources and "sec_edgar" in config.data_sources:
            return config.data_sources["sec_edgar"].get("enabled", False)
        return False

    def get_timeout_seconds(self, tier: DatasetTier) -> int:
        """Get timeout setting for tier"""
        config = self.load_config(tier)
        if config.validation and "timeout_seconds" in config.validation:
            return config.validation["timeout_seconds"]
        return 300  # Default 5 minutes

    def get_expected_file_counts(self, tier: DatasetTier) -> Dict[str, int]:
        """Get expected file counts for validation"""
        config = self.load_config(tier)
        return config.expected_files or {}

    def validate_tier_config(self, tier: DatasetTier) -> bool:
        """Validate that configuration for tier is complete and valid"""
        try:
            config = self.load_config(tier)

            # Basic validation
            if not config.companies:
                return False

            if config.ticker_count != len(config.companies):
                return False

            # Check that all companies have required fields
            for company in config.companies.values():
                if not company.name:
                    return False

            return True

        except Exception:
            return False


# Backward compatibility helper functions
def load_tier_config(tier: DatasetTier) -> UnifiedDatasetConfig:
    """Load configuration for tier (backward compatibility)"""
    loader = UnifiedConfigLoader()
    return loader.load_config(tier)


def get_tier_tickers(tier: DatasetTier) -> List[str]:
    """Get ticker list for tier (backward compatibility)"""
    loader = UnifiedConfigLoader()
    return loader.get_company_tickers(tier)


def get_tier_cik_mapping(tier: DatasetTier) -> Dict[str, str]:
    """Get CIK mapping for tier (backward compatibility)"""
    loader = UnifiedConfigLoader()
    return loader.get_cik_mapping(tier)
