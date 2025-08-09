# Build Report: 20250810_052335

## Build Information

- **Build ID**: 20250810_052335
- **Configuration**: m7
- **Command**: `pixi run build-dataset m7`
- **Status**: completed
- **Start Time**: 2025-08-10T05:23:35.168648
- **End Time**: 2025-08-10T05:23:35.171800

## ETL Stages

### stage_01_extract

- **Status**: completed
- **Start Time**: 2025-08-10T05:23:35.171220
- **End Time**: 2025-08-10T05:23:35.171353
- **Artifacts**: 2 files
  - yfinance_data.json
  - sec_edgar_data.txt

### stage_02_transform

- **Status**: completed
- **Start Time**: 2025-08-10T05:23:35.171447
- **End Time**: 2025-08-10T05:23:35.171535
- **Artifacts**: 1 files
  - cleaned_data.json

### stage_03_load

- **Status**: completed
- **Start Time**: 2025-08-10T05:23:35.171619
- **End Time**: 2025-08-10T05:23:35.171724
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

- **Build Directory**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_052335`
- **Stage Logs**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_052335/stage_logs/`
- **Artifacts**: `/Users/SP14016/zitian/my_finance/data/build/build_20250810_052335/artifacts/`

---
*Generated on 2025-08-10T05:23:35.171945*
