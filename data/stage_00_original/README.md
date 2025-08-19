# Stage 00 - Original Data

This directory contains raw, unprocessed data from external sources in their original format.

## Data Sources

### SEC Edgar (`sec-edgar/`)
Raw SEC filing documents organized by:
- **CIK Number**: Company identifier (e.g., `0000320193` for Apple)
- **Filing Type**: `10k/`, `10q/`, `8k/` subdirectories
- **Document Structure**: Nested by CIK and filing type

**Total Documents**: 336 SEC filings for Magnificent 7 companies

### Yahoo Finance (`yfinance/`)
Raw financial data by ticker symbol:
- **Historical Price Data**: Daily price and volume information
- **Fundamental Data**: Financial statements, ratios, and company info
- **Market Data**: Real-time and historical market statistics

## Data Integrity

⚠️ **Important**: Files in this directory should be treated as immutable source data.
- Do not modify files directly
- Use ETL pipeline for data processing
- Backup important datasets before major changes

## Processing Pipeline

Data flows from this stage to:
1. **Stage 01** (`stage_01_extract/`) - Parsed and extracted data
2. **Stage 02** (`stage_02_transform/`) - Cleaned and transformed data  
3. **Stage 03** (`stage_03_load/`) - Final processed data ready for analysis

## Access Patterns

Access this data through:
- **ETL Pipeline**: `p3 build run m7` for processing
- **Data Validation**: `p3 verify-sec-data` for integrity checks
- **Direct Access**: Use `common.utils.get_project_paths()` for standardized paths