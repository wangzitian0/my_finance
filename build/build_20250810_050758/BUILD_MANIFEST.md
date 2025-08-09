# Build Report: 20250810_050758

## Build Information

- **Build ID**: 20250810_050758
- **Configuration**: m7
- **Command**: `pixi run build-dataset m7`
- **Status**: completed
- **Start Time**: 2025-08-10T05:07:58.261411
- **End Time**: 2025-08-10T05:07:58.265149

## ETL Stages

### stage_01_extract

- **Status**: completed
- **Start Time**: 2025-08-10T05:07:58.264554
- **End Time**: 2025-08-10T05:07:58.264683
- **Artifacts**: 2 files
  - yfinance_data.json
  - sec_edgar_data.txt

### stage_02_transform

- **Status**: completed
- **Start Time**: 2025-08-10T05:07:58.264782
- **End Time**: 2025-08-10T05:07:58.264883
- **Artifacts**: 1 files
  - cleaned_data.json

### stage_03_load

- **Status**: completed
- **Start Time**: 2025-08-10T05:07:58.264976
- **End Time**: 2025-08-10T05:07:58.265062
- **Artifacts**: 2 files
  - graph_nodes.json
  - dcf_results.json

## Data Partitions

- **extract_partition**: `20250810`
- **transform_partition**: `20250810`
- **load_partition**: `20250810`

## Statistics

- **Files Processed**: 0
- **Errors**: 0
- **Warnings**: 0

## File Locations

- **Build Directory**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_050758`
- **Stage Logs**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_050758/stage_logs/`
- **Artifacts**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_050758/artifacts/`

---
*Generated on 2025-08-10T05:07:58.265304*
