# ETL Configuration System

**集中化ETL配置管理系统** - Issue #278 实现

## 🎯 设计原理

### 正交配置三维度
ETL系统采用三个独立的正交维度进行配置，运行时动态组合：

1. **Stock Lists** (股票列表) - 处理哪些公司
2. **Data Sources** (数据源) - 从哪里获取数据
3. **Scenarios** (场景) - 如何处理数据

### 扁平化命名规范
```
common/config/etl/
├── stock_f2.yml      # 2 companies (开发测试)
├── stock_m7.yml      # 7 companies (标准测试)
├── stock_n100.yml    # 100 companies (验证测试)
├── stock_v3k.yml     # 3,485 companies (生产环境)
├── source_yfinance.yml    # Yahoo Finance API
├── source_sec_edgar.yml   # SEC Edgar API
├── scenario_dev.yml       # 开发环境设置
└── scenario_prod.yml      # 生产环境设置
```

## 📋 配置文件格式

### Stock Lists (股票列表)
```yaml
# stock_f2.yml
description: "2-company subset for rapid development testing"
tier: "f2"
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
```

### Data Sources (数据源)
```yaml
# source_yfinance.yml
description: "Yahoo Finance API for historical prices and financial data"
enabled: true

data_types:
  - "historical_prices"
  - "financial_statements"
  - "company_info"

api_config:
  base_url: "https://query1.finance.yahoo.com"
  timeout_seconds: 30

rate_limits:
  requests_per_second: 2
  max_retries: 3
```

### Scenarios (场景)
```yaml
# scenario_dev.yml
description: "Fast development and testing environment"

data_sources:
  - "yfinance"
  - "sec_edgar"

processing_mode: "test"  # test, incremental, full

quality_thresholds:
  min_success_rate: 0.8
  max_error_rate: 0.2

resource_limits:
  max_concurrent_requests: 5
  memory_limit_mb: 1024
```

## 🚀 使用方法

### 基础用法
```python
from common.etl_loader import (
    build_etl_config,
    load_stock_list,
    load_data_source,
    load_scenario
)

# 1. 加载单个配置
stocks = load_stock_list('f2')        # 加载F2股票列表
source = load_data_source('yfinance') # 加载Yahoo Finance配置
scenario = load_scenario('development') # 加载开发场景

# 2. 组合运行时配置 (推荐)
config = build_etl_config(
    stock_list='f2',
    data_sources=['yfinance', 'sec_edgar'],
    scenario='development'
)

# 3. 使用配置
tickers = config.stock_list.tickers
api_config = config.data_sources['yfinance'].api_config
processing_mode = config.scenario.processing_mode
```

### ETL管道中的使用
```python
# 根据环境自动选择配置
if args.production:
    config = build_etl_config('v3k', ['yfinance', 'sec_edgar'], 'production')
else:
    config = build_etl_config('f2', ['yfinance'], 'development')

# 数据采集
for ticker in config.stock_list.tickers:
    for source_name in config.enabled_sources:
        source = config.data_sources[source_name]
        # 使用 source.api_config, source.rate_limits 等进行采集

# 应用场景设置
if config.scenario.processing_mode == 'test':
    # 使用测试模式的特殊逻辑
    pass
```

## 🔧 配置验证

### 内置验证功能
```python
from common.etl_loader import etl_loader

# 验证所有配置文件
errors = etl_loader.validate_config_files()
if errors:
    for error in errors:
        print(f"配置错误: {error}")
```

### 运行时验证
- 自动检查数据源在场景中是否可用
- YAML格式验证
- 文件存在性检查
- 配置完整性验证

## 📊 配置组合示例

### 开发环境
```python
# 快速开发: 2个股票 + YFinance + 开发模式
dev_config = build_etl_config('f2', ['yfinance'], 'development')
```

### 测试环境
```python
# 标准测试: 7个股票 + 双数据源 + 开发模式
test_config = build_etl_config('m7', ['yfinance', 'sec_edgar'], 'development')
```

### 生产环境
```python
# 生产部署: 3485个股票 + 双数据源 + 生产模式
prod_config = build_etl_config('v3k', ['yfinance', 'sec_edgar'], 'production')
```

## 🎯 优势

### 集中化管理
- **单一入口**: 所有ETL配置通过 `etl_loader` 访问
- **统一API**: 一致的接口，降低学习成本
- **自动缓存**: 避免重复文件读取

### 正交配置
- **独立维度**: 股票列表、数据源、场景互不干扰
- **灵活组合**: 运行时动态组合，支持各种场景
- **易于扩展**: 新增配置维度无需修改现有代码

### 维护性
- **扁平命名**: 直观的文件命名，易于理解
- **配置验证**: 自动验证配置正确性
- **错误处理**: 友好的错误信息和异常处理

## 🔄 迁移指南

### 从旧配置系统迁移
```bash
# 1. 执行自动迁移
python scripts/migrate_etl_config.py --migrate

# 2. 验证迁移结果
python scripts/migrate_etl_config.py --validate

# 3. 如有问题可回滚
python scripts/migrate_etl_config.py --rollback
```

### 代码更新模式
```python
# 旧方式 ❌
from common.orthogonal_config import orthogonal_config
config = orthogonal_config.load_stock_list('f2')

# 新方式 ✅
from common.etl_loader import load_stock_list
config = load_stock_list('f2')
```

## 🔗 相关文件

- `common/etl_loader.py` - 核心配置加载器
- `scripts/migrate_etl_config.py` - 配置迁移脚本
- `scripts/examples/etl_config_example.py` - 使用示例
- Issue #278 - 设计文档和需求

## 🚨 注意事项

1. **向后兼容**: 迁移期间旧配置依然可用
2. **缓存管理**: 配置修改后需要重启进程或清除缓存
3. **文件权限**: 确保配置文件具有正确的读取权限
4. **路径依赖**: 相对路径基于项目根目录

## 📈 性能特性

- **缓存机制**: 首次加载后缓存配置，避免重复IO
- **懒加载**: 只在需要时加载特定配置
- **验证缓存**: 文件修改时间戳检查，自动重新加载
- **内存优化**: 合理的数据结构，最小化内存占用