# End-to-End Testing

This directory contains end-to-end testing infrastructure for the my_finance system.

## Purpose

End-to-end testing for:
- Complete data pipeline validation
- Build system functionality
- Cross-component integration
- Production-ready system verification

## Test Levels

**P3 Test Commands**: See [README.md](../../README.md) for complete P3 test commands and [CLAUDE.md](../../CLAUDE.md) for workflow guidance.

### Test Scopes
- **F2**: 2 companies, ~1-2 minutes (development)
- **M7**: 7 companies, ~5-10 minutes (PR validation, required)  
- **N100**: 100 companies, ~30-60 minutes (validation)
- **V3K**: 3500+ companies, several hours (production)

## Test Framework

### Infrastructure Tests
- Environment setup validation
- Service availability checks
- Configuration validation
- Dependency verification

### Data Pipeline Tests  
- ETL stage validation
- Data quality checks
- Build artifact verification
- Output format validation

### Integration Tests
- Cross-module functionality
- API integration validation
- Database connectivity
- Graph RAG system validation

## Test Commands

**P3 Test Commands**: See [README.md](../../README.md) for complete command usage.

## Test Artifacts

Tests generate artifacts in:
- `data/stage_99_build/build_YYYYMMDD_HHMMSS/` - Build results
- `data/log/` - Test execution logs
- `data/quality_reports/` - Quality assessment reports

## CI Integration

End-to-end tests are integrated with:
- PR creation workflows (see [README.md](../../README.md) for P3 commands)
- GitHub Actions validation
- Build system validation
- Release promotion workflows

## Best Practices

1. **Always run M7 tests** before creating PRs
2. **Use F2 for rapid development** iteration
3. **Run N100 for major changes** validation
4. **Reserve V3K for release validation**
5. **Monitor test artifacts** for quality issues