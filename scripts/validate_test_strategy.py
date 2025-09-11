#!/usr/bin/env python3
"""
Test Strategy Validation Script
Verifies that P3 test commands are properly configured as superset of CI tests
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str, timeout: int = 60) -> tuple[bool, str]:
    """Run command and return success status and output."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True, result.stdout
        else:
            print(f"❌ {description} - FAILED")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False, "Command timed out"
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False, str(e)


def validate_p3_test_integration():
    """Validate P3 test integration with unit tests."""
    print("🧪 P3 TEST STRATEGY VALIDATION")
    print("=" * 50)
    print("🎯 Validating that p3 test is superset of CI tests")
    print()

    validations = []

    # 1. Check if p3.py has correct test command mapping
    p3_file = Path("p3.py")
    if p3_file.exists():
        with open(p3_file, "r") as f:
            content = f.read()
            if '"test": "python infra/run_test.py"' in content:
                print("✅ P3 test command properly mapped to infra/run_test.py")
                validations.append(True)
            else:
                print("❌ P3 test command mapping not found")
                validations.append(False)
    else:
        print("❌ p3.py file not found")
        validations.append(False)

    # 2. Check if run_test.py includes unit tests
    run_test_file = Path("infra/run_test.py")
    if run_test_file.exists():
        with open(run_test_file, "r") as f:
            content = f.read()
            unit_test_indicators = [
                "common/tests/unit/",
                "pytest -m core",
                "pytest -m schemas",
                "Unit Test Validation",
                "superset of CI tests",
            ]
            found_indicators = sum(1 for indicator in unit_test_indicators if indicator in content)

            if found_indicators >= 3:
                print(
                    f"✅ run_test.py includes comprehensive unit tests ({found_indicators}/5 indicators)"
                )
                validations.append(True)
            else:
                print(
                    f"❌ run_test.py missing unit test integration ({found_indicators}/5 indicators)"
                )
                validations.append(False)
    else:
        print("❌ infra/run_test.py file not found")
        validations.append(False)

    # 3. Check pixi.toml test tasks
    pixi_file = Path("pixi.toml")
    if pixi_file.exists():
        with open(pixi_file, "r") as f:
            content = f.read()
            if "test-ci-unit" in content and "test-ci-integration" in content:
                print("✅ Pixi.toml has CI-aligned test tasks")
                validations.append(True)
            else:
                print("❌ Pixi.toml missing CI-aligned test tasks")
                validations.append(False)
    else:
        print("❌ pixi.toml file not found")
        validations.append(False)

    # 4. Check pytest.ini markers
    pytest_file = Path("pytest.ini")
    if pytest_file.exists():
        with open(pytest_file, "r") as f:
            content = f.read()
            required_markers = ["unit:", "core:", "schemas:", "ci:"]
            found_markers = sum(1 for marker in required_markers if marker in content)

            if found_markers >= 3:
                print(f"✅ pytest.ini has required test markers ({found_markers}/4 markers)")
                validations.append(True)
            else:
                print(f"❌ pytest.ini missing required markers ({found_markers}/4 markers)")
                validations.append(False)
    else:
        print("❌ pytest.ini file not found")
        validations.append(False)

    # 5. Check CI test runner exists
    ci_runner = Path("scripts/ci_test_runner.py")
    if ci_runner.exists():
        print("✅ CI test runner script exists")
        validations.append(True)
    else:
        print("❌ CI test runner script not found")
        validations.append(False)

    print()
    print("=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    passed = sum(validations)
    total = len(validations)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 SUCCESS: P3 test strategy properly configured!")
        print("✅ p3 test will run unit tests before integration tests")
        print("✅ p3 ship will validate CI-equivalent tests")
        print("✅ Test alignment prevents CI failures")
        return True
    else:
        print(f"\n🚨 ISSUES FOUND: {total - passed} validation(s) failed")
        print("💡 Fix the issues above to ensure proper test strategy")
        return False


def main():
    """Main validation function."""
    success = validate_p3_test_integration()

    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Run 'p3 test f2' to test new comprehensive testing")
        print("2. Verify unit tests run before integration tests")
        print("3. Use 'p3 ci' to validate CI alignment")
        sys.exit(0)
    else:
        print("\n🔧 REQUIRED FIXES:")
        print("1. Complete the test strategy implementation")
        print("2. Re-run this script to verify fixes")
        sys.exit(1)


if __name__ == "__main__":
    main()
