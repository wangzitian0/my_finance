# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: Always read and reference the README.md file first, as it contains the complete project information. This file supplements with Claude-specific instructions only.

## Environment Setup and Dependencies

**See README.md for complete setup instructions.** Key points for Claude:

- **Pixi** for cross-platform package management (replaces conda/brew/apt)
- Python 3.12 + all dependencies managed through pixi.toml
- Ansible automation compatible with Pixi environment
- Use `pixi info` to check environment details for IDE configuration

## Command Line Architecture

**Two-tier management system:**
- **Ansible**: Environment setup and infrastructure (Minikube, Neo4j, system-level)
- **Pixi**: Development operations (data processing, code quality, testing)
- **Python scripts**: Complex operations that can't be handled by above

### Environment Commands (Ansible-managed)
```bash
pixi run setup-env              # Initial environment setup (installs Minikube, Neo4j)
pixi run env-start              # Start all services (Minikube + Neo4j)
pixi run env-stop               # Stop all services
pixi run env-status             # Check environment status
pixi run env-reset              # Reset everything (destructive)
```

### Development Commands (Pixi-managed)
```bash
pixi shell                      # Activate environment
pixi run status                 # Check data status
pixi run build-m7               # Build stable test dataset
pixi run run-job                # Run default data collection
pixi run format                 # Format code
pixi run lint                   # Lint code
pixi run test                   # Run tests
```

## Architecture Overview

**See README.md for complete architecture details.** This is a Graph RAG-powered DCF valuation system with:

- **ETL Pipeline**: Stage-based data processing (extract → transform → load) with daily partitioning
- **Four-tier data strategy**: test (CI) → M7 (git-tracked) → NASDAQ100 (buildable) → VTI (production)
- **Build tracking**: Every execution documented in `data/build/` with comprehensive manifests
- **Neo4j graph database**: neomodel ORM, models in `ETL/models.py`
- **Data spiders**: Yahoo Finance (`spider/yfinance_spider.py`), SEC Edgar (`spider/sec_edgar_spider.py`)
- **Document parsing**: SEC filings with BeautifulSoup (`parser/sec_parser.py`)
- **Configuration-driven**: YAML configs in `data/config/`, `common_config.yml`
- **ETL Data Storage**: 
  - Stage 1 (Extract): `data/stage_01_extract/<source>/<date_partition>/<ticker>/`
  - Stage 2 (Transform): `data/stage_02_transform/<date_partition>/{cleaned,enriched,normalized}/`  
  - Stage 3 (Load): `data/stage_03_load/<date_partition>/{graph_nodes,embeddings,dcf_results}/`
  - Build tracking: `data/build/build_<YYYYMMDD_HHMMSS>/BUILD_MANIFEST.md`
- **Magnificent 7 CIK numbers**: Available in README.md

## Git Workflow and Issue Management

**See README.md for complete git workflow.** Claude-specific requirements:

### MANDATORY Commit Format
```bash
git commit -m "Brief description

Fixes #issue-number

PR: https://github.com/wangzitian0/my_finance/pull/XXX

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Important**: After creating PR, always amend commit to include actual PR URL for GoLand integration:
```bash
git commit --amend -m "Brief description

Fixes #issue-number

PR: https://github.com/wangzitian0/my_finance/pull/ACTUAL_NUMBER

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push --force-with-lease
```

### Issue Association Rules
- **ALL changes must link to GitHub Issues** for traceability
- **Claude Code configurations**: Always link to https://github.com/wangzitian0/my_finance/issues/14
- **Branch naming**: `feature/description-fixes-N`, `bugfix/description-fixes-N`
- **Main branch protection**: Only accepts PRs, all commits must reference issues

### Current Active Issues
- Issue #20: Phase 1.1 - Extend Neo4j schema for SEC filings and DCF calculations
- Issue #21: Phase 1.2 - Implement basic DCF calculation engine  
- Issue #22: Phase 1.3 - Build Graph RAG Q&A system
- Issue #26: Cross-platform conda migration

### Labels and Priorities
**Priority**: P0 (critical) > P1 (high) > P2 (medium)
**Phase**: MVP, data analysis, ETL
**Type**: bug, enhancement, documentation

## Testing and Validation

**See README.md for testing approach.** No standard test framework currently configured.

**Validation Methods**:
- Manual testing scripts in `test_yahoo/` directory
- Output verification in `data/original/` directories
- Log analysis in `data/log/` directories
- Ansible testing: `python scripts/test_ansible.py`

**Always verify**: Data collection outputs and processing logs before committing changes.

## Claude Code Integration Notes

### Development Patterns
- **Always read README.md first** for complete project context
- **Prefer editing existing files** over creating new ones
- **Use Pixi for ALL commands** - NEVER use direct `python script.py`
- **Handle data submodule changes FIRST** before main repo commits
- **Follow three-tier data strategy** when working with datasets (see `docs/data-tiers.md`)
- **Reference CIK numbers** from README.md for SEC data work

### File Organization
- **Core logic**: `spider/`, `ETL/`, `parser/` directories
- **Management**: `ETL/manage.py`, `dcf_engine/build_knowledge_base.py`
- **Configuration**: `data/config/*.yml`, `common/common_config.yml`
- **Documentation**: README.md (primary), `docs/` (detailed docs), this file (Claude-specific)

### Common Tasks
- **Data collection**: Use `pixi run run-job` (NEVER direct python commands)
- **Environment setup**: Use `pixi run setup-env`
- **Dependency management**: Always use `pixi add <package>` and `pixi install`
- **Testing**: Use `pixi run test` (NEVER direct python commands)
- **Data submodule**: Use `pixi run commit-data-changes` before main commits

### Daily Development Workflow for Claude

**CRITICAL RULES - NEVER BREAK THESE:**

1. **ALWAYS use `pixi run <command>` instead of `python <script>.py`**
2. **ALWAYS handle data submodule changes before main repo commits**
3. **ALWAYS check and commit submodule changes first**

**ALWAYS follow this sequence when working on tasks:**

```bash
# 1. Start session
pixi shell                    # Activate environment
pixi run env-status           # Check all services

# 2. Work on tasks - USE PIXI COMMANDS ONLY
pixi run build-m7             # Build test data if needed
# ... make code changes ...
pixi run format               # Format code
pixi run lint                 # Check quality
pixi run test                 # Validate changes

# 3. Handle data submodule FIRST (CRITICAL)
pixi run commit-data-changes  # Auto-commit any data submodule changes

# 4. Then handle main repo changes
# ... commit main repo changes ...

# 5. End session (MANDATORY)
pixi run shutdown-all         # Stop all services
```

### Environment Management Rules
- **Setup once**: `pixi run setup-env` (only for new environments)
- **Daily startup**: `pixi run env-status` (check before starting work)
- **Daily shutdown**: `pixi run shutdown-all` (ALWAYS run before ending session)
- **Emergency reset**: `pixi run env-reset` (destructive - use carefully)

### Git Workflow (MANDATORY for all changes)

**Complete workflow including MR creation:**

```bash
# 1. Create feature branch
git checkout -b feature/description-fixes-ISSUE_NUMBER

# 2. Make changes and commit with placeholder
git add .
git commit -m "Brief description

Fixes #ISSUE_NUMBER

PR: https://github.com/wangzitian0/my_finance/pull/PLACEHOLDER

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 3. Push and create MR
git push -u origin feature/description-fixes-ISSUE_NUMBER
gh pr create --title "..." --body "..."

# 4. Amend with actual PR URL (CRITICAL for GoLand integration)
git commit --amend -m "Brief description

Fixes #ISSUE_NUMBER

PR: https://github.com/wangzitian0/my_finance/pull/ACTUAL_NUMBER

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push --force-with-lease

# 5. AFTER MR IS MERGED: Clean up branches
pixi run cleanup-branches-auto  # Auto-cleanup merged branches

# 6. Clean shutdown
pixi run shutdown-all
```

### Branch Cleanup (MANDATORY after MR merge)

**Automated branch cleanup for merged PRs:**

```bash
# Check what would be cleaned up (safe)
pixi run cleanup-branches-dry-run

# Interactive cleanup with confirmation
pixi run cleanup-branches

# Automatic cleanup (for CI or regular maintenance)
pixi run cleanup-branches-auto
```

**Manual cleanup if needed:**
```bash
# Delete remote branch
git push origin --delete feature/branch-name

# Delete local branch
git branch -d feature/branch-name  # Safe delete
git branch -D feature/branch-name  # Force delete if needed

# Prune remote references
git remote prune origin
```

### Session Management (CRITICAL)
- **Always start with**: `pixi shell` and `pixi run env-status`
- **Always end with**: `pixi run shutdown-all`
- **Never leave services running** between sessions
- **Check status frequently** during long development sessions

This ensures clean environment state and prevents port conflicts or resource issues.