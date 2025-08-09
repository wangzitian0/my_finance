# Management Scripts

This directory contains management and utility scripts for the my_finance project.

## Data Collection & Building

### `build_dataset.py`
Unified dataset building script supporting multiple configuration tiers.

**Usage:**
```bash
# Build different dataset tiers
pixi run build-test          # Test dataset
pixi run build-m7            # M7 dataset (git-managed)
pixi run build-nasdaq100     # NASDAQ100 dataset (buildable)
pixi run build-vti           # VTI dataset (production)

# Direct usage
python scripts/build_dataset.py m7 --validate
python scripts/build_dataset.py nasdaq100 --validate
```

**Dataset Tiers:**
- **TEST**: Minimal dataset for CI/CD validation
- **M7**: Git-managed test dataset (Magnificent 7 companies)
- **NASDAQ100**: Buildable validation dataset (~100 companies)
- **VTI**: Production target dataset (~4000 companies)

### M7 Build Guide

The M7 (Magnificent 7) dataset includes:
- **Apple (AAPL)** - CIK 0000320193
- **Microsoft (MSFT)** - CIK 0000789019  
- **Amazon (AMZN)** - CIK 0001018724
- **Alphabet (GOOGL)** - CIK 0001652044
- **Meta (META)** - CIK 0001326801
- **Tesla (TSLA)** - CIK 0001318605
- **Netflix (NFLX)** - CIK 0001065280

**Build Statistics (typical):**
- Total companies: 7
- SEC filings: 168 documents
- YFinance files: 21 data files
- Data size: ~1.58 GB
- Build time: ~2.8 minutes

**Build Commands:**
```bash
# Quick build
pixi run build-m7

# Check status
pixi run status

# Environment setup (if needed)
pixi run env-status
pixi run env-start
```

## Data Migration & Structure

### `migrate_data_structure.py`
Migrates data from old `data/original/` structure to new ETL stage-based structure.

**Features:**
- Automatic backup creation
- CIK to ticker mapping for SEC data
- Date partition creation (YYYYMMDD format)
- Symlink management for latest partitions
- Build tracking integration

**Usage:**
```bash
pixi run migrate-data-structure
```

### `update_data_paths.py`
Updates code references to use new ETL directory structure.

## Metadata Management

### `manage_metadata.py`
Comprehensive metadata management utilities.

**Usage:**
```bash
# List all sources and tickers
pixi run metadata-list

# Rebuild metadata from existing files
pixi run metadata-rebuild

# Generate/update README.md indexes
pixi run metadata-index

# Show failed downloads
pixi run metadata-failures

# Clean up orphaned metadata entries
pixi run metadata-cleanup
```

### `retry_failed.py`
Retry failed downloads selectively based on metadata tracking.

**Usage:**
```bash
pixi run retry-failed
python scripts/retry_failed.py --source yfinance --ticker AAPL
python scripts/retry_failed.py --dry-run
```

## Environment & Infrastructure

### `env_status.py`
Check status of all infrastructure services (Minikube, Neo4j).

```bash
pixi run env-status
```

### `shutdown_all.py`
One-click shutdown of all services.

```bash
pixi run shutdown-all
```

## Git & Development

### `commit_data_changes.py`
Automatic data submodule commit tool (CRITICAL for workflow).

**Usage:**
```bash
pixi run commit-data-changes
pixi run check-data-status
```

### `cleanup_merged_branches.py`
Automated branch cleanup for merged PRs.

**Usage:**
```bash
# Interactive cleanup with confirmation
pixi run cleanup-branches

# Automatic cleanup (for CI or regular maintenance)
pixi run cleanup-branches-auto

# Check what would be cleaned up (safe)
pixi run cleanup-branches-dry-run
```

### `install_git_hooks.py`
Install git hooks for automated workflow.

```bash
pixi run install-git-hooks
```

## Data Quality & Validation

### `check_coverage.py`
Check data coverage and quality across different tickers and timeframes.

### `fetch_ticker_lists.py`
Update ticker lists from official sources (NASDAQ, VTI).

```bash
python scripts/fetch_ticker_lists.py
```

### `setup_test_environment.py`
Set up test environment with sample data.

## Maintenance & Cleanup

### `cleanup_obsolete_files.py`
Clean up obsolete files after data structure migrations.

## Pixi Integration

All major scripts are integrated with pixi task runner. See `pixi.toml` for complete list of available commands.

**Key Commands:**
```bash
# Data building
pixi run build-m7
pixi run build-nasdaq100

# Environment management
pixi run env-status
pixi run shutdown-all

# Data submodule (CRITICAL)
pixi run commit-data-changes

# Metadata management
pixi run metadata-rebuild
pixi run retry-failed

# Git workflow
pixi run cleanup-branches
```

## Script Dependencies

Scripts use the following key dependencies:
- **Common utilities**: `common/metadata_manager.py`, `common/build_tracker.py`
- **Configuration**: YAML files in `data/config/`
- **Spiders**: `spider/yfinance_spider.py`, `spider/sec_edgar_spider.py`
- **Pixi environment**: Managed dependencies via `pixi.toml`

---

*Scripts implement enterprise-grade data management with comprehensive automation and workflow integration.*