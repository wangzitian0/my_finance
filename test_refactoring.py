#!/usr/bin/env python3
"""
Test script to validate Issue #284 refactoring implementation.
Tests that the new 5-module structure works correctly.
"""

import sys
import traceback
from pathlib import Path


def test_module_imports():
    """Test that all modules can be imported correctly."""
    print("Testing Issue #284 refactoring...")

    # Test the 5 essential L2 modules
    try:
        print("1. Testing config module...")
        from common.config.etl import etl_loader, load_stock_list

        print("   ✅ config/etl module imported successfully")

        print("2. Testing io module...")
        from common.io import directory_manager, get_data_path

        print("   ✅ io module imported successfully")

        print("3. Testing data module...")
        from common.data import normalize_ticker_symbol, validate_ticker_symbol

        print("   ✅ data module imported successfully")

        print("4. Testing system module...")
        from common.system import SystemMonitor, setup_logger

        print("   ✅ system module imported successfully")

        print("5. Testing ml module...")
        from common.ml import FallbackEmbeddings, template_manager

        print("   ✅ ml module imported successfully")

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        traceback.print_exc()
        return False

    return True


def test_legacy_compatibility():
    """Test that legacy imports still work with deprecation warnings."""
    print("\nTesting legacy compatibility...")

    try:
        # Test legacy etl_loader import
        print("1. Testing legacy etl_loader import...")
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from common.etl_loader import etl_loader as legacy_etl

            if w and any("deprecated" in str(warning.message) for warning in w):
                print("   ✅ Legacy etl_loader imported with deprecation warning")
            else:
                print("   ⚠️  Legacy etl_loader imported without deprecation warning")

        # Test legacy logger import
        print("2. Testing legacy logger import...")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from common.logger import setup_logger as legacy_setup

            if w and any("deprecated" in str(warning.message) for warning in w):
                print("   ✅ Legacy logger imported with deprecation warning")
            else:
                print("   ⚠️  Legacy logger imported without deprecation warning")

    except ImportError as e:
        print(f"   ❌ Legacy import error: {e}")
        return False

    return True


def test_new_unified_imports():
    """Test that new unified imports work from main common module."""
    print("\nTesting unified imports from common module...")

    try:
        # Test that all essential functionality is available from common
        from common import (  # Config; I/O; Data; System; ML
            FallbackEmbeddings,
            SystemMonitor,
            directory_manager,
            etl_loader,
            get_data_path,
            load_stock_list,
            normalize_ticker_symbol,
            setup_logger,
            template_manager,
            validate_ticker_symbol,
        )

        print("   ✅ All essential functionality available from common module")

    except ImportError as e:
        print(f"   ❌ Unified import error: {e}")
        traceback.print_exc()
        return False

    return True


def test_functionality():
    """Test that functionality still works correctly."""
    print("\nTesting basic functionality...")

    try:
        # Test data processing
        from common.data import normalize_ticker_symbol, validate_ticker_symbol

        ticker = normalize_ticker_symbol("  aapl  ")
        assert ticker == "AAPL", f"Expected 'AAPL', got '{ticker}'"
        assert validate_ticker_symbol("AAPL") == True
        assert validate_ticker_symbol("invalid_ticker") == False
        print("   ✅ Data processing functions work correctly")

        # Test directory manager
        from common.io import directory_manager

        config_path = directory_manager.get_config_path()
        assert config_path.exists(), f"Config path does not exist: {config_path}"
        print("   ✅ Directory manager functions work correctly")

        # Test template manager
        from common.ml import list_templates, template_manager

        templates = list_templates()
        assert len(templates) > 0, "No templates found"
        print("   ✅ Template manager functions work correctly")

    except Exception as e:
        print(f"   ❌ Functionality error: {e}")
        traceback.print_exc()
        return False

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("ISSUE #284 REFACTORING VALIDATION")
    print("=" * 60)

    tests = [
        test_module_imports,
        test_legacy_compatibility,
        test_new_unified_imports,
        test_functionality,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Refactoring is successful.")
        print("\nNew 5-module structure is working correctly:")
        print("- common/config/    (Configuration management)")
        print("- common/io/        (File I/O and storage)")
        print("- common/data/      (Data processing and validation)")
        print("- common/system/    (System utilities)")
        print("- common/ml/        (ML/AI utilities)")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
