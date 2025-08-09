# Tests Directory

Simple testing structure following the "one codebase, multiple configurations" principle.

## Test Configurations (Data-Driven)

Tests use the same 4 configurations from `data/config/`:

- **test_config.yml**: Minimal test data (3 stocks, CI/CD friendly)
- **job_yfinance_m7.yml**: M7 dataset (7 stocks, git-tracked)  
- **yfinance_nasdaq100.yml**: NASDAQ100 dataset (100+ stocks, buildable)
- **yfinance_vti.yml**: VTI full market dataset (production target)

## Test Files

- `test_simple_validation.py`: Basic CI/CD validation tests
- `test_user_cases.py`: End-to-end user workflow tests (DEPRECATED)
- `conftest.py`: pytest configuration

## ETL Pipeline Testing

### Data Collection Tests
```bash
# Test data extraction (Stage 1)
python spider/yfinance_spider.py data/config/test_config.yml
python spider/yfinance_spider.py data/config/job_yfinance_m7.yml

# Test with different configurations
python spider/yfinance_spider.py data/config/yfinance_nasdaq100.yml
```

### Analysis Pipeline Tests
```bash
# Test DCF analysis with different datasets
python strategy/validator.py --config test_config.yml
python strategy/validator.py --config job_yfinance_m7.yml
python strategy/validator.py --config yfinance_nasdaq100.yml
```

### Build System Tests
```bash
# Test complete ETL pipeline with build tracking
pixi run build-m7                    # M7 build
pixi run build-nasdaq100             # NASDAQ100 build (if configured)
```

## Directory Structure Validation

Tests now validate the new ETL directory structure:
- `stage_01_extract/` - Raw data validation
- `stage_02_transform/` - Transformation quality checks  
- `stage_03_load/` - Final data validation
- `build/` - Build documentation verification

## Test Philosophy

- **One codebase, multiple configurations**: Same code path tested with different data scales
- **ETL stage validation**: Each stage tested independently and end-to-end
- **Data quality checks**: Schema validation, completeness, integrity
- **Build tracking**: Every test execution creates build documentation
- **CI optimization**: Minimal configuration for fast CI/CD pipeline