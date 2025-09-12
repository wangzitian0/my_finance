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

# Add workflows directory to Python path for import
workflows_path = os.path.join(os.path.dirname(__file__), "workflows")
sys.path.insert(0, workflows_path)

from pr_creation import (
    run_command,
    run_end_to_end_test,
    validate_environment_for_pr,
)


def main():
    """Main test runner interface"""
    parser = argparse.ArgumentParser(
        description="Run end-to-end tests with specified scope",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python infra/run_test.py f2     # Fast 2 companies test (default)
  python infra/run_test.py m7     # Magnificent 7 companies test
  python infra/run_test.py n100   # NASDAQ 100 test
  python infra/run_test.py v3k    # VTI 3500+ companies test
        """,
    )

    parser.add_argument(
        "scope",
        nargs="?",
        default="f2",
        choices=["f2", "m7", "n100", "v3k"],
        help="Test scope: f2 (fast 2 companies, default), m7 (Magnificent 7), n100 (NASDAQ 100), v3k (VTI 3500+)",
    )

    args = parser.parse_args()

    print("🧪 DEDICATED TEST RUNNER")
    print("=" * 50)
    print(f"📊 Test scope: {args.scope.upper()}")
    print()

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

    # Run the test
    test_result = run_end_to_end_test(args.scope)

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
