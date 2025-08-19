# Release Management

This directory contains promoted builds and release artifacts for the my_finance system.

## Purpose

Release management for:
- Promoted build artifacts
- Release versioning and tracking
- Production-ready datasets
- Deployment artifact management

## Directory Structure

```
release/
├── release_{YYYYMMDD_HHMMSS}_build_{BUILD_ID}/
│   ├── RELEASE_NOTES.md           # Release documentation
│   ├── BUILD_MANIFEST.json        # Build metadata
│   ├── BUILD_MANIFEST.md          # Human-readable build info
│   ├── M7_LLM_DCF_Report_*.md     # DCF analysis reports
│   ├── sec_integration_examples/  # SEC integration examples
│   └── data/                      # Release datasets
└── latest -> release_*/           # Symlink to latest release
```

## Release Process

### Automatic Promotion
Builds can be promoted to releases during PR creation:
1. Successful M7 end-to-end testing
2. User confirmation during PR workflow
3. Automatic release directory creation
4. Release notes generation
5. Git commit of release artifacts

### Manual Promotion
```bash
# Promote specific build to release
python scripts/manage_build_data.py release --build-id {BUILD_ID}

# Create release from latest build
p3 release-build
```

## Release Versioning

### Timestamp-Based Versioning
- **Format**: `release_{YYYYMMDD_HHMMSS}_build_{BUILD_ID}`
- **Example**: `release_20250119_143022_build_20250119_140515`
- **Benefits**: Chronological ordering, clear build traceability

### Release Metadata
Each release includes:
- Build ID and timestamp
- Source branch and commit hash
- Test validation results
- Data quality metrics
- Release notes and change summary

## Release Content

### Core Artifacts
- **Build Manifests**: Complete build metadata and tracking
- **DCF Reports**: SEC-enhanced analysis reports
- **Dataset Snapshots**: Validated and tested datasets
- **Quality Reports**: Data quality assessment results

### Documentation
- **Release Notes**: Changes and improvements summary
- **Build Documentation**: Technical build information
- **Usage Guidelines**: How to use release artifacts
- **Validation Results**: Test and quality validation outcomes

## Usage

### For Development
- Reference stable datasets for testing
- Compare current development against stable releases
- Validate changes against known-good baselines

### For Deployment
- Deploy validated and tested artifacts
- Use release artifacts for production systems
- Maintain version history for rollback capability

### For Analysis
- Access stable, validated datasets for research
- Use consistent data versions across analysis projects
- Reference historical data states for longitudinal studies

## Release Lifecycle

### Creation
1. Build passes all validation tests
2. Quality metrics meet release criteria
3. User approves promotion during PR process
4. Release artifacts are created and committed

### Maintenance
- Regular cleanup of old releases
- Archive strategy for long-term storage
- Version compatibility tracking
- Security updates for historical releases

### Retention Policy
- **Recent Releases**: Keep all releases from last 3 months
- **Monthly Snapshots**: Keep one release per month for 1 year
- **Quarterly Archives**: Long-term storage for compliance
- **Cleanup**: Automated cleanup of old releases

## Integration

Releases integrate with:
- PR creation and testing workflows
- Deployment automation systems
- Data analysis and research workflows
- Quality assurance and validation processes

## Best Practices

1. **Regular Releases**: Promote builds regularly to maintain fresh releases
2. **Quality Gates**: Only promote builds that pass all quality checks
3. **Documentation**: Maintain comprehensive release notes
4. **Cleanup**: Regularly clean up old releases to manage disk usage
5. **Traceability**: Maintain clear links between releases and source builds