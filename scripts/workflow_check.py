#!/usr/bin/env python3
"""
Workflow-Oriented Command: CHECK
"Validate my code" - format, lint, test, build
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, ignore_errors=False):
    """Execute command and display results."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0 or ignore_errors:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    print("🔍 CHECK - Validating code quality")
    print("=" * 50)

    # Get scope from arguments
    scope = sys.argv[1] if len(sys.argv) > 1 else "f2"

    steps = [
        # 1. Format code
        (
            "pixi run python -m black --line-length 100 . && pixi run python -m isort .",
            "Code formatting",
            False,
        ),
        # 2. Lint code
        (
            "pixi run python -m pylint ETL dcf_engine common graph_rag --disable=C0114,C0115,C0116,R0903,W0613",
            "Code linting",
            True,
        ),
        # 3. Type check
        (
            "pixi run python -m mypy ETL dcf_engine common graph_rag --ignore-missing-imports",
            "Type checking",
            True,
        ),
        # 4. Run tests
        ("pixi run python -m pytest tests/ -v", "Unit tests", False),
        # 5. Quick build validation
        (
            f"pixi run python ETL/build_dataset.py {scope} --fast-mode",
            f"Build validation ({scope})",
            False,
        ),
    ]

    success_count = 0
    total_steps = len(steps)

    for cmd, desc, ignore_errors in steps:
        if run_command(cmd, desc, ignore_errors):
            success_count += 1
        print()  # Empty line separator

    print("=" * 50)
    if success_count == total_steps:
        print("🎉 CHECK PASSED - Code is ready!")
        print("💡 Next: Use 'p3 test' for comprehensive testing")
        sys.exit(0)
    elif success_count >= total_steps - 1:
        print("⚠️  CHECK MOSTLY PASSED - Minor issues detected")
        print("💡 Review warnings above and proceed with caution")
        sys.exit(0)
    else:
        print("❌ CHECK FAILED - Code needs attention")
        print("💡 Fix errors above before proceeding")
        sys.exit(1)


if __name__ == "__main__":
    main()
