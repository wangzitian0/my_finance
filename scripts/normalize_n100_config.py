#!/usr/bin/env python3
"""
Script to normalize NASDAQ 100 configuration to match unified schema.
Standardizes CIK formats and fills in missing metadata fields.
"""

import re
from pathlib import Path
from typing import Dict, Any

import yaml


def normalize_cik(cik_value) -> str:
    """Normalize CIK to standard 10-digit format with leading zeros"""
    if cik_value is None:
        return None
    
    # Convert to string and remove any non-digits
    cik_str = str(cik_value)
    cik_digits = re.sub(r'\D', '', cik_str)
    
    if not cik_digits:
        return None
        
    # Pad with leading zeros to make 10 digits
    return cik_digits.zfill(10)


def standardize_market_cap_category(market_cap) -> str:
    """Standardize market cap category based on market cap value"""
    if not market_cap or market_cap == '':
        return None
        
    # Convert to number if it's a string with commas
    if isinstance(market_cap, str):
        # Remove commas and convert to float
        clean_cap = market_cap.replace(',', '')
        try:
            cap_value = float(clean_cap)
        except ValueError:
            return None
    else:
        cap_value = float(market_cap)
    
    # Categorize based on market cap
    # Values appear to be in dollars, so:
    # Mega: > 200B, Large: 10B-200B, Mid: 2B-10B, Small: < 2B
    if cap_value > 200_000_000_000:
        return "mega"
    elif cap_value > 10_000_000_000:
        return "large" 
    elif cap_value > 2_000_000_000:
        return "mid"
    else:
        return "small"


def normalize_n100_config():
    """Normalize NASDAQ 100 configuration file"""
    config_path = Path(__file__).parent.parent / "data" / "config" / "list_nasdaq_100.yml"
    
    print(f"📋 Loading N100 configuration from: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Track changes
    changes_made = 0
    companies_processed = 0
    
    # Process each company
    if 'companies' in config:
        for ticker, company_data in config['companies'].items():
            companies_processed += 1
            
            # Normalize CIK
            if 'cik' in company_data:
                original_cik = company_data['cik']
                normalized_cik = normalize_cik(original_cik)
                if normalized_cik != str(original_cik).zfill(10) if original_cik else None:
                    company_data['cik'] = normalized_cik
                    changes_made += 1
                    print(f"  📝 {ticker}: Normalized CIK {original_cik} -> {normalized_cik}")
            
            # Add market cap category if missing but market cap present
            if 'market_cap_category' not in company_data or not company_data.get('market_cap_category'):
                if 'market_cap' in company_data and company_data['market_cap']:
                    category = standardize_market_cap_category(company_data['market_cap'])
                    if category:
                        company_data['market_cap_category'] = category
                        changes_made += 1
                        print(f"  📝 {ticker}: Added market_cap_category: {category}")
            
            # Fill in empty sector with placeholder if completely empty
            if 'sector' in company_data and company_data['sector'] == '':
                # Leave as empty string for now - would need external data to fill properly
                pass
    
    # Update metadata
    config['last_updated'] = "2025-08-19T12:00:00.000000"
    changes_made += 1
    
    print(f"\n✅ Processed {companies_processed} companies")
    print(f"📝 Made {changes_made} changes")
    
    # Write back to file
    print(f"💾 Writing normalized configuration back to: {config_path}")
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("✅ N100 configuration normalization complete!")


if __name__ == "__main__":
    normalize_n100_config()