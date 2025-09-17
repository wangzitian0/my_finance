#!/usr/bin/env python3
"""
Validate Issue #284 fixes: Test critical imports that were failing
"""


def test_critical_imports():
    """Test the specific imports mentioned in the Issue #284 error message"""

    # Test 1: FallbackLLM import that was specifically failing
    try:
        from common.ml.fallback import FallbackLLM

        print("✅ FIXED: FallbackLLM import successful")

        # Test instantiation and basic usage
        llm = FallbackLLM()
        response = llm.generate("Test financial analysis")
        assert "FALLBACK" in response
        print("✅ VERIFIED: FallbackLLM works correctly")

    except ImportError as e:
        print(f"❌ CRITICAL: FallbackLLM import still failing: {e}")
        return False

    # Test 2: directory_manager import
    try:
        from common.io.directory import directory_manager

        print("✅ FIXED: directory_manager import successful")

        # Test basic functionality
        config_path = directory_manager.get_config_path()
        print(f"✅ VERIFIED: Config path resolved: {config_path}")

    except ImportError as e:
        print(f"❌ CRITICAL: directory_manager import failing: {e}")
        return False

    # Test 3: High-level common imports
    try:
        from common import FallbackLLM, FallbackRetrieval

        print("✅ FIXED: High-level common ML imports successful")

        from common import DataLayer, directory_manager

        print("✅ FIXED: High-level common IO imports successful")

    except ImportError as e:
        print(f"❌ CRITICAL: High-level common imports failing: {e}")
        return False

    return True


def main():
    """Main validation"""
    print("Validating Issue #284 fixes...")
    print("=" * 50)

    if test_critical_imports():
        print("\n🎉 SUCCESS: All critical import issues are FIXED!")
        print("✅ FallbackLLM is now available")
        print("✅ directory_manager is working")
        print("✅ Common module structure is intact")
        print("\nIssue #284 implementation is ready for testing with `p3 test f2`")
        return 0
    else:
        print("\n❌ FAILURE: Critical imports still failing")
        print("Need additional investigation")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
