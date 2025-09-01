#!/usr/bin/env python3
"""
Test script to verify worktree detection and safety functions work correctly
This validates the P3 worktree safety implementation (Issue #243)
"""

import os
import subprocess
import sys

sys.path.append(".")

# Import the functions we just implemented
from infra.create_pr_with_test import get_current_branch, is_worktree_environment


def main():
    print("🧪 TESTING WORKTREE DETECTION")
    print("=" * 40)

    print(f"Current working directory: {os.getcwd()}")

    # Test worktree detection
    is_worktree = is_worktree_environment()
    print(f"Is worktree environment: {is_worktree}")

    if is_worktree:
        print("✅ WORKTREE DETECTED - Safety features will be used")
        print("🔒 Main branch operations will use fetch+rebase")
    else:
        print("📁 Regular repository - Standard operations will be used")

    # Test current branch detection
    try:
        current_branch = get_current_branch()
        print(f"Current branch: {current_branch}")
    except Exception as e:
        print(f"Error getting current branch: {e}")

    # Test git worktree list if available
    try:
        result = subprocess.run(
            ["git", "worktree", "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("\n📋 Git worktree list:")
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"\nGit worktree list failed: {result.stderr}")
    except Exception as e:
        print(f"Error running git worktree list: {e}")

    print("\n🎯 WORKTREE SAFETY TEST COMPLETED")


if __name__ == "__main__":
    main()
