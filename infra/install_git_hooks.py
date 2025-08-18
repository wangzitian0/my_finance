#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install Git Hooks for Workflow Optimization

This script installs Git hooks to automatically optimize the workflow,
including cleaning up merged branches and maintaining repository hygiene.
"""

import os
import stat
import subprocess
from pathlib import Path


def install_post_merge_hook():
    """Install post-merge hook to clean up branches after pulling main."""

    # Find git directory (could be .git or .git file in worktree)
    git_dir = Path(".git")
    if git_dir.is_file():
        # This is a worktree, read the actual git dir
        with open(git_dir, "r") as f:
            git_dir = Path(f.read().split(": ")[1].strip())

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    post_merge_hook = hooks_dir / "post-merge"

    hook_content = """#!/bin/sh
# Post-merge hook: Clean up merged branches
# This runs after a successful git merge (including git pull)

# Check if we're on main branch
current_branch=$(git branch --show-current)

if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
    echo "🧹 Cleaning up merged branches after merge to $current_branch..."
    
    # Check if cleanup script exists
    if [ -f "scripts/cleanup_merged_branches.py" ]; then
        python scripts/cleanup_merged_branches.py --auto --days 7
    else
        echo "ℹ️  Branch cleanup script not found, skipping cleanup"
    fi
    
    # Prune remote references
    echo "🧽 Pruning remote references..."
    git remote prune origin
    
    echo "✅ Post-merge cleanup completed"
fi
"""

    with open(post_merge_hook, "w") as f:
        f.write(hook_content)

    # Make executable
    os.chmod(post_merge_hook, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    print(f"✅ Installed post-merge hook: {post_merge_hook}")


def install_pre_push_hook():
    """Install pre-push hook to verify branch is up to date."""

    git_dir = Path(".git")
    if git_dir.is_file():
        with open(git_dir, "r") as f:
            git_dir = Path(f.read().split(": ")[1].strip())

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    pre_push_hook = hooks_dir / "pre-push"

    hook_content = """#!/bin/sh
# Pre-push hook: Verify branch status before push

remote="$1"
url="$2"

# Get current branch
current_branch=$(git branch --show-current)

# Skip checks for main branch
if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
    exit 0
fi

echo "🔍 Checking branch status before push..."

# Check if branch is behind main
git fetch origin main >/dev/null 2>&1
behind_count=$(git rev-list --count HEAD..origin/main)

if [ "$behind_count" -gt 0 ]; then
    echo "⚠️  Warning: Your branch is $behind_count commits behind main"
    echo "💡 Consider rebasing or merging main into your branch first"
    echo ""
    echo "To update your branch:"
    echo "  git fetch origin main"
    echo "  git rebase origin/main  # or git merge origin/main"
    echo ""
    read -p "Continue with push anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Push cancelled"
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    git status --short
    echo ""
    read -p "Continue with push anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Push cancelled"
        exit 1
    fi
fi

echo "✅ Pre-push checks passed"
"""

    with open(pre_push_hook, "w") as f:
        f.write(hook_content)

    # Make executable
    os.chmod(pre_push_hook, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    print(f"✅ Installed pre-push hook: {pre_push_hook}")


def install_commit_msg_hook():
    """Install commit-msg hook to ensure proper format."""

    git_dir = Path(".git")
    if git_dir.is_file():
        with open(git_dir, "r") as f:
            git_dir = Path(f.read().split(": ")[1].strip())

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    commit_msg_hook = hooks_dir / "commit-msg"

    hook_content = """#!/bin/sh
# Commit message hook: Ensure proper commit format per CLAUDE.md

commit_file="$1"
commit_msg=$(cat "$commit_file")

# Check if commit already has Claude Code signature (e.g., during amend)
if echo "$commit_msg" | grep -q "🤖 Generated with \[Claude Code\]"; then
    exit 0
fi

# Check if this is a merge commit
if echo "$commit_msg" | grep -q "^Merge "; then
    exit 0
fi

# Check basic format requirements
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"; then
    echo "❌ Commit message format error!"
    echo ""
    echo "Required format:"
    echo "  type(scope): description"
    echo ""
    echo "Examples:"
    echo "  feat: Add new feature"
    echo "  fix(auth): Fix login bug"
    echo "  docs: Update README"
    echo ""
    echo "Current message:"
    echo "$commit_msg"
    exit 1
fi

# Check if issue reference is present (for non-trivial commits)
if ! echo "$commit_msg" | grep -qE "(Fixes|Closes|Refs) #[0-9]+"; then
    echo "⚠️  Warning: No issue reference found"
    echo "💡 Consider adding 'Fixes #123' to link to an issue"
    echo ""
    echo "Current message:"
    echo "$commit_msg"
    echo ""
    read -p "Continue without issue reference? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Commit cancelled"
        exit 1
    fi
fi

echo "✅ Commit message format is valid"
"""

    with open(commit_msg_hook, "w") as f:
        f.write(hook_content)

    # Make executable
    os.chmod(commit_msg_hook, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    print(f"✅ Installed commit-msg hook: {commit_msg_hook}")


def main():
    """Install all Git hooks."""
    print("🔧 Installing Git hooks for workflow optimization...")

    try:
        install_post_merge_hook()
        install_pre_push_hook()
        install_commit_msg_hook()

        print("\n🎉 All Git hooks installed successfully!")
        print("\nInstalled hooks:")
        print("  • post-merge: Cleans up merged branches after pulling main")
        print("  • pre-push: Verifies branch status before pushing")
        print("  • commit-msg: Ensures proper commit message format")

        print("\n💡 To test the hooks:")
        print("  p3 cleanup-branches-dry-run  # Test branch cleanup")
        print("  git commit --amend                 # Test commit message validation")

    except Exception as e:
        print(f"❌ Failed to install Git hooks: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
