# Build Report: 20250818_162550

## Build Information

- **Build ID**: 20250818_162550
- **Configuration**: f2
- **Command**: `pixi run build-dataset f2`
- **Status**: completed
- **Start Time**: 2025-08-18T16:25:50.832480
- **End Time**: 2025-08-18T16:25:50.859891

## ETL Stages

### stage_01_extract

- **Status**: completed
- **Start Time**: 2025-08-18T16:25:50.834357
- **End Time**: 2025-08-18T16:25:50.834512
- **Artifacts**: 2 files
  - yfinance_data.json
  - sec_edgar_data.txt

### stage_02_transform

- **Status**: completed
- **Start Time**: 2025-08-18T16:25:50.834633
- **End Time**: 2025-08-18T16:25:50.834746
- **Artifacts**: 1 files
  - cleaned_data.json

### stage_03_load

- **Status**: completed
- **Start Time**: 2025-08-18T16:25:50.834866
- **End Time**: 2025-08-18T16:25:50.834972
- **Artifacts**: 2 files
  - graph_nodes.json
  - dcf_results.json

### stage_04_analysis

- **Status**: completed
- **Start Time**: 2025-08-18T16:25:50.835088
- **End Time**: 2025-08-18T16:25:50.858594
- **Artifacts**: 0 files

### stage_05_reporting

- **Status**: completed
- **Start Time**: 2025-08-18T16:25:50.858759
- **End Time**: 2025-08-18T16:25:50.859609
- **Artifacts**: 0 files

## Data Partitions

- **extract_partition**: `20250818`
- **transform_partition**: `20250818`
- **load_partition**: `20250818`

## Statistics

- **Files Processed**: 0
- **Errors**: 0
- **Warnings**: 0

## File Locations

- **Build Directory**: `data/stage_99_build/build_20250818_162550`
- **Stage Logs**: `data/stage_99_build/build_20250818_162550/stage_logs/`
- **Artifacts**: `data/stage_99_build/build_20250818_162550/artifacts/`

## 📋 SEC DCF Integration Process

This build includes comprehensive documentation of how SEC filings are integrated into DCF analysis:

- **Documentation**: [`SEC_DCF_Integration_Process.md`](./SEC_DCF_Integration_Process.md)
- **Process Overview**: Detailed explanation of the ETL pipeline and semantic retrieval system
- **Build Integration**: Shows how SEC data flows through the system into final DCF reports

---
*Generated on 2025-08-18T16:25:50.860313*
