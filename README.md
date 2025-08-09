# my_finance_data

ETL Pipeline Data Repository - Issue tracking at https://github.com/wangzitian0/my_finance

## ETL Directory Structure

```
data/
├── config/                     # Configuration files (4 datasets)
│   ├── test_config.yml        # Minimal test data for CI
│   ├── job_yfinance_m7.yml    # M7 dataset (git-tracked)
│   ├── yfinance_nasdaq100.yml # NASDAQ100 dataset  
│   └── yfinance_vti.yml       # VTI full market dataset
├── stage_01_extract/          # Raw data extraction
│   ├── yfinance/
│   │   ├── <YYYYMMDD>/        # Daily partition
│   │   │   └── <TICKER>/      # Stock ticker
│   │   │       ├── <TICKER>_yfinance_<oid>_<timestamp>.json
│   │   │       └── README.md  # Metadata
│   │   └── latest -> <YYYYMMDD>/
│   └── sec_edgar/
│       ├── <YYYYMMDD>/        # Daily partition  
│       │   └── <TICKER>/      # Stock ticker (not CIK)
│       │       ├── <TICKER>_sec_edgar_<filing_type>_<timestamp>.json
│       │       └── README.md  # Metadata
│       └── latest -> <YYYYMMDD>/
├── stage_02_transform/        # Data transformation
│   ├── <YYYYMMDD>/           # Processing date partition
│   │   ├── cleaned/          # Cleaned data
│   │   ├── enriched/         # Enriched data
│   │   └── normalized/       # Normalized data
│   └── latest -> <YYYYMMDD>/
├── stage_03_load/            # Final processed data
│   ├── <YYYYMMDD>/          # Load date partition
│   │   ├── graph_nodes/     # Neo4j nodes
│   │   ├── embeddings/      # Vector embeddings
│   │   └── dcf_results/     # DCF calculations
│   └── latest -> <YYYYMMDD>/
├── build/                    # Build execution tracking
│   ├── build_<YYYYMMDD_HHMMSS>/  # Each build execution
│   │   ├── BUILD_MANIFEST.md     # Build documentation
│   │   ├── stage_logs/          # ETL stage logs
│   │   └── artifacts/           # Build artifacts
│   └── latest -> build_<YYYYMMDD_HHMMSS>/
└── reports/                  # Analysis reports (legacy - to be moved)
    └── <YYYYMMDD>/          # Report date partition
        ├── dcf_analysis/    # DCF reports
        └── strategy_validation/
```

## Data Warehouse Design

- **Partitioning**: Daily partitions (`YYYYMMDD`) for all stages
- **Table Mapping**: Each ETL stage maps to DW tables  
- **Incremental Loading**: Date-based incremental updates
- **Metadata**: README.md files contain schema and lineage
- **Retention**: Configurable per stage (30/90/365 days)

## File Naming Convention

```
<TICKER>_<source>_<oid/filing_type>_<timestamp>.json

Examples:
AAPL_yfinance_1y_1d_250809-143022.json
AAPL_sec_edgar_10K_250809-143023.json
```

## Migration Plan

1. **Backup Current Data**: Archive existing `original/` and `reports/`
2. **Create New Structure**: Build stage-based directories  
3. **Migrate Data**: Move files to appropriate partitions
4. **Update Code**: Modify spiders and processors for new structure
5. **Validate**: Run test suite to ensure compatibility

## One Codebase, Multiple Configurations

The system supports 4 dataset configurations:
- **test**: Single stock for CI/CD (fast)
- **m7**: 7 stocks for development (git-tracked)  
- **nasdaq100**: 100+ stocks for analysis
- **vti**: Full market for production