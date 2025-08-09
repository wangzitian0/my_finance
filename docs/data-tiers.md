# Data Tier Strategy

This document describes the three-tier data management system for the my_finance project.

## Overview

The project uses a three-tier approach to manage data sets of increasing size and complexity:

1. **M7** - Git-managed test dataset (7 companies)
2. **NASDAQ100** - Buildable validation dataset (~100 companies)
3. **VTI** - Production target dataset (~4000 companies)

## Tier 1: M7 (Git-Managed Test Dataset)

### Purpose
- Small, stable test dataset for rapid development
- Unit testing and CI/CD validation
- Development environment setup verification

### Characteristics
- **Size**: 7 companies (Magnificent 7)
- **Storage**: Complete records committed to git
- **Update frequency**: Manual, stable
- **Data quality**: High, curated manually

### Configuration
- **File**: `data/config/job_yfinance_m7.yml`
- **Job name**: `m7`
- **Build command**: `pixi run build-m7`

### Companies
- AAPL (Apple Inc.)
- MSFT (Microsoft Corporation)
- GOOGL (Alphabet Inc. Class A)
- AMZN (Amazon.com Inc.)
- NVDA (NVIDIA Corporation)
- META (Meta Platforms Inc.)
- TSLA (Tesla Inc.)

## Tier 2: NASDAQ100 (Buildable + Validated)

### Purpose
- Medium-size dataset for comprehensive testing
- Algorithm validation and integration testing
- Performance benchmarking

### Characteristics
- **Size**: ~100 companies (NASDAQ-100 index)
- **Storage**: Buildable, not committed to git
- **Validation**: Required 95% success rate
- **Data quality**: Automated quality checks

### Configuration
- **File**: `data/config/yfinance_nasdaq100.yml`
- **Job name**: `nasdaq100`
- **Data source**: https://www.nasdaq.com/market-activity/quotes/nasdaq-ndx-index
- **Update frequency**: Regular updates from official source

### Validation Requirements
```yaml
validation:
  required: true
  min_success_rate: 0.95  # 95% of tickers must have data
  data_quality_checks: true
```

## Tier 3: VTI (Production Target)

### Purpose
- Final production dataset covering total US market
- Graph RAG queries and DCF valuations
- Complete market analysis

### Characteristics
- **Size**: ~4000 companies (VTI ETF holdings)
- **Storage**: Buildable, production-grade quality
- **Coverage**: Total US stock market
- **Data quality**: Production requirements

### Configuration
- **File**: `data/config/yfinance_vti.yml`
- **Job name**: `vti`
- **Data source**: https://advisors.vanguard.com/investments/products/vti
- **Update frequency**: Regular updates from official source

### Production Settings
```yaml
production:
  target_dataset: true
  comprehensive_coverage: true
  data_quality_requirements: "high"
```

## Data Periods

Each tier supports different data collection periods:

### M7
- 1 year daily data (1y_1d)
- 5 year weekly data (5y_1wk)
- 3 month daily data (3mo_1d)

### NASDAQ100
- 1 year daily data (1y_1d)
- 7 year weekly data (7y_1wk)
- 30 year monthly data (30y_1mo)

### VTI
- 1 year daily data (1y_1d)
- 10 year weekly data (10y_1wk)
- Maximum monthly data (max_1mo)

## Usage Guidelines

### For Development
- Use **M7** for initial development and testing
- Use **NASDAQ100** for integration testing
- Use **VTI** only for final production validation

### For Data Collection
```bash
# Build M7 test dataset
pixi run build-m7

# Run specific job
python run_job.py data/config/yfinance_nasdaq100.yml

# Run default job
pixi run run-job
```

### For Validation
- M7: Always passes (curated data)
- NASDAQ100: Must pass validation checks
- VTI: Production-grade quality requirements

## Maintenance

### Updating Ticker Lists
Use the automated script to update ticker lists from official sources:

```bash
python scripts/fetch_ticker_lists.py
```

This script updates:
- NASDAQ100 from Nasdaq official website
- VTI holdings from Vanguard official website
- M7 remains manually curated

### Git Management
- **M7 data**: Committed to git for stability
- **NASDAQ100/VTI data**: Never committed to git
- **Configurations**: All configurations committed to git

## Architecture Integration

This tier strategy integrates with:
- **Neo4j database**: All tiers use same schema
- **Graph RAG system**: Optimized for VTI tier
- **DCF engine**: Scales across all tiers
- **Validation system**: Tier-specific requirements