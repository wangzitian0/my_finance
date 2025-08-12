# CLAUDE.md

> IMPORTANT UPDATE (2025-08-12)
>
> The `data` directory is now directly integrated into the main repository. 
> The previous symlink/submodule structure has been merged for simpler management.
>
> - New structure: `my_finance/data/` (regular directory, part of main repo)
> - All data files are now tracked in the main repository
> - No need for separate repository or symlink management

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
- **Pixi**: Development operations (data processing, code quality, testing)
- **Python scripts**: Complex operations that can't be handled by above

### Environment Commands (Ansible-managed)
```bash
pixi run setup-env              # Initial environment setup (installs Podman, Neo4j)
pixi run env-start              # Start all services (Podman + Neo4j)
pixi run env-stop               # Stop all services
pixi run env-status             # Check environment status
pixi run env-reset              # Reset everything (destructive)
```

### Podman Commands (Local Development)
```bash
pixi run podman-status          # Check container status
pixi run neo4j-logs             # View Neo4j logs
pixi run neo4j-connect          # Connect to Neo4j shell
pixi run neo4j-restart          # Restart Neo4j container
pixi run neo4j-stop             # Stop Neo4j container
pixi run neo4j-start            # Start Neo4j container
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

### Build Data Management Commands
```bash
pixi run create-build           # Create new timestamped build directory (branch-specific)
pixi run release-build          # Promote latest build to release with confirmation
```

## Architecture Overview

**See README.md for complete architecture details.** This is a Graph RAG-powered DCF valuation system with modular architecture:

- **ETL Pipeline**: Stage-based data processing (extract → transform → load) with daily partitioning
- **Four-tier data strategy**: test (CI) → M7 (git-tracked) → NASDAQ100 (buildable) → VTI (production)
- **Build tracking**: Every execution documented in `data/build/` with comprehensive manifests
- **Neo4j graph database**: neomodel ORM, models in `ETL/models.py`
- **Data spiders**: Yahoo Finance (`spider/yfinance_spider.py`), SEC Edgar (`spider/sec_edgar_spider.py`)
- **Document parsing**: SEC filings with BeautifulSoup (`parser/sec_parser.py`)
- **Configuration-driven**: YAML configs in `data/config/`, `common_config.yml`

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

- **Data Storage Structure**:
  - Stage 1 (Extract): `data/stage_01_extract/<source>/<date_partition>/<ticker>/`
  - Stage 2 (Transform): `data/stage_02_transform/<date_partition>/{cleaned,enriched,normalized}/`  
  - Stage 3 (Load): `data/stage_03_load/<date_partition>/{graph_nodes,embeddings,dcf_results,graph_rag_cache}/`
  - Build tracking: `data/stage_99_build/build_<YYYYMMDD_HHMMSS>/` (main branch)
    - Build artifacts: `BUILD_MANIFEST.json`, `BUILD_MANIFEST.md`
    - DCF reports: `M7_DCF_Report_<YYYYMMDD_HHMMSS>.txt`
    - Validation reports: `validation_report_<YYYYMMDD_HHMMSS>.json`
    - Stage logs: `stage_logs/` directory
  - Branch builds: `data/stage_99_build_<branch>/build_<YYYYMMDD_HHMMSS>/` (feature branches)
  - Release management: `data/release/release_<YYYYMMDD_HHMMSS>_build_<ID>/`
  - Latest build symlink: `common/latest_build` (points to most recent build)

- **Magnificent 7 CIK numbers**: Available in README.md

## Branch Protection and Security

**CRITICAL**: The repository relies on process enforcement rather than technical enforcement for quality control.

### Current Protection Status
- ✅ **Basic branch protection**: PRs required for main branch
- ✅ **GitHub Actions validation**: M7 test marker verification runs automatically  
- ⚠️ **Manual enforcement required**: Status checks are NOT mandatory for merge
- ⚠️ **Security gap**: Direct push without testing could bypass validation

### Why Automated Scripts Are MANDATORY

Since GitHub branch protection doesn't enforce required status checks, our automated workflow is the **primary defense** against:
- ❌ Untested code reaching main branch
- ❌ Broken builds in production
- ❌ Data corruption from invalid changes
- ❌ Regression without proper validation

**The `pixi run create-pr` script is not just best practice - it's essential for system stability.**

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
- **Test Marker System**: CI only validates that local tests were run (checks .m7-test-passed marker)
- **Fail Fast**: Direct pushes without local testing will fail CI (this is intentional)

#### Required PR Workflow
```bash
# 1. MANDATORY: Run local M7 end-to-end test first
pixi run test-m7-e2e

# 2. MANDATORY: Create PR only via script (includes test verification)
pixi run create-pr "Brief description" ISSUE_NUMBER

# 3. Optional: Create PR with custom description file
pixi run create-pr "Brief description" ISSUE_NUMBER --description pr_body.md
```

#### Why Manual Git Commands Are Discouraged
- `git push` without local testing → CI failure (by design)
- GitHub UI for direct commit → No test marker → CI rejection
- Manual PR creation → Missing M7 test verification → Merge blocked

**All successful merges require the automated script workflow.**

**⚠️ Manual git commands are DEPRECATED**. The automated script ensures:
- ✅ M7 end-to-end test runs successfully BEFORE PR creation/update
- ✅ Data directory changes are managed as part of main repository
- ✅ Commit messages include proper PR URLs for GoLand integration
- ✅ GitHub branch protection rules enforce M7 validation

**CRITICAL**: ALWAYS use `pixi run create-pr` for ALL PR operations:
- ✅ **Creating new PR**: `pixi run create-pr "Description" ISSUE_NUMBER`
- ✅ **Updating existing PR**: `pixi run create-pr "Update description" ISSUE_NUMBER`
- ✅ **Both operations require M7 testing** - no exceptions
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
- **Use Pixi for ALL commands** - NEVER use direct `python script.py`
- **Stage data directory changes FIRST** before main repo commits
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
- **Data directory**: Use `pixi run commit-data-changes` to stage data changes

### Daily Development Workflow for Claude

**CRITICAL RULES - NEVER BREAK THESE:**

1. **ALWAYS use `pixi run <command>` instead of `python <script>.py`**
2. **ALWAYS stage data directory changes before main repo commits**
3. **ALWAYS check and stage data changes first**
4. **ALWAYS start from latest main (`git checkout main && git pull`)**
5. **ALWAYS test mechanisms before coding (`pixi run build-dataset m7`)**

**ALWAYS follow this sequence when working on tasks:**

```bash
# 1. Start session - ENSURE LATEST BASE
git checkout main && git pull origin main    # CRITICAL: Latest main
pixi shell                                   # Activate environment
pixi run env-status                         # Check all services

# 2. Create branch from LATEST main
git checkout -b feature/description-fixes-N

# 3. VALIDATE mechanisms before coding (CRITICAL)
pixi run build-dataset m7    # Verify build system works
pixi run test-m7-e2e        # Verify end-to-end flow works
rm -f common/latest_build   # Clear build symlinks if needed

# 4. Work on tasks - USE PIXI COMMANDS ONLY
# ... make code changes ...
pixi run format             # Format code
pixi run lint               # Check quality
pixi run test               # Validate changes

# 5. Handle data directory FIRST (CRITICAL)
pixi run commit-data-changes  # Stage any data directory changes

# 6. Then handle main repo changes
git add . && git commit -m "Description

Fixes #N

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 7. Create PR with automated testing
pixi run create-pr "Description" N

# 8. End session (MANDATORY)
pixi run shutdown-all         # Stop all services
```

### Environment Management Rules
- **Setup once**: `pixi run setup-env` (only for new environments)
- **Daily startup**: `pixi run env-status` (check before starting work)
- **Daily shutdown**: `pixi run shutdown-all` (ALWAYS run before ending session)
- **Emergency reset**: `pixi run env-reset` (destructive - use carefully)

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
pixi run build-dataset m7    # Test build system
pixi run test-m7-e2e        # Test end-to-end flow

# 4. Make your changes and commit
git add .
git commit -m "Brief description

Fixes #ISSUE_NUMBER

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. Create OR Update PR with automated M7 testing (CRITICAL)
pixi run create-pr "Brief description" ISSUE_NUMBER  # Works for both new and existing PRs

# 6. For PR updates, ALWAYS use the same script (NEVER direct git push)
# The script will detect existing PR and update it with M7 validation

# 7. AFTER PR IS MERGED: Clean up branches  
pixi run cleanup-branches-auto

# 7. Clean shutdown
pixi run shutdown-all
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
   pixi run build-dataset m7      # NOT "pixi run build m7"
   rm -f common/latest_build     # Clear build symlinks if needed
   pixi run test-m7-e2e          # Full end-to-end validation
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
- ✅ **ALWAYS** test with `pixi run test-m7-e2e` after resolution
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