#!/usr/bin/env python3
"""
Setup test environment for pipeline testing
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def setup_test_data():
    """Setup minimal test data for user case testing"""
    print("🔧 Setting up test data...")

    # Create test directories
    test_dirs = [
        "data/test/stage_01_extract/yfinance",
        "data/test/stage_01_extract/sec_edgar",
        "data/test/reports",
        "test-results",
    ]

    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Create minimal test config
    test_config = {
        "test_mode": True,
        "m7_tickers": ["AAPL", "MSFT", "GOOGL"],  # Reduced for testing
        "data_sources": {
            "yfinance": {"enabled": True, "timeout": 10},
            "sec_edgar": {"enabled": False},  # Disable for faster testing
        },
        "dcf_params": {
            "discount_rate": 0.10,
            "growth_rate": 0.03,
            "terminal_growth": 0.025,
        },
    }

    config_file = Path("data/config/test_config.yml")
    config_file.parent.mkdir(parents=True, exist_ok=True)

    import yaml

    with open(config_file, "w") as f:
        yaml.dump(test_config, f, default_flow_style=False)

    print("✅ Test data setup complete")


def setup_mock_services():
    """Setup mock services for testing"""
    print("🔧 Setting up mock services...")

    # Create test database mock
    mock_db_dir = Path("data/test/db")
    mock_db_dir.mkdir(parents=True, exist_ok=True)

    # Create mock Neo4j connection test
    mock_test = '''
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_neo4j():
    """Mock Neo4j connection for testing"""
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        mock_session = Mock()
        mock_driver.return_value.session.return_value = mock_session
        yield mock_session
'''

    test_conftest = Path("tests/conftest.py")
    with open(test_conftest, "w") as f:
        f.write(mock_test)

    print("✅ Mock services setup complete")


def validate_test_environment():
    """Validate test environment is ready"""
    print("🔍 Validating test environment...")

    required_dirs = ["data/test", "test-results", "tests"]

    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing required directory: {dir_path}")
            return False

    required_files = [
        "data/config/test_config.yml",
        "tests/conftest.py",
        "tests/test_user_cases.py",
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing required file: {file_path}")
            return False

    print("✅ Test environment validation passed")
    return True


def main():
    """Main setup function"""
    print("🚀 Setting up test environment for pipeline testing...")

    try:
        setup_test_data()
        setup_mock_services()

        if validate_test_environment():
            print("\n✅ Test environment setup complete!")
            print("\nYou can now run:")
            print("  pixi run test-all-user-cases")
            print("  pixi run test-with-coverage")
            return 0
        else:
            print("\n❌ Test environment setup failed")
            return 1

    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
