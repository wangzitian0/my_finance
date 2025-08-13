#!/usr/bin/env python3
"""
Test CI validation script correctness
Simple direct testing of validation functions without git repos
"""

import datetime
import importlib.util
import sys


def import_ci_module():
    """Import the CI validation module"""
    spec = importlib.util.spec_from_file_location("ci_m7_validation", "ci_m7_validation.py")
    ci_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ci_module)
    return ci_module


def test_condition_1_positive():
    """Test condition 1 - positive case"""
    print("📝 Test: Condition 1 - Positive (has M7 marker)")

    ci = import_ci_module()
    commit_msg = """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 418 data files validated
🕐 Test Time: 2025-08-13T12:00:00Z"""

    result = ci.check_condition_1_test_run(commit_msg)

    if result:
        print("✅ Test passed: Correctly detected M7 marker")
        return True
    else:
        print("❌ Test failed: Should have detected M7 marker")
        return False


def test_condition_1_negative():
    """Test condition 1 - negative case"""
    print("📝 Test: Condition 1 - Negative (no M7 marker)")

    ci = import_ci_module()
    commit_msg = """Fix some bug

This is a regular commit without M7 validation."""

    result = ci.check_condition_1_test_run(commit_msg)

    if not result:
        print("✅ Test passed: Correctly rejected commit without M7 marker")
        return True
    else:
        print("❌ Test failed: Should have rejected commit without M7 marker")
        return False


def test_condition_2_positive():
    """Test condition 2 - positive case"""
    print("📝 Test: Condition 2 - Positive (test time within range)")

    ci = import_ci_module()
    current_time = datetime.datetime.now(datetime.timezone.utc)
    test_time = current_time - datetime.timedelta(minutes=3)
    commit_time = int(current_time.timestamp())

    commit_msg = f"""Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 418 data files validated
🕐 Test Time: {test_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"""

    result = ci.check_condition_2_test_timing(commit_msg, commit_time)

    if result:
        print("✅ Test passed: Correctly accepted test time within range")
        return True
    else:
        print("❌ Test failed: Should have accepted test time within range")
        return False


def test_condition_2_negative():
    """Test condition 2 - negative case"""
    print("📝 Test: Condition 2 - Negative (test time too early)")

    ci = import_ci_module()
    current_time = datetime.datetime.now(datetime.timezone.utc)
    test_time = current_time - datetime.timedelta(minutes=15)  # Too early
    commit_time = int(current_time.timestamp())

    commit_msg = f"""Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 418 data files validated
🕐 Test Time: {test_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"""

    result = ci.check_condition_2_test_timing(commit_msg, commit_time)

    if not result:
        print("✅ Test passed: Correctly rejected test time too early")
        return True
    else:
        print("❌ Test failed: Should have rejected test time too early")
        return False


def test_condition_3_positive():
    """Test condition 3 - positive case"""
    print("📝 Test: Condition 3 - Positive (commit within 24h)")

    ci = import_ci_module()
    current_time = datetime.datetime.now(datetime.timezone.utc)
    commit_time = int(current_time.timestamp())

    result = ci.check_condition_3_commit_freshness(commit_time)

    if result:
        print("✅ Test passed: Correctly accepted fresh commit")
        return True
    else:
        print("❌ Test failed: Should have accepted fresh commit")
        return False


def test_condition_3_negative():
    """Test condition 3 - negative case"""
    print("📝 Test: Condition 3 - Negative (commit too old)")

    ci = import_ci_module()
    current_time = datetime.datetime.now(datetime.timezone.utc)
    old_time = current_time - datetime.timedelta(hours=25)  # Too old
    commit_time = int(old_time.timestamp())

    result = ci.check_condition_3_commit_freshness(commit_time)

    if not result:
        print("✅ Test passed: Correctly rejected old commit")
        return True
    else:
        print("❌ Test failed: Should have rejected old commit")
        return False


def test_condition_4_positive():
    """Test condition 4 - positive case"""
    print("📝 Test: Condition 4 - Positive (sufficient data files)")

    ci = import_ci_module()
    commit_msg = """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 418 data files validated
🕐 Test Time: 2025-08-13T12:00:00Z"""

    result = ci.check_condition_4_test_results(commit_msg)

    if result:
        print("✅ Test passed: Correctly accepted sufficient data files")
        return True
    else:
        print("❌ Test failed: Should have accepted sufficient data files")
        return False


def test_condition_4_negative():
    """Test condition 4 - negative case"""
    print("📝 Test: Condition 4 - Negative (insufficient data files)")

    ci = import_ci_module()
    commit_msg = """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 3 data files validated
🕐 Test Time: 2025-08-13T12:00:00Z"""

    result = ci.check_condition_4_test_results(commit_msg)

    if not result:
        print("✅ Test passed: Correctly rejected insufficient data files")
        return True
    else:
        print("❌ Test failed: Should have rejected insufficient data files")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing CI M7 Validation Script Functions")
    print("=" * 60)

    tests = [
        test_condition_1_positive,
        test_condition_1_negative,
        test_condition_2_positive,
        test_condition_2_negative,
        test_condition_3_positive,
        test_condition_3_negative,
        test_condition_4_positive,
        test_condition_4_negative,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test exception: {e}")
            results.append(False)
            print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("=" * 60)
    print(f"🎯 Test Summary: {passed}/{total} passed")

    if all(results):
        print("🎉 All tests passed! CI validation functions work correctly")
        sys.exit(0)
    else:
        print("❌ Some tests failed! CI validation functions need fixing")
        sys.exit(1)


if __name__ == "__main__":
    main()
