#!/usr/bin/env python3
"""
Auto-commit data submodule changes before main repo commits.
This script ensures data submodule changes are never lost.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_cmd(cmd, cwd=None, check=True):
    """Run command and return result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            check=check
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_data_submodule_changes():
    """Check if data submodule has uncommitted changes."""
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data"
    
    if not data_dir.exists():
        print("❌ Data directory not found")
        return False, "Data directory not found"
    
    # Check if we're in a git repository
    success, _, _ = run_cmd("git rev-parse --git-dir", cwd=data_dir, check=False)
    if not success:
        print("❌ Data directory is not a git repository")
        return False, "Data directory is not a git repository"
    
    # Check for uncommitted changes in data submodule
    success, status_output, _ = run_cmd("git status --porcelain", cwd=data_dir)
    if not success:
        return False, "Failed to check git status in data submodule"
    
    return len(status_output.strip()) > 0, status_output

def commit_data_changes():
    """Commit any changes in the data submodule."""
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data"
    
    print("🔍 Checking data submodule for uncommitted changes...")
    
    has_changes, status_output = check_data_submodule_changes()
    
    if not has_changes:
        print("✅ No uncommitted changes in data submodule")
        return True
    
    print("📝 Found uncommitted changes in data submodule:")
    print(status_output)
    
    # Add all changes
    success, _, error = run_cmd("git add .", cwd=data_dir)
    if not success:
        print(f"❌ Failed to add changes: {error}")
        return False
    
    # Create commit message with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-commit data changes - {timestamp}"
    
    # Commit changes
    success, _, error = run_cmd(f'git commit -m "{commit_msg}"', cwd=data_dir)
    if not success:
        print(f"❌ Failed to commit changes: {error}")
        return False
    
    print("✅ Successfully committed data submodule changes")
    
    # Push to remote (optional, but recommended)
    success, _, error = run_cmd("git push origin main", cwd=data_dir, check=False)
    if success:
        print("✅ Successfully pushed data submodule changes to remote")
    else:
        print(f"⚠️  Failed to push to remote (this is OK): {error}")
    
    return True

def update_main_repo_submodule():
    """Update the main repository's submodule reference."""
    repo_root = Path(__file__).parent.parent
    
    print("🔄 Updating main repository submodule reference...")
    
    # Add the submodule change to staging
    success, _, error = run_cmd("git add data", cwd=repo_root)
    if not success:
        print(f"❌ Failed to stage submodule update: {error}")
        return False
    
    print("✅ Staged submodule update in main repository")
    return True

def main():
    """Main function to handle data submodule commits."""
    print("🚀 Data Submodule Auto-Commit Tool")
    print("=" * 50)
    
    # Check if we're in the right directory
    repo_root = Path(__file__).parent.parent
    if not (repo_root / ".git").exists() and not (repo_root / ".gitmodules").exists():
        print("❌ Not in a git repository with submodules")
        sys.exit(1)
    
    # Step 1: Commit data submodule changes
    if not commit_data_changes():
        print("❌ Failed to commit data submodule changes")
        sys.exit(1)
    
    # Step 2: Update main repo submodule reference
    if not update_main_repo_submodule():
        print("❌ Failed to update main repository submodule reference")
        sys.exit(1)
    
    print("=" * 50)
    print("✅ All data submodule changes have been committed!")
    print("💡 You can now safely commit your main repository changes")

if __name__ == "__main__":
    main()