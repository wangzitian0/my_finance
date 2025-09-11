#!/usr/bin/env python3
"""
Temporary file cleanup utility for second-round organization cleanup.
Removes policy-violating temporary documentation files.
"""

import os
import subprocess
import sys
from pathlib import Path


def execute_git_command(command, description):
    """Execute git command with proper error handling."""
    try:
        print(f"Executing: {description}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ Success: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Execute second-round cleanup operations."""
    repo_root = Path("/Users/SP14016/zitian/my_finance/.git/worktree/feature-129-ci-revamp-05")
    os.chdir(repo_root)

    print("🧹 PHASE 1: Removing Temporary Documentation Files")
    print("=" * 60)

    # Files to delete (policy violations)
    temp_files = [
        "ROOT_CLEANUP_SUMMARY.md",
        "SCRIPTS_REORGANIZATION_SUMMARY.md",
        "WORKTREE_ISOLATION.md",
    ]

    for file in temp_files:
        if os.path.exists(file):
            success = execute_git_command(f"git rm {file}", f"Remove {file}")
            if not success:
                print(f"⚠️  Warning: Could not git rm {file}, trying regular delete")
                try:
                    os.remove(file)
                    print(f"✅ Deleted {file} with regular removal")
                except Exception as e:
                    print(f"❌ Failed to delete {file}: {e}")
        else:
            print(f"ℹ️  File {file} does not exist, skipping")

    print("\n🔄 PHASE 2: Moving Misplaced Test Files")
    print("=" * 60)

    # Test files to move
    test_moves = [
        ("graph_rag/test_graph_rag.py", "tests/test_graph_rag.py"),
        ("common/test_parallel_optimization.py", "tests/test_parallel_optimization.py"),
        ("dcf_engine/test_dcf_report.py", "tests/test_dcf_report.py"),
    ]

    for src, dst in test_moves:
        if os.path.exists(src):
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            success = execute_git_command(f"git mv {src} {dst}", f"Move {src} to {dst}")
            if not success:
                print(f"❌ Failed to move {src}")
        else:
            print(f"ℹ️  File {src} does not exist, skipping")

    print("\n🛠️  PHASE 3: Moving Misplaced Infrastructure Tools")
    print("=" * 60)

    # Infrastructure tools to move
    infra_moves = [("infra/run_test.py", "scripts/utilities/run_test.py")]

    for src, dst in infra_moves:
        if os.path.exists(src):
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            success = execute_git_command(f"git mv {src} {dst}", f"Move {src} to {dst}")
            if not success:
                print(f"❌ Failed to move {src}")
        else:
            print(f"ℹ️  File {src} does not exist, skipping")

    print("\n🎯 PHASE 4: Demo File Analysis")
    print("=" * 60)

    demo_file = "scripts/demos/test_claude_hooks.py"
    if os.path.exists(demo_file):
        print(f"📁 Found demo test file: {demo_file}")
        print("📝 Analysis: This appears to be a demo/test file for Claude hooks infrastructure")
        print(
            "🔍 Decision: Keep in demos/ as it's testing demo functionality, not core system tests"
        )
        print("✅ No action needed - file is appropriately located")
    else:
        print(f"ℹ️  Demo file {demo_file} does not exist")

    print("\n🎯 Cleanup Complete!")
    print("=" * 60)
    print("Next steps:")
    print("1. Verify all moved files can still be imported/executed")
    print("2. Update any broken import references")
    print("3. Run tests to ensure no functionality is broken")
    print("4. Remove this temporary cleanup script")


if __name__ == "__main__":
    main()
