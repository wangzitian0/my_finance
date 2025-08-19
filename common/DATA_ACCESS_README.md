# Centralized Data Access Utility

This document describes the centralized data access utility (`common/data_access.py`) that provides a unified interface for accessing all data directories and files in the my_finance system.

## Purpose

The `DataAccess` class centralizes all data directory I/O operations to:
- **Eliminate hardcoded paths** throughout the codebase
- **Provide consistent path construction** across different modules
- **Support different data stages** (original, extract, transform, load, build)
- **Handle branch-specific builds** and release management
- **Simplify maintenance** when directory structures change

## Usage

### Basic Import and Initialization

```python
from common.data_access import data_access, get_data_path, get_build_path

# Global instance is available for immediate use
build_dir = data_access.get_build_dir()

# Or create custom instance with different base directory
custom_access = DataAccess("/custom/data/path")
```

### Stage Directory Access

```python
# Get stage directories
original_dir = data_access.get_original_dir()        # data/stage_00_original
extract_dir = data_access.get_extract_dir()          # data/stage_01_extract
transform_dir = data_access.get_transform_dir()      # data/stage_02_transform
load_dir = data_access.get_load_dir()                # data/stage_03_load

# Build directory with optional timestamp and branch
build_dir = data_access.get_build_dir()                              # data/stage_99_build
build_dir = data_access.get_build_dir('20250119_140000')             # data/stage_99_build/build_20250119_140000
build_dir = data_access.get_build_dir('20250119_140000', 'feature')  # data/stage_99_build_feature/build_20250119_140000

# Release directories
release_dir = data_access.get_release_dir()                    # data/release
specific_release = data_access.get_release_dir('release_...')  # data/release/release_...
```

### Configuration and Log Access

```python
# Configuration files
config_dir = data_access.get_config_dir()                      # data/config
yfinance_config = data_access.get_config_file('job_yfinance_m7')  # data/config/job_yfinance_m7.yml

# Log files
log_dir = data_access.get_log_dir()                    # data/log
job_log_dir = data_access.get_log_dir('yfinance')     # data/log/yfinance
log_file = data_access.get_log_file('yfinance')       # data/log/yfinance/YYMMDD-HHMMSS.txt
```

### Source and Ticker Access

```python
# Source-specific directories
yfinance_dir = data_access.get_source_dir('yfinance', 'stage_01_extract')  # data/stage_01_extract/yfinance
sec_dir = data_access.get_source_dir('sec_edgar', 'stage_00_original')     # data/stage_00_original/sec_edgar

# Ticker-specific directories  
aapl_dir = data_access.get_ticker_dir('yfinance', 'AAPL', 'stage_01_extract')  # data/stage_01_extract/yfinance/AAPL
```

### Utility Methods

```python
# Ensure directory exists (create if needed)
new_dir = data_access.ensure_dir_exists(Path("data/new_directory"))

# Get latest date partition from source directory
latest_date = data_access.get_latest_date_partition(source_dir)

# List available builds and releases
builds = data_access.list_builds()           # ['20250119_140000', '20250118_120000', ...]
releases = data_access.list_releases()       # ['release_20250119_140000_build_...', ...]

# Branch-specific builds
feature_builds = data_access.list_builds('feature/my-branch')
```

### Convenience Functions

```python
# Quick path access without class instantiation
from common.data_access import get_data_path, get_build_path, get_config_path, get_log_path

data_path = get_data_path('stage_99_build', 'latest')      # data/stage_99_build/latest
build_path = get_build_path('20250119_140000')             # data/stage_99_build/build_20250119_140000
config_path = get_config_path('job_yfinance_m7')           # data/config/job_yfinance_m7.yml
log_path = get_log_path('yfinance', '250119-140000')       # data/log/yfinance/250119-140000.txt
```

## Migration Examples

### Before (Hardcoded Paths)

```python
# ❌ Old pattern - hardcoded paths
build_dir = Path(f"data/stage_99_build/build_{timestamp}")
build_dir.mkdir(parents=True, exist_ok=True)

log_file = Path("data/log") / "finlang_model_info.json"
config_path = "data/config/job_yfinance_m7.yml"
```

### After (Centralized Access)

```python
# ✅ New pattern - centralized access
from common.data_access import data_access

build_dir = data_access.get_build_dir(build_timestamp=timestamp)
data_access.ensure_dir_exists(build_dir)

log_file = data_access.get_log_dir() / "finlang_model_info.json"  
config_path = data_access.get_config_file('job_yfinance_m7')
```

## Key Benefits

1. **Maintainability**: Single location to update path structures
2. **Consistency**: Standardized path construction across all modules  
3. **Flexibility**: Easy support for branch-specific builds and different environments
4. **Type Safety**: Path objects instead of string concatenation
5. **Error Prevention**: Automatic directory creation and validation

## Integration Points

The centralized data access utility is integrated into:

- **DCF Engine**: Build directory management and report generation
- **ETL Pipeline**: Data stage directory access and processing
- **Common Utilities**: Logging, metadata management, build tracking
- **Scripts**: Maintenance and utility scripts
- **Testing**: Test data and validation frameworks

## Best Practices

1. **Always import the utility** instead of hardcoding paths
2. **Use the global instance** `data_access` for standard operations
3. **Use convenience functions** for simple path access
4. **Create custom instances** only when needed for different base directories
5. **Use `ensure_dir_exists()`** instead of manual `mkdir()` calls
6. **Leverage build listing** for dynamic build management

## Directory Structure Support

The utility supports the complete my_finance directory structure:

```
data/
├── stage_00_original/          # Original source data
├── stage_01_extract/           # Extracted data  
├── stage_02_transform/         # Transformed data
├── stage_03_load/              # Final loaded data
├── stage_99_build/             # Build artifacts (main branch)
├── stage_99_build_{branch}/    # Branch-specific builds
├── release/                    # Release management
├── config/                     # Configuration files
├── log/                        # Application logs
├── llm/                        # LLM configurations
├── test/                       # Test data and fixtures
└── quality_reports/            # Data quality reports
```

This centralized approach ensures consistent, maintainable, and flexible data access across the entire my_finance system.