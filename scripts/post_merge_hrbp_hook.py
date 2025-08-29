#!/usr/bin/env python3
"""
Post-Merge Git Hook for HRBP Automation

Automatically records PR merges to main branch for HRBP 20-PR cycle tracking.
This script should be called from git post-merge hook.
"""
import re
import subprocess
import sys
from pathlib import Path


def get_last_merge_commit_info():
    """Get information about the last merge commit."""
    try:
        # Get the last commit message
        cmd = ["git", "log", "-1", "--pretty=format:%s"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None, None
            
        commit_message = result.stdout.strip()
        
        # Check if this is a merge commit for a PR
        # Format: "Merge pull request #123 from branch-name"
        pr_pattern = r"Merge pull request #(\d+) from"
        match = re.search(pr_pattern, commit_message)
        
        if match:
            pr_number = int(match.group(1))
            return pr_number, commit_message
        
        return None, commit_message
        
    except Exception as e:
        print(f"Error getting merge commit info: {e}")
        return None, None


def is_main_branch():
    """Check if current branch is main."""
    try:
        cmd = ["git", "branch", "--show-current"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            current_branch = result.stdout.strip()
            return current_branch == "main"
        
        return False
    except Exception:
        return False


def trigger_hrbp_tracking(pr_number):
    """Trigger HRBP PR tracking using p3 command."""
    try:
        # Find the project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        # Use p3 command to record the PR
        cmd = [str(project_root / "p3"), "hrbp-record-pr", str(pr_number)]
        
        print(f"🤖 Recording PR #{pr_number} for HRBP automation...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PR #{pr_number} recorded for HRBP tracking")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"⚠️  HRBP tracking failed for PR #{pr_number}")
            if result.stderr.strip():
                print(f"Error: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Exception in HRBP tracking: {e}")
        return False


def main():
    """Main post-merge hook logic."""
    # Only process merges to main branch
    if not is_main_branch():
        # Not on main branch, nothing to do
        sys.exit(0)
    
    # Get merge commit information
    pr_number, commit_message = get_last_merge_commit_info()
    
    if pr_number is None:
        # Not a PR merge, nothing to do
        sys.exit(0)
    
    print(f"🔍 Detected PR #{pr_number} merge to main branch")
    
    # Trigger HRBP tracking
    success = trigger_hrbp_tracking(pr_number)
    
    if success:
        print("🎉 HRBP automation post-merge hook completed successfully")
    else:
        print("⚠️  HRBP automation post-merge hook completed with warnings")
    
    # Always exit successfully to not block the merge
    sys.exit(0)


if __name__ == "__main__":
    main()