# Dataset Configuration Schema

All dataset configuration files should follow this standardized schema for consistency.

## Required Fields

```yaml
dataset_name: string           # Internal dataset name
cli_alias: string             # CLI command alias (f2, m7, n100, v3k)
description: string           # Human-readable description
tier: number                  # Data tier (1=test, 2=m7, 3=n100, 4=v3k)
tracked_in_git: boolean       # Whether data is tracked in git
max_size_mb: number          # Maximum expected dataset size

# Data Sources Configuration
data_sources:
  yfinance:
    enabled: boolean
    stage_config: string      # Reference to stage config file
  sec_edgar:
    enabled: boolean
    stage_config: string      # Reference to stage config file

# Expected file counts for validation
expected_files:
  yfinance: number
  sec_edgar: number

# Validation settings
validation:
  timeout_seconds: number
  required_success_rate: number  # 0.0 to 1.0

# Company definitions
companies:
  TICKER:
    name: string              # Full company name
    sector: string            # Business sector (optional but recommended)
    industry: string          # Specific industry (optional but recommended)  
    cik: string              # SEC CIK number (for SEC integration, format: "0000123456")
    market_cap_category: string  # "mega", "large", "medium", "small" (optional)
    source: string           # Data source reference (optional)
    weight: string           # Portfolio weight if applicable (optional)

ticker_count: number          # Total number of tickers
last_updated: string         # ISO timestamp of last update
```

## Data Source Documentation

Each configuration must include:

1. **Source Attribution**: Where the ticker list came from
2. **Update Process**: How to refresh the data
3. **Selection Criteria**: Why these tickers were chosen
4. **CIK Mapping**: For SEC-enabled datasets

## Example Reference Patterns

- **F2**: References M7, selects subset for speed
- **M7**: Manually curated tech companies with full metadata
- **N100**: NASDAQ-100 index components (need source documentation)  
- **V3K**: VTI ETF holdings (need source documentation)