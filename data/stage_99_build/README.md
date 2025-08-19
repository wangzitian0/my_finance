# Stage 99 - Build Tracking

This directory contains timestamped build artifacts and comprehensive analysis results.

## Build Structure

### Build Directories
Each build creates a timestamped directory: `build_YYYYMMDD_HHMMSS/`

**Contents of each build:**
- **`BUILD_MANIFEST.json`** - Detailed build metadata and configuration
- **`BUILD_MANIFEST.md`** - Human-readable build summary
- **DCF Reports** - `M7_LLM_DCF_Report_*.md` analysis results
- **SEC Integration** - `sec_integration_examples/`, `sec_recall_examples/`
- **Quality Reports** - Data validation and integrity checks

### Branch-Specific Builds
Feature branches create separate build directories:
- **Main Branch**: `build_YYYYMMDD_HHMMSS/`  
- **Feature Branches**: `../data/stage_99_build_<branch>/build_YYYYMMDD_HHMMSS/`

## Build Tracking

Builds are managed through:
- **Latest Build Symlink**: `common/latest_build` points to most recent
- **Build Tracker**: `common/build_tracker.py` for programmatic access
- **Release Management**: Promoted builds move to `data/release/`

## Build Commands

```bash
# Create new build
p3 create-build

# Check build status
p3 build-status

# View build size
p3 build-size

# Clean old builds
p3 clean-builds

# Release build to production
p3 release-build
```

## Build Lifecycle

1. **Creation**: Timestamped directory with metadata
2. **Population**: Analysis results and artifacts added
3. **Validation**: Quality checks and integrity validation
4. **Release**: Optional promotion to release directory
5. **Cleanup**: Periodic removal of old builds

## Integration

Build artifacts are used by:
- **DCF Analysis**: Latest financial models and valuations
- **Graph RAG**: Semantic search and knowledge base
- **Quality Reporting**: Data integrity and coverage analysis
- **Release Management**: Production deployment artifacts