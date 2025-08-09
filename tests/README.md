# Integration Testing Framework

This directory contains **integration and end-to-end tests** for the my_finance system.

> **Architecture**: Module-specific tests are now located within their respective modules. Root `tests/` only contains integration and E2E tests.

## Test Distribution

### Root Tests (Integration/E2E Only)
- `e2e/test_user_cases.py` - Complete user workflow validation
- Coverage and integration configuration

### Module-Specific Tests (Moved)
- **ETL Tests**: `ETL/tests/` - Data processing, spiders, pipelines
- **Common Tests**: `common/tests/` - Utilities, configurations, shared components
- **DTS Tests**: `dts/tests/` - Data transport services (to be added)
- **DCF Engine Tests**: `dcf_engine/tests/` - Strategy calculations (to be added)
- **Evaluation Tests**: `evaluation/tests/` - Backtesting, LLM evaluation (to be added)

## Running Tests

### Complete Test Suite (All Modules)
```bash
pixi run test                    # All tests (integration + modules)
pixi run test-with-coverage      # With coverage report
```

### Integration Tests Only
```bash
pytest tests/ -v                # Root integration tests
pixi run test-all-user-cases     # User workflow tests
```

### Module-Specific Tests
```bash
pytest ETL/tests/ -v            # ETL module tests
pytest common/tests/ -v         # Common module tests
pytest dcf_engine/tests/ -v     # DCF engine tests
pytest evaluation/tests/ -v     # Evaluation tests
```

## Architecture Benefits

1. **Module Independence**: Each module tests its own functionality
2. **Clear Separation**: Root tests focus on integration scenarios
3. **Faster Feedback**: Module tests run independently
4. **Better Isolation**: Module test failures don't affect others