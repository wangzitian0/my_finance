#!/usr/bin/env python3
"""
Pytest-based test runner for the common module test suite.
Provides convenient commands for running tests with coverage analysis.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    if description:
        print(f"🧪 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\n❌ Command failed with return code {result.returncode}")
        return False
    else:
        print(f"\n✅ Command completed successfully")
        return True


def run_unit_tests(verbose=False):
    """Run unit tests."""
    cmd = ["python", "-m", "pytest", "common/tests/unit/", "-v" if verbose else "", "--tb=short"]
    cmd = [arg for arg in cmd if arg]  # Remove empty strings

    return run_command(cmd, "Running Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests."""
    cmd = [
        "python",
        "-m",
        "pytest",
        "common/tests/integration/",
        "-v" if verbose else "",
        "--tb=short",
    ]
    cmd = [arg for arg in cmd if arg]  # Remove empty strings

    return run_command(cmd, "Running Integration Tests")


def run_all_tests(verbose=False):
    """Run all tests."""
    cmd = ["python", "-m", "pytest", "common/tests/", "-v" if verbose else "", "--tb=short"]
    cmd = [arg for arg in cmd if arg]  # Remove empty strings

    return run_command(cmd, "Running All Tests")


def run_tests_with_coverage(target_coverage=80, verbose=False):
    """Run tests with coverage analysis."""
    cmd = [
        "python",
        "-m",
        "pytest",
        "common/tests/",
        f"--cov=common",
        f"--cov-report=html:common/tests/coverage_html",
        f"--cov-report=term-missing",
        f"--cov-fail-under={target_coverage}",
        "-v" if verbose else "",
        "--tb=short",
    ]
    cmd = [arg for arg in cmd if arg]  # Remove empty strings

    return run_command(cmd, f"Running Tests with {target_coverage}% Coverage Requirement")


def run_specific_test(test_pattern, verbose=False):
    """Run specific test by pattern."""
    cmd = ["python", "-m", "pytest", "-k", test_pattern, "-v" if verbose else "", "--tb=short"]
    cmd = [arg for arg in cmd if arg]  # Remove empty strings

    return run_command(cmd, f"Running Tests Matching Pattern: {test_pattern}")


def run_tests_by_marker(marker, verbose=False):
    """Run tests by pytest marker."""
    cmd = ["python", "-m", "pytest", "-m", marker, "-v" if verbose else "", "--tb=short"]
    cmd = [arg for arg in cmd if arg]  # Remove empty strings

    return run_command(cmd, f"Running Tests with Marker: {marker}")


def check_test_structure():
    """Check test directory structure and files."""
    print("\n" + "=" * 60)
    print("🔍 Checking Test Structure")
    print("=" * 60)

    tests_dir = Path("common/tests")
    if not tests_dir.exists():
        print("❌ Tests directory not found")
        return False

    structure_checks = [
        ("conftest.py", tests_dir / "conftest.py"),
        ("pytest.ini", tests_dir / "pytest.ini"),
        ("requirements.txt", tests_dir / "requirements.txt"),
        ("unit tests", tests_dir / "unit"),
        ("integration tests", tests_dir / "integration"),
    ]

    all_good = True
    for name, path in structure_checks:
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (missing)")
            all_good = False

    # Count test files
    unit_tests = (
        list((tests_dir / "unit").glob("test_*.py")) if (tests_dir / "unit").exists() else []
    )
    integration_tests = (
        list((tests_dir / "integration").glob("test_*.py"))
        if (tests_dir / "integration").exists()
        else []
    )

    print(f"\n📊 Test Files Found:")
    print(f"   Unit tests: {len(unit_tests)}")
    print(f"   Integration tests: {len(integration_tests)}")
    print(f"   Total: {len(unit_tests) + len(integration_tests)}")

    if unit_tests:
        print(f"\n📝 Unit Test Files:")
        for test_file in sorted(unit_tests):
            print(f"   - {test_file.name}")

    if integration_tests:
        print(f"\n📝 Integration Test Files:")
        for test_file in sorted(integration_tests):
            print(f"   - {test_file.name}")

    return all_good


def install_test_dependencies():
    """Install test dependencies."""
    print(f"\n{'='*60}")
    print("📦 Testing Dependencies in Pixi Environment")
    print("=" * 60)
    print("✅ Core testing dependencies (pytest, pytest-cov) are managed by pixi")
    print("✅ Additional test utilities are installed via pip in pixi environment")

    # Check if we're in pixi environment
    cmd_check = [
        "python",
        "-c",
        "import pytest, pytest_cov; print('✅ Core test dependencies available')",
    ]
    success = run_command(cmd_check, "Checking Core Test Dependencies")

    if success:
        # Install additional test utilities that may not be in pixi.toml
        cmd_extras = [
            "pip",
            "install",
            "pytest-mock",
            "pytest-asyncio",
            "factory-boy",
            "freezegun",
            "responses",
            "pytest-benchmark",
            "pytest-xdist",
            "parameterized",
            "testfixtures",
        ]
        return run_command(cmd_extras, "Installing Additional Test Utilities")
    else:
        print("❌ Core test dependencies not found. Please ensure you're in pixi environment:")
        print("   pixi shell")
        return False


def generate_coverage_report():
    """Generate detailed coverage report."""
    # First run tests with coverage
    cmd = [
        "python",
        "-m",
        "pytest",
        "common/tests/",
        "--cov=common",
        "--cov-report=html:common/tests/coverage_html",
        "--cov-report=xml:common/tests/coverage.xml",
        "--cov-report=json:common/tests/coverage.json",
        "--cov-report=term-missing",
        "--quiet",
    ]

    success = run_command(cmd, "Generating Coverage Report")

    if success:
        print(f"\n📊 Coverage reports generated:")
        print(f"   HTML: common/tests/coverage_html/index.html")
        print(f"   XML: common/tests/coverage.xml")
        print(f"   JSON: common/tests/coverage.json")

        # Show coverage summary
        cmd = [
            "python",
            "-c",
            """
import json
try:
    with open('common/tests/coverage.json', 'r') as f:
        data = json.load(f)
    total = data['totals']
    print(f"\\n📈 Coverage Summary:")
    print(f"   Lines: {total['covered_lines']}/{total['num_statements']} ({total['percent_covered']:.1f}%)")
    print(f"   Branches: {total.get('covered_branches', 0)}/{total.get('num_branches', 0)} ({total.get('percent_covered_display', 'N/A')})")
    if total['percent_covered'] >= 80:
        print(f"   ✅ Coverage target met (≥80%)")
    else:
        print(f"   ❌ Coverage target not met (<80%)")
except Exception as e:
    print(f"   Could not parse coverage data: {e}")
""",
        ]
        subprocess.run(cmd, shell=True)

    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pytest-based test runner for common module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python common/tests/pytest_runner.py --unit                 # Run unit tests only
  python common/tests/pytest_runner.py --integration         # Run integration tests only  
  python common/tests/pytest_runner.py --all                 # Run all tests
  python common/tests/pytest_runner.py --coverage            # Run with coverage analysis
  python common/tests/pytest_runner.py --coverage --target 90  # Require 90% coverage
  python common/tests/pytest_runner.py --pattern storage     # Run tests matching 'storage'
  python common/tests/pytest_runner.py --marker core         # Run tests marked 'core'
  python common/tests/pytest_runner.py --install             # Install test dependencies
  python common/tests/pytest_runner.py --check               # Check test structure
  python common/tests/pytest_runner.py --report              # Generate coverage report
        """,
    )

    # Test execution options
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage analysis")
    parser.add_argument(
        "--target", type=int, default=80, help="Coverage target percentage (default: 80)"
    )

    # Test filtering options
    parser.add_argument("--pattern", help="Run tests matching pattern")
    parser.add_argument("--marker", help="Run tests with specific marker")

    # Utility options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--install", action="store_true", help="Install test dependencies")
    parser.add_argument("--check", action="store_true", help="Check test structure")
    parser.add_argument("--report", action="store_true", help="Generate coverage report")

    args = parser.parse_args()

    # Check if we're in the right directory
    if not Path("common").exists():
        print("❌ Error: Must run from project root directory (common/ should exist)")
        sys.exit(1)

    success = True

    # Handle utility commands first
    if args.install:
        success = install_test_dependencies()
    elif args.check:
        success = check_test_structure()
    elif args.report:
        success = generate_coverage_report()

    # Handle test execution commands
    elif args.unit:
        success = run_unit_tests(args.verbose)
    elif args.integration:
        success = run_integration_tests(args.verbose)
    elif args.all:
        success = run_all_tests(args.verbose)
    elif args.coverage:
        success = run_tests_with_coverage(args.target, args.verbose)
    elif args.pattern:
        success = run_specific_test(args.pattern, args.verbose)
    elif args.marker:
        success = run_tests_by_marker(args.marker, args.verbose)
    else:
        # Default: run all tests with coverage
        success = run_tests_with_coverage(args.target, args.verbose)

    if success:
        print(f"\n🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 One or more operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
