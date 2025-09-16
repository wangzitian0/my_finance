# Configuration Management

**L2 Module**: Centralized configuration files for infrastructure and system management

**Business Purpose**: Centralized storage for configuration files moved from root directory

## Configuration Files

### Development Tools
- **`.pre-commit-config.yaml`** - Pre-commit hooks configuration for code quality enforcement
  - Supports all L1 modules: common, tests, ETL, engine, evaluation, infra
  - Includes format, lint, and test validation
  - Module-aware test execution and structure validation

## Architecture Compliance

Following **Issue #282** root directory cleanup:
- Configuration files moved from root directory to proper L1/L2 module locations
- Maintains SSOT (Single Source of Truth) principle for all configuration management
- Supports modular testing architecture with unit tests co-located in modules

## Usage

Configuration files are automatically used by their respective tools:
- Pre-commit hooks: Managed through git workflow integration
- Coverage: Testing-specific configuration in `tests/.coveragerc`
- Pytest: Root-level `pytest.ini` for unified test management