#!/usr/bin/env python3
"""
CI M7 Validation Script - Pure 4-condition validation logic
Used in GitHub Actions, no test logic included
"""

import datetime
import re
import subprocess
import sys
from typing import Optional


def get_commit_info():
    """Get commit information - check actual PR commits, not merge commit"""
    import os

    try:
        # In GitHub Actions, check if we have PR-specific environment variables
        github_sha = os.environ.get("GITHUB_SHA")
        github_event_name = os.environ.get("GITHUB_EVENT_NAME")

        if github_event_name == "pull_request" and github_sha:
            # In PR context, GitHub_SHA is the merge commit
            # We need to find the actual PR branch head
            print("🔍 GitHub Actions PR context detected...")

            # Check if current HEAD is a merge commit
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%P"], capture_output=True, text=True, check=True
            )
            parents = result.stdout.strip().split()

            if len(parents) > 1:
                print("🔍 Found merge commit, getting PR branch commits...")
                print(f"🔍 Merge parents: {parents}")

                # Fix: Check both parents to find the most recent PR commit with test markers
                candidates = []
                for i, parent in enumerate(parents):
                    try:
                        print(f"🔍 Checking parent {i+1}: {parent[:8]}")

                        # Get commit message from this parent
                        result = subprocess.run(
                            ["git", "log", "-1", "--pretty=%B", parent],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        parent_msg = result.stdout.strip()

                        # Get commit timestamp from this parent
                        result = subprocess.run(
                            ["git", "log", "-1", "--pretty=%ct", parent],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        commit_time = int(result.stdout.strip())

                        # Check if this parent has F2-TESTED or M7-TESTED marker
                        has_test_marker = "F2-TESTED" in parent_msg or "M7-TESTED" in parent_msg
                        print(
                            f"🔍 Parent {i+1} has test marker: {has_test_marker}, commit time: {commit_time}"
                        )

                        if has_test_marker:
                            candidates.append((parent_msg, commit_time, parent, i + 1))

                    except Exception as e:
                        print(f"🔍 Error checking parent {i+1}: {e}")
                        continue

                if candidates:
                    # Sort by commit timestamp (most recent first) and prefer second parent if timestamps are close
                    candidates.sort(
                        key=lambda x: (-x[1], x[3])
                    )  # Sort by -timestamp, then parent number
                    chosen = candidates[0]
                    print(
                        f"🔍 Selected most recent PR commit: {chosen[2][:8]} (parent {chosen[3]})"
                    )
                    return chosen[0], chosen[1]

                # Fallback: if no parent has test markers, use the second parent (usually PR branch)
                if len(parents) >= 2:
                    print("🔍 No test markers found, using second parent as fallback")
                    fallback_parent = parents[1]

                    result = subprocess.run(
                        ["git", "log", "-1", "--pretty=%B", fallback_parent],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    commit_msg = result.stdout.strip()

                    result = subprocess.run(
                        ["git", "log", "-1", "--pretty=%ct", fallback_parent],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    commit_time = int(result.stdout.strip())

                    return commit_msg, commit_time
                else:
                    print("🔍 Cannot determine PR commit, falling back to HEAD")

        # Not in PR context or no merge commit detected, use HEAD
        print("🔍 Using HEAD commit...")

        # Get commit message
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True
        )
        commit_msg = result.stdout.strip()

        # Get commit timestamp
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%ct"], capture_output=True, text=True, check=True
        )
        commit_time = int(result.stdout.strip())

        return commit_msg, commit_time
    except Exception as e:
        print(f"❌ Failed to get commit info: {e}")
        sys.exit(1)


def check_condition_1_test_run(commit_msg: str) -> bool:
    """Condition 1: Tests were run (M7 or F2 fast-build accepted)"""
    print("🔍 Checking condition 1: Test execution verification")

    # Accept both M7 and F2 test markers
    has_m7_test = (
        "M7-TESTED" in commit_msg and "This commit passed M7 end-to-end testing" in commit_msg
    )
    has_f2_test = (
        "F2-TESTED" in commit_msg and "This commit passed F2 fast-build testing" in commit_msg
    )

    if has_m7_test:
        print("✅ Condition 1 passed: Found M7 complete test marker")
        return True
    elif has_f2_test:
        print("✅ Condition 1 passed: Found F2 fast test marker")
        return True
    else:
        print("❌ Condition 1 FAILED: Missing valid test execution marker")
        print()
        print("🚨 ERROR: This commit was not created using the required workflow!")
        print()
        print("🔧 Correct workflow:")
        print("   1. Run tests: p3 e2e                      # Execute F2 fast test")
        print('   2. Create PR: p3 create-pr "title" ISSUE   # Auto validation and PR creation')
        print()
        print("❌ Forbidden methods (CI will fail):")
        print("   • Direct git push/commit")
        print("   • Manual GitHub UI PR creation")
        print("   • Hand-crafted test markers")
        print("   • Bypassing automation scripts")
        print()
        print("📖 See CLAUDE.md for why manual methods fail")
        return False


def extract_test_time(commit_msg: str) -> Optional[datetime.datetime]:
    """Extract test time from commit message"""
    for line in commit_msg.split("\n"):
        if "Test Time:" in line:
            time_match = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", line)
            if time_match:
                try:
                    return datetime.datetime.fromisoformat(
                        time_match.group(1).replace("Z", "+00:00")
                    )
                except:
                    pass
    return None


def check_condition_2_test_timing(commit_msg: str, commit_time: int) -> bool:
    """Condition 2: Test time within 10 minutes of commit time"""
    print("🔍 Checking condition 2: Test timing validation (within 10 minutes)")

    test_time = extract_test_time(commit_msg)
    if not test_time:
        print("❌ Condition 2 FAILED: Cannot extract valid test timestamp")
        print()
        print("🚨 This indicates hand-crafted or invalid test markers!")
        print()
        print("✅ Solution: Use automated workflow:")
        print("   1. p3 e2e                           # Real tests embed valid timestamps")
        print('   2. p3 create-pr "title" ISSUE       # Proper commit message format')
        return False

    commit_dt = datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)
    time_diff = (commit_dt - test_time).total_seconds()
    time_diff_min = time_diff / 60

    print(f"   Test time: {test_time}")
    print(f"   Commit time: {commit_dt}")
    print(f"   Time difference: {time_diff:.0f}s ({time_diff_min:.1f}min)")

    if time_diff > 600:  # 10 minutes
        print(f"❌ Condition 2 FAILED: Test timestamp too early ({time_diff_min:.1f}min ago)")
        print()
        print("🚨 This indicates fake or stale test results!")
        print("✅ Solution: Run fresh tests immediately before PR creation:")
        print("   1. p3 e2e                           # Fresh test execution")
        print('   2. p3 create-pr "title" ISSUE       # Immediate PR creation')
        return False
    elif time_diff < -120:  # -2 minutes
        print(f"❌ Condition 2 FAILED: Test timestamp too late ({-time_diff_min:.1f}min after)")
        print("🚨 This indicates manipulated timestamps!")
        return False
    else:
        print("✅ Condition 2 passed: Test timing is within acceptable range")
        return True


def check_condition_3_commit_freshness(commit_time: int) -> bool:
    """Condition 3: Commit within 24 hours"""
    print("🔍 Checking condition 3: Commit freshness validation (within 24 hours)")

    now = datetime.datetime.now(datetime.timezone.utc)
    commit_dt = datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)
    time_diff = (now - commit_dt).total_seconds()
    hours_diff = time_diff / 3600

    print(f"   Current time: {now}")
    print(f"   Commit time: {commit_dt}")
    print(f"   Time difference: {hours_diff:.1f}h")

    if hours_diff > 24:
        print(f"❌ Condition 3 FAILED: Commit too old ({hours_diff:.1f}h ago)")
        print()
        print("🚨 This commit exceeds the 24-hour freshness requirement!")
        print()
        print("✅ Solution: Create a fresh commit using automated workflow:")
        print("   1. Make any small code change (or run p3 format)")
        print("   2. p3 e2e                           # Fresh test execution")
        print('   3. p3 create-pr "title" ISSUE       # Fresh commit within 24h')
        return False
    else:
        print("✅ Condition 3 passed: Commit is within 24 hours")
        return True


def check_condition_4_test_results(commit_msg: str) -> bool:
    """Condition 4: Sufficient test results (≥2 data files for F2)"""
    print("🔍 Checking condition 4: Test results validation (data sufficiency)")

    if "Test Results:" in commit_msg and "data files validated" in commit_msg:
        for line in commit_msg.split("\n"):
            if "Test Results:" in line:
                numbers = re.findall(r"\d+", line)
                if numbers:
                    file_count = int(numbers[0])
                    print(f"   Found test results: {file_count} data files")
                    # Accept both M7 (≥7 files) and F2 (≥2 files) test results
                    if file_count >= 2:
                        test_type = "M7 complete test" if file_count >= 7 else "F2 fast test"
                        print(
                            f"✅ Condition 4 passed: Validated {file_count} data files ({test_type})"
                        )
                        return True
                    else:
                        print(f"❌ Condition 4 FAILED: Insufficient data files ({file_count} < 2)")
                        print()
                        print("🚨 This indicates incomplete test execution!")
                        print()
                        print("✅ Solution: Run proper testing:")
                        print("   1. p3 e2e                           # F2 fast test validation")
                        print(
                            '   2. p3 create-pr "title" ISSUE       # Proper test result embedding'
                        )
                        return False
        print("❌ Condition 4 FAILED: Cannot parse test results count")
        print("🚨 This indicates corrupted or hand-crafted test markers!")
        return False
    else:
        print("❌ Condition 4 FAILED: Test results not found")
        print()
        print("🚨 This indicates the commit was not created through proper testing!")
        print()
        print("✅ Solution:")
        print("   1. p3 e2e                           # Execute real tests")
        print('   2. p3 create-pr "title" ISSUE       # Embed test results in commit')
        return False


def check_condition_5_code_formatting() -> bool:
    """Condition 5: Python code formatting with black and isort"""
    print("🔍 Checking condition 5: Python code formatting validation")

    try:
        # Install formatting tools if needed
        try:
            subprocess.run(
                ["python3", "-c", "import black, isort"], capture_output=True, check=True
            )
        except subprocess.CalledProcessError:
            print("   Installing black and isort...")
            subprocess.run(["pip", "install", "black", "isort"], capture_output=True, check=True)

        # Define project directories to check (avoid checking dependencies)
        project_dirs = [
            "ETL/",
            "dcf_engine/",
            "common/",
            "graph_rag/",
            "tests/",
            "infra/",
            "scripts/",
            "ci_m7_validation.py",
            "p3.py",
        ]

        # Check black formatting on project files only
        print("   Running black format check...")
        black_cmd = ["python3", "-m", "black", "--check", "--line-length", "100"] + project_dirs
        black_result = subprocess.run(black_cmd, capture_output=True, text=True)

        # Check isort formatting on project files only
        print("   Running isort format check...")
        isort_cmd = ["python3", "-m", "isort", "--check-only"] + project_dirs
        isort_result = subprocess.run(isort_cmd, capture_output=True, text=True)

        if black_result.returncode == 0 and isort_result.returncode == 0:
            print("✅ Condition 5 passed: Python code is properly formatted")
            return True
        else:
            print("❌ Condition 5 FAILED: Python code formatting issues found")
            print()
            if black_result.returncode != 0:
                print("🐍 Black formatting errors:")
                print(f"   {black_result.stderr}")
                print()
            if isort_result.returncode != 0:
                print("📦 Import sorting errors:")
                print(f"   {isort_result.stderr}")
                print()
            print("✅ SOLUTION: Fix formatting before creating PR:")
            print("   1. p3 format                        # Auto-fix all formatting")
            print("   2. p3 e2e                           # Validate after formatting")
            print('   3. p3 create-pr "title" ISSUE_NUMBER # Clean, formatted PR')
            return False

    except Exception as e:
        print(f"❌ Condition 5 FAILED: Error checking code formatting: {e}")
        print()
        print("🚨 This may indicate missing formatting tools or system issues!")
        print()
        print("✅ SOLUTION: Ensure clean environment:")
        print("   1. p3 activate                      # Ensure proper environment")
        print("   2. p3 format                        # Install and run formatters")
        return False


def main():
    """Main validation function - CI only"""
    print("🔍 CI Test Validation Starting - Checking 5 Core Conditions")
    print("1. ✅ Tests executed (M7 or F2)")
    print("2. ⏰ Test timing within 10 minutes of push")
    print("3. 📅 Push time within 24 hours")
    print("4. 📊 Simple tests pass on CI")
    print("5. 🎨 Python code formatting validation")
    print("=" * 60)

    # Get commit info
    commit_msg, commit_time = get_commit_info()

    print(f"📝 Commit time: {datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)}")
    print(f"📝 Message length: {len(commit_msg)} characters")

    # Debug: Show first few lines of commit message for troubleshooting
    lines = commit_msg.split("\n")
    print(f"📝 First line: {lines[0]}")
    if len(lines) > 1:
        print(f"📝 Total lines: {len(lines)}")
        for i, line in enumerate(lines[1:6], 1):  # Show lines 1-5
            print(f"📝 Line {i}: {line}")
    print()

    # Run all checks
    checks = [
        check_condition_1_test_run(commit_msg),
        check_condition_2_test_timing(commit_msg, commit_time),
        check_condition_3_commit_freshness(commit_time),
        check_condition_4_test_results(commit_msg),
        check_condition_5_code_formatting(),
    ]

    passed = sum(checks)
    total = len(checks)

    print("=" * 60)
    if all(checks):
        print(f"🎉 ALL M7 VALIDATION CHECKS PASSED! ({passed}/{total})")
        print("✅ This commit meets all quality requirements and can be safely merged")
        print("✅ The automated workflow was followed correctly")
        sys.exit(0)
    else:
        print(f"❌ M7 VALIDATION FAILED! ({passed}/{total} passed)")
        print("🚫 This commit does not meet quality requirements and should NOT be merged")
        print()
        print("🚨 ROOT CAUSE: This commit was not created using the required automated workflow")
        print()
        print("✅ COMPLETE SOLUTION (follow this exact sequence):")
        print("   1. p3 format                        # Fix any code formatting issues")
        print("   2. p3 e2e                           # Execute complete M7 testing")
        print('   3. p3 create-pr "Brief desc" ISSUE_NUM # Create/update PR with validation')
        print()
        print("❌ NEVER do these (they will always fail CI):")
        print("   • Direct git push/commit commands")
        print("   • Manual PR creation via GitHub UI")
        print("   • Hand-crafting M7-TESTED markers")
        print("   • Bypassing the p3 create-pr script")
        print()
        print("📖 For detailed explanation, see: CLAUDE.md (Why Manual Git Commands WILL FAIL CI)")
        sys.exit(1)


if __name__ == "__main__":
    main()
