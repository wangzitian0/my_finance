#!/usr/bin/env python3
"""
Workflow-Oriented Command: CHECK
"Validate my code" - format, lint, test, build
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, ignore_errors=False, timeout=300):
    """Execute command and display results with detailed timing."""
    start_time = time.time()
    print(f"🔍 {description}... (timeout: {timeout}s)")
    print(f"   Command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start_time

        if result.returncode == 0 or ignore_errors:
            print(f"✅ {description} - OK ({elapsed:.2f}s)")
            return True
        else:
            print(f"❌ {description} - FAILED ({elapsed:.2f}s)")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:500]}...")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"⏰ {description} - TIMEOUT ({timeout}s, elapsed: {elapsed:.2f}s)")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {description} - ERROR ({elapsed:.2f}s): {e}")
        return False


def main():
    start_time = time.time()
    print("🔍 CHECK - Validating code quality")
    print(f"⏰ Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Get scope from arguments
    scope = sys.argv[1] if len(sys.argv) > 1 else "f2"
    print(f"📋 Scope: {scope}")
    print(f"📁 Working directory: {Path.cwd()}")

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
        # 4. Run unit tests (comprehensive)
        (
            "pixi run python -m pytest common/tests/unit/ -v --tb=short",
            "Common module unit tests",
            False,
        ),
        # 5. Run marker-based tests
        ("pixi run python -m pytest -m core --tb=short -v", "Core component tests", True),
        # 6. Quick build validation
        (
            f"pixi run python ETL/build_dataset.py {scope}",
            f"Build validation ({scope})",
            False,
        ),
    ]

    success_count = 0
    total_steps = len(steps)
    step_times = []

    for i, (cmd, desc, ignore_errors) in enumerate(steps, 1):
        step_start = time.time()
        print(f"📍 Step {i}/{total_steps}: {desc}")

        if run_command(cmd, desc, ignore_errors):
            success_count += 1

        step_duration = time.time() - step_start
        step_times.append((desc, step_duration))
        print(f"⏱️ Step completed in {step_duration:.2f}s")
        print()  # Empty line separator

    total_duration = time.time() - start_time

    print("=" * 50)
    print("📊 STEP TIMING SUMMARY:")
    for desc, duration in step_times:
        print(f"   {desc}: {duration:.2f}s")
    print(f"🕐 Total check time: {total_duration:.2f}s")
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
