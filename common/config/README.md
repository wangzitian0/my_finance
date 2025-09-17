# Configuration Architecture

This directory contains the modular configuration system for the My Finance DCF Analysis Tool. The architecture has been modernized with **Issue #278** to use centralized ETL configuration with three orthogonal dimensions.

## 🎯 Current Architecture (Post Issue #278 + #111)

The configuration system supports **P3 CLI integration** and **three orthogonal ETL dimensions** that can be combined dynamically at runtime:

### 📁 P3 CLI Dataset Configurations (Root Level)
**Direct P3 CLI integration** - Stock lists accessible via DatasetTier enum and functional aliases:

**Stock Lists** (P3 CLI accessible):
- `list_fast_2.yml` - F2 tier: 2 companies (CI testing, alias: TEST)
- `list_magnificent_7.yml` - M7 tier: 7 companies (performance testing, alias: PERF)
- `list_nasdaq_100.yml` - N100 tier: 100 companies (validation testing)
- `list_vti_3500.yml` - V3K tier: 3,485 companies (production)

### 📁 ETL Configuration Directory (`etl/`)
**Centralized ETL configuration system** - Detailed ETL configurations in the `etl/` subdirectory:

**ETL Stock Lists** (ETL pipeline specific):
- `stock_f2.yml` - Fast-2 development test dataset (2 companies)
- `stock_m7.yml` - Magnificent 7 technology companies (7 companies)
- `stock_n100.yml` - NASDAQ-100 index companies (~100 companies)
- `stock_v3k.yml` - VTI ETF holdings (~3,485 companies)

**Data Sources** (Where to get data from):
- `source_yfinance.yml` - Yahoo Finance API configuration
- `source_sec_edgar.yml` - SEC Edgar filings API configuration

**Scenarios** (How to process data):
- `scenario_dev.yml` - Development environment settings
- `scenario_prod.yml` - Production environment settings

### 🔄 Configuration Integration

**P3 CLI Integration** - Direct command access:
```bash
p3 test f2        # Uses list_fast_2.yml (alias: TEST)
p3 test perf      # Uses list_magnificent_7.yml (alias: PERF)
p3 build n100     # Uses list_nasdaq_100.yml
p3 ship "Title" 123  # Auto-detects appropriate test configuration
```

**Python DatasetTier Integration**:
```python
from ETL.tests.test_config import DatasetTier, TestConfigManager

manager = TestConfigManager()
f2_config = manager.get_config(DatasetTier.F2)     # list_fast_2.yml
test_config = manager.get_config(DatasetTier.TEST) # Same as F2
perf_config = manager.get_config(DatasetTier.PERF) # list_magnificent_7.yml
```

**ETL Runtime Configuration Building**:
```python
from common.etl_loader import build_etl_config

# Example: F2 stocks + YFinance data + Development scenario
config = build_etl_config('f2', ['yfinance'], 'development')
print(f"Config: {config.combination}")  # f2_yfinance_development
```

## 📋 Configuration Management

### Adding New Configurations
1. **Stock Lists**: Create `etl/stock_[name].yml` and update `etl_loader.py` mappings
2. **Data Sources**: Create `etl/source_[name].yml` and add API integration
3. **Scenarios**: Create `etl/scenario_[name].yml` and define processing parameters

### Migration from Legacy
- **Migration Script**: `infra/scripts/migrate_etl_config.py`
- **Validation Tool**: `infra/scripts/config/check_etl_config.py`
- **Examples**: `infra/scripts/examples/etl_config_example.py`

## 🗂️ Legacy Structure (Deprecated)

The following structure has been **migrated and removed** as part of Issue #278:

```
❌ REMOVED:
├── stock_lists/           # Moved to etl/stock_*.yml
├── data_sources/          # Moved to etl/source_*.yml
├── scenarios/             # Moved to etl/scenario_*.yml
├── list_*.yml            # Consolidated into etl/stock_*.yml
├── sec_edgar_*.yml       # Functionality moved to etl_loader
└── stage_00_original_*.yml # Replaced by source configurations
```

## 🎯 Design Benefits

### Before (Scattered Configuration)
- ❌ Configuration files spread across multiple directories
- ❌ Duplicate configuration management code
- ❌ Inconsistent naming conventions
- ❌ Manual file path handling

### After (Centralized ETL Configuration)
- ✅ Single `etl/` directory with flat structure
- ✅ DRY principle applied - one script, multiple configs
- ✅ Consistent naming: `stock_*.yml`, `source_*.yml`, `scenario_*.yml`
- ✅ Automated configuration loading with caching
- ✅ Orthogonal design enables flexible combinations

## 📚 Documentation

- **ETL Configuration System**: `etl/README.md`
- **Core Implementation**: `common/etl_loader.py`
- **Test Suite**: `tests/test_etl_config.py`
- **Migration Guide**: `infra/scripts/migrate_etl_config.py`

---

**Configuration Version**: 2.0 (Issue #278)
**Last Updated**: 2025-01-15
**Migration Status**: ✅ Complete