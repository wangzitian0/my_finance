# Git Workflow Optimization

## Overview

This document describes Git workflow optimization measures for the project, including automatic branch cleanup, Git hooks, and best practices.

## Core Principles

1. **Timely Cleanup**: Clean up related branches immediately after MR merge
2. **Automation**: Use scripts and hooks to automatically execute common tasks
3. **Consistency**: Unified commit format and PR process
4. **Security**: Prevent accidental data loss or incorrect commits

## Branch Cleanup System

### Automatic Branch Cleanup Script

Location: `scripts/cleanup_merged_branches.py`

Features:
- Automatically identify merged PR branches
- Clean up obsolete local and remote branches
- Prune remote references
- Support interactive and automatic modes

### Usage

```bash
# View branches to be cleaned (safe)
p3 cleanup-branches --dry-run

# Interactive cleanup (recommended)
p3 cleanup-branches

# Automatic cleanup (for CI or regular maintenance)
p3 cleanup-branches --auto
```

### Cleanup Rules

- **Auto cleanup**: PR branches merged within the last 30 days
- **Protected branches**: main, master, develop, staging, production never deleted
- **Safety check**: Verify branch is actually merged before deletion
- **Remote first**: Delete remote branch first, then local branch

## Git Hooks System

### Automatic Installation

```bash
pixi run install-git-hooks
```

### Hook Functions

#### 1. Post-merge Hook
- **Trigger time**: After git merge or git pull succeeds
- **Functions**: 
  - Detect if on main branch
  - Auto cleanup merged branches (within 7 days)
  - Prune remote references
- **Location**: `.git/hooks/post-merge`

#### 2. Pre-push Hook  
- **Trigger time**: Before git push
- **Functions**:
  - Check if branch is behind main
  - Warn about uncommitted changes
  - User confirmation to continue
- **Location**: `.git/hooks/pre-push`

#### 3. Commit-msg Hook
- **Trigger time**: Before git commit
- **Functions**:
  - Validate commit format (type: description)
  - Check issue references
  - Skip Claude Code signed commits
- **Location**: `.git/hooks/commit-msg`

## Complete Workflow

### 1. Start New Feature

```bash
# Ensure on latest main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/description-fixes-ISSUE_NUMBER

# Develop feature...
```

### 2. Commit and Push

```bash
# Add changes
git add .

# Commit (commit-msg hook validates format)
git commit -m "feat: Add new functionality

Fixes #123

PR: https://github.com/wangzitian0/my_finance/pull/PLACEHOLDER

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push (pre-push hook checks status)
git push -u origin feature/description-fixes-123
```

### 3. Create and Manage PR

```bash
# Create PR
gh pr create --title "feat: Add new functionality" --body "..."

# Update commit with actual PR URL
git commit --amend -m "feat: Add new functionality

Fixes #123

PR: https://github.com/wangzitian0/my_finance/pull/456

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push --force-with-lease
```

### 4. Post-MR Merge Cleanup

```bash
# Check PR status
gh pr view 456

# If merged, auto cleanup branches
p3 cleanup-branches --auto

# Or manual cleanup
git push origin --delete feature/description-fixes-123
git branch -D feature/description-fixes-123
```

## Maintenance Commands

### Regular Maintenance

```bash
# Run weekly to clean obsolete branches
p3 cleanup-branches --auto

# Update Git hooks
pixi run install-git-hooks

# Check repository health
git fsck
git gc --prune=now
```

### Emergency Cleanup

```bash
# Force delete local branch
git branch -D branch-name

# Delete remote branch
git push origin --delete branch-name

# Prune all remote references
git remote prune origin

# Clean untracked files
git clean -fd
```

## Best Practices

### Commit Format

Follow conventional commit format:
```
type(scope): description

Fixes #issue-number

PR: https://github.com/owner/repo/pull/number

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Type categories**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation change
- `style`: Format change
- `refactor`: Refactoring
- `test`: Test related
- `chore`: Build/tool change

### Branch Naming

```
feature/description-fixes-ISSUE_NUMBER
bugfix/description-fixes-ISSUE_NUMBER
hotfix/description-fixes-ISSUE_NUMBER
```

### PR Best Practices

1. **One PR per feature**: Keep PRs focused and reviewable
2. **Detailed description**: Include feature description, test results, screenshots, etc.
3. **Timely merge**: Avoid long-running branches
4. **Post-merge cleanup**: Delete feature branch immediately

## Troubleshooting

### Common Issues

1. **Cannot delete branch**
   ```bash
   # If branch has unmerged changes, use force delete
   git branch -D branch-name
   ```

2. **Hook not executing**
   ```bash
   # Check hook file permissions
   ls -la .git/hooks/
   chmod +x .git/hooks/*
   ```

3. **Remote branch deletion fails**
   ```bash
   # Check if you have permission to delete remote branch
   git push origin --delete branch-name
   ```

### Debug Mode

```bash
# Enable verbose output
GIT_TRACE=1 git push origin branch-name

# Check hook execution
echo "test" | .git/hooks/commit-msg /tmp/test-msg
```

## Configuration Options

### Custom Cleanup Rules

Edit `scripts/cleanup_merged_branches.py`:
```python
# Modify days threshold
days_back = 14  # Default 30 days

# Modify protected branches list
protected_branches = {'main', 'master', 'develop', 'custom-branch'}
```

### Hook Configuration

Edit corresponding hook files in `.git/hooks/` directory to customize behavior.

## Security Considerations

1. **Backup important branches**: Confirm branch is properly merged before deletion
2. **Test first**: Use `--dry-run` parameter to test cleanup operations
3. **Permission control**: Ensure only authorized users can delete remote branches
4. **Monitor logs**: Regularly check hook and cleanup script log output

---

*Through these optimization measures, the project's Git workflow will be more efficient, consistent, and secure.*