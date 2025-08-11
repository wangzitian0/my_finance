# Build Report: 20250811_203211

## Build Information

- **Build ID**: 20250811_203211
- **Configuration**: m7
- **Command**: `pixi run build-dataset m7`
- **Status**: completed
- **Start Time**: 2025-08-11T20:32:11.787364
- **End Time**: 2025-08-11T20:32:12.496252

## ETL Stages

### stage_01_extract

- **Status**: completed
- **Start Time**: 2025-08-11T20:32:11.790116
- **End Time**: 2025-08-11T20:32:11.790248
- **Artifacts**: 2 files
  - yfinance_data.json
  - sec_edgar_data.txt

### stage_02_transform

- **Status**: completed
- **Start Time**: 2025-08-11T20:32:11.790358
- **End Time**: 2025-08-11T20:32:11.790473
- **Artifacts**: 1 files
  - cleaned_data.json

### stage_03_load

- **Status**: completed
- **Start Time**: 2025-08-11T20:32:11.790574
- **End Time**: 2025-08-11T20:32:11.790662
- **Artifacts**: 2 files
  - graph_nodes.json
  - dcf_results.json

### stage_04_analysis

- **Status**: completed
- **Start Time**: 2025-08-11T20:32:11.790748
- **End Time**: 2025-08-11T20:32:12.489665
- **Artifacts**: 0 files

### stage_05_reporting

- **Status**: completed
- **Start Time**: 2025-08-11T20:32:12.489794
- **End Time**: 2025-08-11T20:32:12.492552
- **Artifacts**: 1 files
  - dcf_report_path.txt

## Data Partitions

- **extract_partition**: `20250811`
- **transform_partition**: `20250811`
- **load_partition**: `20250811`

## Statistics

- **Files Processed**: 7
- **Errors**: 0
- **Warnings**: 0

## File Locations

- **Build Directory**: `data/build/build_20250811_203211`
- **Stage Logs**: `data/build/build_20250811_203211/stage_logs/`
- **Artifacts**: `data/build/build_20250811_203211/artifacts/`

---
*Generated on 2025-08-11T20:32:12.496516*
