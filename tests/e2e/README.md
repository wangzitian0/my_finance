# End-to-End Testing

This directory contains end-to-end testing infrastructure for the my_finance system.

## Purpose

End-to-end testing for:
- Complete data pipeline validation
- Build system functionality
- Cross-component integration
- Production-ready system verification

## Test Levels

### F2 Testing (Fast Development)
- **Scope**: 2 companies (MSFT, NVDA)
- **Purpose**: Fast development testing
- **Duration**: ~1-2 minutes
- **Usage**: `p3 e2e f2` or `p3 e2e test`

### M7 Testing (Standard)
- **Scope**: Magnificent 7 companies
- **Purpose**: Standard PR validation
- **Duration**: ~5-10 minutes  
- **Usage**: `p3 e2e` or `p3 e2e m7`
- **Required**: Before all PR creation

### N100 Testing (Validation)
- **Scope**: NASDAQ 100 companies
- **Purpose**: Extended validation testing
- **Duration**: ~30-60 minutes
- **Usage**: `p3 e2e n100`

### V3K Testing (Production)
- **Scope**: VTI 3500+ companies  
- **Purpose**: Production-scale validation
- **Duration**: Several hours
- **Usage**: `p3 e2e v3k`

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

```bash
# Standard M7 end-to-end test (required for PRs)
p3 e2e

# Fast development testing
p3 e2e f2

# Extended validation testing  
p3 e2e n100

# Production-scale testing
p3 e2e v3k
```

## Test Artifacts

Tests generate artifacts in:
- `data/stage_99_build/build_YYYYMMDD_HHMMSS/` - Build results
- `data/log/` - Test execution logs
- `data/quality_reports/` - Quality assessment reports

## CI Integration

End-to-end tests are integrated with:
- PR creation workflows (`p3 create-pr`)
- GitHub Actions validation
- Build system validation
- Release promotion workflows

## Best Practices

1. **Always run M7 tests** before creating PRs
2. **Use F2 for rapid development** iteration
3. **Run N100 for major changes** validation
4. **Reserve V3K for release validation**
5. **Monitor test artifacts** for quality issues