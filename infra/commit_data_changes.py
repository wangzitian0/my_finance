#!/usr/bin/env python3
"""
Auto-commit changes in the external data repository (symlinked at repo_root/data).
This replaces the previous submodule-based workflow.

Behavior:
- Detect if repo_root/data is a symlink to a sibling repo (../my_finance_data)
- Ensure the target is a git repository
- Stage, commit, and optionally push changes to its remote
- Do NOT touch main repo index except staging the symlink itself if needed
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

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

def check_data_repo_changes():
    """Check if external data repository (symlink target) has uncommitted changes."""
    repo_root = Path(__file__).parent.parent
    data_link = repo_root / "data"
    
    if not data_link.exists():
        print("❌ Data directory not found")
        return False, "Data directory not found"
    
    # Resolve symlink target if it's a link, otherwise use path as-is
    target_dir = data_link.resolve()
    
    # Check if target is a git repository
    success, _, _ = run_cmd("git rev-parse --git-dir", cwd=target_dir, check=False)
    if not success:
        print("❌ Data repository target is not a git repository")
        return False, "Data repository target is not a git repository"
    
    # Check for uncommitted changes
    success, status_output, _ = run_cmd("git status --porcelain", cwd=target_dir)
    if not success:
        return False, "Failed to check git status in data repository"
    
    return len(status_output.strip()) > 0, status_output

def commit_data_changes():
    """Commit any changes in the external data repository."""
    repo_root = Path(__file__).parent.parent
    data_link = repo_root / "data"
    target_dir = data_link.resolve()
    
    print("🔍 Checking data repository for uncommitted changes...")
    
    has_changes, status_output = check_data_repo_changes()
    
    if not has_changes:
        print("✅ No uncommitted changes in data repository")
        return True
    
    print("📝 Found uncommitted changes in data repository:")
    print(status_output)
    
    # Add all changes
    success, _, error = run_cmd("git add .", cwd=target_dir)
    if not success:
        print(f"❌ Failed to add changes: {error}")
        return False
    
    # Create commit message with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-commit data changes - {timestamp}"
    
    # Commit changes
    success, _, error = run_cmd(f'git commit -m "{commit_msg}"', cwd=target_dir)
    if not success:
        print(f"❌ Failed to commit changes: {error}")
        return False
    
    print("✅ Successfully committed data repository changes")
    
    # Push to remote (optional, but recommended)
    success, _, error = run_cmd("git push origin main", cwd=target_dir, check=False)
    if success:
        print("✅ Successfully pushed data submodule changes to remote")
    else:
        print(f"⚠️  Failed to push to remote (this is OK): {error}")
    
    return True

def update_main_repo_symlink():
    """Stage the data symlink in the main repository if needed."""
    repo_root = Path(__file__).parent.parent
    
    print("🔄 Ensuring data symlink is staged in main repository...")
    
    # Add the symlink path to staging
    success, _, error = run_cmd("git add data", cwd=repo_root)
    if not success:
        print(f"❌ Failed to stage data link: {error}")
        return False
    
    print("✅ Staged data link in main repository")
    return True

def main():
    """Main function to handle data submodule commits."""
    print("🚀 Data Repository Auto-Commit Tool (symlink mode)")
    print("=" * 50)
    
    # Check if we're in the right directory
    repo_root = Path(__file__).parent.parent
    if not (repo_root / ".git").exists():
        print("❌ Not in a git repository")
        sys.exit(1)
    
    # Step 1: Commit data repository changes
    if not commit_data_changes():
        print("❌ Failed to commit data repository changes")
        sys.exit(1)
    
    # Step 2: Ensure data symlink is staged
    if not update_main_repo_symlink():
        print("❌ Failed to stage data symlink in main repository")
        sys.exit(1)
    
    print("=" * 50)
    print("✅ All data repository changes have been committed!")
    print("💡 You can now safely commit your main repository changes")

if __name__ == "__main__":
    main()