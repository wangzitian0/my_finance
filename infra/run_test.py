#!/usr/bin/env python3
"""
P3 Test Runner - Comprehensive End-to-End Testing
Workflow-Oriented Command: TEST
"Test everything" - Complete end-to-end validation
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, timeout=600, ignore_errors=False):
    """Execute command and display results with timeout."""
    print(f"🔍 {description}...")
    start_time = time.time()

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        duration = time.time() - start_time

        if result.returncode == 0 or ignore_errors:
            print(f"✅ {description} - OK ({duration:.1f}s)")
            if result.stdout.strip() and len(result.stdout.strip()) < 200:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED ({duration:.1f}s)")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:500]}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:500]}")
            return False

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"⏰ {description} - TIMEOUT ({duration:.1f}s)")
        return False
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ {description} - ERROR ({duration:.1f}s): {e}")
        return False


def check_environment():
    """Quick environment validation before testing."""
    print("🌍 Pre-Test Environment Validation")
    print("-" * 40)

    checks = [
        ("python --version", "Python version", 10),
        ("pixi --version", "Pixi installation", 10),
        ("podman ps", "Podman containers", 15),
        ("curl -s http://localhost:7474 -o /dev/null", "Neo4j connectivity", 10),
    ]

    env_ok = True
    for cmd, desc, timeout in checks:
        if not run_command(cmd, desc, timeout, ignore_errors=True):
            env_ok = False

    if not env_ok:
        print("\n⚠️  Environment issues detected - proceeding with caution")

    print()
    return env_ok


def run_comprehensive_tests(scope="f2"):
    """Run comprehensive test suite."""
    print(f"🧪 TEST - Comprehensive End-to-End Validation ({scope})")
    print("=" * 60)

    # Environment check first
    env_ok = check_environment()

    # Test configuration based on scope
    test_config = {
        "f2": {
            "timeout": 300,  # 5 minutes
            "companies": 2,
            "description": "Fast development testing",
        },
        "m7": {
            "timeout": 1200,  # 20 minutes
            "companies": 7,
            "description": "Standard integration testing",
        },
        "n100": {
            "timeout": 3600,  # 1 hour
            "companies": 100,
            "description": "Production validation testing",
        },
        "v3k": {
            "timeout": 14400,  # 4 hours
            "companies": 3000,
            "description": "Full production testing",
        },
    }

    config = test_config.get(scope, test_config["f2"])
    timeout = config["timeout"]

    print(f"📊 Test Scope: {scope.upper()} - {config['description']}")
    print(f"📈 Companies: {config['companies']}")
    print(f"⏱️  Timeout: {timeout}s ({timeout//60}min)")
    print()

    # Test phases
    phases = [
        # Phase 1: Code Quality
        {
            "name": "🔍 Phase 1: Code Quality",
            "tests": [
                ("pixi run python -m black --check .", "Code formatting check", 60),
                ("pixi run python -m isort --check-only .", "Import sorting check", 60),
                (
                    "pixi run python -m pylint ETL dcf_engine common graph_rag --disable=C0114,C0115,C0116,R0903,W0613 --exit-zero",
                    "Code linting",
                    120,
                ),
            ],
        },
        # Phase 2: System Integration
        {
            "name": "🔧 Phase 2: System Integration",
            "tests": [
                ("python common/tests/run_tests.py", "DirectoryManager tests", 60),
                ("python infra/development/validate_io_compliance.py", "I/O compliance check", 30),
                ("python infra/system/fast_env_check.py", "Environment validation", 30),
            ],
        },
        # Phase 3: Unit Tests
        {
            "name": "🧪 Phase 3: Unit Tests",
            "tests": [
                (
                    "pixi run python -m pytest tests/ -v --tb=short --maxfail=5",
                    "Unit test suite",
                    300,
                ),
                ("pixi run python -m pytest common/tests/ -v --tb=short", "Common lib tests", 120),
            ],
        },
        # Phase 4: Data Pipeline
        {
            "name": "📊 Phase 4: Data Pipeline",
            "tests": [
                (
                    f"pixi run python ETL/build_dataset.py {scope}",
                    f"Build dataset ({scope})",
                    timeout,
                ),
                ("python common/tests/test_simple_validation.py", "Data validation", 60),
            ],
        },
        # Phase 5: End-to-End Integration
        {
            "name": "🚀 Phase 5: End-to-End Integration",
            "tests": [
                ("python graph_rag/test_rag_system.py", "RAG system test", 180),
                ("python dcf_engine/test_dcf_engine.py", "DCF engine test", 120),
            ],
        },
    ]

    # Execute test phases
    total_tests = 0
    passed_tests = 0
    failed_phases = []

    for phase in phases:
        print(phase["name"])
        print("-" * 40)

        phase_passed = 0
        phase_total = len(phase["tests"])

        for cmd, desc, test_timeout in phase["tests"]:
            total_tests += 1
            if run_command(cmd, desc, test_timeout, ignore_errors=False):
                passed_tests += 1
                phase_passed += 1

        # Phase summary
        if phase_passed == phase_total:
            print(f"✅ {phase['name']} - ALL PASSED ({phase_passed}/{phase_total})")
        elif phase_passed >= phase_total * 0.8:  # 80% pass rate
            print(f"⚠️  {phase['name']} - MOSTLY PASSED ({phase_passed}/{phase_total})")
        else:
            print(f"❌ {phase['name']} - FAILED ({phase_passed}/{phase_total})")
            failed_phases.append(phase["name"])

        print()

    # Final summary
    print("=" * 60)
    print(f"🎯 TEST SUMMARY ({scope.upper()})")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

    if failed_phases:
        print(f"\n❌ Failed Phases: {', '.join(failed_phases)}")

    # Determine exit status
    success_rate = (passed_tests / total_tests) * 100

    if success_rate >= 95:
        print("\n🎉 TESTS PASSED - System ready for deployment!")
        return 0
    elif success_rate >= 80:
        print("\n⚠️  TESTS MOSTLY PASSED - Review failures before proceeding")
        return 0 if scope in ["f2", "m7"] else 1  # Allow dev/test failures, block prod
    else:
        print("\n❌ TESTS FAILED - System not ready")
        return 1


def main():
    """Main entry point."""
    # Get scope from arguments
    scope = sys.argv[1] if len(sys.argv) > 1 else "f2"

    valid_scopes = ["f2", "m7", "n100", "v3k"]
    if scope not in valid_scopes:
        print(f"❌ Invalid scope: {scope}")
        print(f"Valid scopes: {', '.join(valid_scopes)}")
        sys.exit(1)

    # Run comprehensive tests
    exit_code = run_comprehensive_tests(scope)

    # Save test results for CI/CD
    results = {
        "scope": scope,
        "timestamp": time.time(),
        "exit_code": exit_code,
        "status": "PASSED" if exit_code == 0 else "FAILED",
    }

    results_file = Path("build_data/logs/test_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📊 Test results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save test results: {e}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
