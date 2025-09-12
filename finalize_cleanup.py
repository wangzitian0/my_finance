#!/usr/bin/env python3
"""
Final cleanup script to remove original test files from root after moving to tests/
"""

from pathlib import Path


def main():
    root_path = Path("/Users/SP14016/zitian/my_finance/.git/worktree/feature-256-dir-adjust")

    # Test files that should be removed from root (now copied to tests/)
    test_files_to_remove = [
        "test_dual_config_compatibility.py.disabled",
        "test_f2_sec.py.disabled",
        "test_orthogonal_config.py.disabled",
        "test_sec_config.py.disabled",
    ]

    print("🧹 FINALIZING Issue #256 Directory Cleanup")
    print("=" * 50)

    removed_count = 0

    for test_file in test_files_to_remove:
        original_file = root_path / test_file
        moved_file = root_path / "tests" / test_file

        # Check if both original and moved versions exist
        if original_file.exists() and moved_file.exists():
            print(f"Removing original: {test_file}")
            try:
                # Since we've successfully moved it to tests/, remove original
                original_file.unlink()
                removed_count += 1
                print(f"  ✅ Removed from root")
            except Exception as e:
                print(f"  ❌ Error removing: {e}")
        elif moved_file.exists():
            print(f"Already moved: {test_file} ✅")
        elif original_file.exists():
            print(f"Still in root: {test_file} (moving...)")
            try:
                # Move it now if we missed it
                import shutil

                shutil.move(str(original_file), str(moved_file))
                removed_count += 1
                print(f"  ✅ Moved to tests/")
            except Exception as e:
                print(f"  ❌ Error moving: {e}")
        else:
            print(f"Not found: {test_file}")

    print(f"\n📊 SUMMARY:")
    print(f"Files processed: {removed_count}")
    print(f"✅ Test files moved from root to tests/ directory")

    # Check for any remaining coverage files
    import glob

    coverage_files = glob.glob(str(root_path / ".coverage*"))
    if coverage_files:
        print(f"\n🔍 Found {len(coverage_files)} coverage files to clean:")
        for coverage_file in coverage_files:
            coverage_path = Path(coverage_file)
            print(f"  Removing: {coverage_path.name}")
            try:
                coverage_path.unlink()
                print(f"    ✅ Removed")
            except Exception as e:
                print(f"    ❌ Error: {e}")

    print(f"\n🎉 Issue #256 Phase 1 Cleanup COMPLETED")
    print(f"✅ Root directory structure cleaned and organized")


if __name__ == "__main__":
    main()
