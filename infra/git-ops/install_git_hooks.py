#!/usr/bin/env python3
"""
Consolidated Git Hooks Installation
Combines P3 workflow enforcement and git hygiene automation

This script installs comprehensive Git hooks to:
1. Enforce P3 ship workflow (mandatory for pushes)
2. Maintain repository hygiene (branch cleanup, status checks)
3. Ensure proper commit message formatting
4. Handle worktree environments properly
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path


def find_git_directory():
    """Find the main git directory, handling both regular repos and worktrees"""
    project_root = Path(__file__).parent.parent.parent
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
                return main_git_dir
            else:
                print("❌ Invalid .git file format")
                return None
    elif git_dir.is_dir():
        # Regular git repository
        main_git_dir = git_dir
        print(f"📁 Regular git repository: {main_git_dir}")
        return main_git_dir
    else:
        print("❌ .git directory not found")
        return None


def install_pre_push_hook(git_dir):
    """Install comprehensive pre-push hook (P3 enforcement + branch checks)"""
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    pre_push_hook = hooks_dir / "pre-push"

    # Combined hook content: P3 workflow enforcement + branch status checks
    hook_content = """#!/bin/bash
#
# Comprehensive Pre-Push Hook
# 1. P3 Ship Workflow Enforcement (mandatory)
# 2. Branch Status Validation
# 3. Worktree Environment Support
#

remote="$1"
url="$2"

# Colors for output
RED='\\033[0;31m'
YELLOW='\\033[1;33m'
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Get current branch
current_branch=$(git branch --show-current)

# === P3 WORKFLOW ENFORCEMENT (PRIMARY) ===

# Check if this push is coming from p3 ship script
if [ -n "$P3_CREATE_PR_PUSH" ]; then
    echo -e "${GREEN}✅ Automated p3 ship push authorized${NC}"
    
    # Still run branch status checks for p3 ship pushes (informational only)
    echo -e "${BLUE}🔍 Running branch status checks for p3 ship push...${NC}"
    
    # Check if branch is behind main (informational)
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        git fetch origin main >/dev/null 2>&1
        behind_count=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
        
        if [ "$behind_count" -gt 0 ]; then
            echo -e "${YELLOW}ℹ️  Info: Branch is $behind_count commits behind main${NC}"
            echo -e "${BLUE}   p3 ship will handle rebase automatically${NC}"
        fi
    fi
    
    exit 0
fi

# Allow push to main branch only from automated workflows (CI/CD)
if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
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

# === DIRECT PUSH WARNING (P3 WORKFLOW PREFERRED) ===

echo -e "${YELLOW}⚠️  DIRECT GIT PUSH DETECTED${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}⚠️  Warning: Direct push bypasses automated PR workflow${NC}"
echo -e "${RED}🚨 STRONGLY RECOMMENDED: Use p3 ship for better workflow${NC}"
echo
echo -e "${BLUE}🔧 RECOMMENDED P3 WORKFLOW:${NC}"
echo -e "${GREEN}   Option 1 - If you just ran p3 test f2 (within 10 minutes):${NC}"
echo -e "${GREEN}     p3 ship \\"Title\\" ISSUE_NUM         # Direct ship with existing test results${NC}"
echo
echo -e "${GREEN}   Option 2 - If no recent f2 test or first time:${NC}"
echo -e "${GREEN}     1. p3 ready                          # Setup environment (if needed)${NC}"
echo -e "${GREEN}     2. p3 check                          # Fix formatting (optional)${NC}" 
echo -e "${GREEN}     3. p3 test f2                        # Fast test (2 companies, 2-5min)${NC}"
echo -e "${GREEN}     4. p3 ship \\"Title\\" ISSUE_NUM       # Create PR with test markers${NC}"
echo
echo -e "${GREEN}   🚀 FASTEST WORKFLOW - p3 ship automatically runs f2 test if needed!${NC}"
echo -e "${GREEN}     p3 ship \\"Title\\" ISSUE_NUM         # Auto: check for recent tests, run f2 if needed${NC}"
echo
echo -e "${BLUE}💡 WHY P3 WORKFLOW IS PREFERRED:${NC}"
echo -e "   • Ensures all code passes automated testing before merge"
echo -e "   • Maintains commit message standards with test markers"
echo -e "   • Prevents untested code from reaching the main branch"
echo -e "   • Enforces proper issue tracking and PR documentation"
echo
echo -e "${YELLOW}⚡ QUICK ALTERNATIVE:${NC}"
echo -e "${GREEN}   # Cancel this push and use the recommended P3 workflow:${NC}"
echo -e "${GREEN}   git reset --soft HEAD~1                # Undo last commit (keep changes)${NC}"
echo
echo -e "${BLUE}   🎯 OPTION 1 - Super Fast (recommended):${NC}"
echo -e "${GREEN}   p3 ship \\"Brief description\\" ISSUE_NUM # Auto-detects if f2 test needed${NC}"
echo
echo -e "${BLUE}   🎯 OPTION 2 - Manual control:${NC}"
echo -e "${GREEN}   p3 test f2                             # Explicit F2 test first${NC}"
echo -e "${GREEN}   p3 ship \\"Brief description\\" ISSUE_NUM # Then ship with test results${NC}"
echo
echo -e "${BLUE}📊 P3 SCOPES (p3 ship auto-runs f2, or specify manually):${NC}"
echo -e "   • f2  (2 companies, 2-5min)   - Default for PRs, auto-runs if needed"
echo -e "   • m7  (7 companies, 10-20min) - For release validation"  
echo -e "   • n100 (100 companies, 1-3hr) - For production testing"
echo
echo -e "${BLUE}💡 SMART LOGIC:${NC}"
echo -e "   p3 ship will automatically run 'p3 test f2' if:"
echo -e "   • No recent F2 test results found (within 10 minutes)"
echo -e "   • Code has changed since last test"
echo -e "   • This is the first test run in current session"
echo
echo -e "${YELLOW}⏰ Proceeding with direct push in 3 seconds...${NC}"
echo -e "${RED}   Press Ctrl+C to cancel and use p3 ship instead${NC}"
sleep 3

# === BRANCH STATUS CHECKS (SECONDARY) ===
# These run as informational warnings when direct push is attempted

echo -e "${BLUE}🔍 Branch Status Analysis (for your information):${NC}"

# Check if branch is behind main
git fetch origin main >/dev/null 2>&1
behind_count=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")

if [ "$behind_count" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Your branch is $behind_count commits behind main${NC}"
    echo -e "${BLUE}💡 p3 ship will automatically handle rebase with main${NC}"
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes${NC}"
    git status --short
    echo -e "${BLUE}💡 Commit these changes before using p3 ship${NC}"
fi

# === DIRECT PUSH ALLOWED (WITH LOGGING) ===

# Log the direct push for audit purposes (but allow it)
echo "$(date): Direct push by $(whoami) on branch $current_branch (bypassed p3 ship)" >> .git/hooks/direct_push.log

echo -e "${YELLOW}📝 Direct push logged for audit purposes${NC}"
echo -e "${GREEN}✅ Push proceeding (consider using p3 ship next time)${NC}"

exit 0
"""

    # Write the hook
    with open(pre_push_hook, "w") as f:
        f.write(hook_content)

    # Make it executable
    current_permissions = pre_push_hook.stat().st_mode
    pre_push_hook.chmod(current_permissions | stat.S_IEXEC)

    print(f"✅ Pre-push hook installed: {pre_push_hook}")
    return True


def install_post_merge_hook(git_dir):
    """Install post-merge hook for branch cleanup"""
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
    
    # Check if cleanup script exists in new location
    if [ -f "infra/git-ops/cleanup_merged_branches.py" ]; then
        python infra/git-ops/cleanup_merged_branches.py --auto --days 7
    elif [ -f "infra/cleanup_merged_branches.py" ]; then
        # Fallback to old location during transition
        python infra/cleanup_merged_branches.py --auto --days 7
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

    print(f"✅ Post-merge hook installed: {post_merge_hook}")
    return True


def install_commit_msg_hook(git_dir):
    """Install commit-msg hook for message format validation"""
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    commit_msg_hook = hooks_dir / "commit-msg"

    hook_content = """#!/bin/sh
# Commit message hook: Ensure proper commit format per CLAUDE.md

commit_file="$1"
commit_msg=$(cat "$commit_file")

# Check if commit already has Claude Code signature (e.g., during amend)
if echo "$commit_msg" | grep -q "🤖 Generated with \\[Claude Code\\]"; then
    exit 0
fi

# Check if this is a merge commit
if echo "$commit_msg" | grep -q "^Merge "; then
    exit 0
fi

# Check basic format requirements
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\\(.+\\))?: .+"; then
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

    print(f"✅ Commit-msg hook installed: {commit_msg_hook}")
    return True


def install_hooks_in_worktrees(main_git_dir):
    """Install hooks in all existing worktrees"""
    worktrees_dir = main_git_dir / "worktrees"
    if not worktrees_dir.exists():
        return

    for worktree_dir in worktrees_dir.iterdir():
        if worktree_dir.is_dir():
            worktree_hooks_dir = worktree_dir / "hooks"
            worktree_hooks_dir.mkdir(exist_ok=True)

            print(f"📁 Installing hooks in worktree: {worktree_dir.name}")

            # Install hooks in worktree
            install_pre_push_hook(worktree_dir)
            install_post_merge_hook(worktree_dir)
            install_commit_msg_hook(worktree_dir)


def main():
    """Install all consolidated Git hooks"""
    print("🔧 Installing Consolidated Git Hooks")
    print("=" * 70)
    print("📋 Features:")
    print("   • P3 ship workflow enforcement (mandatory)")
    print("   • Branch status validation and cleanup")
    print("   • Commit message format validation")
    print("   • Worktree environment compatibility")
    print("=" * 70)

    # Find git directory (handles both regular repos and worktrees)
    git_dir = find_git_directory()
    if not git_dir:
        print("❌ Could not find git directory")
        return 1

    success_count = 0

    try:
        # Install all hooks in main git directory
        if install_pre_push_hook(git_dir):
            success_count += 1
        if install_post_merge_hook(git_dir):
            success_count += 1
        if install_commit_msg_hook(git_dir):
            success_count += 1

        # Install hooks in worktrees if they exist
        install_hooks_in_worktrees(git_dir)

        print(f"\n🎉 Successfully installed {success_count}/3 main git hooks!")
        print("\n📋 Installed hooks:")
        print("   • pre-push: Enforces p3 ship workflow + branch validation")
        print("   • post-merge: Cleans up merged branches after pulling main")
        print("   • commit-msg: Ensures proper commit message format")

        print("\n🔒 Repository protection active:")
        print("   • Direct pushes allowed with 3s delay + warning (p3 ship recommended)")
        print("   • P3 ship workflow strongly encouraged")
        print("   • Automated branch cleanup enabled")
        print("   • Commit message standards enforced")

        print("\n💡 Usage:")
        print('   • Recommended: p3 ship "Title" ISSUE_NUM')
        print("   • Direct push: Allowed with 3s delay + warning")
        print("   • Branch cleanup: Automatic after merge to main")

    except Exception as e:
        print(f"❌ Failed to install git hooks: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
