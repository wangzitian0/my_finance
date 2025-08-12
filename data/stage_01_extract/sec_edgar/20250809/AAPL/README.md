# SEC Filings for AAPL

## Company Information
- **Ticker**: AAPL
- **Company**: Apple Inc.  
- **CIK**: 0000320193
- **Industry**: Technology Hardware Storage & Peripherals
- **Sector**: Technology

## Available Filings

| Filing Type | File Name | Filing Date | Accession Number | Size | Status |
|------------|-----------|-------------|------------------|------|--------|
| 10-K | AAPL_sec_edgar_10K_20240101_120000.json | 2024-01-01 | 0000320193-24-000123 | 2.1MB | ✅ Parsed |
| 10-Q | AAPL_sec_edgar_10Q_20240331_120000.json | 2024-03-31 | 0000320193-24-000081 | 1.8MB | ✅ Parsed |
| 8-K  | AAPL_sec_edgar_8K_20240315_120000.json  | 2024-03-15 | 0000320193-24-000080 | 0.5MB | ✅ Parsed |

## Data Quality Metrics
- **Last Updated**: 2025-02-09 14:30:22 UTC
- **Filing Coverage**: 2017-2025 (8 years)
- **Total Filings**: 45 files
- **Data Integrity**: ✅ Verified
- **Parsing Success Rate**: 98.7%

## Processing Pipeline
- **Extraction**: SEC Edgar API → Raw JSON
- **Parsing**: BeautifulSoup → Structured data
- **Validation**: Schema check → Quality score
- **Storage**: ETL stage_01_extract partition

## Schema Information
```json
{
  "ticker": "AAPL",
  "filing_type": "10-K",
  "filing_date": "2024-01-01",
  "cik": "0000320193",
  "accession_number": "0000320193-24-000123",
  "document_url": "https://...",
  "sections": {
    "business_overview": "...",
    "risk_factors": "...",
    "financial_statements": "...",
    "md_and_a": "..."
  },
  "processed_at": "2025-02-09T14:30:22Z",
  "parsing_success": true
}
```

## Related Data Sources
- **YFinance**: `../../../yfinance/20250809/AAPL/`
- **Graph Database**: Stock node with SEC relationships
- **Vector Embeddings**: Business overview, risk factors
- **Reports**: DCF analysis incorporates SEC fundamentals