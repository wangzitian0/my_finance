# Git Operations - Workflow Management and Automation

Centralized Git workflow management, repository hygiene, and automated Git operations supporting the P3 workflow system.

## Overview

This directory provides comprehensive Git workflow automation, focusing on repository hygiene, P3 workflow enforcement, and safe Git operations in both regular and worktree environments.

## Core Components

### Git Hooks System (`install_git_hooks.py`)
**Comprehensive Git workflow enforcement and automation**:
- **P3 workflow enforcement**: Mandatory `p3 ship` workflow for all pushes
- **Branch protection**: Direct push blocking with intelligent bypass options
- **Repository hygiene**: Automated branch cleanup, commit message validation
- **Worktree compatibility**: Safe operation in git worktree environments

### Repository Management (`cleanup_merged_branches.py`)
**Automated repository maintenance and hygiene**:
- **Merged branch cleanup**: Automatic deletion of merged feature branches
- **Remote reference pruning**: Cleanup of stale remote references
- **Safe operation**: Confirmation prompts, branch protection for important branches
- **Integration**: Triggered by post-merge hooks, manual execution support

## Key Features

### 1. P3 Workflow Enforcement
**Mandatory P3 ship workflow for all repository pushes**:

**Primary Protection**:
- **Direct push blocking**: All direct `git push` commands are blocked
- **P3 ship requirement**: Only `p3 ship` workflow allows pushes to repository
- **Test validation**: F2 testing required before any PR creation
- **Quality gates**: Code formatting, environment validation enforced

**Smart Bypass System** (Emergency Only):
- **Double confirmation**: Two-step confirmation for emergency bypasses
- **Audit logging**: All bypasses logged for compliance tracking
- **Warning messages**: Clear explanation of risks and consequences
- **Usage tracking**: Bypass usage monitored and reported

### 2. Worktree Environment Support
**Safe Git operations optimized for worktree environments**:

**Worktree Detection**:
- **Environment awareness**: Automatic detection of worktree vs regular repository
- **Safe operations**: Worktree-specific Git operation patterns
- **Data protection**: Prevention of data loss between multiple worktrees
- **Branch isolation**: Independent branch operations per worktree

**Hook Installation**:
- **Universal coverage**: Hooks installed in main repository and all worktrees
- **Automatic detection**: Hook installer detects and handles worktree scenarios
- **Consistent enforcement**: Same workflow rules across all worktrees

### 3. Repository Hygiene Automation
**Automated maintenance keeping repository clean and efficient**:

**Branch Management**:
- **Merged branch cleanup**: Automatic deletion of branches merged to main
- **Age-based cleanup**: Configurable retention periods for feature branches
- **Protected branches**: Safety mechanisms preventing accidental deletion
- **Remote synchronization**: Cleanup of local and remote references

**Commit Standards**:
- **Message format validation**: Enforced commit message standards
- **Issue linking**: GitHub issue reference validation and suggestions
- **Automated signatures**: Claude Code signature injection for tool-generated commits

## Git Hooks Implementation

### Pre-Push Hook
**Primary workflow enforcement and branch validation**:

**P3 Workflow Enforcement**:
```bash
# Authorized push (from p3 ship)
if [ -n "$P3_CREATE_PR_PUSH" ]; then
    echo "✅ Automated p3 ship push authorized"
    exit 0
fi

# Blocked direct push
echo "🚨 DIRECT GIT PUSH BLOCKED"
echo "Use: p3 ship 'Title' ISSUE_NUM"
exit 1
```

**Emergency Bypass** (Strongly Discouraged):
- Double confirmation prompts with clear warnings
- Audit logging of all bypass attempts
- Risk explanation and alternative suggestions
- Compliance tracking for security review

### Post-Merge Hook
**Automated repository cleanup after merges**:
```bash
# After successful merge to main
if [ "$current_branch" = "main" ]; then
    echo "🧹 Cleaning up merged branches..."
    python infra/git-ops/cleanup_merged_branches.py --auto --days 7
fi
```

### Commit-Msg Hook
**Commit message format validation and enhancement**:
```bash
# Validate commit message format
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)"; then
    echo "❌ Commit message format error!"
    exit 1
fi
```

## Repository Management Tools

### Branch Cleanup (`cleanup_merged_branches.py`)
**Automated merged branch cleanup with safety mechanisms**:

**Features**:
- **Merged branch detection**: Identify branches fully merged to main
- **Age-based filtering**: Configurable retention periods (default: 7 days)
- **Interactive mode**: Confirmation prompts for manual cleanup
- **Automatic mode**: Silent cleanup for automated workflows
- **Protected branches**: Never delete main, develop, or other critical branches

**Usage**:
```bash
# Interactive cleanup
python infra/git-ops/cleanup_merged_branches.py

# Automatic cleanup (7-day retention)
python infra/git-ops/cleanup_merged_branches.py --auto --days 7

# Custom retention period
python infra/git-ops/cleanup_merged_branches.py --auto --days 14
```

### Hook Management (`install_git_hooks.py`)
**Comprehensive Git hooks installation and management**:

**Installation Process**:
```bash
# Install all Git hooks
python infra/git-ops/install_git_hooks.py

# Output:
🔧 Installing Consolidated Git Hooks
✅ Pre-push hook installed
✅ Post-merge hook installed  
✅ Commit-msg hook installed
🎉 Successfully installed 3/3 main git hooks!
```

**Hook Features**:
- **Automatic detection**: Repository vs worktree environment detection
- **Universal installation**: Hooks installed in main repo and all worktrees
- **Comprehensive coverage**: Pre-push, post-merge, commit-msg hooks
- **Intelligent bypass**: Emergency bypass with double confirmation

## Integration Points

### With P3 Workflow System
- **Command integration**: Git operations invoked through P3 commands
- **Workflow enforcement**: P3 ship workflow mandatory for all pushes
- **Testing integration**: F2 validation required before any PR creation

### With CI/CD Workflows
- **PR creation**: Integration with `infra/workflows/pr_creation.py`
- **Automated testing**: Hooks trigger test validation workflows
- **Quality gates**: Pre-PR validation and quality assurance

### With Repository Management
- **Branch lifecycle**: Creation, development, merging, cleanup automation
- **Release coordination**: Integration with release management workflows
- **Issue tracking**: GitHub issue linking and automated tracking

## Usage Examples

### Initial Setup
```bash
# Install Git hooks for P3 workflow enforcement
python infra/git-ops/install_git_hooks.py

# Verify hook installation
ls -la .git/hooks/
# pre-push, post-merge, commit-msg should be present and executable
```

### Daily Development Workflow
```bash
# Normal development (blocked)
git push origin feature-branch
# ❌ DIRECT GIT PUSH BLOCKED - Use: p3 ship 'Title' ISSUE_NUM

# Correct P3 workflow (allowed)
p3 ship "Add new feature" 123
# ✅ Automated p3 ship push authorized
```

### Repository Maintenance
```bash
# Manual branch cleanup
python infra/git-ops/cleanup_merged_branches.py
# Interactive prompts for branch deletion confirmation

# Automated cleanup (post-merge hook)
# Triggered automatically after merging PRs to main
# Cleans up merged branches older than 7 days
```

## Safety and Compliance

### Security Measures
- **Audit logging**: All bypass attempts logged with timestamps and user information
- **Double confirmation**: Emergency bypass requires two explicit confirmations
- **Risk warnings**: Clear explanation of consequences for policy violations
- **Usage monitoring**: Bypass usage tracked for compliance review

### Data Protection
- **Worktree safety**: Specialized Git operations preventing data loss
- **Branch protection**: Critical branches protected from accidental deletion
- **Recovery guidance**: Clear instructions for recovering from errors
- **Backup recommendations**: Guidance for maintaining local backups

### Compliance Standards
- **Workflow enforcement**: Consistent application of P3 workflow requirements
- **Quality gates**: Mandatory testing and validation before PR creation
- **Issue tracking**: Required GitHub issue linking for all changes
- **Documentation**: Comprehensive logging and audit trail maintenance

## Troubleshooting

### Common Issues

**Hook Installation Problems**:
```bash
# Issue: Hooks not executable
chmod +x .git/hooks/pre-push .git/hooks/post-merge .git/hooks/commit-msg

# Issue: Worktree hooks not working
python infra/git-ops/install_git_hooks.py  # Reinstall with worktree detection
```

**P3 Workflow Issues**:
```bash
# Issue: Push blocked by hooks
# Solution: Use proper P3 workflow
p3 ship "Commit title" ISSUE_NUMBER

# Issue: Emergency bypass needed
# Follow double confirmation prompts (strongly discouraged)
```

**Branch Cleanup Issues**:
```bash
# Issue: Protected branch deletion attempt
# Cleanup script has built-in protection for main/develop branches

# Issue: Unmerged branch false positive
python infra/git-ops/cleanup_merged_branches.py --dry-run  # Preview mode
```

---

**Integration References**:
- **P3 Workflow**: [Main README.md](../../README.md#p3-command-system) for complete workflow
- **CI/CD Integration**: [infra/workflows/README.md](../workflows/README.md) for automation
- **Company Policies**: [CLAUDE.md](../../CLAUDE.md) for compliance requirements