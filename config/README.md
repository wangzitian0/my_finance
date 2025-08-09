# Configuration Architecture

This directory contains the modular configuration system for the My Finance DCF Analysis Tool. The architecture follows the principle of **separation of concerns** with complete decoupling between data sources and ticker lists.

## Architecture Overview

The configuration system is organized into two distinct categories:

### 1. Data Source Configurations (`source_*.yml`)
These files define **how** to collect data from different sources, independent of **which** companies to collect data for.

- `source_yfinance.yml` - Yahoo Finance data collection parameters
- `source_sec_edgar.yml` - SEC Edgar filings collection parameters

### 2. Ticker List Configurations (`list_*.yml`)  
These files define **which** companies to process, with their CLI aliases and metadata.

- `list_magnificent_7.yml` - Magnificent 7 tech companies (CLI: `m7`)
- `list_nasdaq_100.yml` - NASDAQ-100 index companies (CLI: `n100`) 
- `list_vti_3500.yml` - VTI ETF holdings (~3500 companies) (CLI: `v3k`)

## Usage

### Command Line Interface
```bash
# Build datasets using CLI aliases
pixi run build m7        # Magnificent 7 
pixi run build n100      # NASDAQ-100
pixi run build v3k       # VTI 3500

# Full names also work
pixi run build magnificent_7
pixi run build nasdaq_100  
pixi run build vti_3500
```

### Configuration Combination
The build system automatically combines:
- Ticker list configuration (defines WHICH companies)
- Data source configurations (defines HOW to collect data)

For example, `pixi run build n100` will:
1. Load `list_nasdaq_100.yml` to get 100 NASDAQ companies
2. Load `source_yfinance.yml` for Yahoo Finance collection settings
3. Load `source_sec_edgar.yml` for SEC filing settings (if enabled)
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

### Data Source Files (`source_*.yml`)
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
1. Create `source_newservice.yml` with collection parameters
2. Update ticker list files to enable the new source:
   ```yaml
   data_sources:
     newservice:
       enabled: true
       parameters: ["param1", "param2"]
   ```

### Adding New Ticker Lists
1. Create `list_new_dataset.yml` following the existing format
2. Choose a unique `cli_alias` (e.g., `sp500` → `s5h`)
3. Update the build system to recognize the new alias

## Benefits of This Architecture

1. **Modularity** - Change data sources without affecting ticker lists
2. **Reusability** - Same data source config works for any ticker list
3. **Maintainability** - Clear separation of concerns
4. **Automation** - Official APIs keep ticker lists current
5. **Flexibility** - Easy to add new sources or datasets
6. **Validation** - Built-in quality checks and expectations
7. **Documentation** - Self-documenting through structured metadata