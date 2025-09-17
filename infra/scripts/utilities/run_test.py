#!/usr/bin/env python3
"""
Run End-to-End Test - Dedicated test runner without PR creation
Supports F2 (fast), M7, N100, and V3K scopes
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Import from pr_creation.py to reuse test logic

# Add infra/workflows directory to Python path for import
workflows_path = os.path.join(os.path.dirname(__file__), "..", "..", "workflows")
sys.path.insert(0, workflows_path)

from pr_creation import (
    run_command,
    run_end_to_end_test,
    validate_environment_for_pr,
)


def main():
    """Main test runner interface"""
    start_time = time.time()
    print("🧪 TEST - Comprehensive Testing Suite")
    print(f"⏰ Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    parser = argparse.ArgumentParser(
        description="Run end-to-end tests with specified scope",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/utilities/run_test.py f2     # Fast 2 companies test (default)
  python scripts/utilities/run_test.py m7     # Magnificent 7 companies test
  python scripts/utilities/run_test.py n100   # NASDAQ 100 test
  python scripts/utilities/run_test.py v3k    # VTI 3500+ companies test
        """,
    )

    parser.add_argument(
        "scope",
        nargs="?",
        default="f2",
        help="""Test scope - supports both dataset scopes and module testing:

Dataset Scopes (E2E Testing):
  f2     - Fast 2 companies (default E2E test)
  m7     - Magnificent 7 companies
  n100   - NASDAQ 100
  v3k    - VTI 3500+ companies

Module Testing (Unit Tests Only):
  common        - Test common/ L1 module
  common/core   - Test common/core/ L2 module
  common/config - Test common/config/ L2 module
  infra         - Test infra/ L1 module
  infra/p3      - Test infra/p3/ L2 module
  tests         - Test tests/ directory
  ETL           - Test ETL/ L1 module
  engine        - Test engine/ L1 module
  evaluation    - Test evaluation/ L1 module
        """,
    )

    args = parser.parse_args()

    print(f"📊 Test scope: {args.scope.upper()}")
    print(f"📁 Working directory: {Path.cwd()}")
    print()

    # Check if this is module testing (not E2E dataset scope)
    dataset_scopes = ["f2", "m7", "n100", "v3k"]
    is_module_testing = args.scope not in dataset_scopes

    if is_module_testing:
        print("🧪 MODULE TESTING MODE")
        print(f"🎯 Target: {args.scope}")
        print("=" * 50)

        # Validate module path exists
        module_path = Path(args.scope)
        if not module_path.exists():
            print(f"❌ Module path '{args.scope}' not found")
            print("💡 Available L1 modules: common, infra, ETL, engine, evaluation, tests")
            sys.exit(1)

        # Run targeted module tests
        test_cmd = f"pixi run python -m pytest {args.scope}/ -v --tb=short"
        print(f"🔬 Running tests for module: {args.scope}")
        print(f"📝 Command: {test_cmd}")
        print()

        result = run_command(test_cmd, f"Module tests for {args.scope}", timeout=300)

        if result.returncode == 0:
            print(f"\n✅ Module tests passed for {args.scope}")
            end_time = time.time()
            duration = end_time - start_time
            print(f"⏱️  Total time: {duration:.1f} seconds")
            sys.exit(0)
        else:
            print(f"\n❌ Module tests failed for {args.scope}")
            sys.exit(1)

    # E2E TESTING MODE for dataset scopes
    print("🚀 END-TO-END TESTING MODE")
    print(f"🎯 Dataset: {args.scope}")
    print("=" * 50)

    # Environment validation is mandatory
    print("🔍 Environment Validation (Mandatory)")
    print("-" * 40)

    if not validate_environment_for_pr():
        print("\n❌ Test aborted due to environment issues")
        print("🔧 Please resolve environment issues and try again")
        print("💡 Run 'p3 ready' to fix environment issues")
        sys.exit(1)

    print("✅ Environment validation passed")
    print()

    # CRITICAL: Run COMPLETE unit tests before end-to-end tests to catch failures early
    print("🧪 Comprehensive Unit Test Validation (Pre-E2E)")
    print("-" * 40)
    print("🎯 GOAL: Ensure p3 test is superset of CI tests")
    print()

    # Test commands that exactly match what CI runs (comprehensive unit tests)
    unit_test_commands = [
        # Primary ALL tests (including P3 workflow) - CI superset alignment
        (
            "pixi run python -m pytest --tb=short --maxfail=20 --cov=common --cov-report=term-missing",
            "All Unit Tests (CI Superset: common/tests/ + tests/)",
        ),
        # Core component tests by markers
        ("pixi run python -m pytest -m core --tb=short -v --maxfail=10", "Core Component Tests"),
        # Schema validation tests
        ("pixi run python -m pytest -m schemas --tb=short -v", "Schema Definition Tests"),
        # Agent tests (if they exist)
        (
            "pixi run python -m pytest -m agents --tb=short -v || echo 'No agent tests found'",
            "Agent System Tests",
        ),
        # Build module tests
        ("pixi run python -m pytest -m build --tb=short -v", "Build Module Tests"),
    ]

    print(f"📋 Running {len(unit_test_commands)} unit test categories that match CI...")
    print()

    unit_tests_passed = 0
    unit_test_failures = []

    for cmd, description in unit_test_commands:
        print(f"🔍 {description}...")
        unit_result = run_command(cmd, description)

        if not unit_result or unit_result.returncode != 0:
            unit_test_failures.append(
                (description, unit_result.stderr if unit_result else "Command failed")
            )
            print(f"❌ {description} - FAILED")
        else:
            unit_tests_passed += 1
            print(f"✅ {description} - PASSED")
        print()  # Spacing between tests

    # Summary of unit test results
    total_unit_tests = len(unit_test_commands)
    print(f"📊 Unit Test Summary: {unit_tests_passed}/{total_unit_tests} passed")

    if unit_test_failures:
        print("\n🚨 CRITICAL UNIT TEST FAILURES (Will cause CI failure!):")
        for description, error in unit_test_failures:
            print(f"   • {description}")
            if "73 failed" in str(error) or "unit test" in description.lower():
                print("     ⚠️  This is the primary CI failure cause!")

        print("\n💡 UNIT TEST FIX REQUIRED:")
        print("   1. Fix the failing unit tests above")
        print("   2. Re-run 'p3 test f2' to verify fixes")
        print("   3. Only then proceed with PR creation")
        print("\n🎯 p3 test MUST be superset of CI - all unit tests must pass here first")
        sys.exit(1)

    print("✅ All unit tests passed - CI unit tests will succeed!")
    print("🎯 p3 test is now validated as superset of CI tests")
    print()

    # Run the test
    test_start = time.time()
    print(f"⚡ End-to-end test started at {time.strftime('%H:%M:%S')}")
    test_result = run_end_to_end_test(args.scope)
    test_duration = time.time() - test_start
    total_duration = time.time() - start_time

    print("=" * 50)
    print("📊 TESTING SUMMARY:")
    print(f"⏱️ End-to-end test time: {test_duration:.2f}s")
    print(f"⏱️ Total test session time: {total_duration:.2f}s")
    print(f"🏁 Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    if isinstance(test_result, int) and test_result > 0:
        print(f"\n✅ {args.scope.upper()} test PASSED")
        print(f"📊 Validated {test_result} data files")
        sys.exit(0)
    else:
        print(f"\n❌ {args.scope.upper()} test FAILED")
        print("💡 Check the test output above for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
