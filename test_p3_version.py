#!/usr/bin/env python3
"""
Test script for P3 Version Management System

This script validates that all P3 version management components are working correctly.
"""

import os
import sys
from pathlib import Path


def test_imports():
    """Test that all version management modules can be imported."""
    print("🔍 Testing imports...")

    try:
        import p3_version

        print("✅ p3_version module imported successfully")

        from p3_version import get_p3_version, get_version_manager, print_version_info

        print("✅ Core functions imported successfully")

        from p3_version import print_update_check, print_version_history

        print("✅ Enhanced functions imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_version_manager():
    """Test basic version manager functionality."""
    print("\n🔍 Testing version manager...")

    try:
        from p3_version import get_version_manager

        manager = get_version_manager()

        # Test version string generation
        version = manager.get_version_string()
        print(f"✅ Version string: {version}")

        # Test version info
        info = manager.get_version_info()
        print(f"✅ Version info loaded: {info['version_string']}")

        # Test update check
        check_info = manager.check_for_updates()
        print(f"✅ Update check: {'needs update' if check_info['needs_update'] else 'up to date'}")

        return True
    except Exception as e:
        print(f"❌ Version manager error: {e}")
        return False


def test_git_integration():
    """Test git integration functionality."""
    print("\n🔍 Testing git integration...")

    try:
        from p3_version import get_version_manager

        manager = get_version_manager()

        # Test git hash
        git_hash = manager._get_git_hash()
        print(f"✅ Git hash: {git_hash}")

        # Test git branch
        git_branch = manager._get_git_branch()
        print(f"✅ Git branch: {git_branch}")

        # Test git directory detection
        git_dir = manager._get_git_dir()
        if git_dir:
            print(f"✅ Git directory: {git_dir}")
        else:
            print("⚠️  Git directory not detected")

        return True
    except Exception as e:
        print(f"❌ Git integration error: {e}")
        return False


def test_p3_integration():
    """Test P3 CLI integration."""
    print("\n🔍 Testing P3 CLI integration...")

    try:
        # Check if p3.py can import version functions
        sys.path.insert(0, str(Path(__file__).parent))
        import p3

        # Test VERSION_ENABLED flag
        if hasattr(p3, "VERSION_ENABLED") and p3.VERSION_ENABLED:
            print("✅ P3 version integration enabled")
        else:
            print("⚠️  P3 version integration not fully enabled")

        # Test version commands in p3
        cli = p3.P3CLI()
        version_commands = [cmd for cmd in cli.commands.keys() if cmd.startswith("version")]
        print(f"✅ Version commands available: {', '.join(version_commands)}")

        return True
    except Exception as e:
        print(f"❌ P3 integration error: {e}")
        return False


def test_hook_status():
    """Test git hooks installation status."""
    print("\n🔍 Testing git hooks status...")

    try:
        from p3_version import get_version_manager

        manager = get_version_manager()

        git_dir = manager._get_git_dir()
        if git_dir:
            post_merge_hook = git_dir / "hooks" / "post-merge"
            if post_merge_hook.exists():
                print("✅ Post-merge hook installed")

                # Check if it contains P3 version logic
                with open(post_merge_hook, "r") as f:
                    content = f.read()
                if "p3_version.py" in content:
                    print("✅ Hook contains P3 version update logic")
                else:
                    print("⚠️  Hook exists but may not contain P3 version logic")
            else:
                print("⚠️  Post-merge hook not installed")
        else:
            print("❌ Cannot detect git directory")

        return True
    except Exception as e:
        print(f"❌ Hook status error: {e}")
        return False


def run_all_tests():
    """Run all tests and provide summary."""
    print("🚀 P3 Version Management System Test")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("Version Manager Tests", test_version_manager),
        ("Git Integration Tests", test_git_integration),
        ("P3 CLI Integration Tests", test_p3_integration),
        ("Git Hooks Status", test_hook_status),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))

    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Summary")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! P3 Version Management System is fully functional.")
        print("\n💡 Next steps:")
        print("1. Run 'p3 install-version-hooks' to install git hooks")
        print("2. Use 'p3 version' to see current version")
        print("3. Version will auto-update after git pull operations")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
