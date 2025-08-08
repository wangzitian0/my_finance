# M7 Data Collection Build Guide

## Overview

This guide documents the Magnificent 7 (M7) data collection build process, configuration, and results.

## M7 Companies

The system collects data for the following companies:

- **Apple (AAPL)** - CIK 0000320193
- **Microsoft (MSFT)** - CIK 0000789019  
- **Amazon (AMZN)** - CIK 0001018724
- **Alphabet (GOOGL)** - CIK 0001652044
- **Meta (META)** - CIK 0001326801
- **Tesla (TSLA)** - CIK 0001318605
- **Netflix (NFLX)** - CIK 0001065280

## Configuration Files

### Yahoo Finance Configuration (`job_yfinance_m7.yml`)

```yaml
source: yfinance
job: yfinance_m7
description: Yahoo Finance data for Magnificent 7 companies
tickers:
  - AAPL    # Apple Inc.
  - MSFT    # Microsoft Corporation  
  - AMZN    # Amazon.com Inc.
  - GOOGL   # Alphabet Inc. (Class A)
  - META    # Meta Platforms Inc.
  - TSLA    # Tesla Inc.
  - NFLX    # Netflix Inc.
data_periods:
  - oid: m7_D1
    period: 3y     # 3 years of daily data
    interval: 1d
  - oid: m7_W7
    period: 5y     # 5 years of weekly data  
    interval: 1wk
  - oid: m7_M30
    period: 10y    # 10 years of monthly data
    interval: 1mo
```

### SEC Edgar Configuration (`sec_edgar_m7.yml`)

```yaml
source: sec_edgar
job: sec_edgar_m7
description: SEC Edgar filings for Magnificent 7 companies
email: ZitianSG (wangzitian0@gmail.com)
file_types:
  - 10K     # Annual reports
  - 10Q     # Quarterly reports
  - 8K      # Current reports
tickers:
  - AAPL    # Apple Inc. - CIK 0000320193
  - MSFT    # Microsoft Corporation - CIK 0000789019
  - AMZN    # Amazon.com Inc. - CIK 0001018724
  - GOOGL   # Alphabet Inc. - CIK 0001652044
  - META    # Meta Platforms Inc. - CIK 0001326801
  - TSLA    # Tesla Inc. - CIK 0001318605
  - NFLX    # Netflix Inc. - CIK 0001065280
```

## Build Commands

### Quick Build
```bash
pixi run build-m7
```

### Check Status
```bash
pixi run status
```

### Environment Setup (if needed)
```bash
pixi run env-status
pixi run env-start  # Start services if needed
```

## Build Results

### Latest Build Statistics (2025-08-08)

- **Total companies**: 7
- **SEC filings**: 168 documents
- **YFinance files**: 21 data files
- **Data size**: 1.58 GB
- **Build time**: ~2.8 minutes (169 seconds)

### Data Structure

```
data/original/
├── sec-edgar/
│   ├── AAPL/
│   │   ├── 10k/ (8 annual reports)
│   │   ├── 10q/ (8 quarterly reports)
│   │   └── 8k/ (current reports)
│   ├── MSFT/
│   ├── AMZN/
│   ├── GOOGL/
│   ├── META/
│   ├── TSLA/
│   └── NFLX/
└── yfinance/
    ├── AAPL/
    │   ├── AAPL_yfinance_m7_D1_*.json (daily data)
    │   ├── AAPL_yfinance_m7_W7_*.json (weekly data)
    │   └── AAPL_yfinance_m7_M30_*.json (monthly data)
    └── [similar structure for other companies]
```

## Troubleshooting

### Common Issues

1. **Missing Configuration Files**
   - Ensure `data/config/job_yfinance_m7.yml` exists
   - Ensure `data/config/sec_edgar_m7.yml` exists

2. **Build Timeout**
   - SEC data collection can take time due to rate limits
   - Normal build time is 2-4 minutes

3. **Network Issues**
   - Check internet connection
   - SEC Edgar may have temporary rate limits

4. **Docker/Neo4j Not Required**
   - M7 build works without Docker services running
   - Data is collected and stored locally

### Build Validation

Check successful build:
```bash
# Verify data was collected
pixi run status

# Check build report
ls -la data/build_report_m7_*.json

# Verify file structure
ls -la data/original/yfinance/
ls -la data/original/sec-edgar/
```

## Data Usage

The collected M7 data can be used with:

1. **Graph RAG System** - For intelligent financial Q&A
2. **DCF Valuation Models** - For company valuation analysis
3. **Neo4j Database** - When services are running
4. **Direct File Analysis** - JSON and text files are human-readable

## Performance Notes

- **Initial build**: ~3 minutes for full M7 dataset
- **Incremental updates**: Faster, only new data collected
- **Storage**: ~1.6 GB for complete M7 dataset
- **Memory**: Minimal during collection, more during processing

## Next Steps

After successful M7 build:

1. Start Neo4j services for graph database usage
2. Run Graph RAG setup for intelligent Q&A
3. Execute DCF valuation analysis
4. Build additional datasets (NASDAQ100, US-ALL) as needed

## Configuration Notes

- **Naming Convention**: Files must be named `job_yfinance_m7.yml` (not just `yfinance_m7.yml`)
- **Email Required**: SEC Edgar requires valid email in configuration
- **Rate Limits**: SEC Edgar has built-in rate limiting to comply with API limits
- **Data Periods**: Configurable periods and intervals for different analysis needs