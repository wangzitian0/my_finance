# Build Execution Tracking

This directory tracks each ETL pipeline execution with comprehensive documentation.

## Structure

```
build/
├── build_YYYYMMDD_HHMMSS/     # Unique build ID
│   ├── BUILD_MANIFEST.md      # Complete build documentation
│   ├── stage_logs/           # ETL stage execution logs
│   │   ├── extract/
│   │   ├── transform/
│   │   └── load/
│   └── artifacts/            # Build artifacts and metrics
│       ├── data_quality.json
│       ├── pipeline_metrics.json
│       └── validation_results.json
└── latest -> build_YYYYMMDD_HHMMSS/  # Always points to most recent
```

## Build ID Format

- **Format**: `build_YYYYMMDD_HHMMSS`
- **Example**: `build_20250809_143022`
- **Timezone**: UTC for consistency
- **Uniqueness**: Guaranteed per-second uniqueness

## BUILD_MANIFEST.md Contents

Each build manifest documents:

1. **Build Configuration**
   - Dataset configuration used
   - Pipeline parameters
   - Environment settings

2. **ETL Stage Details**
   - Stage execution order and timing
   - Data partitions created/updated
   - Input/output data volumes

3. **Quality Metrics**
   - Data validation results
   - Quality scores and thresholds
   - Error rates and resolution

4. **Artifacts Location**
   - Log file locations
   - Data partition references
   - Report output locations