#!/usr/bin/env python3
"""
Test script for centralized data access utility.
Validates that the data access patterns work correctly.
"""

import sys
from pathlib import Path

# Add common to path for import
sys.path.append(str(Path(__file__).parent.parent))

from common.data_access import data_access, get_data_path, get_build_path, get_config_path


def test_data_access():
    """Test the centralized data access functionality."""
    print("🧪 Testing centralized data access utility...")
    
    # Test basic directory access
    print(f"Base data directory: {data_access.base_dir}")
    print(f"Original data directory: {data_access.get_original_dir()}")
    print(f"Extract directory: {data_access.get_extract_dir()}")
    print(f"Transform directory: {data_access.get_transform_dir()}")
    print(f"Load directory: {data_access.get_load_dir()}")
    print(f"Build directory: {data_access.get_build_dir()}")
    print(f"Release directory: {data_access.get_release_dir()}")
    
    # Test configuration access
    print(f"Config directory: {data_access.get_config_dir()}")
    print(f"YFinance M7 config: {data_access.get_config_file('job_yfinance_m7')}")
    print(f"SEC Edgar M7 config: {data_access.get_config_file('sec_edgar_m7')}")
    
    # Test log access
    print(f"Log directory: {data_access.get_log_dir()}")
    print(f"YFinance log directory: {data_access.get_log_dir('yfinance')}")
    print(f"Sample log file: {data_access.get_log_file('test_job')}")
    
    # Test source/ticker access
    print(f"YFinance source dir: {data_access.get_source_dir('yfinance', 'stage_01_extract')}")
    print(f"AAPL ticker dir: {data_access.get_ticker_dir('yfinance', 'AAPL', 'stage_01_extract')}")
    
    # Test build with timestamps and branches
    print(f"Timestamped build: {data_access.get_build_dir('20250119_140000')}")
    print(f"Feature branch build: {data_access.get_build_dir('20250119_140000', 'feature/test')}")
    
    # Test convenience functions
    print(f"Convenience data path: {get_data_path('stage_99_build')}")
    print(f"Convenience build path: {get_build_path('20250119_140000')}")
    print(f"Convenience config path: {get_config_path('job_yfinance_m7')}")
    
    # Test directory existence checks
    config_dir = data_access.get_config_dir()
    if config_dir.exists():
        print(f"✅ Config directory exists: {config_dir}")
    else:
        print(f"⚠️  Config directory does not exist: {config_dir}")
    
    # Test build listing functionality
    builds = data_access.list_builds()
    if builds:
        print(f"Available builds: {builds[:3]}...")  # Show first 3
    else:
        print("No builds found")
    
    releases = data_access.list_releases()
    if releases:
        print(f"Available releases: {releases[:3]}...")  # Show first 3
    else:
        print("No releases found")
    
    print("✅ Data access utility test completed")


if __name__ == "__main__":
    test_data_access()