#!/usr/bin/env python3
"""
Dataset Schema Standardization Script
Updates all dataset configuration files to use consistent schema structure.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
except ImportError:
    print("Warning: yaml not available, schema validation limited")


def validate_schema(config: Dict[str, Any], config_file: str) -> Dict[str, Any]:
    """Validate and enhance configuration schema."""
    
    issues = []
    
    # Required top-level fields
    required_fields = [
        'dataset_name', 'cli_alias', 'description', 'tier', 
        'tracked_in_git', 'max_size_mb', 'data_sources', 
        'expected_files', 'validation', 'companies', 'ticker_count'
    ]
    
    for field in required_fields:
        if field not in config:
            issues.append(f"Missing required field: {field}")
    
    # Validate data_sources structure
    if 'data_sources' in config:
        data_sources = config['data_sources']
        for source in ['yfinance', 'sec_edgar']:
            if source in data_sources:
                if 'enabled' not in data_sources[source]:
                    issues.append(f"Missing 'enabled' field in data_sources.{source}")
                if 'stage_config' not in data_sources[source]:
                    issues.append(f"Missing 'stage_config' field in data_sources.{source}")
    
    # Validate companies structure
    if 'companies' in config:
        companies = config['companies']
        companies_with_cik = 0
        companies_with_sector = 0
        
        for ticker, company_info in companies.items():
            if 'name' not in company_info:
                issues.append(f"Missing 'name' for ticker {ticker}")
            
            if 'cik' in company_info and company_info['cik']:
                companies_with_cik += 1
            
            if 'sector' in company_info and company_info['sector']:
                companies_with_sector += 1
        
        # Schema completeness metrics
        total_companies = len(companies)
        cik_coverage = companies_with_cik / total_companies * 100 if total_companies > 0 else 0
        sector_coverage = companies_with_sector / total_companies * 100 if total_companies > 0 else 0
        
        if cik_coverage < 10:  # Less than 10% have CIK
            issues.append(f"Low CIK coverage: {cik_coverage:.1f}% ({companies_with_cik}/{total_companies})")
        
        if sector_coverage < 50:  # Less than 50% have sector
            issues.append(f"Low sector coverage: {sector_coverage:.1f}% ({companies_with_sector}/{total_companies})")
    
    return {
        'file': config_file,
        'issues': issues,
        'companies_total': len(config.get('companies', {})),
        'companies_with_cik': companies_with_cik if 'companies' in config else 0,
        'companies_with_sector': companies_with_sector if 'companies' in config else 0,
        'has_data_source_info': 'data_source_info' in config
    }


def main():
    """Main schema validation and reporting."""
    
    config_dir = Path('data/config')
    config_files = [
        'list_fast_2.yml',
        'list_magnificent_7.yml', 
        'list_nasdaq_100.yml',
        'list_vti_3500.yml'
    ]
    
    print("📋 Dataset Schema Validation Report")
    print("=" * 60)
    
    for config_file in config_files:
        config_path = config_dir / config_file
        
        if not config_path.exists():
            print(f"\n❌ {config_file}: File not found")
            continue
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            validation_result = validate_schema(config, config_file)
            
            print(f"\n📄 {config_file}")
            print(f"   Dataset: {config.get('dataset_name', 'Unknown')}")
            print(f"   Alias: {config.get('cli_alias', 'Unknown')}")
            print(f"   Tier: {config.get('tier', 'Unknown')}")
            print(f"   Companies: {validation_result['companies_total']}")
            print(f"   CIK Coverage: {validation_result['companies_with_cik']}/{validation_result['companies_total']} ({validation_result['companies_with_cik']/max(validation_result['companies_total'],1)*100:.1f}%)")
            print(f"   Sector Coverage: {validation_result['companies_with_sector']}/{validation_result['companies_total']} ({validation_result['companies_with_sector']/max(validation_result['companies_total'],1)*100:.1f}%)")
            print(f"   Data Source Info: {'✅' if validation_result['has_data_source_info'] else '❌'}")
            
            # SEC Edgar status
            sec_enabled = config.get('data_sources', {}).get('sec_edgar', {}).get('enabled', False)
            print(f"   SEC Edgar: {'✅ Enabled' if sec_enabled else '⚪ Disabled'}")
            
            if validation_result['issues']:
                print(f"   Issues:")
                for issue in validation_result['issues']:
                    print(f"     ⚠️  {issue}")
            else:
                print(f"   ✅ Schema compliant")
                
        except Exception as e:
            print(f"\n❌ {config_file}: Error loading - {e}")
    
    print("\n" + "=" * 60)
    print("📝 Schema Standardization Recommendations:")
    print("1. Add CIK numbers to all companies for SEC integration")
    print("2. Add sector/industry information for better categorization")
    print("3. Include data_source_info block with source attribution")
    print("4. Ensure consistent field naming across all configs")
    print("5. Add market_cap_category for better filtering")


if __name__ == "__main__":
    main()