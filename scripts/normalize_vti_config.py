#!/usr/bin/env python3
"""
Script to normalize VTI 3500 configuration to match unified schema.
Adds missing CIK numbers and standardizes company metadata.
"""

import re
from pathlib import Path
from typing import Dict, Any

import yaml


def normalize_vti_config():
    """Normalize VTI 3500 configuration file"""
    config_path = Path(__file__).parent.parent / "data" / "config" / "list_vti_3500.yml"
    
    print(f"📋 Loading VTI configuration from: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Track changes
    changes_made = 0
    companies_processed = 0
    
    # Process each company
    if 'companies' in config:
        for ticker, company_data in config['companies'].items():
            companies_processed += 1
            
            # Skip the VTI ETF entry itself
            if ticker == 'VTI':
                continue
                
            # Standardize missing CIK to None (VTI doesn't have CIK data)
            if 'cik' not in company_data:
                company_data['cik'] = None
                
            # Add market_cap_category based on weight if missing
            if 'market_cap_category' not in company_data and 'weight' in company_data:
                weight_str = company_data['weight'].rstrip('%')
                try:
                    weight_val = float(weight_str)
                    if weight_val > 5.0:
                        company_data['market_cap_category'] = "mega"
                        changes_made += 1
                    elif weight_val > 1.0:
                        company_data['market_cap_category'] = "large"
                        changes_made += 1
                    elif weight_val > 0.1:
                        company_data['market_cap_category'] = "mid"
                        changes_made += 1
                    else:
                        company_data['market_cap_category'] = "small"
                        changes_made += 1
                except ValueError:
                    company_data['market_cap_category'] = None
                    
            # Normalize sector field (VTI uses sector instead of industry)
            if 'sector' in company_data and company_data['sector'] and 'industry' not in company_data:
                company_data['industry'] = company_data['sector']
                changes_made += 1
    
    # Update metadata
    config['last_updated'] = "2025-08-19T12:00:00.000000"
    changes_made += 1
    
    print(f"\n✅ Processed {companies_processed} companies")
    print(f"📝 Made {changes_made} changes")
    
    # Write back to file
    print(f"💾 Writing normalized configuration back to: {config_path}")
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("✅ VTI configuration normalization complete!")


if __name__ == "__main__":
    normalize_vti_config()