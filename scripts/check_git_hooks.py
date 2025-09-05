#!/usr/bin/env python3
"""
Check Git Hooks Status
Verifies that pre-push hook is properly installed and configured
"""

import os
import subprocess
from pathlib import Path


def find_git_hooks_dir():
    """Find the correct git hooks directory (handle worktrees)"""
    try:
        # Get the git directory path
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True, text=True, check=True
        )
        git_dir = Path(result.stdout.strip())

        # For worktrees, we might need to check both local and main hooks
        hooks_dirs = []

        # Local hooks directory (worktree-specific)
        local_hooks = git_dir / "hooks"
        if local_hooks.exists():
            hooks_dirs.append(("Local (worktree)", local_hooks))

        # Main repository hooks directory
        if git_dir.name == "worktrees" or "worktrees" in str(git_dir):
            # We're in a worktree, find the main repo
            main_git = git_dir
            while main_git.name != ".git":
                main_git = main_git.parent
            main_hooks = main_git / "hooks"
            if main_hooks.exists():
                hooks_dirs.append(("Main repository", main_hooks))

        return hooks_dirs

    except subprocess.CalledProcessError:
        return []


def check_pre_push_hook(hooks_dir):
    """Check if pre-push hook exists and is executable"""
    pre_push = hooks_dir / "pre-push"

    if not pre_push.exists():
        return False, "Hook file not found"

    if not os.access(pre_push, os.X_OK):
        return False, "Hook file not executable"

    # Check if it contains our enforcement logic
    try:
        with open(pre_push, "r") as f:
            content = f.read()

        if "DIRECT GIT PUSH BLOCKED" in content and "p3 ship" in content:
            return True, "Hook properly configured"
        else:
            return False, "Hook exists but not configured for p3 ship enforcement"
    except Exception as e:
        return False, f"Could not read hook file: {e}"


def main():
    """Main check function"""
    print("🔍 Checking Git Hooks Status")
    print("=" * 50)

    hooks_dirs = find_git_hooks_dir()

    if not hooks_dirs:
        print("❌ Could not find git hooks directory")
        print("🔧 Make sure you're in a git repository")
        return 1

    all_good = True

    for location_name, hooks_dir in hooks_dirs:
        print(f"\n📁 Checking {location_name}: {hooks_dir}")

        is_installed, message = check_pre_push_hook(hooks_dir)

        if is_installed:
            print(f"   ✅ Pre-push hook: {message}")
        else:
            print(f"   ❌ Pre-push hook: {message}")
            all_good = False

    print("\n" + "=" * 50)

    if all_good:
        print("🎉 All git hooks properly installed!")
        print("🔒 Repository is protected from direct git push")
        print("📖 Use 'p3 ship \"Title\" ISSUE_NUM' for all changes")
        return 0
    else:
        print("⚠️  Git hooks need attention!")
        print("🔧 Run 'p3 install-hooks' to fix hook installation")
        print("💡 This will install pre-push hook to enforce ship workflow")
        return 1


if __name__ == "__main__":
    exit(main())
