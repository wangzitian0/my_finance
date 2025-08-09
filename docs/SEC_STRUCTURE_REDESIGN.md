# SEC Edgar Directory Structure Redesign

## Current Problem

```
stage_01_extract/sec_edgar/
├── 0000320193/           # CIK number (confusing)
│   ├── 10k/
│   │   └── 0000320193/   # Duplicate CIK structure
│   │       └── 10-K/     # Filing type
│   │           └── *.txt # Filing files
```

This structure is overly complex and doesn't follow the data source paradigm.

## New Structure (Data Source Oriented)

```
stage_01_extract/sec_edgar/
├── <date_partition>/          # Daily partition (e.g., 20250809)
│   ├── AAPL/                  # Stock ticker (user-friendly)
│   │   ├── AAPL_sec_edgar_10K_<timestamp>.json
│   │   ├── AAPL_sec_edgar_10Q_<timestamp>.json  
│   │   ├── AAPL_sec_edgar_8K_<timestamp>.json
│   │   └── README.md          # Metadata for AAPL
│   ├── MSFT/
│   │   ├── MSFT_sec_edgar_10K_<timestamp>.json
│   │   └── README.md          # Metadata for MSFT
│   └── ...
└── latest -> <date_partition>/ # Symlink to latest
```

## README.md Format (per ticker)

```markdown
# SEC Filings for {TICKER}

## Company Information
- **Ticker**: AAPL
- **Company**: Apple Inc.
- **CIK**: 0000320193
- **Industry**: Technology Hardware Storage & Peripherals

## Available Filings
| Filing Type | File Name | Filing Date | Document URL |
|------------|-----------|-------------|--------------|
| 10-K | AAPL_sec_edgar_10K_250209-120000.json | 2024-11-01 | https://... |
| 10-Q | AAPL_sec_edgar_10Q_250209-120001.json | 2024-10-31 | https://... |

## Data Quality
- Last Updated: 2025-02-09
- Filing Coverage: 2017-2025
- Data Integrity: ✅ Verified
```

## Migration Strategy

1. **Map CIK to Ticker**: Use existing CIK mappings in code
2. **Flatten Structure**: Remove nested CIK directories  
3. **Standardize Naming**: Use consistent filename pattern
4. **Add Metadata**: Generate README.md for each ticker
5. **Date Partition**: Group by extraction date

## Benefits

- **User-Friendly**: Ticker names instead of CIK numbers
- **Consistent**: Same pattern as yfinance data
- **Metadata Rich**: README.md contains all context
- **Warehouse Ready**: Date partitioned for easy ingestion