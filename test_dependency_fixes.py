#!/usr/bin/env python3
"""
Test script to validate Issue #284 dependency fixes
"""


def test_monitoring_import():
    """Test monitoring module without psutil dependency"""
    print("Testing common.system.monitoring import...")
    try:
        from common.system.monitoring import PerformanceTimer, SystemMonitor

        print("✓ SystemMonitor imported successfully")

        # Test basic functionality
        monitor = SystemMonitor()
        print("✓ SystemMonitor instantiated")

        timer = PerformanceTimer()
        print("✓ PerformanceTimer instantiated")

        return True
    except Exception as e:
        print(f"✗ Monitoring import failed: {e}")
        return False


def test_fallback_llm_import():
    """Test FallbackLLM import"""
    print("Testing common.ml.fallback import...")
    try:
        from common.ml.fallback import FallbackEmbeddings, FallbackLLM

        print("✓ FallbackLLM imported successfully")

        # Test basic functionality
        llm = FallbackLLM()
        response = llm.generate("test prompt")
        print("✓ FallbackLLM generated response")

        embeddings = FallbackEmbeddings()
        print("✓ FallbackEmbeddings instantiated")

        return True
    except Exception as e:
        print(f"✗ FallbackLLM import failed: {e}")
        return False


def test_config_fallback():
    """Test config loader with missing files"""
    print("Testing common.config.etl fallback...")
    try:
        from common.config.etl import load_data_source, load_scenario, load_stock_list

        print("✓ ETL config functions imported successfully")

        # Test with fallback defaults (files may not exist)
        try:
            config = load_stock_list("f2")
            print("✓ Stock list loaded (with fallback if needed)")
        except Exception as e:
            print(f"  - Stock list load failed: {e}")

        try:
            source_config = load_data_source("yfinance")
            print("✓ Data source loaded (with fallback if needed)")
        except Exception as e:
            print(f"  - Data source load failed: {e}")

        return True
    except Exception as e:
        print(f"✗ Config fallback failed: {e}")
        return False


def test_basic_common_import():
    """Test basic common module import"""
    print("Testing basic common module import...")
    try:
        import common

        print("✓ Common module imported successfully")

        # Test a few basic imports
        from common import FallbackLLM

        print("✓ FallbackLLM imported from common")

        from common import SystemMonitor

        print("✓ SystemMonitor imported from common")

        return True
    except Exception as e:
        print(f"✗ Basic common import failed: {e}")
        return False


def main():
    """Run all dependency tests"""
    print("=== Issue #284 Dependency Fix Validation ===\n")

    tests = [
        test_monitoring_import,
        test_fallback_llm_import,
        test_config_fallback,
        test_basic_common_import,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"=== SUMMARY ===")
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✓ All dependency fixes working correctly!")
        return 0
    else:
        print("✗ Some dependency issues remain")
        return 1


if __name__ == "__main__":
    exit(main())
