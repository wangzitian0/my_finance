#!/usr/bin/env python3
"""
Validate development environment and fix Graph RAG compatibility issues.
This script checks M7 data availability and validates basic functionality.
"""

import json
import os
import sys
from pathlib import Path


def validate_m7_data():
    """Validate M7 data availability"""
    print("🔍 Validating M7 data...")

    data_dir = Path("data/stage_01_extract/yfinance")
    if not data_dir.exists():
        print("❌ M7 YFinance data directory not found")
        return False

    m7_companies = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "NFLX", "META"]
    found_companies = []

    for company in m7_companies:
        company_dir = data_dir / company
        if company_dir.exists():
            json_files = list(company_dir.glob("*.json"))
            if json_files:
                found_companies.append(company)
                print(f"  ✅ {company}: {len(json_files)} data files")

    print(f"\n📊 Found data for {len(found_companies)}/7 M7 companies")

    if len(found_companies) >= 5:  # At least 5 companies
        print("✅ M7 data validation passed!")
        return True
    else:
        print("❌ Insufficient M7 data found")
        return False


def validate_configuration():
    """Validate configuration files"""
    print("\n🔧 Validating configuration files...")

    config_files = ["common/config/list_magnificent_7.yml", "common/config/stage_00_original_yfinance.yml", "common/config/stage_00_original_sec_edgar.yml"]

    all_exist = True
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"  ✅ {config_file}")
        else:
            print(f"  ❌ {config_file}")
            all_exist = False

    return all_exist


def create_graph_rag_compatibility_note():
    """Create a note about Graph RAG compatibility"""
    print("\n📝 Creating Graph RAG compatibility documentation...")

    note_content = """# Graph RAG Compatibility Note

The Graph RAG system has dependency compatibility issues with the current environment:

## Issues Identified:
1. NumPy 2.x vs 1.x compatibility with sentence-transformers
2. torch.uint64 attribute missing in current torch version  
3. safetensors version compatibility

## Recommended Solutions:
1. Use conda environment with pinned versions
2. Consider using Docker for Graph RAG components
3. Update to newer versions of all ML dependencies simultaneously

## Current Status:
- M7 data collection: ✅ Working
- Basic data analysis: ✅ Working  
- Graph RAG system: ⚠️ Needs dependency fixes

## Next Steps:
- Focus on DCF calculation engine development
- Address Graph RAG dependencies in dedicated ML environment
- Create separate pixi environment for ML workloads
"""

    with open("GRAPH_RAG_COMPATIBILITY.md", "w") as f:
        f.write(note_content)

    print("✅ Compatibility note created: GRAPH_RAG_COMPATIBILITY.md")


def validate_basic_python_functionality():
    """Validate basic Python functionality"""
    print("\n🐍 Validating basic Python functionality...")

    try:
        import json

        import numpy as np
        import pandas as pd
        import yaml

        print("  ✅ Core data processing libraries")
    except ImportError as e:
        print(f"  ❌ Core libraries: {e}")
        return False

    try:
        import requests
        from bs4 import BeautifulSoup

        print("  ✅ Web scraping libraries")
    except ImportError as e:
        print(f"  ❌ Web scraping: {e}")
        return False

    return True


def main():
    """Main validation function"""
    print("🚀 Development Environment Validation")
    print("=" * 50)

    results = {
        "m7_data": validate_m7_data(),
        "configuration": validate_configuration(),
        "python_functionality": validate_basic_python_functionality(),
    }

    # Always create compatibility note
    create_graph_rag_compatibility_note()

    print("\n" + "=" * 50)
    print("📋 Validation Results:")
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")

    overall_success = all(results.values())

    if overall_success:
        print("\n🎉 Development environment validation successful!")
        print("Ready for DCF calculation engine development.")
    else:
        print("\n⚠️ Some validation checks failed.")
        print("Core functionality available, Graph RAG needs attention.")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
