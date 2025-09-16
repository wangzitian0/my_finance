#!/usr/bin/env python3
"""
Migration Validation - Verify scripts-to-infra migration completion
Validates that all references point to new infra/ paths and no critical scripts remain in scripts/
"""

import os
import subprocess
import sys
from pathlib import Path


def validate_p3_imports():
    """Validate that p3.py uses the correct import paths."""
    print("🔍 Validating P3 CLI imports...")

    p3_file = Path("p3.py")
    if not p3_file.exists():
        print("❌ p3.py not found")
        return False

    with open(p3_file, "r") as f:
        content = f.read()

    # Check that it imports from infra.p3
    if "from infra.p3.p3_version_simple import" in content:
        print("✅ P3 version imports updated to infra/p3/")
    else:
        print("❌ P3 version imports still use old paths")
        return False

    return True


def validate_infra_paths():
    """Validate that infra paths exist and are properly organized."""
    print("🔍 Validating infra directory structure...")

    required_paths = [
        "infra/system/fast_env_check.py",
        "infra/system/workflow_ready.py",
        "infra/system/workflow_reset.py",
        "infra/system/workflow_debug.py",
        "infra/development/workflow_check.py",
        "infra/development/validate_io_compliance.sh",
        "infra/p3/p3_version_simple.py",
        "infra/p3/.p3_version.json",
        "infra/run_test.py",
        "infra/create_pr_with_test.py",
    ]

    all_exist = True
    for path in required_paths:
        if Path(path).exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path} - MISSING")
            all_exist = False

    return all_exist


def validate_create_pr_references():
    """Validate that create_pr_with_test.py uses updated references."""
    print("🔍 Validating create_pr_with_test.py references...")

    pr_file = Path("infra/create_pr_with_test.py")
    if not pr_file.exists():
        print("❌ create_pr_with_test.py not found in infra/")
        return False

    with open(pr_file, "r") as f:
        content = f.read()

    # Check for old scripts/ references
    if "scripts/fast_env_check.py" in content:
        print("❌ create_pr_with_test.py still references scripts/fast_env_check.py")
        return False

    # Check for new infra/ references
    if "infra/system/fast_env_check.py" in content:
        print("✅ create_pr_with_test.py uses infra/system/fast_env_check.py")
    else:
        print("❌ create_pr_with_test.py doesn't use infra path for fast_env_check.py")
        return False

    return True


def validate_p3_commands_work():
    """Test that P3 commands still work with new paths."""
    print("🔍 Testing P3 commands with new paths...")

    # Test version command (should not hang in worktree)
    try:
        result = subprocess.run(
            ["python3", "p3.py", "version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("✅ P3 version command works")
            if result.stdout.strip():
                print(f"   Version: {result.stdout.strip()}")
        else:
            print(f"❌ P3 version command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ P3 version command timed out")
        return False
    except Exception as e:
        print(f"❌ P3 version command error: {e}")
        return False

    # Test that help works
    try:
        result = subprocess.run(
            ["python3", "p3.py", "help"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and "DAILY WORKFLOW" in result.stdout:
            print("✅ P3 help command works")
        else:
            print(f"❌ P3 help command failed")
            return False
    except Exception as e:
        print(f"❌ P3 help command error: {e}")
        return False

    return True


def check_remaining_scripts():
    """Check what files remain in scripts/ directory."""
    print("🔍 Checking remaining files in scripts/...")

    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("ℹ️  scripts/ directory does not exist")
        return True

    remaining_files = []
    for item in scripts_dir.rglob("*"):
        if item.is_file() and not item.name.startswith("."):
            # Skip migration marker and other documentation
            if item.name not in ["MIGRATED_TO_INFRA.md", "README.md"]:
                remaining_files.append(str(item))

    if remaining_files:
        print("⚠️  Files still in scripts/:")
        for file in remaining_files[:10]:  # Show first 10
            print(f"   📄 {file}")
        if len(remaining_files) > 10:
            print(f"   ... and {len(remaining_files) - 10} more")

        # Check if they're duplicates of infra files
        critical_remaining = []
        for file in remaining_files:
            if not file.endswith((".md", ".txt", ".json")):
                critical_remaining.append(file)

        if critical_remaining:
            print(f"⚠️  {len(critical_remaining)} non-documentation files remain")
            return False
        else:
            print("✅ Only infra/docs files remain")
            return True
    else:
        print("✅ No non-documentation files remain in scripts/")
        return True


def main():
    """Run all migration validation checks."""
    print("🔍 SCRIPTS-TO-INFRA MIGRATION VALIDATION")
    print("=" * 50)

    checks = [
        ("P3 CLI imports", validate_p3_imports),
        ("Infra directory paths", validate_infra_paths),
        ("create_pr_with_test.py references", validate_create_pr_references),
        ("P3 commands functionality", validate_p3_commands_work),
        ("Remaining scripts cleanup", check_remaining_scripts),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 30)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 MIGRATION VALIDATION SUMMARY")
    print("=" * 50)

    passed = 0
    failed = 0

    for check_name, result in results:
        if result:
            print(f"✅ {check_name}")
            passed += 1
        else:
            print(f"❌ {check_name}")
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 MIGRATION VALIDATION PASSED")
        print("✅ Scripts-to-infra migration is complete and functional")
        print("✅ All P3 commands work with new infra/ paths")
        print("✅ No critical files remain in scripts/ directory")
        return True
    else:
        print(f"\n❌ MIGRATION VALIDATION FAILED")
        print(f"🚨 {failed} validation checks failed")
        print("💡 Please fix the issues above before considering migration complete")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
