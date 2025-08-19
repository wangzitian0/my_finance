# Test Data

This directory contains test datasets and fixtures for unit testing and integration testing.

## Purpose

Test data management for:
- Unit test fixtures and mock data
- Integration test datasets
- Performance testing data
- Regression testing baselines

## Directory Structure

```
test/
├── fixtures/              # Static test fixtures
├── mock_data/             # Generated mock datasets
├── integration/           # Integration test datasets
├── baselines/            # Regression test baselines
└── performance/          # Performance test data
```

## Test Data Types

### Mock Financial Data
- **Stock Prices**: Sample historical price data
- **Company Info**: Mock company information and metadata  
- **SEC Filings**: Sample SEC document excerpts
- **Financial Metrics**: Test financial calculation inputs

### Test Fixtures
- **Configuration Files**: Test-specific config variations
- **API Responses**: Cached API response samples
- **Database States**: Known database states for testing
- **Expected Outputs**: Golden standard outputs for validation

## Usage

### Unit Testing
```python
# Load test fixtures
from tests.fixtures import load_test_data
test_data = load_test_data('sample_stock_data.json')

# Use mock data generators
from common.test_utils import generate_mock_prices
mock_prices = generate_mock_prices('AAPL', days=30)
```

### Integration Testing
- Small, controlled datasets for end-to-end testing
- Predictable data for deterministic test results
- Cross-module integration validation datasets
- API interaction test data and responses

## Data Generation

### Automated Generation
- Mock data generators for various financial instruments
- Synthetic time series data with known properties
- Configurable data volume and characteristics
- Deterministic generation for reproducible tests

### Real Data Sampling
- Anonymized samples from production datasets
- Representative data distributions
- Edge cases and boundary conditions
- Historical data snapshots for regression testing

## Test Data Management

### Version Control
- Test data is committed to git for consistency
- Large datasets use Git LFS where appropriate
- Sensitive data is anonymized or synthetic only
- Version history tracks test data changes

### Maintenance
- Regular updates to match production data schemas
- Cleanup of obsolete test fixtures
- Performance optimization for large test datasets
- Documentation of test data sources and generation

## Best Practices

1. **Synthetic Data**: Prefer synthetic over real customer data
2. **Minimal Datasets**: Use smallest datasets that validate functionality
3. **Deterministic**: Ensure test data produces predictable results
4. **Versioning**: Track test data changes alongside code changes
5. **Cleanup**: Remove obsolete test data regularly

## Test Data Categories

### Unit Test Data
- **Small Scale**: Focused on specific function testing
- **Edge Cases**: Boundary conditions and error cases
- **Mock Objects**: Isolated component testing
- **Fast Execution**: Optimized for quick test execution

### Integration Test Data
- **Multi-Component**: Tests cross-module interactions
- **Realistic Scale**: Representative of production workloads
- **End-to-End**: Complete workflow validation datasets
- **Quality Metrics**: Known quality characteristics for validation

### Performance Test Data
- **Volume Testing**: Large datasets for performance validation
- **Stress Testing**: High-volume, high-frequency data
- **Benchmark Baselines**: Historical performance references
- **Scalability Testing**: Variable-size datasets for scaling tests

## Security Considerations

- No real customer data in test fixtures
- Anonymization of any production-derived data
- Synthetic data generation for sensitive scenarios
- Regular review of test data for compliance requirements