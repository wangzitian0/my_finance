# My Finance Data Repository

ETL Pipeline Data Repository with four-tier dataset strategy and enterprise-grade build tracking.

## Data Tier Strategy

The project uses a four-tier approach to manage data sets of increasing size and complexity:

### Tier 1: TEST - CI/CD Validation Dataset
- **Size**: 1 company (minimal)
- **Purpose**: Fast CI/CD validation
- **Storage**: Temporary, not committed
- **Update frequency**: On-demand

### Tier 2: M7 - Git-Managed Test Dataset  
- **Size**: 7 companies (Magnificent 7)
- **Purpose**: Development and unit testing
- **Storage**: Complete records committed to git
- **Companies**: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA
- **Update frequency**: Manual, stable
- **Build command**: `pixi run build-m7`

### Tier 3: NASDAQ100 - Buildable Validation Dataset
- **Size**: ~100 companies (NASDAQ-100 index)
- **Purpose**: Algorithm validation and integration testing
- **Storage**: Buildable, not committed to git
- **Validation**: Required 95% success rate
- **Build command**: `pixi run build-nasdaq100`

### Tier 4: VTI - Production Target Dataset
- **Size**: ~4000 companies (VTI ETF holdings)
- **Purpose**: Complete market analysis and production queries
- **Storage**: Buildable, production-grade quality
- **Coverage**: Total US stock market
- **Build command**: `pixi run build-vti`

## ETL Directory Structure

```
data/
├── config/                     # Configuration files (4 datasets)
│   ├── test_config.yml        # TEST: Minimal test data for CI
│   ├── job_yfinance_m7.yml    # M7: Git-tracked dataset
│   ├── yfinance_nasdaq100.yml # NASDAQ100: Validation dataset  
│   └── yfinance_vti.yml       # VTI: Full market dataset
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
└── reports/                  # Analysis reports
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

## Build Commands

```bash
# Build different dataset tiers
pixi run build-test          # TEST dataset
pixi run build-m7            # M7 dataset 
pixi run build-nasdaq100     # NASDAQ100 dataset
pixi run build-vti           # VTI dataset

# Check build status
pixi run build-status

# Environment management
pixi run env-status
pixi run env-start
```

## One Codebase, Multiple Configurations

All datasets use the same codebase with different configuration files:
- **Unified build system**: `scripts/build_dataset.py`
- **Configuration-driven**: YAML files in `data/config/`
- **Scalable architecture**: From 1 stock (TEST) to 4000+ stocks (VTI)
- **Consistent patterns**: Same ETL structure across all tiers