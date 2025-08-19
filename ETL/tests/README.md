# ETL Tests

This directory contains test suites for the ETL data processing pipeline.

## Test Structure

### Integration Tests (`integration/`)
- **`test_yfinance.py`** - Yahoo Finance data integration tests
- **`init_schema.py`** - Schema initialization for test environment
- **`init_db.py`** - Database setup for integration testing
- **`fetch_*.py`** - Various data fetching test scenarios
- **`common.py`** - Shared test utilities and fixtures

### Test Configuration
- **`test_config.py`** - Configuration validation tests
- **`test_data_structure.py`** - Data structure integrity tests

### Fixtures (`fixtures/`)
- Sample data and mock responses for testing
- Test configuration files and schemas

## Running Tests

```bash
# Run all ETL tests
p3 test

# Run specific integration tests
p3 test-yfinance
p3 test-config

# Run data structure tests
python -m pytest ETL/tests/test_data_structure.py -v
```

## Test Data

Tests use isolated test environments and mock data to avoid affecting production data sources. Integration tests validate:

- Data source connectivity (Yahoo Finance, SEC Edgar)
- Data parsing and transformation accuracy
- Schema compliance and data integrity
- Error handling and retry mechanisms

## Adding New Tests

When adding new ETL functionality:
1. Create corresponding tests in appropriate subdirectory
2. Use fixtures for consistent test data
3. Mock external API calls to avoid rate limiting
4. Validate data quality and schema compliance