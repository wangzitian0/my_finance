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
│   ├── list_fast_2.yml        # F2: Fast testing dataset (2 companies)
│   ├── list_magnificent_7.yml # M7: Git-tracked dataset (7 companies)
│   ├── list_nasdaq_100.yml    # NASDAQ100: Validation dataset  
│   ├── list_vti_3500.yml      # VTI: Full market dataset
│   ├── source_yfinance.yml    # YFinance data source config
│   └── source_sec_edgar.yml   # SEC Edgar data source config
├── stage_00_original/         # Original data storage
│   ├── yfinance/              # YFinance raw data
│   │   └── <TICKER>/          # Stock ticker
│   │       ├── <TICKER>_yfinance_m7_daily_<timestamp>.json
│   │       ├── <TICKER>_yfinance_m7_monthly_<timestamp>.json
│   │       └── <TICKER>_yfinance_m7_quarterly_<timestamp>.json
│   └── sec-edgar/             # SEC Edgar raw data (organized by CIK)
│       └── <CIK>/             # SEC Central Index Key
│           ├── 10k/           # Annual reports
│           ├── 10q/           # Quarterly reports
│           └── 8k/            # Current reports
├── stage_01_extract/          # Extracted and processed data
│   ├── yfinance/
│   │   ├── <YYYYMMDD>/        # Daily partition
│   │   │   └── <TICKER>/      # Stock ticker
│   │   │       ├── <TICKER>_yfinance_<period>_<timestamp>.json
│   │   │       └── README.md  # Metadata
│   │   └── latest -> <YYYYMMDD>/
│   └── sec_edgar/
│       ├── <YYYYMMDD>/        # Daily partition  
│       │   └── <TICKER>/      # Stock ticker (not CIK)
│       │       ├── <TICKER>_sec_edgar_<filing_type>_<timestamp>.txt
│       │       └── README.md  # Metadata
│       └── latest -> <YYYYMMDD>/
├── stage_02_transform/        # Data transformation (future expansion)
│   ├── <YYYYMMDD>/           # Processing date partition
│   │   ├── cleaned/          # Cleaned data
│   │   ├── enriched/         # Enriched data
│   │   └── normalized/       # Normalized data
│   └── latest -> <YYYYMMDD>/
├── stage_03_load/            # Final processed data and analysis results
│   ├── <YYYYMMDD>/          # Load date partition
│   │   ├── graph_nodes/     # Neo4j graph nodes
│   │   ├── embeddings/      # Vector embeddings for semantic search
│   │   ├── dcf_results/     # DCF calculation results
│   │   └── graph_rag_cache/ # Graph RAG cached results
│   └── latest -> <YYYYMMDD>/
├── stage_99_build/           # Build execution tracking
│   ├── build_<YYYYMMDD_HHMMSS>/  # Each build execution
│   │   ├── BUILD_MANIFEST.json   # Machine-readable build info
│   │   ├── BUILD_MANIFEST.md     # Human-readable build documentation
│   │   ├── M7_LLM_DCF_Report_<timestamp>.md  # M7 DCF analysis report
│   │   ├── DCF_Report_<timestamp>.md         # General DCF report
│   │   ├── stage_logs/          # ETL stage execution logs
│   │   └── artifacts/           # Build artifacts and metadata
│   └── latest -> build_<YYYYMMDD_HHMMSS>/  # Symlink to latest build
├── release/                  # Released builds for production use
│   └── release_<YYYYMMDD_HHMMSS>_build_<ID>/
│       ├── RELEASE_NOTES.md  # Release documentation
│       └── [copied build contents]
├── llm/                      # LLM-related data and configs
│   ├── configs/              # LLM configuration files
│   ├── semantic_results/     # Semantic search results
│   ├── templates/            # LLM prompt templates
│   └── thinking_process/     # LLM reasoning logs
└── log/                      # Application logs
    ├── yfinance/            # YFinance data collection logs
    ├── sec_edgar/           # SEC Edgar data collection logs
    └── [various log files]
```

## Data Warehouse Design

- **Partitioning**: Daily partitions (`YYYYMMDD`) for all stages
- **Table Mapping**: Each ETL stage maps to DW tables  
- **Incremental Loading**: Date-based incremental updates
- **Metadata**: README.md files contain schema and lineage
- **Retention**: Configurable per stage (30/90/365 days)

## File Naming Convention

### Data Files
```
<TICKER>_<source>_<oid/filing_type>_<timestamp>.json

Examples:
AAPL_yfinance_m7_daily_250809-143022.json
AAPL_sec_edgar_10k_250809-143023.txt
```

### Report Files  
```
M7_LLM_DCF_Report_<YYYYMMDD_HHMMSS>.md    # M7 DCF analysis (markdown format)
DCF_Report_<YYYYMMDD_HHMMSS>.md           # General DCF reports (markdown format)
BUILD_MANIFEST.md                         # Build documentation (markdown format)
RELEASE_NOTES.md                          # Release documentation (markdown format)
```

## Build Commands

**Simplified Command System**: `pixi run <command> [scope]` (defaults to `m7`)

### Core Commands
```bash
# Build datasets
pixi run build f2            # F2 dataset (fast testing, 2 companies)
pixi run build               # M7 dataset (standard, 7 companies, default)
pixi run build m7            # M7 dataset (explicit)
pixi run build n100          # NASDAQ100 dataset (validation, ~100 companies)  
pixi run build v3k           # VTI dataset (production, 3500+ companies)

# End-to-end testing
pixi run e2e f2              # Fast F2 end-to-end test (~1-2 minutes)
pixi run e2e                 # Standard M7 end-to-end test (~5-10 minutes, default)
pixi run e2e n100            # Extended NASDAQ100 testing
pixi run e2e v3k             # Full VTI production testing
```

### Environment & Management
```bash
# Environment management
pixi run env-status          # Check all services
pixi run env-start           # Start all services (Podman + Neo4j)
pixi run env-stop            # Stop all services
pixi run env-reset           # Reset everything (destructive)

# Build management
pixi run create-build        # Create new timestamped build
pixi run release-build       # Promote build to release

# Status & utilities
pixi run status              # Check data and build status
pixi run run-job             # Run default data collection
```

## One Codebase, Multiple Configurations

All datasets use the same codebase with different configuration files:
- **Unified build system**: `scripts/build_dataset.py`
- **Configuration-driven**: YAML files in `data/config/`
- **Scalable architecture**: From 1 stock (TEST) to 4000+ stocks (VTI)
- **Consistent patterns**: Same ETL structure across all tiers