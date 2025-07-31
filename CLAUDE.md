# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: Always read and reference the README.md file first, as it contains the complete project information. This file supplements with Claude-specific instructions only.

## Environment Setup and Dependencies

**See README.md for complete setup instructions.** Key points for Claude:

- Python 3.12 + pipenv dependency management
- Cross-platform conda environment recommended
- Ansible automation for Neo4j and system setup
- Use `pipenv --py` to find Python interpreter path for IDE configuration

## Core Commands

**See README.md for complete command reference.** Quick reference for Claude:

```bash
# Essential commands
pipenv shell                    # Activate environment
python manage.py build m7       # Build stable test dataset
python manage.py status         # Check data status
python run_job.py               # Run default data collection
ansible-playbook ansible/init.yml --ask-become-pass  # Environment setup
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

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
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
- **Use pipenv** for Python dependency management
- **Follow three-tier data strategy** when working with datasets
- **Reference CIK numbers** from README.md for SEC data work

### File Organization
- **Core logic**: `spider/`, `ETL/`, `parser/` directories
- **Management**: `manage.py`, `build_knowledge_base.py`
- **Configuration**: `data/config/*.yml`, `common_config.yml`
- **Documentation**: README.md (primary), this file (Claude-specific)

### Common Tasks
- **Data collection**: Use `python run_job.py [config.yml]`
- **Environment setup**: Use Ansible playbooks in `ansible/` directory
- **Dependency management**: Always use `pipenv install` and `pipenv lock`
- **Testing**: Run manual validation, check outputs in `data/` directories