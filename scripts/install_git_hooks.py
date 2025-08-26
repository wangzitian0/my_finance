#!/usr/bin/env python3
"""
Install Git Hooks - Mandatory create-pr Script Enforcement
Installs pre-push hook to enforce p3 create-pr workflow usage
"""

import os
import shutil
import stat
from pathlib import Path


def install_pre_push_hook():
    """Install pre-push hook to enforce create-pr workflow"""

    # Find the main .git directory (handle worktrees)
    project_root = Path(__file__).parent.parent
    git_dir = project_root / ".git"

    # Handle worktree case where .git is a file pointing to the actual git directory
    if git_dir.is_file():
        with open(git_dir, "r") as f:
            git_path_line = f.read().strip()
            if git_path_line.startswith("gitdir: "):
                # Extract the git directory path
                actual_git_dir = Path(git_path_line[8:])  # Remove 'gitdir: ' prefix
                # Get the main .git directory (parent of worktrees)
                main_git_dir = actual_git_dir.parent.parent
                print(f"📁 Detected worktree, main git dir: {main_git_dir}")
            else:
                print("❌ Invalid .git file format")
                return False
    elif git_dir.is_dir():
        # Regular git repository
        main_git_dir = git_dir
        print(f"📁 Regular git repository: {main_git_dir}")
    else:
        print("❌ .git directory not found")
        return False

    hooks_dir = main_git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    pre_push_hook = hooks_dir / "pre-push"

    # Pre-push hook content
    hook_content = """#!/bin/bash
#
# Git Pre-Push Hook - Mandatory create-pr Script Usage
# This hook prevents direct git push and enforces the use of p3 create-pr workflow
#

# Colors for output
RED='\\033[0;31m'
YELLOW='\\033[1;33m'
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Get current branch
current_branch=$(git branch --show-current)

# Check if this push is coming from p3 create-pr script
if [ -n "$P3_CREATE_PR_PUSH" ]; then
    echo -e "${GREEN}✅ Automated p3 create-pr push authorized${NC}"
    exit 0
fi

# Allow push to main branch only from automated workflows (CI/CD)
if [ "$current_branch" = "main" ]; then
    # Check if this is coming from GitHub Actions or automated workflow
    if [ -n "$GITHUB_ACTIONS" ] || [ -n "$CI" ]; then
        echo -e "${GREEN}✅ Automated workflow push to main branch allowed${NC}"
        exit 0
    else
        echo -e "${RED}❌ DIRECT PUSH TO MAIN BRANCH BLOCKED${NC}"
        echo -e "${RED}🚫 Direct pushes to main branch are not allowed${NC}"
        echo -e "${YELLOW}📖 Only pull requests are permitted to main branch${NC}"
        exit 1
    fi
fi

echo -e "${RED}🚨 DIRECT GIT PUSH BLOCKED${NC}"
echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}❌ This repository requires the use of automated PR workflow${NC}"
echo -e "${YELLOW}❌ Direct git push commands are not permitted${NC}"
echo
echo -e "${BLUE}🔧 REQUIRED WORKFLOW:${NC}"
echo -e "${GREEN}   1. p3 e2e f2                          # Run F2 fast tests${NC}"
echo -e "${GREEN}   2. p3 create-pr \\"Title\\" ISSUE_NUM      # Create PR with validation${NC}"
echo
echo -e "${BLUE}💡 WHY THIS RESTRICTION EXISTS:${NC}"
echo -e "   • Ensures all code passes automated testing before merge"
echo -e "   • Maintains commit message standards with test validation"
echo -e "   • Prevents untested code from reaching the main branch"
echo -e "   • Enforces proper issue tracking and PR documentation"
echo
echo -e "${YELLOW}⚡ QUICK SOLUTION:${NC}"
echo -e "${GREEN}   # Cancel this push and use the proper workflow:${NC}"
echo -e "${GREEN}   git reset --soft HEAD~1                # Undo last commit (keep changes)${NC}"
echo -e "${GREEN}   p3 e2e f2                              # Run fast tests${NC}"
echo -e "${GREEN}   p3 create-pr \\"Brief description\\" ISSUE_NUM # Create PR properly${NC}"
echo

# Double confirmation bypass (for emergency use only)
echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${RED}🚨 EMERGENCY BYPASS (NOT RECOMMENDED)${NC}"
echo -e "${YELLOW}If you absolutely must bypass this protection, you need TWO confirmations:${NC}"
echo

# First confirmation
read -p "❓ Are you sure you want to bypass the automated workflow? [type 'YES' to continue]: " first_confirm
if [ "$first_confirm" != "YES" ]; then
    echo -e "${GREEN}✅ Push cancelled. Please use the proper workflow.${NC}"
    exit 1
fi

echo
echo -e "${RED}⚠️  WARNING: Bypassing automated workflow can lead to:${NC}"
echo -e "   • Broken builds in main branch"
echo -e "   • Failed CI validation"
echo -e "   • Code quality issues"
echo -e "   • Missing test validation"
echo

# Second confirmation
read -p "❓ Do you REALLY want to bypass all safety checks? [type 'BYPASS' to proceed]: " second_confirm
if [ "$second_confirm" != "BYPASS" ]; then
    echo -e "${GREEN}✅ Push cancelled. Please use p3 create-pr workflow.${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}⚠️  EMERGENCY BYPASS ACTIVATED${NC}"
echo -e "${YELLOW}🔓 Allowing direct push (this will be logged)${NC}"
echo -e "${RED}🚨 Remember to run tests manually and ensure code quality${NC}"

# Log the bypass for audit purposes
echo "$(date): Emergency bypass used by $(whoami) on branch $current_branch" >> .git/hooks/bypass.log

exit 0
"""

    # Write the hook
    with open(pre_push_hook, "w") as f:
        f.write(hook_content)

    # Make it executable
    current_permissions = pre_push_hook.stat().st_mode
    pre_push_hook.chmod(current_permissions | stat.S_IEXEC)

    print(f"✅ Pre-push hook installed: {pre_push_hook}")

    # Also install in worktrees if they exist
    worktrees_dir = main_git_dir / "worktrees"
    if worktrees_dir.exists():
        for worktree_dir in worktrees_dir.iterdir():
            if worktree_dir.is_dir():
                worktree_hooks_dir = worktree_dir / "hooks"
                worktree_hooks_dir.mkdir(exist_ok=True)

                worktree_hook = worktree_hooks_dir / "pre-push"
                with open(worktree_hook, "w") as f:
                    f.write(hook_content)

                # Make it executable
                current_permissions = worktree_hook.stat().st_mode
                worktree_hook.chmod(current_permissions | stat.S_IEXEC)

                print(f"✅ Pre-push hook installed in worktree: {worktree_hook}")

    return True


def main():
    """Main installation function"""
    print("🔧 Installing Git Pre-Push Hook - Mandatory create-pr Enforcement")
    print("=" * 70)

    success = install_pre_push_hook()

    if success:
        print("\n🎉 Git hooks installed successfully!")
        print("\n📋 What this does:")
        print("   • Blocks all direct 'git push' commands")
        print("   • Requires use of 'p3 create-pr' workflow")
        print("   • Allows emergency bypass with double confirmation")
        print("   • Logs all bypass attempts for audit")
        print("\n🔒 Repository is now protected from direct pushes")
        print("📖 Use 'p3 create-pr \"Title\" ISSUE_NUM' for all changes")
    else:
        print("\n❌ Failed to install git hooks")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
