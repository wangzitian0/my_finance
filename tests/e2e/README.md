# End-to-End Tests

This directory contains end-to-end tests that validate complete user workflows and system integration.

## Purpose

End-to-end testing for the my_finance system covering:
- Complete data processing pipelines
- Multi-module integration scenarios
- User workflow validation
- System-level functionality testing

## Test Structure

- `test_module_integration.py` - Cross-module integration tests
- `test_user_cases.py` - Complete user workflow validation

## Key Test Scenarios

1. **Data Pipeline Integration**
   - YFinance data collection → ETL processing → Neo4j storage
   - SEC filing retrieval → Semantic processing → Graph storage
   - Multi-source data integration and consistency

2. **DCF Engine Workflows**
   - Data retrieval → DCF calculation → Report generation
   - Graph RAG query processing → LLM integration
   - Multi-model DCF analysis workflows

3. **Build System Validation**
   - Complete dataset building (F2/M7/N100/V3K scopes)
   - Build artifact generation and tracking
   - Data quality validation across tiers

## Running E2E Tests

Use the unified testing commands:

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run specific E2E test files
pytest tests/e2e/test_user_cases.py -v
pytest tests/e2e/test_module_integration.py -v

# Run with the p3 wrapper
p3 test                    # Includes E2E tests
```

## Test Environment

E2E tests require:
- Complete pixi environment setup
- Neo4j database running (via `p3 env start`)
- Network access for data collection
- Sufficient disk space for test datasets

## Architecture

- **Integration Focus**: Tests cross-module interactions
- **Real Data**: Uses actual APIs and datasets where possible
- **Build Validation**: Validates complete build processes
- **System Health**: Checks end-to-end system functionality

## Notes

- E2E tests are included in the standard `p3 test` workflow
- Tests may take longer due to real data processing
- Some tests require network connectivity
- Build artifacts are preserved for debugging when tests fail