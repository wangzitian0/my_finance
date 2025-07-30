# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup and Dependencies

This project uses Python 3.12 with pipenv for dependency management. To set up the development environment:

```bash
pip install pipenv
pipenv shell
pipenv install
```

For deployment setup with Neo4j database and system configuration:
```bash
# Requires sudo permissions for system setup
ansible-playbook ansible/init.yml --ask-become-pass
# Pulls latest data and code updates
ansible-playbook ansible/setup.yml
```

## Core Commands

### Layered Data Management System

**Three-Tier Strategy**:
- **Tier 1 (M7)**: Stable test dataset (7 companies, ~500MB, tracked in git)
- **Tier 2 (NASDAQ100)**: Extended dataset (~100 companies, ~5GB, buildable)  
- **Tier 3 (US-ALL)**: Complete dataset (~8000 companies, ~50GB, buildable)

**Management Commands**:
```bash
# Build stable test dataset (always safe)
python manage.py build m7

# Build extended datasets (large downloads)
python manage.py build nasdaq100    # ~5GB
python manage.py build us-all       # ~50GB

# Check data status
python manage.py status

# Validate data integrity  
python manage.py validate

# Clean old data (for non-git tiers)
python manage.py clean nasdaq100
```

**Legacy Commands** (still supported):
```bash
# Run specific configuration directly
python run_job.py yfinance_nasdaq100.yml
python run_job.py sec_edgar_m7.yml
```

### Development Workflow
```bash
# Enter pipenv environment
pipenv shell

# Install new dependencies
pipenv install <package_name>
pipenv install <package_name> --dev

# Update lock file after dependency changes
pipenv lock --verbose

# Find Python interpreter path (for IDE setup)
which python
```

## Architecture Overview

This is a financial data collection and processing system with the following key components:

### Data Flow Architecture
1. **Configuration-driven Jobs** (`run_job.py`): Main entry point that selects appropriate spider based on config file prefix
2. **Data Spiders**: Collect data from different sources
   - `spider/yfinance_spider.py`: Yahoo Finance data collection 
   - `spider/sec_edgar_spider.py`: SEC Edgar filings collection
3. **Data Storage**: Raw data saved to `data/original/<source>/<ticker>/` with JSON format
4. **ETL Pipeline**: `ETL/` directory contains Neo4j database models and import scripts
5. **Parsers**: `parser/` directory handles SEC filing parsing and processing

### Key Components

**Database Layer (Neo4j)**:
- Uses neomodel ORM for graph database operations
- Models defined in `ETL/models.py` with relationships between Stock, Info, PriceData, etc.
- Stock ticker as unique identifier with relationships to financial data nodes

**Configuration System**:
- `common_config.yml`: Shared logging and system configuration
- Job-specific YAML configs in `data/config/`: Control data collection parameters
- `common/config.py`: Configuration loading utilities

**Data Collection**:
- Yahoo Finance spider: Collects stock prices, company info, recommendations, sustainability data
- SEC Edgar spider: Downloads regulatory filings (10-K, 10-Q, etc.) using CIK numbers
- Progress tracking and logging built into all spiders

**Parsing and Processing**:
- `parser/sec_parser.py`: Handles SEC filing XML/SGML parsing with BeautifulSoup
- `parser/rcts.py`: Additional SEC filing processing capabilities
- Data sanitization and validation in `common/utils.py`

### Data Organization
- Raw data: `data/original/<source>/<ticker>/`
- Logs: `data/log/<job_id>/<date_str>.txt`
- Configuration files: `data/config/*.yml`

### Important CIK Numbers (Magnificent 7)
The system can work with stock tickers or direct CIK numbers for SEC data:
- Apple (AAPL): 0000320193
- Microsoft (MSFT): 0000789019  
- Amazon (AMZN): 0001018724
- Alphabet (GOOGL): 0001652044
- Meta (FB): 0001326801
- Tesla (TSLA): 0001318605
- Netflix (NFLX): 0001065280

## Git Workflow and Issue Management

**MANDATORY: All changes must be associated with GitHub Issues for traceability**

### Standard Workflow with GoLand Integration
```bash
# 1. Create feature branch
git checkout -b feature/descriptive-name

# 2. Make changes and commit with PR reference for GoLand integration
git add .
git commit -m "Brief description

Fixes #issue-number

PR: https://github.com/wangzitian0/my_finance/pull/XXX"

# 3. Push and create PR with Issue link
git push -u origin feature/descriptive-name
gh pr create --title "Title - Fixes #issue-number" --body "Summary

Fixes #issue-number
Related to https://github.com/wangzitian0/my_finance/issues/14"

# 4. Update commit message with actual PR URL (for GoLand right-click)
git commit --amend -m "Brief description

Fixes #issue-number

PR: https://github.com/wangzitian0/my_finance/pull/ACTUAL_PR_NUMBER"
git push --force-with-lease
```

### Issue Association Rules
- **All PRs must link to an Issue**: Use "Fixes #N" or "Related to #N"
- **Claude Code configurations**: Always link to https://github.com/wangzitian0/my_finance/issues/14
- **Feature development**: Create specific issues for each major feature
- **Documentation updates**: Link to relevant feature issues

### GoLand Integration Benefits
- **Right-click commit → Open in Browser**: Direct access to GitHub PR
- **Commit message format**: Include "PR: https://github.com/..." for clickable links
- **Traceability**: From code change to issue to PR in one click

### Branch and Commit Standards
- `main`: Protected branch, only updated via merged PRs
- `feature/*`: Feature development branches  
- `hotfix/*`: Emergency fixes
- Commit messages must reference issue numbers AND PR URLs
- Include Claude Code attribution footer in commits

## GitHub Project Management

### Issue Management Guidelines
**Current Labels**: bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix, P0, P1, P2, data analysis, ETL, MVP

**Priority System**:
- **P0**: Blocking/Critical - Must fix immediately
- **P1**: High priority - Should fix this iteration
- **P2**: Medium priority - Can be scheduled later

**Phase Labels**:
- **MVP**: Minimum viable product features
- **data analysis**: Data processing and analysis tasks
- **ETL**: Extract, Transform, Load operations

### Project Board Workflow
**Standard Columns**: Todo → In Progress → Done

**Issue Assignment**:
- Link all development tasks to specific GitHub Issues
- Use GitHub Projects for tracking Phase 1/2/3 progress
- Update issue status as work progresses

### Current Active Issues (Created by Claude)
- Issue #20: Phase 1.1 - Extend Neo4j schema for SEC filings and DCF calculations
- Issue #21: Phase 1.2 - Implement basic DCF calculation engine
- Issue #22: Phase 1.3 - Build Graph RAG Q&A system

### Milestone Management
Create milestones for each project phase:
- **Phase 1 MVP**: Core DCF + Graph RAG capabilities
- **Phase 2 Complete**: Web interface + scaling
- **Phase 3 Production**: Full US stock support + optimization

## Testing and Validation

There is no standard test framework configured. The `test_yahoo/` directory contains manual testing scripts for Yahoo Finance functionality. Always verify data collection by checking output files in `data/original/` and log files.