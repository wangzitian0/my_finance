# Build Report: 20250810_055630

## Build Information

- **Build ID**: 20250810_055630
- **Configuration**: m7
- **Command**: `pixi run build-dataset m7`
- **Status**: completed
- **Start Time**: 2025-08-10T05:56:30.408800
- **End Time**: 2025-08-10T05:56:30.765549

## ETL Stages

### stage_01_extract

- **Status**: completed
- **Start Time**: 2025-08-10T05:56:30.411366
- **End Time**: 2025-08-10T05:56:30.411492
- **Artifacts**: 2 files
  - yfinance_data.json
  - sec_edgar_data.txt

### stage_02_transform

- **Status**: completed
- **Start Time**: 2025-08-10T05:56:30.411598
- **End Time**: 2025-08-10T05:56:30.411695
- **Artifacts**: 1 files
  - cleaned_data.json

### stage_03_load

- **Status**: completed
- **Start Time**: 2025-08-10T05:56:30.411788
- **End Time**: 2025-08-10T05:56:30.411872
- **Artifacts**: 2 files
  - graph_nodes.json
  - dcf_results.json

### stage_04_analysis

- **Status**: completed
- **Start Time**: 2025-08-10T05:56:30.411956
- **End Time**: 2025-08-10T05:56:30.758312
- **Artifacts**: 0 files

### stage_05_reporting

- **Status**: completed
- **Start Time**: 2025-08-10T05:56:30.758456
- **End Time**: 2025-08-10T05:56:30.761387
- **Artifacts**: 1 files
  - dcf_report_path.txt

## Data Partitions

- **extract_partition**: `20250810`
- **transform_partition**: `20250810`
- **load_partition**: `20250810`

## Statistics

- **Files Processed**: 7
- **Errors**: 0
- **Warnings**: 0

## File Locations

- **Build Directory**: `data/build/build_20250810_055630`
- **Stage Logs**: `data/build/build_20250810_055630/stage_logs/`
- **Artifacts**: `data/build/build_20250810_055630/artifacts/`

---
*Generated on 2025-08-10T05:56:30.765855*
