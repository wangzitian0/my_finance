#!/usr/bin/env python3
"""
Script to add CIK numbers to N100 configuration.
This script will look up CIK numbers for companies that don't have them.
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, Optional

import requests
import yaml

def lookup_cik_for_ticker(ticker: str) -> Optional[str]:
    """
    Look up CIK number for a given ticker using SEC company lookup.
    """
    try:
        # Use SEC company tickers JSON endpoint
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': 'ZitianSG wangzitian0@gmail.com'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        companies = response.json()
        
        # Search for ticker in the companies data
        for company_data in companies.values():
            if company_data.get('ticker', '').upper() == ticker.upper():
                cik = str(company_data.get('cik_str', '')).zfill(10)
                return cik
                
        print(f"⚠️  CIK not found for ticker: {ticker}")
        return None
        
    except Exception as e:
        print(f"❌ Error looking up CIK for {ticker}: {e}")
        return None

def update_n100_config_with_ciks():
    """
    Update the N100 configuration file to add missing CIK numbers.
    """
    config_path = Path(__file__).parent.parent / "data" / "config" / "list_nasdaq_100.yml"
    
    print(f"📋 Loading N100 configuration from: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    companies = config.get('companies', {})
    updated_count = 0
    
    print(f"🔍 Checking {len(companies)} companies for missing CIK numbers...")
    
    for ticker, company_data in companies.items():
        if not company_data.get('cik'):
            print(f"🔍 Looking up CIK for {ticker}...")
            
            cik = lookup_cik_for_ticker(ticker)
            if cik:
                company_data['cik'] = cik
                updated_count += 1
                print(f"✅ Added CIK {cik} for {ticker}")
            else:
                print(f"❌ Could not find CIK for {ticker}")
            
            # Rate limiting to be respectful to SEC servers
            time.sleep(0.1)
    
    if updated_count > 0:
        print(f"\n💾 Saving updated configuration with {updated_count} new CIK numbers...")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=1000)
        
        print(f"✅ Updated {updated_count} companies with CIK numbers")
    else:
        print("✅ All companies already have CIK numbers")

def create_n100_sec_edgar_config():
    """
    Create a proper SEC Edgar configuration for all N100 companies.
    """
    config_path = Path(__file__).parent.parent / "data" / "config" / "list_nasdaq_100.yml"
    sec_config_path = Path(__file__).parent.parent / "data" / "config" / "sec_edgar_nasdaq100.yml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        n100_config = yaml.safe_load(f)
    
    companies = n100_config.get('companies', {})
    
    # Extract CIK numbers for companies that have them
    cik_numbers = []
    companies_with_cik = []
    companies_without_cik = []
    
    for ticker, company_data in companies.items():
        cik = company_data.get('cik')
        if cik:
            cik_numbers.append(cik)
            companies_with_cik.append(ticker)
        else:
            companies_without_cik.append(ticker)
    
    print(f"📊 N100 SEC Edgar Analysis:")
    print(f"   Companies with CIK: {len(companies_with_cik)}")
    print(f"   Companies without CIK: {len(companies_without_cik)}")
    
    if companies_without_cik:
        print(f"   Missing CIK for: {', '.join(companies_without_cik[:10])}{'...' if len(companies_without_cik) > 10 else ''}")
    
    # Create SEC Edgar configuration
    sec_config = {
        "# SEC Edgar configuration for NASDAQ-100 dataset": None,
        "# Generated automatically from list_nasdaq_100.yml": None,
        "": None,
        "tickers": cik_numbers,
        "count": 8,
        "file_types": ["10K", "10Q", "8K"],
        "email": "ZitianSG (wangzitian0@gmail.com)",
        "collection": {
            "start_date": "2022-01-01",
            "rate_limit_seconds": 2,
            "max_retries": 3,
            "timeout_per_filing": 60
        },
        f"# Note: {len(cik_numbers)} out of 100 N100 companies have CIK numbers": None,
        f"# Companies without CIK: {len(companies_without_cik)}": None
    }
    
    # Write SEC configuration
    with open(sec_config_path, 'w', encoding='utf-8') as f:
        # Write comments and configuration manually for better formatting
        f.write("# SEC Edgar configuration for NASDAQ-100 dataset\n")
        f.write("# Generated automatically from list_nasdaq_100.yml\n")
        f.write(f"# Contains {len(cik_numbers)} companies with CIK numbers out of 100 total\n\n")
        
        f.write("# CIK numbers for N100 companies\n")
        f.write("tickers:\n")
        for cik in cik_numbers:
            f.write(f'  - "{cik}"\n')
        
        f.write(f"\n# Number of filings per type to fetch\n")
        f.write(f"count: 8\n\n")
        
        f.write("# Filing types to collect\n")
        f.write("file_types:\n")
        f.write('  - "10K"  # Annual reports\n')
        f.write('  - "10Q"  # Quarterly reports\n')
        f.write('  - "8K"   # Current reports\n\n')
        
        f.write("# User identification for SEC API\n")
        f.write('email: "ZitianSG (wangzitian0@gmail.com)"\n\n')
        
        f.write("# Data collection settings\n")
        f.write("collection:\n")
        f.write('  start_date: "2022-01-01"\n')
        f.write("  rate_limit_seconds: 2\n")
        f.write("  max_retries: 3\n")
        f.write("  timeout_per_filing: 60\n\n")
        
        f.write(f"# Companies with CIK numbers ({len(companies_with_cik)}/100):\n")
        for ticker in companies_with_cik:
            f.write(f"# {ticker}\n")
        
        if companies_without_cik:
            f.write(f"\n# Companies missing CIK numbers ({len(companies_without_cik)}/100):\n")
            for ticker in companies_without_cik:
                f.write(f"# {ticker} - CIK lookup needed\n")
    
    print(f"✅ Created SEC Edgar config: {sec_config_path}")
    print(f"   Supports {len(cik_numbers)} companies out of 100 total")
    
    return len(companies_with_cik), len(companies_without_cik)

def main():
    """Main function to update N100 with CIK numbers"""
    print("🔧 N100 CIK Number Update Tool")
    print("=" * 50)
    
    # Step 1: Add missing CIK numbers
    print("\n📋 Step 1: Looking up missing CIK numbers...")
    update_n100_config_with_ciks()
    
    # Step 2: Create comprehensive SEC Edgar config
    print(f"\n📋 Step 2: Creating N100 SEC Edgar configuration...")
    companies_with_cik, companies_without_cik = create_n100_sec_edgar_config()
    
    print(f"\n🎉 Summary:")
    print(f"   ✅ N100 configuration now has 100 tickers")
    print(f"   ✅ SEC Edgar config supports {companies_with_cik} companies")
    print(f"   ⚠️  {companies_without_cik} companies still need CIK lookup")
    
    if companies_without_cik > 0:
        print(f"\n💡 Next steps:")
        print(f"   - Manual CIK lookup for remaining {companies_without_cik} companies")
        print(f"   - Update SEC Edgar config when more CIKs are available")

if __name__ == "__main__":
    main()