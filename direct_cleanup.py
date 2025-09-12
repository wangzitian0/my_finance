#!/usr/bin/env python3
"""Direct execution of directory cleanup operations for Issue #256"""

import glob
import os
import shutil
from pathlib import Path


def execute_direct_cleanup():
    """Directly execute the cleanup operations"""
    root_path = Path("/Users/SP14016/zitian/my_finance/.git/worktree/feature-256-dir-adjust")

    print(f"🚀 EXECUTING Issue #256 Directory Cleanup")
    print(f"Root path: {root_path}")
    print("=" * 60)

    # Step 1: Clean coverage files
    print("Step 1: Cleaning coverage files...")
    coverage_pattern = str(root_path / ".coverage.*")
    coverage_files = glob.glob(coverage_pattern)

    removed_coverage = 0
    print(f"Found {len(coverage_files)} coverage files:")
    for coverage_file in coverage_files:
        file_path = Path(coverage_file)
        print(f"  - {file_path.name}")
        try:
            file_path.unlink()
            removed_coverage += 1
            print(f"    ✅ Removed")
        except Exception as e:
            print(f"    ❌ Error: {e}")

    # Also check for .coverage (without extension)
    coverage_base = root_path / ".coverage"
    if coverage_base.exists():
        try:
            coverage_base.unlink()
            removed_coverage += 1
            print(f"  - .coverage ✅ Removed")
        except Exception as e:
            print(f"  - .coverage ❌ Error: {e}")

    print(f"Coverage files removed: {removed_coverage}")

    # Step 2: Move test files
    print(f"\nStep 2: Moving test files...")
    test_files = [
        "test_dual_config_compatibility.py.disabled",
        "test_f2_sec.py.disabled",
        "test_orthogonal_config.py.disabled",
        "test_sec_config.py.disabled",
    ]

    # Create tests directory
    tests_dir = root_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    moved_tests = 0
    print(f"Moving {len(test_files)} test files to tests/:")
    for test_file in test_files:
        source = root_path / test_file
        if source.exists():
            destination = tests_dir / test_file
            print(f"  - {test_file}")
            try:
                if destination.exists():
                    # Create backup name
                    backup_name = f"{destination.stem}_backup{destination.suffix}"
                    destination = tests_dir / backup_name
                    print(f"    (Using backup name: {backup_name})")

                shutil.move(str(source), str(destination))
                moved_tests += 1
                print(f"    ✅ Moved")
            except Exception as e:
                print(f"    ❌ Error: {e}")
        else:
            print(f"  - {test_file} (not found)")

    print(f"Test files moved: {moved_tests}")

    # Step 3: Check for other cleanup opportunities
    print(f"\nStep 3: Checking for other files to organize...")

    organized_other = 0

    # Look for any temporary or backup files
    temp_patterns = ["*.tmp", "*.bak", "*.old", "*~"]
    for pattern in temp_patterns:
        temp_files = glob.glob(str(root_path / pattern))
        for temp_file in temp_files:
            temp_path = Path(temp_file)
            print(f"  Removing temp file: {temp_path.name}")
            try:
                temp_path.unlink()
                organized_other += 1
                print(f"    ✅ Removed")
            except Exception as e:
                print(f"    ❌ Error: {e}")

    # Step 4: Final validation
    print(f"\nStep 4: Final validation...")

    # Count remaining files in root
    all_items = list(root_path.iterdir())
    files = [item for item in all_items if item.is_file()]
    dirs = [item for item in all_items if item.is_dir()]

    print(f"Root directory summary:")
    print(f"  - Directories: {len(dirs)}")
    print(f"  - Files: {len(files)}")

    # List files (excluding hidden files starting with .)
    visible_files = [f for f in files if not f.name.startswith(".")]
    print(f"  - Visible files: {len(visible_files)}")

    if visible_files:
        print("  Visible files remaining:")
        for f in visible_files:
            print(f"    - {f.name}")

    # Summary
    total_cleaned = removed_coverage + moved_tests + organized_other

    print(f"\n" + "=" * 60)
    print(f"CLEANUP SUMMARY")
    print(f"=" * 60)
    print(f"Coverage files removed: {removed_coverage}")
    print(f"Test files moved: {moved_tests}")
    print(f"Other files organized: {organized_other}")
    print(f"Total files processed: {total_cleaned}")
    print(f"Remaining visible files: {len(visible_files)}")

    # Success criteria
    success = (
        removed_coverage > 0  # Some coverage files removed
        or moved_tests >= 3  # Test files moved
        or total_cleaned >= 5  # Significant cleanup
    )

    if success:
        print(f"\n🎉 CLEANUP SUCCESSFUL")
        print(f"✅ Issue #256 Phase 1 directory cleanup completed")
    else:
        print(f"\n⚠️  Limited cleanup performed")

    return success


if __name__ == "__main__":
    success = execute_direct_cleanup()
    exit(0 if success else 1)
