# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: Always read and reference the README.md file first, as it contains the complete project information. This file supplements with Claude-specific instructions only.

## Environment Setup and Dependencies

**See README.md for complete setup instructions.** Key points for Claude:

- **Pixi** for cross-platform package management (replaces conda/brew/apt)
- Python 3.12 + all dependencies managed through pixi.toml
- Ansible automation compatible with Pixi environment
- Use `pixi info` to check environment details for IDE configuration

## Core Commands

**See README.md for complete command reference.** Quick reference for Claude:

```bash
# Essential commands
pixi shell                      # Activate environment (or run pixi run <task>)
pixi run build-m7               # Build stable test dataset
pixi run status                 # Check data status
pixi run run-job                # Run default data collection
pixi run setup-env              # Ansible environment setup with Pixi
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

### Standard Development Workflow
1. **Create feature branch**: `git checkout -b feature/description-fixes-N`
2. **Make changes and initial commit**: Include placeholder PR URL
3. **Push branch**: `git push -u origin feature/description-fixes-N`
4. **Create PR**: `gh pr create --title "..." --body "..."`
5. **Amend commit**: Replace placeholder with actual PR URL
6. **Force push**: `git push --force-with-lease`

This ensures GoLand integration works properly with clickable PR links in commit messages.