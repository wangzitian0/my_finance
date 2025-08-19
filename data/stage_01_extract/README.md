# Stage 01 - Extract

This directory contains extracted and parsed data from Stage 00 original sources.

## Data Organization

### SEC Edgar (`sec_edgar/`)
Extracted SEC document content organized by:
- **Date Partitions**: `YYYYMMDD/` directories for temporal organization
- **Company Ticker**: `TICKER/` subdirectories (e.g., `AAPL/`, `MSFT/`)
- **Document Files**: `TICKER_sec_edgar_{type}_*.txt` format
- **Latest Data**: `latest/` symlinks to most recent extractions

### Yahoo Finance (`yfinance/`)
Processed financial data by ticker:
- **Date Partitions**: Same structure as SEC data
- **JSON Files**: `TICKER_yfinance_*.json` format
- **Data Types**: Historical prices, fundamentals, company info

## Processing Status

Data in this stage has been:
✅ **Extracted** from original formats
✅ **Parsed** into structured text/JSON
✅ **Validated** for basic integrity
✅ **Partitioned** by date and company

## Next Stage

Data flows to **Stage 02** (`stage_02_transform/`) for:
- Data cleaning and normalization
- Cross-source data enrichment
- Quality validation and filtering

## Access Commands

```bash
# Build latest extraction
p3 build run m7

# Verify extraction integrity
p3 check-data-integrity

# View extraction status
p3 build-status
```