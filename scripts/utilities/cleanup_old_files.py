#!/usr/bin/env python3
"""
Cleanup old files after scripts reorganization
"""

import os
from pathlib import Path


def cleanup_old_files():
    """Remove old files that have been moved to new locations"""
    files_to_remove = [
        # Old workflow files (moved to scripts/workflow/)
        "scripts/workflow_ready.py",
        "scripts/workflow_check.py",
        "scripts/workflow_debug.py",
        "scripts/workflow_reset.py",
        # Old utility files (moved to scripts/utilities/)
        "scripts/worktree_isolation.py",
        "scripts/directory_cleanup_executor.py",
        "scripts/directory_hygiene_analysis.py",
        "scripts/config_summary.py",
        "scripts/fast_env_check.py",
        # Reorganization script (cleanup)
        "scripts_reorganization.py",
        "cleanup_old_files.py",  # This file itself
    ]

    removed_count = 0
    for file_path in files_to_remove:
        path = Path(file_path)
        if path.exists():
            try:
                os.remove(path)
                print(f"✅ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
        else:
            print(f"ℹ️  File not found: {file_path}")

    print(f"\n🧹 Cleanup complete: {removed_count} files removed")


if __name__ == "__main__":
    cleanup_old_files()