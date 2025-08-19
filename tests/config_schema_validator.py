#!/usr/bin/env python3
"""
Configuration Schema Validator
Ensures all dataset configuration files follow the unified schema structure.
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml


@dataclass
class CompanyInfo:
    """Company information with required and optional fields"""
    name: str
    cik: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap_category: Optional[str] = None
    market_cap: Optional[Union[int, str]] = None
    weight: Optional[str] = None  # For VTI configurations


@dataclass
class DataSourceConfig:
    """Data source configuration structure"""
    enabled: bool
    stage_config: str


@dataclass
class DataSourceInfo:
    """Data source attribution information"""
    primary_source: str
    last_verified: str
    update_method: str
    selection_criteria: str
    notes: Optional[str] = None
    source_url: Optional[str] = None
    total_companies: Optional[int] = None


@dataclass
class ExpectedFiles:
    """Expected file counts for validation"""
    yfinance: int
    sec_edgar: int


@dataclass
class ValidationConfig:
    """Validation settings"""
    timeout_seconds: int
    required_success_rate: float
    min_files_threshold: Optional[int] = None


@dataclass
class UnifiedConfigSchema:
    """Unified configuration schema for all dataset types"""
    
    # Required fields
    dataset_name: str
    cli_alias: str
    description: str
    tier: int
    tracked_in_git: bool
    max_size_mb: int
    ticker_count: int
    last_updated: str
    
    # Company data (either companies dict or reference_config)
    companies: Optional[Dict[str, CompanyInfo]] = None
    reference_config: Optional[str] = None
    selected_companies: Optional[List[str]] = None
    
    # Configuration sections
    data_source_info: Optional[DataSourceInfo] = None
    data_sources: Optional[Dict[str, DataSourceConfig]] = None
    expected_files: Optional[ExpectedFiles] = None
    validation: Optional[ValidationConfig] = None


class ConfigSchemaValidator:
    """Validates configuration files against unified schema"""
    
    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            project_root = Path(__file__).parent.parent
            config_dir = project_root / "data" / "config"
        
        self.config_dir = config_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Required configuration files
        self.required_configs = [
            "list_fast_2.yml",
            "list_magnificent_7.yml", 
            "list_nasdaq_100.yml",
            "list_vti_3500.yml"
        ]
        
        # Valid market cap categories
        self.valid_market_cap_categories = {"mega", "large", "mid", "small"}
        
        # Valid tier values
        self.valid_tiers = {1, 2, 3, 4}

    def validate_all_configs(self) -> bool:
        """Validate all required configuration files"""
        self.errors.clear()
        self.warnings.clear()
        
        success = True
        for config_file in self.required_configs:
            config_path = self.config_dir / config_file
            if not config_path.exists():
                self.errors.append(f"Required config file missing: {config_file}")
                success = False
                continue
                
            if not self.validate_single_config(config_path):
                success = False
                
        # Validate schema consistency across configs
        if success:
            success = self.validate_schema_consistency()
            
        return success

    def validate_single_config(self, config_path: Path) -> bool:
        """Validate a single configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"{config_path.name}: Failed to load YAML: {e}")
            return False
            
        return self._validate_config_structure(config_path.name, config_data)

    def _validate_config_structure(self, filename: str, config: Dict[str, Any]) -> bool:
        """Validate configuration structure against unified schema"""
        success = True
        
        # Required top-level fields
        required_fields = [
            'dataset_name', 'cli_alias', 'description', 'tier',
            'tracked_in_git', 'max_size_mb', 'ticker_count', 'last_updated'
        ]
        
        for field in required_fields:
            if field not in config:
                self.errors.append(f"{filename}: Missing required field '{field}'")
                success = False
        
        # Validate tier value
        if 'tier' in config and config['tier'] not in self.valid_tiers:
            self.errors.append(f"{filename}: Invalid tier value {config['tier']}, must be one of {self.valid_tiers}")
            success = False
            
        # Validate company data structure
        if not self._validate_company_data(filename, config):
            success = False
            
        # Validate data sources
        if not self._validate_data_sources(filename, config):
            success = False
            
        # Validate expected files
        if not self._validate_expected_files(filename, config):
            success = False
            
        # Validate validation config
        if not self._validate_validation_config(filename, config):
            success = False
            
        return success

    def _validate_company_data(self, filename: str, config: Dict[str, Any]) -> bool:
        """Validate company data structure (either companies dict or reference)"""
        success = True
        
        has_companies = 'companies' in config
        has_reference = 'reference_config' in config and 'selected_companies' in config
        
        if not has_companies and not has_reference:
            self.errors.append(f"{filename}: Must have either 'companies' section or 'reference_config'+'selected_companies'")
            return False
            
        if has_companies and has_reference:
            self.warnings.append(f"{filename}: Has both 'companies' and 'reference_config' - using 'companies'")
            
        if has_companies:
            success = self._validate_companies_section(filename, config['companies'])
            
        if has_reference:
            if not isinstance(config['reference_config'], str) or not config['reference_config'].endswith('.yml'):
                self.errors.append(f"{filename}: 'reference_config' must be a YAML filename")
                success = False
                
            if not isinstance(config['selected_companies'], list) or not config['selected_companies']:
                self.errors.append(f"{filename}: 'selected_companies' must be a non-empty list")
                success = False
                
        return success

    def _validate_companies_section(self, filename: str, companies: Dict[str, Any]) -> bool:
        """Validate companies section structure"""
        success = True
        
        if not isinstance(companies, dict) or not companies:
            self.errors.append(f"{filename}: 'companies' must be a non-empty dictionary")
            return False
            
        for ticker, company_data in companies.items():
            if not isinstance(company_data, dict):
                self.errors.append(f"{filename}: Company data for {ticker} must be a dictionary")
                success = False
                continue
                
            # Required field: name
            if 'name' not in company_data:
                self.errors.append(f"{filename}: Company {ticker} missing required 'name' field")
                success = False
                
            # Validate CIK format if present
            if 'cik' in company_data:
                cik = company_data['cik']
                if cik is not None:
                    # Normalize CIK to string for validation
                    cik_str = str(cik).zfill(10)  # Pad with zeros to 10 digits
                    if not cik_str.isdigit() or len(cik_str) != 10:
                        self.errors.append(f"{filename}: Company {ticker} has invalid CIK format: {cik}")
                        success = False
                        
            # Validate market cap category if present
            if 'market_cap_category' in company_data:
                category = company_data['market_cap_category']
                if category not in self.valid_market_cap_categories:
                    self.errors.append(f"{filename}: Company {ticker} has invalid market_cap_category: {category}")
                    success = False
                    
        return success

    def _validate_data_sources(self, filename: str, config: Dict[str, Any]) -> bool:
        """Validate data_sources section"""
        success = True
        
        if 'data_sources' not in config:
            self.errors.append(f"{filename}: Missing required 'data_sources' section")
            return False
            
        data_sources = config['data_sources']
        if not isinstance(data_sources, dict):
            self.errors.append(f"{filename}: 'data_sources' must be a dictionary")
            return False
            
        # Required data sources
        required_sources = ['yfinance', 'sec_edgar']
        for source in required_sources:
            if source not in data_sources:
                self.errors.append(f"{filename}: Missing required data source '{source}'")
                success = False
                continue
                
            source_config = data_sources[source]
            if not isinstance(source_config, dict):
                self.errors.append(f"{filename}: Data source '{source}' must be a dictionary")
                success = False
                continue
                
            # Required fields for each data source
            if 'enabled' not in source_config:
                self.errors.append(f"{filename}: Data source '{source}' missing 'enabled' field")
                success = False
                
            if 'stage_config' not in source_config:
                self.errors.append(f"{filename}: Data source '{source}' missing 'stage_config' field")
                success = False
            elif not source_config['stage_config'].endswith('.yml'):
                self.errors.append(f"{filename}: Data source '{source}' stage_config must be a YAML filename")
                success = False
                
        return success

    def _validate_expected_files(self, filename: str, config: Dict[str, Any]) -> bool:
        """Validate expected_files section"""
        success = True
        
        if 'expected_files' not in config:
            self.errors.append(f"{filename}: Missing required 'expected_files' section")
            return False
            
        expected_files = config['expected_files']
        if not isinstance(expected_files, dict):
            self.errors.append(f"{filename}: 'expected_files' must be a dictionary")
            return False
            
        # Required file counts
        required_counts = ['yfinance', 'sec_edgar']
        for file_type in required_counts:
            if file_type not in expected_files:
                self.errors.append(f"{filename}: Missing expected file count for '{file_type}'")
                success = False
            elif not isinstance(expected_files[file_type], int) or expected_files[file_type] < 0:
                self.errors.append(f"{filename}: Expected file count for '{file_type}' must be non-negative integer")
                success = False
                
        return success

    def _validate_validation_config(self, filename: str, config: Dict[str, Any]) -> bool:
        """Validate validation section"""
        success = True
        
        if 'validation' not in config:
            self.errors.append(f"{filename}: Missing required 'validation' section")
            return False
            
        validation = config['validation']
        if not isinstance(validation, dict):
            self.errors.append(f"{filename}: 'validation' must be a dictionary")
            return False
            
        # Required validation fields
        required_fields = ['timeout_seconds', 'required_success_rate']
        for field in required_fields:
            if field not in validation:
                self.errors.append(f"{filename}: Missing required validation field '{field}'")
                success = False
                
        # Validate timeout
        if 'timeout_seconds' in validation:
            timeout = validation['timeout_seconds']
            if not isinstance(timeout, int) or timeout <= 0:
                self.errors.append(f"{filename}: 'timeout_seconds' must be positive integer")
                success = False
                
        # Validate success rate
        if 'required_success_rate' in validation:
            rate = validation['required_success_rate']
            if not isinstance(rate, (int, float)) or not (0.0 <= rate <= 1.0):
                self.errors.append(f"{filename}: 'required_success_rate' must be between 0.0 and 1.0")
                success = False
                
        return success

    def validate_schema_consistency(self) -> bool:
        """Validate consistency across all configuration schemas"""
        success = True
        
        # Load all configs for consistency checks
        configs = {}
        for config_file in self.required_configs:
            config_path = self.config_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        configs[config_file] = yaml.safe_load(f)
                except Exception as e:
                    self.errors.append(f"Failed to load {config_file} for consistency check: {e}")
                    success = False
                    
        if not configs:
            return success
            
        # Check for consistent schema structure
        first_config_name = next(iter(configs))
        first_config = configs[first_config_name]
        expected_top_level_keys = set(first_config.keys())
        
        for config_name, config_data in configs.items():
            actual_keys = set(config_data.keys())
            
            # Allow some flexibility for different config types
            flexible_keys = {'companies', 'reference_config', 'selected_companies', 'data_source_info'}
            core_keys = expected_top_level_keys - flexible_keys
            config_core_keys = actual_keys - flexible_keys
            
            if core_keys != config_core_keys:
                missing_keys = core_keys - config_core_keys
                extra_keys = config_core_keys - core_keys
                
                if missing_keys:
                    self.errors.append(f"{config_name}: Missing core keys: {sorted(missing_keys)}")
                    success = False
                if extra_keys:
                    self.warnings.append(f"{config_name}: Extra keys: {sorted(extra_keys)}")
        
        return success

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation results summary"""
        return {
            'success': len(self.errors) == 0,
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'configs_checked': self.required_configs
        }

    def print_validation_results(self):
        """Print validation results to console"""
        if self.errors:
            print("❌ Configuration Schema Validation FAILED")
            print("\n🚨 ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("✅ Configuration Schema Validation PASSED")
            
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        print(f"\n📋 Validated {len(self.required_configs)} configuration files")


def main():
    """Main validation entry point"""
    validator = ConfigSchemaValidator()
    success = validator.validate_all_configs()
    validator.print_validation_results()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()