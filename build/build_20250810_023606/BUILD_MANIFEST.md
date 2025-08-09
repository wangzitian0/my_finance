# Build Report: 20250810_023606

## Build Information

- **Build ID**: 20250810_023606
- **Configuration**: m7
- **Command**: `pixi run build-dataset m7`
- **Status**: completed
- **Start Time**: 2025-08-10T02:36:06.579163
- **End Time**: 2025-08-10T02:36:07.095715

## ETL Stages

### stage_01_extract

- **Status**: completed
- **Start Time**: 2025-08-10T02:36:06.580389
- **End Time**: 2025-08-10T02:36:07.095133
- **Artifacts**: 2 files
  - yfinance_data.json
  - sec_edgar_data.txt

### stage_02_transform

- **Status**: completed
- **Start Time**: 2025-08-10T02:36:07.095307
- **End Time**: 2025-08-10T02:36:07.095419
- **Artifacts**: 1 files
  - cleaned_data.json

### stage_03_load

- **Status**: completed
- **Start Time**: 2025-08-10T02:36:07.095521
- **End Time**: 2025-08-10T02:36:07.095610
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

- **Build Directory**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_023606`
- **Stage Logs**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_023606/stage_logs/`
- **Artifacts**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_023606/artifacts/`

---
*Generated on 2025-08-10T02:36:07.095879*
