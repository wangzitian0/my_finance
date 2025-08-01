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

- **Three-tier data management**: M7 (git-tracked) → NASDAQ100 (buildable) → US-ALL (buildable)
- **Neo4j graph database**: neomodel ORM, models in `ETL/models.py`
- **Data spiders**: Yahoo Finance (`spider/yfinance_spider.py`), SEC Edgar (`spider/sec_edgar_spider.py`)
- **Document parsing**: SEC filings with BeautifulSoup (`parser/sec_parser.py`)
- **Configuration-driven**: YAML configs in `data/config/`, `common_config.yml`
- **Data storage**: `data/original/<source>/<ticker>/` (JSON format)
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
- **Use Pixi** for all dependency management (replaces pipenv/conda/brew/apt)
- **Follow three-tier data strategy** when working with datasets
- **Reference CIK numbers** from README.md for SEC data work

### File Organization
- **Core logic**: `spider/`, `ETL/`, `parser/` directories
- **Management**: `manage.py`, `build_knowledge_base.py`
- **Configuration**: `data/config/*.yml`, `common_config.yml`
- **Documentation**: README.md (primary), this file (Claude-specific)

### Common Tasks
- **Data collection**: Use `pixi run run-job` or `python run_job.py [config.yml]`
- **Environment setup**: Use `pixi run setup-env` or Ansible playbooks in `ansible/` directory
- **Dependency management**: Always use `pixi add <package>` and `pixi install`
- **Testing**: Run manual validation, check outputs in `data/` directories

### Daily Development Workflow for Claude

**ALWAYS follow this sequence when working on tasks:**

```bash
# 1. Start session
pixi shell                    # Activate environment
pixi run env-status           # Check all services

# 2. Work on tasks
pixi run build-m7             # Build test data if needed
# ... make code changes ...
pixi run format               # Format code
pixi run lint                 # Check quality
pixi run test                 # Validate changes

# 3. End session (MANDATORY)
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

# 5. Clean shutdown
pixi run shutdown-all
```

### Session Management (CRITICAL)
- **Always start with**: `pixi shell` and `pixi run env-status`
- **Always end with**: `pixi run shutdown-all`
- **Never leave services running** between sessions
- **Check status frequently** during long development sessions

This ensures clean environment state and prevents port conflicts or resource issues.