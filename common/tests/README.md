# Common Module Tests

This directory contains tests for the common utilities and shared components.

## Test Structure

### Current Tests
- **`test_simple_validation.py`** - Basic validation and utility function tests

## Test Coverage

The common module tests cover:
- **Configuration loading** (`config.py`)
- **Logging functionality** (`logger.py`)
- **Data I/O utilities** (`utils.py`)
- **Build tracking** (`build_tracker.py`)
- **Progress reporting** (`progress.py`)
- **Metadata management** (`metadata_manager.py`)

## Running Tests

```bash
# Run all tests including common module
p3 test

# Run only common module tests
python -m pytest common/tests/ -v
```

## Adding New Tests

When adding new utilities to the common module:
1. Create corresponding test files following naming convention `test_*.py`
2. Test both success and failure scenarios
3. Validate error handling and edge cases
4. Ensure tests are isolated and don't depend on external resources

## Test Dependencies

Common module tests should:
- Be independent of data directory contents
- Mock external dependencies where possible
- Use temporary directories for file operations
- Clean up test artifacts after execution