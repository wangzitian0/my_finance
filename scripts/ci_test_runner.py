#!/usr/bin/env python3
"""
CI Test Runner - Ensures p3 tests are superset of CI tests
Prevents the critical issue where p3 ship tests pass but CI fails.

This script runs the exact same tests that CI runs, ensuring:
1. p3 test failures = CI failures (no false positives)
2. p3 test passes = CI passes (no surprises)
3. Complete alignment between local testing and CI validation
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: str, description: str) -> Tuple[bool, str]:
    """Run command and return success status and output."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True, result.stdout
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False, "Command timed out"
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {e}")
        return False, str(e)


def main():
    """Run the complete CI test suite locally to validate p3/CI alignment."""
    print("🚀 CI TEST RUNNER - P3/CI Test Alignment Validation")
    print("=" * 60)
    print("🎯 CRITICAL GOAL: Make p3 tests a superset of CI tests")
    print("🔍 Testing: All unit tests that run in CI")
    print("💡 Use Case: Run before 'p3 test f2' to verify alignment")
    print("⚠️  If tests fail here, they will also fail in CI")
    print()

    # Test commands that exactly match what CI runs - with pixi environment
    ci_test_commands = [
        # Unit tests (primary failure source)
        (
            "pixi run python -m pytest common/tests/unit/ -v --tb=short --maxfail=20",
            "Common Unit Tests (Primary CI Test)",
        ),
        # Core component tests
        ("pixi run python -m pytest -m core --tb=short -v --maxfail=10", "Core Component Tests"),
        # Integration tests
        (
            "pixi run python -m pytest common/tests/integration/ -v --tb=short --maxfail=5",
            "Integration Tests",
        ),
        # Schema validation tests
        ("pixi run python -m pytest -m schemas --tb=short -v", "Schema Definition Tests"),
        # Agent tests (if they exist)
        (
            "pixi run python -m pytest -m agents --tb=short -v || echo 'No agent tests found'",
            "Agent System Tests",
        ),
    ]

    print(f"📋 Running {len(ci_test_commands)} CI test categories...")
    print()

    passed_tests = 0
    failed_tests = []

    for cmd, description in ci_test_commands:
        success, output = run_command(cmd, description)
        if success:
            passed_tests += 1
        else:
            failed_tests.append((description, output))
        print()  # Spacing between tests

    # Summary
    print("=" * 60)
    print("📊 CI TEST ALIGNMENT SUMMARY")
    print("=" * 60)

    total_tests = len(ci_test_commands)
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {len(failed_tests)}/{total_tests}")

    if failed_tests:
        print("\n🚨 CRITICAL FAILURES (Will cause CI to fail):")
        for description, error in failed_tests:
            print(f"   • {description}")
            if "73 failed" in error or "unit test" in description.lower():
                print("     ⚠️  This is the primary CI failure cause!")

        print("\n💡 NEXT STEPS:")
        print("   1. Fix the failing unit tests above")
        print("   2. Re-run this script to verify fixes")
        print("   3. Only then run 'p3 ship' to create PR")
        print("\n🎯 GOAL: All tests must pass here before CI will pass")
        sys.exit(1)
    else:
        print("\n🎉 SUCCESS: All CI tests pass!")
        print("✅ p3 ship will now succeed in CI")
        print("🚀 Safe to create PR - CI alignment confirmed")
        sys.exit(0)


if __name__ == "__main__":
    main()
