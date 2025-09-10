#!/usr/bin/env python3
"""
Migration Validation Script
Validates that all scripts have been properly migrated and are accessible
"""

import sys
from pathlib import Path


def validate_migration():
    """Validate the migration is complete and working"""
    print("🔍 Validating Scripts-to-Infra Migration")
    print("=" * 50)

    # Define expected migrated files
    expected_files = [
        "infra/system/workflow_ready.py",
        "infra/system/workflow_reset.py",
        "infra/system/workflow_debug.py",
        "infra/system/worktree_isolation.py",
        "infra/development/workflow_check.py",
        "infra/development/validate_io_compliance.py",
        "infra/development/validate_io_compliance.sh",
    ]

    missing_files = []
    success_count = 0

    for file_path in expected_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✅ {file_path}")
            success_count += 1
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)

    print()
    print(f"📊 Migration Status: {success_count}/{len(expected_files)} files")

    # Check p3.py has updated paths
    print("\n🔍 Checking P3 path updates...")
    p3_file = Path("p3.py")
    if p3_file.exists():
        content = p3_file.read_text()

        # Check for updated paths
        updated_paths = [
            "infra/system/workflow_ready.py",
            "infra/system/workflow_reset.py",
            "infra/development/workflow_check.py",
            "infra/system/workflow_debug.py",
            "infra/system/worktree_isolation",
        ]

        path_updates_ok = True
        for path in updated_paths:
            if path in content:
                print(f"✅ P3 references {path}")
            else:
                print(f"❌ P3 missing reference to {path}")
                path_updates_ok = False

        if path_updates_ok:
            print("✅ P3 path updates complete")
        else:
            print("❌ P3 path updates incomplete")
    else:
        print("❌ p3.py file not found")
        path_updates_ok = False

    # Summary
    print("\n" + "=" * 50)

    if success_count == len(expected_files) and path_updates_ok:
        print("🎉 MIGRATION VALIDATION PASSED")
        print("✅ All scripts migrated successfully")
        print("✅ P3 integration updated")
        print("✅ Module structure complete")
        return True
    else:
        print("❌ MIGRATION VALIDATION FAILED")
        if missing_files:
            print(f"📋 Missing files: {', '.join(missing_files)}")
        if not path_updates_ok:
            print("📋 P3 path updates needed")
        return False


def main():
    """Main validation function"""
    success = validate_migration()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
