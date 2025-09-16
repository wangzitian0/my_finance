# ETL Configuration System

**Centralized ETL Configuration Management System** - Issue #278 Implementation

## 🎯 Design Principles

### Three Orthogonal Configuration Dimensions
The ETL system uses three independent orthogonal dimensions for configuration, combined dynamically at runtime:

1. **Stock Lists** - Which companies to process
2. **Data Sources** - Where to get data from
3. **Scenarios** - How to process the data

### Flattened Naming Convention
```
common/config/etl/
├── stock_f2.yml      # 2 companies (development testing)
├── stock_m7.yml      # 7 companies (standard testing)
├── stock_n100.yml    # 100 companies (validation testing)
├── stock_v3k.yml     # 3,485 companies (production environment)
├── source_yfinance.yml    # Yahoo Finance API
├── source_sec_edgar.yml   # SEC Edgar API
├── scenario_dev.yml       # Development environment settings
└── scenario_prod.yml      # Production environment settings
```

## 📋 Configuration File Formats

### Stock Lists
```yaml
# Example: stock_f2.yml
description: "Fast-2 development test dataset"
tier: "f2"
tracked_in_git: true
max_size_mb: 20

companies:
  MSFT:
    name: "Microsoft Corporation"
    sector: "Technology"
    industry: "Software"
    cik: "0000789019"
    market_cap_category: "mega"

  NVDA:
    name: "NVIDIA Corporation"
    sector: "Technology"
    industry: "Semiconductors"
    cik: "0001045810"
    market_cap_category: "large"

selection_criteria: "2 largest technology companies for fast development testing"
last_updated: "2025-01-15T10:00:00.000000"
```

### Data Sources
```yaml
# Example: source_yfinance.yml
description: "Yahoo Finance API data source"
enabled: true

data_types:
  - "historical_prices"
  - "financial_statements"
  - "company_info"

api_config:
  base_url: "https://query1.finance.yahoo.com"
  timeout_seconds: 30
  retry_attempts: 3

rate_limits:
  requests_per_second: 2
  daily_limit: 2000

output_format:
  file_extension: ".json"
  date_format: "YYYY-MM-DD"
  timestamp_format: "ISO"
```

### Scenarios
```yaml
# Example: scenario_dev.yml
description: "Development environment configuration"

data_sources:
  - "yfinance"
  - "sec_edgar"

processing_mode: "test"  # test, incremental, full

output_formats:
  - "json"
  - "parquet"

quality_thresholds:
  min_success_rate: 0.8
  max_error_rate: 0.2
  data_completeness: 0.7

resource_limits:
  max_concurrent_requests: 5
  memory_limit_mb: 1024
  timeout_minutes: 30

optimizations:
  cache_enabled: true
  parallel_processing: false
  batch_size: 10
```

## 🚀 Usage Examples

### Basic Configuration Loading
```python
from common.etl_loader import load_stock_list, load_data_source, load_scenario

# Load individual configurations
f2_stocks = load_stock_list('f2')
yfinance_config = load_data_source('yfinance')
dev_scenario = load_scenario('development')

print(f"F2 has {f2_stocks.count} stocks")
print(f"YFinance supports: {yfinance_config.data_types}")
print(f"Development mode: {dev_scenario.processing_mode}")
```

### Runtime Configuration Building
```python
from common.etl_loader import build_etl_config

# Combine orthogonal dimensions
config = build_etl_config(
    stock_list='f2',
    data_sources=['yfinance', 'sec_edgar'],
    scenario='development'
)

print(f"Configuration: {config.combination}")
print(f"Processing {config.ticker_count} stocks")
print(f"Using sources: {config.enabled_sources}")
```

### ETL Pipeline Integration
```python
from common.etl_loader import build_etl_config

# Production configuration
prod_config = build_etl_config('v3k', ['yfinance', 'sec_edgar'], 'production')

# Process each stock
for ticker in prod_config.stock_list.tickers:
    print(f"Processing {ticker}")

    # Use data source configurations
    for source_name in prod_config.enabled_sources:
        source_config = prod_config.data_sources[source_name]
        api_config = source_config.api_config
        rate_limit = source_config.rate_limits.get('requests_per_second', 1)

        # Apply rate limiting and processing
        # ... ETL pipeline logic here
```

## 🔄 Migration from Legacy Configuration

### Old Configuration Structure (Deprecated)
```
common/config/
├── stock_lists/
│   ├── f2.yml
│   ├── m7.yml
│   └── ...
├── data_sources/
│   ├── yfinance.yml
│   └── sec_edgar.yml
└── scenarios/
    ├── development.yml
    └── production.yml
```

### Migration Script
```bash
# Run migration to new flat structure
python infra/scripts/migrate_etl_config.py --migrate

# Validate migration
python infra/scripts/migrate_etl_config.py --validate

# Rollback if needed
python infra/scripts/migrate_etl_config.py --rollback
```

### Code Migration Patterns
```python
# OLD WAY (deprecated)
from common.orthogonal_config import orthogonal_config
config = orthogonal_config.load_stock_list('f2')

# NEW WAY (current)
from common.etl_loader import load_stock_list
config = load_stock_list('f2')
```

## 🧪 Testing and Validation

### Configuration Checker
```bash
# Check all configurations
python infra/scripts/config/check_etl_config.py --all

# Check specific configuration
python infra/scripts/config/check_etl_config.py --stock-list f2 --details
python infra/scripts/config/check_etl_config.py --data-source yfinance
python infra/scripts/config/check_etl_config.py --scenario development

# Test runtime configuration
python infra/scripts/config/check_etl_config.py --runtime f2 yfinance development
```

### Unit Tests
```bash
# Run ETL configuration tests
python -m pytest tests/test_etl_config.py -v

# Test with coverage
python -m pytest tests/test_etl_config.py --cov=common.etl_loader
```

## 📊 Configuration Matrix

### Supported Combinations
| Stock List | Data Sources | Scenarios | Use Case |
|------------|-------------|-----------|----------|
| f2 | yfinance | development | Fast development testing |
| m7 | yfinance, sec_edgar | development | Standard feature testing |
| n100 | yfinance, sec_edgar | development | Integration validation |
| v3k | yfinance, sec_edgar | production | Full production pipeline |

### Performance Characteristics
| Configuration | Stocks | Expected Runtime | Memory Usage | Disk Space |
|--------------|--------|------------------|--------------|------------|
| f2_yfinance_development | 2 | 30-60 seconds | 100 MB | 20 MB |
| m7_yfinance+sec_edgar_development | 7 | 2-5 minutes | 200 MB | 50 MB |
| n100_yfinance+sec_edgar_development | 100 | 15-30 minutes | 500 MB | 200 MB |
| v3k_yfinance+sec_edgar_production | 3,485 | 2-6 hours | 2 GB | 10 GB |

## 🔧 Configuration Management

### Adding New Stock Lists
1. Create new file: `common/config/etl/stock_[name].yml`
2. Follow the established YAML format
3. Add mapping in `etl_loader.py`: `_stock_list_mapping`
4. Update tests and documentation

### Adding New Data Sources
1. Create new file: `common/config/etl/source_[name].yml`
2. Define API configuration and rate limits
3. Add mapping in `etl_loader.py`: `_data_source_mapping`
4. Implement data source integration

### Adding New Scenarios
1. Create new file: `common/config/etl/scenario_[name].yml`
2. Define processing parameters and resource limits
3. Add mapping in `etl_loader.py`: `_scenario_mapping`
4. Update scenario validation logic

## 🎯 Design Benefits

### Before (Scattered Configuration)
- ❌ Configuration files spread across multiple directories
- ❌ Duplicate configuration management code
- ❌ Inconsistent naming conventions
- ❌ Manual file path handling
- ❌ No caching or validation

### After (Centralized Configuration)
- ✅ Single directory with flat structure
- ✅ DRY principle applied - one script, multiple configs
- ✅ Consistent naming: `stock_*.yml`, `source_*.yml`, `scenario_*.yml`
- ✅ Automated configuration loading with caching
- ✅ Built-in validation and error handling
- ✅ Orthogonal design enables flexible combinations

## 📚 References

- **Issue #278**: ETL Configuration Centralization
- **Migration Script**: `infra/scripts/migrate_etl_config.py`
- **Configuration Checker**: `infra/scripts/config/check_etl_config.py`
- **Usage Examples**: `infra/scripts/examples/etl_config_example.py`
- **Core Implementation**: `common/etl_loader.py`
- **Test Suite**: `tests/test_etl_config.py`

---

**Last Updated**: 2025-01-15
**Configuration Version**: 1.0
**Maintained By**: ETL Configuration System