# Common Module Test Suite

This directory contains comprehensive unit and integration tests for all modules in the `common/` package, designed to achieve 80% code coverage and ensure robust testing of all components.

## 🏗️ Test Architecture

The test suite is organized following pytest best practices with clear separation between unit and integration tests:

```
common/tests/
├── conftest.py                 # Shared fixtures and configuration
├── pytest.ini                 # Pytest configuration with markers and coverage
├── requirements.txt            # Test dependencies
├── run_tests.py               # Legacy simple test runner
├── pytest_runner.py          # Comprehensive pytest-based runner
├── unit/                      # Unit tests for individual modules
│   ├── test_config_manager.py
│   ├── test_directory_manager.py
│   ├── test_storage_manager.py
│   ├── test_agent_task_tracker.py
│   ├── test_build_tracker.py
│   ├── test_execution_monitor.py
│   ├── test_graph_rag_schema.py
│   └── test_utils_data_processing.py
└── integration/               # Cross-module integration tests
    └── test_cross_module_integration.py
```

## 🎯 Test Coverage Goals

- **Target Coverage**: 80% minimum across all modules
- **Focus Areas**: Core functionality, error handling, edge cases
- **Testing Strategy**: Unit tests for individual components, integration tests for cross-module workflows

### Coverage by Module

| Module | Test File | Coverage Focus |
|--------|-----------|----------------|
| **Core Modules** | | |
| `directory_manager` | `test_directory_manager.py` | Path resolution, caching, security |
| `config_manager` | `test_config_manager.py` | Configuration loading, validation, caching |
| `storage_manager` | `test_storage_manager.py` | Storage backends, file operations |
| **Build System** | | |
| `build_tracker` | `test_build_tracker.py` | Build tracking, stage management, artifacts |
| **Monitoring** | | |
| `execution_monitor` | `test_execution_monitor.py` | Execution tracking, error categorization |
| **Agents** | | |
| `agent_task_tracker` | `test_agent_task_tracker.py` | Task tracking, performance analysis |
| **Schemas** | | |
| `graph_rag_schema` | `test_graph_rag_schema.py` | Schema validation, data structures |
| **Utilities** | | |
| `utils_data_processing` | `test_utils_data_processing.py` | Data processing utilities |

## 🧪 Test Categories and Markers

Tests are organized using pytest markers for easy filtering:

### Core Markers
- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for cross-module functionality
- `@pytest.mark.slow` - Tests that may take longer to run

### Module-Specific Markers
- `@pytest.mark.core` - Tests for core system components
- `@pytest.mark.agents` - Tests for agent-related modules
- `@pytest.mark.build` - Tests for build and quality modules
- `@pytest.mark.monitoring` - Tests for monitoring components
- `@pytest.mark.schemas` - Tests for schema definitions

## 🚀 Running Tests

### Quick Start

This project uses **pixi** for environment management. Make sure you're in the pixi environment:

```bash
# Enter pixi environment
pixi shell

# Check environment is ready
pixi run check-env

# Run all tests with coverage (recommended)
pixi run test-common

# Check test structure
pixi run test-common-check
```

**Alternative using pytest_runner.py:**
```bash
# Install additional test dependencies (in pixi environment)
python common/tests/pytest_runner.py --install

# Run tests with coverage
python common/tests/pytest_runner.py --coverage
```

### Test Execution Options

#### By Test Type

**Using pixi tasks (recommended):**
```bash
# Unit tests only
pixi run test-common-unit

# Integration tests only  
pixi run test-common-integration

# All tests with coverage
pixi run test-common

# Coverage report generation
pixi run test-common-coverage
```

**Using pytest_runner.py:**
```bash
# Unit tests only
python common/tests/pytest_runner.py --unit

# Integration tests only
python common/tests/pytest_runner.py --integration

# All tests
python common/tests/pytest_runner.py --all
```

#### By Module/Marker

**Using pixi tasks:**
```bash
# Core module tests
pixi run test-core

# Agent tests
pixi run test-agents

# Build system tests
pixi run test-build

# Monitoring tests
pixi run test-monitoring

# Schema tests
pixi run test-schemas
```

**Using pytest_runner.py:**
```bash
# Core module tests
python common/tests/pytest_runner.py --marker core

# Agent tests
python common/tests/pytest_runner.py --marker agents

# Build system tests
python common/tests/pytest_runner.py --marker build

# Monitoring tests
python common/tests/pytest_runner.py --marker monitoring
```

#### By Pattern
```bash
# Tests matching specific pattern
python common/tests/pytest_runner.py --pattern storage

# Tests for specific module
python common/tests/pytest_runner.py --pattern directory_manager
```

#### Coverage Analysis
```bash
# Run with 80% coverage requirement (default)
python common/tests/pytest_runner.py --coverage

# Run with 90% coverage requirement
python common/tests/pytest_runner.py --coverage --target 90

# Generate detailed coverage report
python common/tests/pytest_runner.py --report
```

### Legacy Test Runner

For environments without pytest:
```bash
# Simple test runner (no dependencies)
python common/tests/run_tests.py
```

## 📊 Coverage Reporting

The test suite generates multiple coverage report formats:

- **HTML Report**: `common/tests/coverage_html/index.html` - Interactive web interface
- **Terminal**: Real-time coverage displayed during test execution
- **XML Report**: `common/tests/coverage.xml` - For CI/CD integration
- **JSON Report**: `common/tests/coverage.json` - Programmatic access

### Reading Coverage Reports

```bash
# View HTML report
open common/tests/coverage_html/index.html

# View coverage summary in terminal
python common/tests/pytest_runner.py --report
```

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = common/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests for individual components
    integration: Integration tests for cross-module functionality
    slow: Tests that may take longer to run
    core: Tests for core system components
    agents: Tests for agent-related modules
    build: Tests for build and quality modules
    monitoring: Tests for monitoring components
    schemas: Tests for schema definitions
addopts = 
    --tb=short
    --strict-markers
    -ra
```

### Shared Fixtures (`conftest.py`)

Key fixtures available to all tests:

- `temp_dir` - Temporary directory for test isolation
- `mock_project_root` - Mock project structure
- `sample_config_data` - Sample configuration for testing
- `mock_storage_backend` - Mock storage backend
- `mock_directory_manager` - Mock directory manager
- Environment setup and cleanup fixtures

## 🧩 Test Structure Patterns

### Unit Test Pattern

```python
@pytest.mark.unit
@pytest.mark.core
class TestModuleName:
    """Test ModuleName functionality."""
    
    def test_basic_functionality(self):
        """Test basic module functionality."""
        # Arrange
        # Act  
        # Assert
        
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ExpectedException):
            # Test code that should raise exception
```

### Integration Test Pattern

```python
@pytest.mark.integration
class TestModuleIntegration:
    """Test module integration with other components."""
    
    def test_cross_module_workflow(self):
        """Test complete workflow across modules."""
        # Setup multiple modules
        # Execute workflow
        # Verify integration points
```

### Mock Usage Pattern

```python
def test_with_mocks(self):
    """Test using mocks for external dependencies."""
    with patch('module.external_dependency') as mock_dep:
        mock_dep.return_value = "expected_value"
        # Test code
        mock_dep.assert_called_once()
```

## 🚦 Continuous Integration

### GitHub Actions Integration

The project includes a dedicated CI workflow for common module testing at `.github/workflows/test-common-modules.yml`.

**Automated Testing Triggers:**
- Push to `main`, `feature/**`, or `hotfix/**` branches
- Pull requests to `main` branch
- Changes to `common/**` files or test configuration

**CI Pipeline Features:**
- ✅ **Unit Tests**: Complete unit test suite execution
- ✅ **Integration Tests**: Cross-module functionality testing
- ✅ **Coverage Validation**: 80% coverage requirement enforcement
- ✅ **Test Structure Validation**: Automated test completeness checks
- ✅ **Marker-based Testing**: Tests organized by component markers
- ✅ **Artifact Upload**: Test results and coverage reports preserved
- ✅ **Coverage Reporting**: Codecov integration with PR comments

**Manual CI Integration Example:**

```yaml
jobs:
  test-common:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install test dependencies
      run: pip install -r requirements-test.txt

    - name: Run tests with coverage
      run: |
        python -m pytest common/tests/ \
          --cov=common \
          --cov-report=xml:coverage.xml \
          --cov-fail-under=80

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: coverage.xml
        flags: common-modules
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
  - id: run-tests
    name: Run common module tests
    entry: python common/tests/pytest_runner.py --coverage
    language: system
    pass_filenames: false
```

## 🐛 Debugging Tests

### Verbose Output

```bash
# Run with verbose output
python common/tests/pytest_runner.py --all --verbose

# Run specific failing test
python common/tests/pytest_runner.py --pattern test_specific_function --verbose
```

### Test Debugging

```bash
# Run tests with pdb debugger
python -m pytest common/tests/ --pdb

# Stop on first failure
python -m pytest common/tests/ -x

# Show local variables in tracebacks
python -m pytest common/tests/ -l
```

## 📝 Writing New Tests

### Guidelines

1. **Test Organization**: Place unit tests in `unit/`, integration tests in `integration/`
2. **File Naming**: Use `test_<module_name>.py` pattern
3. **Class Naming**: Use `TestModuleName` pattern  
4. **Method Naming**: Use `test_<functionality>` pattern
5. **Markers**: Add appropriate pytest markers
6. **Documentation**: Include docstrings describing test purpose

### Example New Test File

```python
#!/usr/bin/env python3
"""
Unit tests for new_module.py - Module Description
Tests core functionality, error handling, and edge cases.
"""

import pytest
from unittest.mock import patch, MagicMock

from common.path.new_module import NewModule


@pytest.mark.unit
@pytest.mark.core  # or appropriate marker
class TestNewModule:
    """Test NewModule functionality."""
    
    def test_initialization(self):
        """Test module initialization."""
        module = NewModule()
        assert module is not None
        
    def test_main_functionality(self):
        """Test main module functionality."""
        # Test implementation
        pass
        
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ExpectedException):
            # Test code that should raise exception
            pass


@pytest.mark.integration
class TestNewModuleIntegration:
    """Test NewModule integration."""
    
    def test_integration_with_other_modules(self):
        """Test integration with other modules."""
        # Integration test implementation
        pass
```

## 📚 Dependencies

### Test Requirements (`requirements-test.txt`)

Testing dependencies are located in the project root as `requirements-test.txt`:

```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0
coverage>=7.0.0
pytest-html>=3.1.0
factory-boy>=3.2.0
freezegun>=1.2.0
responses>=0.23.0
pytest-benchmark>=4.0.0
pytest-xdist>=3.0.0
parameterized>=0.8.1
testfixtures>=7.0.0
PyYAML>=6.0.0
```

### Installation

```bash
# Install test dependencies (from project root)
pip install -r requirements-test.txt

# Or use the test runner
python common/tests/pytest_runner.py --install
```

## 🎯 Test Quality Standards

### Code Coverage Requirements

- **Minimum**: 80% line coverage
- **Target**: 85%+ line coverage
- **Critical Paths**: 95%+ coverage for core functionality

### Test Quality Metrics

- ✅ All tests must pass consistently
- ✅ Tests must be deterministic (no flaky tests)
- ✅ Tests must run in isolation
- ✅ Tests must be fast (unit tests <1s, integration tests <10s)
- ✅ Tests must have clear, descriptive names
- ✅ Tests must include appropriate assertions

### Performance Guidelines

- Unit tests should complete in under 1 second each
- Integration tests should complete in under 10 seconds each
- Full test suite should complete in under 5 minutes
- Use mocks for external dependencies to improve speed

## 🚨 Common Issues and Solutions

### Import Errors
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:/path/to/project"

# Or run from project root directory
cd /path/to/project && python common/tests/pytest_runner.py
```

### Missing Dependencies
```bash
# Install all test dependencies
python common/tests/pytest_runner.py --install
```

### Slow Tests
```bash
# Run only fast tests
python common/tests/pytest_runner.py --marker "not slow"

# Run tests in parallel
pip install pytest-xdist
python -m pytest common/tests/ -n auto
```

### Coverage Issues
```bash
# Generate detailed coverage report
python common/tests/pytest_runner.py --report

# View missing coverage in HTML report
open common/tests/coverage_html/index.html
```

## 📞 Support and Contribution

### Adding New Tests

1. Create test file following naming conventions
2. Add appropriate pytest markers
3. Include unit and integration tests as needed
4. Ensure tests achieve minimum coverage requirements
5. Update this README if adding new test categories

### Test Maintenance

- Review and update tests when modifying code
- Maintain test documentation
- Monitor test execution time and optimize slow tests
- Keep test dependencies up to date

For questions or issues with the test suite, refer to the project documentation or create an issue in the project repository.