#!/usr/bin/env python3
"""
Auto-commit changes in the data directory (now part of the main repository).
This replaces the previous symlink/submodule-based workflow.

Behavior:
- Check for uncommitted changes in the data directory
- Stage and provide feedback about data changes
- Data is now part of the main repository, so no separate commits needed
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_cmd(cmd, cwd=None, check=True):
    """Run command and return result."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, check=check
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_data_changes():
    """Check if data directory has uncommitted changes."""
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data"

    if not data_dir.exists():
        print("❌ Data directory not found")
        return False, "Data directory not found"

    # Check for uncommitted changes in data directory
    success, status_output, _ = run_cmd("git status --porcelain data/", cwd=repo_root)
    if not success:
        return False, "Failed to check git status for data directory"

    return len(status_output.strip()) > 0, status_output


def stage_data_changes():
    """Stage any changes in the data directory."""
    repo_root = Path(__file__).parent.parent

    print("🔍 Checking data directory for uncommitted changes...")

    has_changes, status_output = check_data_changes()

    if not has_changes:
        print("✅ No uncommitted changes in data directory")
        return True

    print("📝 Found uncommitted changes in data directory:")
    print(status_output)

    # Add data directory changes
    success, _, error = run_cmd("git add data/", cwd=repo_root)
    if not success:
        print(f"❌ Failed to add data changes: {error}")
        return False

    print("✅ Successfully staged data directory changes")
    print("💡 Data changes are now part of the main repository")

    return True


def main():
    """Main function to handle data directory changes."""
    print("🚀 Data Directory Management Tool (integrated mode)")
    print("=" * 50)

    # Check if we're in the right directory
    repo_root = Path(__file__).parent.parent
    if not (repo_root / ".git").exists():
        print("❌ Not in a git repository")
        sys.exit(1)

    # Stage data directory changes
    if not stage_data_changes():
        print("❌ Failed to stage data directory changes")
        sys.exit(1)

    print("=" * 50)
    print("✅ All data directory changes have been staged!")
    print("💡 You can now commit your changes to the main repository")


if __name__ == "__main__":
    main()
