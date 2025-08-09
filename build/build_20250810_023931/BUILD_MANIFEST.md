# Build Report: 20250810_023931

## Build Information

- **Build ID**: 20250810_023931
- **Configuration**: m7
- **Command**: `pixi run build-dataset m7`
- **Status**: completed
- **Start Time**: 2025-08-10T02:39:31.145535
- **End Time**: 2025-08-10T02:39:31.503396

## ETL Stages

### stage_01_extract

- **Status**: completed
- **Start Time**: 2025-08-10T02:39:31.146747
- **End Time**: 2025-08-10T02:39:31.502845
- **Artifacts**: 2 files
  - yfinance_data.json
  - sec_edgar_data.txt

### stage_02_transform

- **Status**: completed
- **Start Time**: 2025-08-10T02:39:31.503013
- **End Time**: 2025-08-10T02:39:31.503115
- **Artifacts**: 1 files
  - cleaned_data.json

### stage_03_load

- **Status**: completed
- **Start Time**: 2025-08-10T02:39:31.503209
- **End Time**: 2025-08-10T02:39:31.503301
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

- **Build Directory**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_023931`
- **Stage Logs**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_023931/stage_logs/`
- **Artifacts**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_023931/artifacts/`

---
*Generated on 2025-08-10T02:39:31.503570*
