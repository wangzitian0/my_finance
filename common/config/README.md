# Configuration Architecture

This directory contains the modular configuration system for the My Finance DCF Analysis Tool. The architecture follows the principle of **separation of concerns** with complete decoupling between data sources and ticker lists.

## Architecture Overview

The configuration system is organized into two distinct categories:

### 1. Stage Original Configurations (`stage_00_original_*.yml`)
These files define **how** to collect data from different sources, independent of **which** companies to collect data for.

- `stage_00_original_yfinance.yml` - Yahoo Finance data collection parameters
- `stage_00_original_sec_edgar.yml` - SEC Edgar filings collection parameters

### 2. Ticker List Configurations (`list_*.yml`)  
These files define **which** companies to process, with their CLI aliases and metadata.

**Production Datasets:**
- `list_magnificent_7.yml` - Magnificent 7 tech companies (CLI: `m7`) - 7 companies
- `list_nasdaq_100.yml` - NASDAQ-100 index companies (CLI: `n100`) - ~100 companies
- `list_vti_3500.yml` - VTI ETF holdings (CLI: `v3k`) - ~3500 companies

**Testing Datasets:**
- `list_fast_2.yml` - Fast 2-company subset from M7 (CLI: `fast`) - For development

### 3. Test Target Configurations (`stage_00_target_*.yml`)
These files define **testing strategies** and requirements for different validation scenarios.

- `stage_00_target_pre_pr.yml` - Pre-PR validation requirements using fast_2 ticker list

## Usage

### Command Line Interface

**Production Dataset Building:**
```bash
# Build full datasets using CLI aliases
pixi run build m7        # Magnificent 7 (7 companies) - REQUIRED FOR PR
pixi run build n100      # NASDAQ-100 (~100 companies)
pixi run build v3k       # VTI 3500 (~3500 companies)

# Full names also work
pixi run build magnificent_7
pixi run build nasdaq_100  
pixi run build vti_3500
```

**Development Testing:**
```bash
# Fast development testing (2 companies only)
pixi run build fast      # Fast 2-company subset (MSFT, NVDA)

# PR creation with mandatory M7 testing
p3 ship "PR title" ISSUE_NUMBER  # Runs full M7 test (7 companies)

# Standalone M7 testing for PR validation
p3 test m7         # Tests all 7 companies, creates .m7-test-passed marker
```

### Configuration Combination
The build system automatically combines:
- Ticker list configuration (defines WHICH companies)
- Data source configurations (defines HOW to collect data)

For example, `pixi run build n100` will:
1. Load `list_nasdaq_100.yml` to get 100 NASDAQ companies
2. Load `stage_00_original_yfinance.yml` for Yahoo Finance collection settings
3. Load `stage_00_original_sec_edgar.yml` for SEC filing settings (if enabled)
4. Combine them to collect data for all 100 companies from both sources

## Auto-Generated Content

### NASDAQ-100 and VTI Lists
The ticker lists for NASDAQ-100 and VTI are automatically updated using official APIs:

```bash
# Update ticker lists with latest data
python ETL/fetch_ticker_lists.py
```

This script:
- Fetches current NASDAQ-100 constituents from official NASDAQ API
- Fetches current VTI holdings from Vanguard API  
- Updates the configuration files with:
  - Current ticker symbols
  - Company names and market cap data
  - Last updated timestamps
  - Expected file counts

**Important**: Do not manually edit the `companies` section in `list_nasdaq_100.yml` or `list_vti_3500.yml` as they will be overwritten by the update script.

### Magnificent 7 List
The Magnificent 7 list is manually maintained as it represents a stable set of core technology companies for testing.

## Configuration Fields

### Stage Original Files (`stage_00_original_*.yml`)
```yaml
source: "yfinance"  # Source identifier
description: "Data source description"
data_periods:       # Collection periods and intervals
  period_name:
    period: "1y"
    interval: "1d"
    description: "Period description"
# Collection settings, validation rules, output format, etc.
```

### Ticker List Files (`list_*.yml`)  
```yaml
dataset_name: "nasdaq100"      # Dataset identifier
cli_alias: "n100"             # CLI command alias
description: "Dataset description"
tier: 3                       # Tier in 4-tier strategy
tracked_in_git: false         # Whether to commit to git
max_size_mb: 5000            # Size limits

companies:                    # Company definitions
  AAPL:
    name: "Apple Inc."
    sector: "Technology" 
    cik: "0000320193"         # SEC CIK number
    market_cap: "3,403,643,446,500"

data_sources:                 # Which sources to use
  yfinance:
    enabled: true
    periods: ["daily_3mo", "weekly_5y", "monthly_max"]
  sec_edgar:
    enabled: false            # Disabled for large datasets

expected_files:               # Validation expectations
  yfinance: 300              # 100 tickers × 3 periods
  sec_edgar: 0

validation:                   # Quality requirements
  timeout_seconds: 1800
  required_success_rate: 0.95
```

## Maintenance

### Regular Updates
Run the ticker list update script monthly or when index compositions change:
```bash
python ETL/fetch_ticker_lists.py
```

### Adding New Data Sources
1. Create `stage_00_original_newservice.yml` with collection parameters
2. Update ticker list files to enable the new source:
   ```yaml
   data_sources:
     newservice:
       enabled: true
       stage_config: "stage_00_original_newservice.yml"
   ```

### Adding New Ticker Lists
1. Create `list_new_dataset.yml` following the existing format
2. Choose a unique `cli_alias` (e.g., `sp500` → `s5h`)
3. Update the build system to recognize the new alias

## Testing Configuration Architecture

### Development vs PR Testing Strategy

The configuration system supports a **two-tier testing strategy** optimized for development speed and PR quality:

#### 1. Fast Development Testing (`list_fast_2.yml`)
- **Purpose**: Quick feedback during development
- **Companies**: 2 (MSFT, NVDA) - selected for speed and reliability
- **Duration**: ~30 seconds
- **Usage**: `pixi run build fast`
- **Data Sources**: YFinance only (SEC disabled for speed)

#### 2. Complete PR Testing (`list_magnificent_7.yml`)
- **Purpose**: Mandatory validation before PR creation
- **Companies**: 7 (All M7 companies)
- **Duration**: ~5-10 minutes
- **Usage**: `p3 ship` (automatic) or `p3 test m7` (standalone)
- **Data Sources**: YFinance + SEC Edgar (complete validation)

### Test Target Configuration (`stage_00_target_pre_pr.yml`)

This configuration defines the testing strategy for pre-PR validation:

```yaml
test_config:
  ticker_list: "list_fast_2.yml"  # Uses fast 2-company subset
  timeout_seconds: 120            # 2-minute timeout
  enable_sec_edgar: false         # Disabled for speed
  
quality_gates:
  - data_collection: "files_count >= ticker_count"
  - build_completion: "build_status == 'completed'"
  - validation_passed: "validation_passed == true"
```

### PR Workflow Integration

The testing configuration integrates with the automated PR workflow:

1. **Development**: Use `list_fast_2.yml` for rapid iteration
2. **Pre-PR**: Run `p3 test m7` with full M7 validation
3. **PR Creation**: `p3 ship` enforces M7 test success
4. **GitHub Validation**: Checks for `.m7-test-passed` marker file

This ensures **quality without sacrificing development speed**.

## Benefits of This Architecture

1. **Modularity** - Change data sources without affecting ticker lists
2. **Reusability** - Same data source config works for any ticker list
3. **Maintainability** - Clear separation of concerns
4. **Automation** - Official APIs keep ticker lists current
5. **Flexibility** - Easy to add new sources or datasets
6. **Validation** - Built-in quality checks and expectations
7. **Documentation** - Self-documenting through structured metadata
8. **Speed** - Fast development testing with rigorous PR validation
9. **Quality Assurance** - Mandatory M7 testing prevents regressions