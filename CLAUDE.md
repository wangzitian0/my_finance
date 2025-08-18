# CLAUDE.md

> IMPORTANT UPDATE (2025-08-18)
>
> **Major System Enhancements Completed:**
> - ✅ **Stage Data Quality Reporting System**: Integrated into build process with automatic quality analysis
> - ✅ **DCF Report Generation & Tracking**: Complete SEC-enhanced DCF analysis with quality monitoring  
> - ✅ **Git Conflict Resolution Framework**: Proven workflow for handling complex merge conflicts
> - ✅ **Build Tracking Integration**: Quality reports auto-generated at each stage completion
> - ✅ **Directory Structure Unification**: Standardized stage-based data management
>
> The `data` directory is directly integrated into the main repository with comprehensive quality monitoring.

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
- **Ansible**: Environment setup and infrastructure (Podman, Neo4j, system-level)
- **p3 (Python CLI)**: Unified developer commands (data processing, quality, testing)
- **Pixi**: Environment activation and dependency management only

### Environment Commands (via p3)
```bash
p3 env setup                    # Initial environment setup (installs Podman, Neo4j)
p3 env start                    # Start all services (Podman + Neo4j)
p3 env stop                     # Stop all services
p3 env status                   # Check environment status
p3 env reset                    # Reset everything (destructive)
```

### Podman Commands (Local Development)
```bash
p3 podman status                # Check container status
p3 neo4j logs                   # View Neo4j logs
p3 neo4j connect                # Connect to Neo4j shell
p3 neo4j restart                # Restart Neo4j container
p3 neo4j stop                   # Stop Neo4j container
p3 neo4j start                  # Start Neo4j container
```

### Development Commands (Unified p3)
```bash
pixi shell                      # Activate environment (CORRECTED)
p3 refresh m7                   # Build stable test dataset
p3 format                       # Format code
p3 lint                         # Lint code
p3 test                         # Run tests
```

### Build Data Management Commands
```bash
p3 create-build                 # Create new timestamped build directory (branch-specific)
p3 release-build                # Promote latest build to release with confirmation

# Quality Reporting Commands (NEW)
p3 build run m7                 # Full build with integrated quality reporting
p3 e2e                          # End-to-end test with quality assessment
# Quality reports automatically generated at: data/quality_reports/<build_id>/
```

## Stage Data Quality Reporting System (NEW)

**CRITICAL**: Every build stage now automatically generates quality reports with success rate analysis.

### Quality Reporting Integration
**Automatically activated during build process:**

```python
from common.build_tracker import BuildTracker
from common.quality_reporter import setup_quality_reporter

# Quality reporting is automatically integrated into BuildTracker
tracker = BuildTracker()
build_id = tracker.start_build('m7', 'p3 build run m7')

# Each stage completion generates quality reports
tracker.complete_stage('stage_01_extract', partition='20250818')
# → Automatically creates: data/quality_reports/<build_id>/stage_01_extract_<timestamp>.json

# Build completion generates comprehensive summary
tracker.complete_build('completed')
# → Automatically creates: data/quality_reports/<build_id>/quality_summary_<timestamp>.md
```

### Quality Report Structure
- **Location**: `data/quality_reports/<build_id>/`
- **Stage Reports**: `stage_XX_<name>_<timestamp>.json`
- **Summary Reports**: `quality_summary_<timestamp>.{json,md}`
- **Metrics Tracked**: Success rates, file counts, processing efficiency, issues, recommendations

### Success Rate Analysis
- **YFinance Data Collection**: Downloads vs expected files
- **SEC Edgar Processing**: Document retrieval and parsing rates
- **Data Transformation**: Cleaning and normalization efficiency
- **Graph Loading**: Node creation and embedding generation
- **DCF Analysis**: Company analysis completion rates
- **Report Generation**: DCF report creation success

## Directory Management Principles

**CRITICAL**: All data follows the unified stage-based directory structure with quality monitoring.

### Standard Directory Format
```
stage_xx_yyyy/YYYYMMDD/TICKER/<files>
```

**Examples**:
- `stage_00_original/20250818/AAPL/AAPL_yfinance_daily.json`
- `stage_01_extract/20250818/AAPL/AAPL_sec_edgar_10k_001.txt`
- `stage_02_transform/20250818/AAPL/AAPL_cleaned_financials.json`
- `stage_03_load/20250818/AAPL/AAPL_graph_nodes.json`

### Directory Management Library
**Always use `common/directory_manager.py`** for all directory operations:

```python
from common.directory_manager import DirectoryManager

dm = DirectoryManager()

# Create standard directory
path = dm.create_directory_structure("stage_00_original", "AAPL", "20250818")

# Get standardized path
file_path = dm.get_standard_path("stage_01_extract", "AAPL", "20250818", "AAPL_data.json")

# List tickers in stage
tickers = dm.list_tickers_in_stage("stage_00_original", "20250818")

# Migrate legacy structures
stats = dm.migrate_legacy_structure("stage_00_original", legacy_path, "20250818")
```

### Stage Definitions
- **stage_00_original**: Raw data collection (SEC Edgar, YFinance)
- **stage_01_extract**: Extracted and parsed data
- **stage_02_transform**: Cleaned and normalized data
- **stage_03_load**: Graph nodes and embeddings
- **stage_04_analysis**: DCF analysis results
- **stage_05_reporting**: Final reports and visualizations
- **stage_99_build**: Build artifacts and manifests

### File Naming Conventions
- **Format**: `{TICKER}_{source}_{type}_{metadata}.{ext}`
- **Examples**:
  - `AAPL_yfinance_daily_1y.json`
  - `AAPL_sec_edgar_10k_20231002.txt`
  - `AAPL_graph_nodes_embedded.json`
  - `AAPL_dcf_results_comprehensive.json`

### Migration Requirements
- **Never create non-standard directories**
- **Always migrate legacy structures** using `scripts/migrate_directory_structure.py`
- **Validate structure compliance** with `DirectoryManager.validate_structure()`

## Architecture Overview

**See README.md for complete architecture details.** This is a SEC Filing-Enhanced Graph RAG-powered DCF valuation system with modular architecture:

- **ETL Pipeline**: Stage-based data processing with SEC document semantic embedding
- **Four-tier data strategy**: test (CI) → M7 (git-tracked + SEC) → NASDAQ100 (buildable) → VTI (production)
- **SEC Integration**: 336 SEC documents (10-K/10-Q/8-K) with semantic retrieval for M7 companies
- **Build tracking**: Every execution documented with comprehensive manifests and SEC citations
- **Neo4j graph database**: neomodel ORM with semantic embeddings storage
- **Data spiders**: SEC Edgar API (`spider/sec_edgar_spider.py`), Yahoo Finance integration
- **Semantic Retrieval**: Sentence transformers with FAISS vector search (`ETL/semantic_retrieval.py`)
- **Configuration-driven**: Stage-based YAML configs with SEC filing parameters

### Graph RAG Architecture (Modular Design)

- **Common Layer** (`common/`):
  - `graph_rag_schema.py`: Unified data structures, enums, and Neo4j query templates
  - Shared across ETL (data layer) and dcf_engine (business layer)

- **ETL Data Layer** (`ETL/`):
  - `graph_data_integration.py`: Neo4j graph data processing and node creation
  - `semantic_retrieval.py`: Vector embeddings generation and similarity search
  - Responsible for data integration and retrieval operations

- **DCF Engine Business Layer** (`dcf_engine/`):
  - `graph_rag_engine.py`: Natural language query processing and answer templates
  - `rag_orchestrator.py`: System coordination between ETL retrieval and answer generation
  - Responsible for question understanding and response generation

- **Unified Data Storage Structure**:
  - Stage 00: Original Data (`data/stage_00_original/YYYYMMDD/TICKER/`)
    - SEC Edgar: `TICKER_sec_edgar_{10k,10q,8k}_*.txt` (344 documents for M7)
    - YFinance: `TICKER_yfinance_{daily,weekly,monthly}_*.json` (45+ tickers for N100)
  - Stage 01: Extract (`data/stage_01_extract/YYYYMMDD/TICKER/`)
    - Extracted documents: `TICKER_extracted_{type}_*.{json,txt}`
  - Stage 02: Transform (`data/stage_02_transform/YYYYMMDD/TICKER/`)
    - Cleaned data: `TICKER_cleaned_{type}_*.json`
  - Stage 03: Load (`data/stage_03_load/YYYYMMDD/TICKER/`)
    - Graph nodes: `TICKER_graph_nodes_*.json`
    - Embeddings: `TICKER_embeddings_*.npy`
    - Vector indices: `TICKER_vector_index_*.faiss`
  - Build tracking: `data/stage_99_build/build_<YYYYMMDD_HHMMSS>/` (main branch)
    - Build artifacts: `BUILD_MANIFEST.json`, `BUILD_MANIFEST.md`
    - SEC-enhanced DCF reports: `M7_LLM_DCF_Report_<YYYYMMDD_HHMMSS>.md`
    - SEC integration examples: `sec_integration_examples/`, `sec_recall_examples/`
  - Branch builds: `data/stage_99_build_<branch>/build_<YYYYMMDD_HHMMSS>/` (feature branches)
  - Release management: `data/release/release_<YYYYMMDD_HHMMSS>_build_<ID>/`
  - Latest build symlink: `common/latest_build` (points to most recent build)

- **Magnificent 7 CIK numbers**: Available in README.md

## Branch Protection and Security

**CRITICAL**: The repository relies on process enforcement rather than technical enforcement for quality control.

### Current Protection Status
- ✅ **Basic branch protection**: PRs required for main branch
- ✅ **GitHub Actions validation**: M7 test validation in commit messages runs automatically  
- ✅ **Improved conflict management**: Eliminated .m7-test-passed file to reduce merge conflicts
- ⚠️ **Manual enforcement required**: Status checks are NOT mandatory for merge
- ⚠️ **Security gap**: Direct push without testing could bypass validation

### Why Automated Scripts Are MANDATORY

Since GitHub branch protection doesn't enforce required status checks, our automated workflow is the **primary defense** against:
- ❌ Untested code reaching main branch
- ❌ Broken builds in production
- ❌ Data corruption from invalid changes
- ❌ Regression without proper validation

**The `p3 create-pr` command is mandatory and central to the workflow.**

### Security Recommendations
1. **NEVER bypass automated scripts** - they prevent production issues
2. **Always verify M7 tests pass locally** before any PR operation
3. **Monitor CI status** - failed checks indicate serious problems
4. **Consider upgrading branch protection** to enforce required status checks

## Git Workflow and Issue Management

**See README.md for complete git workflow.** Claude-specific requirements:

### MANDATORY PR Creation Workflow

**CRITICAL**: PRs MUST be created using the automated script after local testing passes.

#### Design Philosophy
- **Local Testing First**: All tests must pass locally before PR creation
- **Commit Message Validation**: CI validates that local tests were run (checks commit message for M7 test validation)
- **No Conflict Files**: Eliminated .m7-test-passed file to prevent merge conflicts
- **Fail Fast**: Direct pushes without local testing will fail CI (this is intentional)

#### Required PR Workflow
```bash
# 1. MANDATORY: Run end-to-end test first
p3 e2e                    # Standard M7 test (required for PRs)

# 2. MANDATORY: Create PR only via unified CLI (includes test verification)
p3 create-pr "Brief description" ISSUE_NUMBER

# 3. Optional: Create PR with custom description file
p3 create-pr "Brief description" ISSUE_NUMBER --description pr_body.md
```

#### Why Manual Git Commands Are Discouraged
- `git push` without local testing → CI failure (by design)
- GitHub UI for direct commit → No test validation in commit message → CI rejection
- Manual PR creation → Missing test verification → Merge blocked

**All successful merges require the automated script workflow.**

**⚠️ Manual git commands are DEPRECATED**. The automated script ensures:
- ✅ End-to-end test runs successfully BEFORE PR creation/update
- ✅ Data directory changes are managed as part of main repository
- ✅ Commit messages include M7 test validation and PR URLs for GoLand integration
- ✅ GitHub branch protection rules enforce test validation via commit message parsing
- ✅ No conflict-prone marker files (.m7-test-passed eliminated)

**CRITICAL**: ALWAYS use `p3 create-pr` for ALL PR operations:
- ✅ **Creating new PR**: `p3 create-pr "Description" ISSUE_NUMBER`
- ✅ **Updating existing PR**: `p3 create-pr "Update description" ISSUE_NUMBER`
- ✅ **Both operations require end-to-end testing** - no exceptions
- ❌ **NEVER** use direct `git push` or manual PR updates

**Legacy manual workflow (NOT RECOMMENDED)**:
```bash
# Only use if automated script fails
git commit -m "Brief description

Fixes #issue-number

PR: PLACEHOLDER

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push -u origin feature/description-fixes-ISSUE_NUMBER
gh pr create --title "..." --body "..."
git commit --amend -m "Brief description with actual PR URL"
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

### Recently Completed Issues
- Issue #91: ✅ **COMPLETED** - Stage Data Quality Reporting System (2025-08-18)
  - ✅ **Git conflict resolution**: Comprehensive rebase workflow for complex merge conflicts
  - ✅ **Data cleanup**: Non-release old data cleanup and organization
  - ✅ **Quality reporting system**: Integrated stage-by-stage quality analysis into build process
  - ✅ **BuildTracker integration**: Quality reports auto-generated at each stage completion
  - ✅ **DCF report tracking**: Enhanced detection and monitoring of DCF report generation
  - ✅ **Success rate monitoring**: YFinance, SEC Edgar, transformation, loading efficiency tracking
  - ✅ **Automated recommendations**: Issue detection and actionable improvement suggestions
  - ✅ **Comprehensive documentation**: Complete SEC-DCF integration process documentation

- Issue #80: ✅ **COMPLETED** - Eliminated .m7-test-passed file conflicts (2025-08-13)
  - Replaced file-based test validation with commit message validation
  - Updated create-pr script to embed M7 test results directly in commit messages
  - Created new GitHub Actions workflow for commit message validation
  - Removed conflict-prone .m7-test-passed files entirely
  - Improved merge conflict resolution by eliminating file-based markers
  - Enhanced test timing validation (tests must be within reasonable time of push)

- Issue #75: ✅ **COMPLETED** - SEC Filing Data Integration and Enhancement (2025-08-13)
  - Unified company schema (ticker→name, cik) in configuration files
  - Renamed source configurations to stage-based naming convention
  - Created SEC integration template for DCF reports with citation management
  - Built complete SEC dataset with 336 documents for M7 companies
  - Implemented SEC recall usage examples with semantic retrieval
  - Installed ML dependencies (PyTorch, scikit-learn, sentence-transformers)
  
- Issue #58: ✅ **COMPLETED** - Automated file management system with directory structure refactoring
  - Directory restructuring: `data/original` → `data/stage_00_original`, `data/build` → `data/stage_99_build`
  - Report isolation: DCF reports now saved in specific build directories
  - Path consistency: Updated all hardcoded path references
  - Submodule management: Proper data submodule configuration

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
- **Use p3 for ALL operational commands** - prefer Python CLI over shell
- **Stage data directory changes FIRST** before main repo commits
- **Follow three-tier data strategy** when working with datasets (see `docs/data-tiers.md`)
- **Reference CIK numbers** from README.md for SEC data work

### File Organization
- **Core logic**: `spider/`, `ETL/`, `parser/` directories
- **Management**: `ETL/manage.py`, `dcf_engine/build_knowledge_base.py`
- **Configuration**: `data/config/*.yml`, `common/common_config.yml`
- **Documentation**: README.md (primary), `docs/` (detailed docs), this file (Claude-specific)

### Common Tasks
- **Data collection**: Use `p3 build run m7` (NEVER direct python script invocations)
- **Environment setup**: Use `p3 env setup`
- **Dependency management**: Always use `pixi add <package>` and `pixi install`
- **Testing**: Use `p3 test` (NEVER direct python commands)
- **Data directory**: Use `p3 commit-data-changes` to stage data changes

### Simplified Command System

**Format**: `p3 <command> [scope]`

**Commands**:
- `build` - Build dataset and run analysis
- `e2e` - End-to-end testing  
- `clean-branch` - Clean up branches
- `commit-xx` - Commit operations
- `create-xx` - Create operations (PR, build, etc.)
- `env-xx` - Environment management

**Scopes** (defaults to `m7` if not specified):
- `f2` - Fast 2 companies (development testing)
- `m7` - Magnificent 7 companies (standard/PR testing)  
- `n100` - NASDAQ 100 companies (validation testing)
- `v3k` - VTI 3500+ companies (production testing)

### Testing Strategy
- **Fast Development Testing**: `p3 e2e` (~1-2 minutes)
  - Quick validation during development
  - Sufficient for most code changes and bug fixes
- **Standard PR Testing**: `p3 e2e` or `p3 e2e m7` (~5-10 minutes)  
  - **REQUIRED** before creating PRs
  - Full M7 validation (default scope)
  - Production-grade quality assurance
- **Extended Testing**: `p3 e2e n100` or `p3 e2e v3k` (comprehensive validation)

### Daily Development Workflow for Claude

**CRITICAL RULES - NEVER BREAK THESE:**

1. **ALWAYS use `p3 <command>` instead of `python <script>.py`**
2. **ALWAYS stage data directory changes before main repo commits**
3. **ALWAYS check and stage data changes first**
4. **ALWAYS start from latest main (`git checkout main && git pull`)**
5. **ALWAYS test mechanisms before coding (`p3 build run m7`)**
6. **ALWAYS verify SEC data availability before semantic retrieval work**
7. **ALWAYS use proper citations when working with SEC filing integration**

**ALWAYS follow this sequence when working on tasks:**

```bash
# 1. Start session - ENSURE LATEST BASE
git checkout main && git pull origin main    # CRITICAL: Latest main
pixi shell                                   # Activate environment (CORRECTED)
p3 env status                                # Check all services

# 2. Create branch from LATEST main
git checkout -b feature/description-fixes-N

# 3. VALIDATE mechanisms before coding (CRITICAL)
p3 build run m7             # Verify build system works (with quality reporting)
p3 e2e                      # End-to-end flow validation (with quality analysis)
rm -f common/latest_build   # Clear build symlinks if needed

# 4. Work on tasks - USE P3 COMMANDS ONLY
# ... make code changes ...
p3 format                   # Format code
p3 lint                     # Check quality
p3 test                     # Validate changes

# 5. Handle data directory FIRST (CRITICAL)
 p3 commit-data-changes        # Stage any data directory changes

# 6. Then handle main repo changes
git add . && git commit -m "Description

Fixes #N

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 7. Create PR with automated testing
 p3 create-pr "Description" N

# 8. End session (MANDATORY)
 p3 shutdown-all               # Stop all services
```

### Environment Management Rules
- **Setup once**: `p3 env setup` (only for new environments)
- **Daily startup**: `p3 env status` (check before starting work)
- **Daily shutdown**: `p3 shutdown-all` (ALWAYS run before ending session)
- **Emergency reset**: `p3 env reset` (destructive - use carefully)

### Git Workflow (MANDATORY for all changes)

**CRITICAL: Always base branches on latest main to avoid conflicts**

```bash
# 1. ALWAYS start from latest main (CRITICAL)
git checkout main && git pull origin main
git checkout -b feature/description-fixes-ISSUE_NUMBER

# 2. For long-running tasks: regularly sync with main
git fetch origin main
git log --oneline HEAD..origin/main  # Check if main has new commits
# If main is ahead, consider: git rebase origin/main

# 3. Verify mechanisms work BEFORE making changes
 p3 build run m7             # Test build system
 p3 e2e                      # End-to-end test

# 4. Make your changes and commit
git add .
git commit -m "Brief description

Fixes #ISSUE_NUMBER

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. Create OR Update PR with automated M7 testing (CRITICAL)
 p3 create-pr "Brief description" ISSUE_NUMBER  # Works for both new and existing PRs

# 6. For PR updates, ALWAYS use the same script (NEVER direct git push)
# The script will detect existing PR and update it with M7 validation

# 7. AFTER PR IS MERGED: Clean up branches  
 p3 cleanup-branches --auto

# 7. Clean shutdown
 p3 shutdown-all
```

**Benefits of automated workflow:**
- ✅ **M7 testing**: Runs full end-to-end test BEFORE creating PR
- ✅ **Data directory**: Stages data changes as part of main repository  
- ✅ **PR URLs**: Updates commit messages with actual PR URLs
- ✅ **Branch protection**: GitHub enforces M7 validation on all PRs
- ✅ **No failures**: PRs cannot be created if M7 tests fail

### Conflict Prevention and Resolution (CRITICAL)

**Common Causes of Rework and How to Avoid Them:**

1. **Branch Base Issues** (Most Critical):
   ```bash
   ❌ WRONG: git checkout -b feature/task old-commit
   ❌ WRONG: git checkout -b feature/task (without updating main)
   ✅ CORRECT: git checkout main && git pull && git checkout -b feature/task
   ```

2. **Mechanism Failures** - Test Before Coding:
   ```bash
   # Always verify these work BEFORE starting development
    p3 build run m7               # Test build system with M7 scope
   rm -f common/latest_build     # Clear build symlinks if needed
    p3 e2e                        # End-to-end validation
   ```

3. **Long-running Branch Syndrome**:
   ```bash
   # Check for main updates frequently (daily for long tasks)
   git fetch origin main
   git log --oneline HEAD..origin/main
   
   # If main is ahead, rebase early (easier than resolving later)
   git rebase origin/main
   ```

**When Conflicts Occur - MANDATORY Resolution Workflow:**

**CRITICAL**: NEVER handle conflicts without first updating main branch:

```bash
# STEP 1: Always start by updating main (MANDATORY)
git checkout main
git pull origin main

# STEP 2: Return to feature branch and rebase
git checkout feature/branch-name
git rebase origin/main  # This will show conflicts

# STEP 3: Resolve conflicts in files, then continue
git add .
git rebase --continue

# STEP 4: Push the resolved branch
git push origin feature/branch-name --force-with-lease
```

**Conflict Resolution Rules:**
- ⚠️ **NEVER** attempt conflict resolution without latest main
- ⚠️ **NEVER** continue working on conflicted branches
- ✅ **ALWAYS** pull main first, then handle feature branch
- ✅ **ALWAYS** test with `p3 e2e` after resolution
- ✅ When in doubt, start fresh from latest main

**Complex Conflicts** (major rework needed):
```bash
# NUCLEAR OPTION: Start fresh from latest main
git checkout main && git pull
git checkout -b feature/task-v2
# Manually recreate changes - prevents conflict debt
```

### Branch Cleanup (MANDATORY after MR merge)

**Automated branch cleanup for merged PRs:**

```bash
# Check what would be cleaned up (safe)
 p3 cleanup-branches --dry-run

# Interactive cleanup with confirmation
p3 cleanup-branches

# Automatic cleanup (for CI or regular maintenance)
p3 cleanup-branches --auto
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
- **Always start with**: `pixi shell` and `p3 env status` (CORRECTED)
- **Always end with**: `p3 shutdown-all`
- **Never leave services running** between sessions
- **Check status frequently** during long development sessions

This ensures clean environment state and prevents port conflicts or resource issues.

## Git Conflict Resolution Framework (NEW)

**Proven workflow for handling complex merge conflicts based on Issue #91 experience:**

### Conflict Prevention
1. **Always start from latest main**: `git checkout main && git pull origin main`
2. **Regular syncing**: `git fetch origin main` and check `git log --oneline HEAD..origin/main`
3. **Early rebasing**: Rebase frequently during long-running branches
4. **Test before pushing**: Always run `p3 e2e` before creating PRs

### Conflict Resolution Process
**When conflicts occur during rebase:**

```bash
# Step 1: Start rebase
git rebase origin/main
# → Git will pause at first conflict

# Step 2: Analyze conflicts
git status  # See conflicted files
# Look for conflict markers: <<<<<<< HEAD, =======, >>>>>>> 

# Step 3: Resolve conflicts methodically
# Choose appropriate version (HEAD vs incoming) for each section
# Remove conflict markers
# Test functionality after each file

# Step 4: Continue rebase
git add .  # Stage resolved files
git rebase --continue  # Continue to next conflict or complete

# Step 5: Force push with lease (safer)
git push --force-with-lease origin feature/branch-name

# Step 6: Verify with quality testing
p3 e2e  # Ensure everything still works after conflict resolution
```

### Common Conflict Patterns
- **Build tracking code**: Usually take HEAD (current branch) version
- **Import statements**: Merge both, removing duplicates
- **Configuration files**: Merge functionality from both branches
- **Method signatures**: Take the newer version and update callers
- **Data structures**: Merge fields and update all references

### Conflict Resolution Best Practices
- ✅ **Resolve file by file**: Don't try to fix everything at once
- ✅ **Test after each resolution**: Ensure functionality still works
- ✅ **Keep detailed commit messages**: Document what conflicts were resolved
- ✅ **Use quality reports**: Verify no regressions with `p3 e2e`
- ❌ **Never force push without --force-with-lease**: Could overwrite others' work
- ❌ **Never continue with unresolved conflicts**: Fix all conflicts before continuing

### Emergency Recovery
**If conflicts become too complex:**
```bash
# Abort current rebase
git rebase --abort

# Start fresh from latest main
git checkout main && git pull
git checkout -b feature/task-v2
# Manually recreate your changes - cleaner than resolving complex conflicts
```