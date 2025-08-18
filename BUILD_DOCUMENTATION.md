# Build System Documentation

## Dataset Configuration Schema Standardization

### Current Status

All four dataset tiers now have enhanced configuration with data source attribution:

#### F2 (Fast Test - 2 companies)
- ✅ **Source**: References M7, selects MSFT + NVDA for speed
- ✅ **Schema**: Complete with reference_config pattern
- ✅ **SEC Edgar**: Disabled for speed (PR testing)

#### M7 (Magnificent 7 - 7 companies)  
- ✅ **Source**: Manually curated tech giants with full metadata
- ✅ **Schema**: Complete with CIK, sector, industry for all companies
- ✅ **SEC Edgar**: Configured (sec_edgar_m7.yml - needs creation)

#### N100 (NASDAQ-100 - 100 companies)
- ✅ **Source**: NASDAQ-100 index components (documented)
- 🔄 **Schema**: Partially standardized (M7 companies have full metadata) 
- ✅ **SEC Edgar**: Enabled with sec_edgar_nasdaq100.yml (7 M7 CIKs)

#### V3K (VTI - 3485 companies)
- ✅ **Source**: Vanguard Total Stock Market ETF holdings (documented)
- ❌ **Schema**: Basic structure, needs CIK and sector enhancement
- ❌ **SEC Edgar**: Disabled (would require 3485 CIK lookups)

### Schema Requirements

```yaml
# Required for all configurations
dataset_name: string
cli_alias: string  
description: string
tier: number
tracked_in_git: boolean
max_size_mb: number

# Data source documentation (NEW)
data_source_info:
  primary_source: string
  source_url: string (optional)
  last_verified: date
  update_method: string
  selection_criteria: string
  notes: string

# Company metadata (ENHANCED)
companies:
  TICKER:
    name: string
    sector: string           # Required for SEC integration
    industry: string         # Required for SEC integration  
    cik: string             # Required for SEC Edgar ("0000123456" format)
    market_cap_category: string  # "mega", "large", "medium", "small"
```

### SEC Edgar Integration Status

| Dataset | SEC Enabled | CIK Coverage | Config File | Status |
|---------|-------------|--------------|-------------|--------|
| F2      | ❌ Disabled  | N/A (refs M7) | N/A         | ✅ By design |
| M7      | ✅ Enabled   | 7/7 (100%)   | sec_edgar_m7.yml | ❌ Needs creation |
| N100    | ✅ Enabled   | 7/100 (7%)   | sec_edgar_nasdaq100.yml | ✅ Working |
| V3K     | ❌ Disabled  | 0/3485 (0%)  | N/A         | ✅ By design |

### Build Integration Verification

✅ **N100 SEC Edgar Integration Confirmed**:
- SEC data collection successfully triggered
- Downloaded 8 AAPL 10-K filings (20250818)
- Total SEC files: 344 files across data sources
- Build system properly integrates SEC spider
- Comprehensive reporting includes SEC file counts

### Next Steps for Full Schema Compliance

1. **Complete N100 CIK Mapping**: Add CIK numbers for remaining 93 companies
2. **Create M7 SEC Config**: Create `data/config/sec_edgar_m7.yml`
3. **Enhance V3K Metadata**: Add sector/industry for major holdings
4. **Automate Schema Validation**: Fix yaml dependency for validation script

### Data Source Attribution

Each configuration now documents:
- **Where data came from** (NASDAQ official, VTI holdings, manual curation)
- **How to update** (manual verification, automated extraction)
- **Selection criteria** (index components, ETF weights, tech focus)
- **Last verification date** (2025-08-18)

This ensures reproducibility and maintenance of the 4-tier data strategy.