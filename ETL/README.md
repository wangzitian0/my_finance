# ETL - 数据处理管道

爬虫、数据加工清洗的完整ETL流程。从原始数据采集到结构化数据输出。

## 组件结构

### 数据采集 (Spider)
- `yfinance_spider.py` - Yahoo Finance数据爬虫
- `sec_edgar_spider.py` - SEC Edgar文件爬虫  
- `fetch_ticker_lists.py` - 股票代码列表获取

### 数据解析 (Parser)
- `sec_parser.py` - SEC文档解析器
- `rcts.py` - RCTS格式解析器

### 数据处理
- `build_dataset.py` - 数据集构建工具
- `migrate_data_structure.py` - 数据结构迁移
- `check_coverage.py` - 数据覆盖率检查
- `retry_failed.py` - 失败重试工具
- `update_data_paths.py` - 路径更新工具

### 数据建模
- `models.py` - Neo4j数据模型定义
- `build_schema.py` - Schema构建工具
- `import_data.py` - 数据导入工具

## 数据流程

```
原始数据源 → Spider采集 → Parser解析 → ETL处理 → DTS输出
    ↓           ↓          ↓         ↓        ↓
  YFinance   原始文件   结构化数据  清洗数据  标准接口
  SEC Edgar
```

## 使用方式

```bash
# 数据采集
python run_job.py data/config/job_yfinance_m7.yml

# Via pixi commands
pixi run build-m7
```

### SEC Edgar Spider (`sec_edgar_spider.py`)
Collects SEC filing data using ticker-based structure.

**Data Structure (Redesigned):**

**Old Problem:**
```
original/sec-edgar/
├── 0000320193/           # CIK number (confusing)
│   ├── 10k/
│   │   └── 0000320193/   # Duplicate CIK structure
│   │       └── 10-K/     # Filing type
│   │           └── *.txt # Filing files
```

**New Structure (Data Source Oriented):**
```
stage_01_extract/sec_edgar/
├── <date_partition>/          # Daily partition (e.g., 20250809)
│   ├── AAPL/                  # Stock ticker (user-friendly)
│   │   ├── AAPL_sec_edgar_10K_<timestamp>.json
│   │   ├── AAPL_sec_edgar_10Q_<timestamp>.json  
│   │   ├── AAPL_sec_edgar_8K_<timestamp>.json
│   │   └── README.md          # Metadata for AAPL
│   ├── MSFT/
│   │   ├── MSFT_sec_edgar_10K_<timestamp>.json
│   │   └── README.md          # Metadata for MSFT
│   └── ...
└── latest -> <date_partition>/ # Symlink to latest
```

**README.md Format (per ticker):**
```markdown
# SEC Filings for {TICKER}

## Company Information
- **Ticker**: AAPL
- **Company**: Apple Inc.
- **CIK**: 0000320193
- **Industry**: Technology Hardware Storage & Peripherals

## Available Filings
| Filing Type | File Name | Filing Date | Document URL |
|------------|-----------|-------------|--------------|
| 10-K | AAPL_sec_edgar_10K_250209-120000.json | 2024-11-01 | https://... |
| 10-Q | AAPL_sec_edgar_10Q_250209-120001.json | 2024-10-31 | https://... |

## Data Quality
- Last Updated: 2025-02-09
- Filing Coverage: 2017-2025
- Data Integrity: ✅ Verified
```

## Configuration Files

Spiders use YAML configuration files located in `data/config/`:

### M7 Configuration (`job_yfinance_m7.yml`)
```yaml
source: yfinance
job: yfinance_m7
description: Yahoo Finance data for Magnificent 7 companies
tickers:
  - AAPL    # Apple Inc.
  - MSFT    # Microsoft Corporation  
  - AMZN    # Amazon.com Inc.
  - GOOGL   # Alphabet Inc. (Class A)
  - META    # Meta Platforms Inc.
  - TSLA    # Tesla Inc.
  - NFLX    # Netflix Inc.
data_periods:
  - oid: m7_D1
    period: 3y     # 3 years of daily data
    interval: 1d
  - oid: m7_W7
    period: 5y     # 5 years of weekly data  
    interval: 1wk
  - oid: m7_M30
    period: 10y    # 10 years of monthly data
    interval: 1mo
```

### SEC Edgar Configuration (`sec_edgar_m7.yml`)
```yaml
source: sec_edgar
job: sec_edgar_m7
description: SEC Edgar filings for Magnificent 7 companies
email: ZitianSG (wangzitian0@gmail.com)
file_types:
  - 10K     # Annual reports
  - 10Q     # Quarterly reports
  - 8K      # Current reports
tickers:
  - AAPL    # Apple Inc. - CIK 0000320193
  - MSFT    # Microsoft Corporation - CIK 0000789019
  - AMZN    # Amazon.com Inc. - CIK 0001018724
  - GOOGL   # Alphabet Inc. - CIK 0001652044
  - META    # Meta Platforms Inc. - CIK 0001326801
  - TSLA    # Tesla Inc. - CIK 0001318605
  - NFLX    # Netflix Inc. - CIK 0001065280
```

## CIK to Ticker Mapping

For SEC Edgar spider, the following CIK to ticker mappings are used:

```python
cik_to_ticker = {
    "0000320193": "AAPL",   # Apple Inc.
    "0000789019": "MSFT",   # Microsoft Corporation
    "0001018724": "AMZN",   # Amazon.com Inc.
    "0001652044": "GOOGL",  # Alphabet Inc. (Class A)
    "0001326801": "META",   # Meta Platforms Inc.
    "0001318605": "TSLA",   # Tesla Inc.
    "0001065280": "NFLX"    # Netflix Inc.
}
```

## Migration Benefits

The new ticker-based structure provides:
- **User-Friendly**: Ticker names instead of CIK numbers
- **Consistent**: Same pattern as yfinance data
- **Metadata Rich**: README.md contains all context
- **Warehouse Ready**: Date partitioned for easy ingestion

## Integration

Both spiders integrate with:
- **MetadataManager**: Anti-duplicate downloads
- **BuildTracker**: Comprehensive build tracking
- **ETL Pipeline**: Stage-based data storage
- **Date Partitioning**: YYYYMMDD format for data warehouse compatibility

## Usage Commands

```bash
# Build M7 dataset
pixi run build-m7

# Run specific job
python run_job.py <config_file.yml>

# Check build status
pixi run build-status

# View latest build
ls data/build/
```

---

*Spiders implement enterprise-grade ETL patterns with comprehensive metadata tracking and anti-duplicate functionality.*