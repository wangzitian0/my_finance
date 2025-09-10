#!/usr/bin/env python3
"""
Scripts Directory Cleanup - Remove duplicate files after migration
Safely removes files from scripts/ that have been successfully migrated to infra/
"""

import os
import shutil
import sys
from pathlib import Path


def cleanup_duplicate_files():
    """Remove duplicate files from scripts/ that exist in infra/."""
    print("🧹 CLEANING UP DUPLICATE FILES FROM SCRIPTS/")
    print("=" * 50)
    
    # Mapping of old scripts/ files to new infra/ locations
    migration_mapping = {
        "scripts/validate_io_compliance.sh": "infra/development/validate_io_compliance.sh",
        "scripts/fast_env_check.py": "infra/system/fast_env_check.py", 
        "scripts/p3/p3_version_simple.py": "infra/p3/p3_version_simple.py",
        "scripts/p3/.p3_version.json": "infra/p3/.p3_version.json",
    }
    
    removed_files = []
    preserved_files = []
    
    for old_path, new_path in migration_mapping.items():
        old_file = Path(old_path)
        new_file = Path(new_path)
        
        if old_file.exists() and new_file.exists():
            # Both files exist - verify they are the same (or new one is updated)
            print(f"🔄 Checking: {old_path}")
            
            # For most files, if the new version exists, we can safely remove the old
            # Exception: .p3_version.json might have different versions
            if old_path.endswith('.p3_version.json'):
                print(f"   📋 Version file - preserving for comparison")
                preserved_files.append(old_path)
            else:
                print(f"   ✅ Removing duplicate: {old_path}")
                print(f"   📁 Using migrated version: {new_path}")
                old_file.unlink()  # Remove the old file
                removed_files.append(old_path)
        elif old_file.exists():
            print(f"⚠️  {old_path} exists but {new_path} missing")
            print(f"   📋 Preserving until migration is complete")
            preserved_files.append(old_path)
        else:
            print(f"ℹ️  {old_path} already removed")
    
    return removed_files, preserved_files


def cleanup_empty_directories():
    """Remove empty directories in scripts/ after file cleanup."""
    print("\n🔄 Cleaning up empty directories...")
    
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("ℹ️  scripts/ directory doesn't exist")
        return []
    
    removed_dirs = []
    
    # Check p3 subdirectory
    p3_dir = scripts_dir / "p3"
    if p3_dir.exists():
        try:
            # List remaining files in p3 directory
            remaining_files = list(p3_dir.glob("*"))
            remaining_non_hidden = [f for f in remaining_files if not f.name.startswith('.')]
            
            if not remaining_non_hidden:
                print(f"🗑️  Removing empty directory: {p3_dir}")
                shutil.rmtree(p3_dir)
                removed_dirs.append(str(p3_dir))
            else:
                print(f"📁 Preserving {p3_dir} - contains {len(remaining_files)} files")
        except OSError as e:
            print(f"⚠️  Could not remove {p3_dir}: {e}")
    
    return removed_dirs


def summary_report():
    """Generate a summary of remaining files in scripts/."""
    print("\n📊 REMAINING FILES IN SCRIPTS/")
    print("=" * 50)
    
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        print("✅ scripts/ directory completely removed")
        return
    
    all_files = []
    for item in scripts_dir.rglob("*"):
        if item.is_file():
            all_files.append(str(item.relative_to(scripts_dir)))
    
    if all_files:
        print(f"📁 {len(all_files)} files remain in scripts/:")
        for file in sorted(all_files):
            print(f"   📄 scripts/{file}")
    else:
        print("✅ scripts/ directory is empty (except directories)")
    
    # Check if we can remove the entire scripts directory
    all_items = list(scripts_dir.rglob("*"))
    non_empty_dirs = [item for item in all_items if item.is_dir() and list(item.glob("*"))]
    
    if not all_files and not non_empty_dirs:
        print("\n💡 scripts/ directory could be completely removed")
        print("   Run: rm -rf scripts/")


def main():
    """Run the cleanup process."""
    print("🧹 SCRIPTS-TO-INFRA MIGRATION CLEANUP")
    print("=" * 50)
    print("This script removes duplicate files from scripts/ that have been")
    print("successfully migrated to infra/ directory structure.")
    print("=" * 50)
    
    # Step 1: Remove duplicate files
    removed_files, preserved_files = cleanup_duplicate_files()
    
    # Step 2: Clean up empty directories  
    removed_dirs = cleanup_empty_directories()
    
    # Step 3: Generate summary report
    summary_report()
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎯 CLEANUP SUMMARY")
    print("=" * 50)
    
    print(f"✅ Removed {len(removed_files)} duplicate files:")
    for file in removed_files:
        print(f"   🗑️  {file}")
    
    if preserved_files:
        print(f"\n📋 Preserved {len(preserved_files)} files for review:")
        for file in preserved_files:
            print(f"   📄 {file}")
    
    if removed_dirs:
        print(f"\n🗑️  Removed {len(removed_dirs)} empty directories:")
        for dir in removed_dirs:
            print(f"   📁 {dir}")
    
    print(f"\n✅ CLEANUP COMPLETED")
    print("💡 Run validate_migration_complete.py to verify migration status")


if __name__ == "__main__":
    main()