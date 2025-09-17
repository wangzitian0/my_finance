# Integration Testing Framework

**Clean Testing Architecture (Issue #282)**: Following L1/L2 modular testing strategy

This directory contains **integration and end-to-end tests** for the my_finance system.

> **Architecture**: Unit tests are located within their respective L1/L2 modules alongside source code. Root `tests/` contains integration and E2E tests for cross-module validation.

## Test Distribution

### Root Tests (Integration/E2E Only)
- `e2e/test_user_cases.py` - Complete user workflow validation
- `test_etl_config.py` - Centralized ETL configuration system tests (Issue #278)
- `pytest.ini` - Testing configuration (moved from root as part of Issue #282)
- Coverage and integration configuration

### L1/L2 Module Unit Tests (Co-located)
- **ETL Tests**: `ETL/tests/` - Data processing, SEC parsing, pipeline validation
- **Engine Tests**: `engine/tests/` - Graph-RAG, DCF calculations, reasoning logic
- **Evaluation Tests**: `evaluation/tests/` - Backtesting, metrics, benchmark analysis
- **Common Tests**: `common/tests/` - Utilities, configurations, shared components
- **Infra Tests**: `infra/tests/` - Infrastructure tools, deployment, system validation

## Running Tests

**P3 Commands**: See [README.md](../README.md) for complete P3 test commands and scopes.

### Integration Tests
```bash
pytest tests/ -v                # Root integration tests only
```

### L1/L2 Module Tests
```bash
pytest ETL/tests/ -v            # ETL module unit tests
pytest engine/tests/ -v         # Engine module unit tests
pytest evaluation/tests/ -v     # Evaluation module unit tests
pytest common/tests/ -v         # Common module unit tests
pytest infra/tests/ -v          # Infra module unit tests
```

## Testing Architecture Benefits

1. **Co-located Unit Tests**: Unit tests live alongside module source code for better maintainability
2. **Clear Separation**: Root tests focus on integration and cross-module scenarios
3. **Faster Feedback**: Module unit tests run independently without dependencies
4. **Better Isolation**: Unit test failures don't affect integration test execution
5. **L1/L2 Compliance**: Testing structure follows modular architecture principles

## Configuration

- **Coverage**: `tests/.coveragerc` - Testing-specific coverage configuration
- **Pytest**: Root `pytest.ini` - Unified pytest configuration for all test types
- **Pre-commit**: `infra/config/.pre-commit-config.yaml` - Code quality enforcement