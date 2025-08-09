# Data Directory ETL Structure Design

## ETL Pipeline Stages

```
data/
├── config/                          # Configuration files
├── stage_01_extract/               # Raw data extraction
│   ├── yfinance/                   # Yahoo Finance data source
│   │   ├── <date_partition>/       # Partition by extraction date
│   │   │   └── <ticker>/           # Stock ticker directory
│   │   │       ├── <ticker>_yfinance_<oid>_<timestamp>.json
│   │   │       └── README.md       # Metadata for this ticker
│   │   └── latest -> <date_partition>/  # Symlink to latest partition
│   └── sec_edgar/                  # SEC Edgar data source
│       ├── <date_partition>/       # Partition by extraction date
│       │   └── <ticker>/           # Stock ticker directory
│       │       ├── <ticker>_sec_edgar_<filing_type>_<timestamp>.json
│       │       └── README.md       # Metadata for this ticker
│       └── latest -> <date_partition>/  # Symlink to latest partition
├── stage_02_transform/             # Data transformation results
│   ├── <date_partition>/           # Partition by processing date
│   │   ├── cleaned/                # Cleaned data
│   │   ├── enriched/              # Enriched data
│   │   └── normalized/            # Normalized data
│   └── latest -> <date_partition>/ # Symlink to latest partition
├── stage_03_load/                  # Final processed data
│   ├── <date_partition>/           # Partition by load date
│   │   ├── graph_nodes/           # Neo4j graph data
│   │   ├── embeddings/            # Vector embeddings
│   │   └── dcf_results/           # DCF calculation results
│   └── latest -> <date_partition>/ # Symlink to latest partition
├── reports/                        # Analysis reports
│   ├── <date_partition>/          # Partition by report date
│   │   ├── dcf_analysis/         # DCF analysis reports
│   │   ├── strategy_validation/   # Strategy validation reports
│   │   └── risk_assessment/      # Risk assessment reports
│   └── latest -> <date_partition>/ # Symlink to latest reports
├── logs/                          # ETL processing logs
│   └── <date_partition>/          # Partition by execution date
│       ├── extract/               # Extraction logs
│       ├── transform/             # Transform logs
│       └── load/                  # Load logs
└── build/                         # Build artifacts and documentation
    └── <build_id>/                # Each build gets unique ID
        ├── BUILD_MANIFEST.md      # Build documentation
        ├── stage_logs/           # Logs for this build
        └── artifacts/            # Build artifacts
```

## Date Partitioning Strategy

- **Format**: `YYYYMMDD` (e.g., `20250809`)
- **Granularity**: Daily partitions for all stages
- **Retention**: Configurable per stage (e.g., keep last 30 days for extract, 90 days for reports)
- **Symlinks**: `latest` symlink always points to most recent partition

## Data Warehouse Compatibility

This structure is designed for eventual data warehouse ingestion:

1. **Partition Columns**: `extract_date`, `transform_date`, `load_date`, `report_date`
2. **Table Structure**: Each ETL stage maps to warehouse tables
3. **Metadata**: README.md files contain schema and lineage information
4. **Incremental Loading**: Date partitions enable efficient incremental updates

## Migration from Current Structure

Current `data/original/` → New `data/stage_01_extract/`
Current `data/reports/` → New `data/reports/<date_partition>/`
Current `data/logs/` → New `data/logs/<date_partition>/`