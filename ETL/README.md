# ETL - Data Processing Pipeline

Complete ETL pipeline for web scraping and data processing. From raw data collection to structured data output.

## Component Structure

### Data Collection (Spider)
- `yfinance_spider.py` - Yahoo Finance data spider
- `sec_edgar_spider.py` - SEC Edgar file spider  
- `fetch_ticker_lists.py` - Stock ticker list fetcher

### Data Parsing (Parser)
- `sec_parser.py` - SEC document parser
- `rcts.py` - RCTS format parser

### Data Processing
- `build_dataset.py` - Dataset construction tool
- `migrate_data_structure.py` - Data structure migration
- `check_coverage.py` - Data coverage checker
- `retry_failed.py` - Failed task retry tool
- `update_data_paths.py` - Path update tool

### Data Modeling
- `models.py` - Neo4j data model definitions
- `build_schema.py` - Schema construction tool
- `import_data.py` - Data import tool

## Data Flow

```
Raw Data Sources → Spider Collection → Parser Processing → ETL Pipeline → DTS Output
    ↓                ↓                  ↓                ↓              ↓
  YFinance        Raw Files       Structured Data    Clean Data    Standard API
  SEC Edgar
```

## Usage

```bash
# Data collection
python run_job.py common/config/job_yfinance_m7.yml

# Via pixi commands
p3 build run m7
```

### SEC Edgar Spider (`sec_edgar_spider.py`)
Collects SEC filing data using ticker-based structure.

**Data Structure (Redesigned):**

**Old Problem:**
```
original/sec-edgar/
├── 0000320193/           # CIK number (confusing)
│   ├── 10k/
│   │   └── 0000320193/   # Duplicate CIK structure
│   │       └── 10-K/     # Filing type
│   │           └── *.txt # Filing files
```

**New Structure (Data Source Oriented):**
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

**README.md Format (per ticker):**
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

## Configuration Files

Spiders use YAML configuration files located in `common/config/`:

### M7 Configuration (`job_yfinance_m7.yml`)
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

## CIK to Ticker Mapping

For SEC Edgar spider, the following CIK to ticker mappings are used:

```python
cik_to_ticker = {
    "0000320193": "AAPL",   # Apple Inc.
    "0000789019": "MSFT",   # Microsoft Corporation
    "0001018724": "AMZN",   # Amazon.com Inc.
    "0001652044": "GOOGL",  # Alphabet Inc. (Class A)
    "0001326801": "META",   # Meta Platforms Inc.
    "0001318605": "TSLA",   # Tesla Inc.
    "0001065280": "NFLX"    # Netflix Inc.
}
```

## Migration Benefits

The new ticker-based structure provides:
- **User-Friendly**: Ticker names instead of CIK numbers
- **Consistent**: Same pattern as yfinance data
- **Metadata Rich**: README.md contains all context
- **Warehouse Ready**: Date partitioned for easy ingestion

## Integration

Both spiders integrate with:
- **MetadataManager**: Anti-duplicate downloads
- **BuildTracker**: Comprehensive build tracking
- **ETL Pipeline**: Stage-based data storage
- **Date Partitioning**: YYYYMMDD format for data warehouse compatibility

## Usage Commands

```bash
# Build M7 dataset
p3 build run m7

# Run specific job
python run_job.py <config_file.yml>

# Check build status
p3 build-status

# View latest build
ls data/build/
```

---

*Spiders implement enterprise-grade ETL patterns with comprehensive metadata tracking and anti-duplicate functionality.*