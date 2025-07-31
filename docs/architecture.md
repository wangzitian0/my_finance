# Architecture Documentation

## System Overview

This is a **Graph RAG-powered DCF valuation system** that combines financial data collection, graph database storage, and intelligent analysis capabilities.

## Three-Tier Data Management Strategy

### Tier 1: M7 (Magnificent 7) - Stable Test Dataset
- **Size**: ~500MB
- **Companies**: 7 (Apple, Microsoft, Amazon, Alphabet, Meta, Tesla, Netflix)
- **Storage**: Git-tracked in repository
- **Purpose**: Development, testing, and CI/CD
- **Data**: 3 years of historical data

### Tier 2: NASDAQ100 - Extended Dataset  
- **Size**: ~5GB
- **Companies**: ~100 NASDAQ companies
- **Storage**: Buildable, gitignored
- **Purpose**: Extended validation and demo scenarios
- **Data**: 3 years of historical data

### Tier 3: US-ALL - Complete Dataset
- **Size**: ~50GB  
- **Companies**: ~8000+ US public companies
- **Storage**: Buildable, gitignored
- **Purpose**: Production-scale analysis
- **Data**: 3 years of historical data

## Core Components

### Data Collection Layer

#### Yahoo Finance Spider (`spider/yfinance_spider.py`)
- **Purpose**: Collect stock prices, company info, recommendations, sustainability data
- **Features**: Progress tracking, rate limiting, error handling
- **Output**: JSON files in `data/original/yfinance/<ticker>/`

#### SEC Edgar Spider (`spider/sec_edgar_spider.py`)  
- **Purpose**: Download regulatory filings (10-K, 10-Q, 8-K)
- **Features**: CIK number mapping, filing type filtering
- **Output**: Raw filings in `data/original/sec/<ticker>/`

### Database Layer

#### Neo4j Graph Database
- **ORM**: neomodel for Python integration
- **Models**: Defined in `ETL/models.py`
- **Relationships**: Stock → Info, PriceData, Filings, etc.
- **Query Interface**: Cypher queries via neomodel

#### Key Node Types
- **Stock**: Central node with ticker as unique identifier
- **Info**: Company information and metadata
- **PriceData**: Historical price and volume data
- **Filing**: SEC regulatory documents
- **Recommendation**: Analyst recommendations

### Document Processing Layer

#### SEC Parser (`parser/sec_parser.py`)
- **Purpose**: Parse XML/SGML SEC filings
- **Technology**: BeautifulSoup for parsing
- **Features**: Text extraction, structure preservation
- **Output**: Structured data for graph database

#### Advanced Processing (`parser/rcts.py`)
- **Purpose**: Additional SEC filing capabilities
- **Features**: Enhanced text processing, metadata extraction

### Configuration System

#### Central Configuration (`common_config.yml`)
- **Purpose**: Shared logging and system settings
- **Features**: Environment-specific configurations

#### Job Configurations (`data/config/*.yml`)
- **Purpose**: Control data collection parameters
- **Examples**: `yfinance_nasdaq100.yml`, `sec_edgar_m7.yml`
- **Features**: Ticker lists, date ranges, data types

### Management Layer

#### Management Interface (`manage.py`)
- **Purpose**: User-friendly command interface
- **Commands**: build, status, validate, clean, setup
- **Features**: Progress tracking, error reporting

#### Knowledge Base Builder (`build_knowledge_base.py`)
- **Purpose**: Automated data pipeline orchestration
- **Features**: Tier management, dependency handling
- **Architecture**: Modular, extensible design

## Data Flow Architecture

```
1. Configuration → 2. Data Collection → 3. Raw Storage → 4. Processing → 5. Graph Database
     ↓                    ↓                  ↓              ↓              ↓
Job Config         Yahoo Finance      data/original/   SEC Parser     Neo4j Graph
Files           + SEC Edgar APIs      JSON Files     + Validation   + neomodel ORM
```

## Important Reference Data

### Magnificent 7 CIK Numbers
- **Apple (AAPL)**: 0000320193
- **Microsoft (MSFT)**: 0000789019
- **Amazon (AMZN)**: 0001018724
- **Alphabet (GOOGL)**: 0001652044
- **Meta (META)**: 0001326801
- **Tesla (TSLA)**: 0001318605
- **Netflix (NFLX)**: 0001065280

### Directory Structure
```
data/
├── original/          # Raw collected data
│   ├── yfinance/     # Yahoo Finance data by ticker
│   └── sec/          # SEC Edgar filings by ticker
├── config/           # Job configuration files
└── log/              # Processing and build logs
```

## Technology Stack

### Core Technologies
- **Python 3.12**: Primary development language
- **pipenv**: Dependency management
- **Neo4j**: Graph database
- **neomodel**: Python ORM for Neo4j
- **BeautifulSoup**: HTML/XML parsing
- **Ansible**: Environment automation

### Development Tools  
- **Git**: Version control with mandatory issue association
- **GitHub Issues**: Project management and tracking
- **Conda**: Cross-platform environment management
- **pytest**: Testing framework (planned)

## Scalability Considerations

### Performance Optimization
- **Parallel Processing**: Multi-threaded data collection
- **Incremental Updates**: Only collect new/changed data
- **Efficient Storage**: JSON with compression for large datasets
- **Database Indexing**: Optimized Neo4j indexes for queries

### Resource Requirements
- **Development**: 8GB RAM, 4 CPU cores
- **Production**: 16GB+ RAM, SSD storage
- **Network**: Stable connection for API access
- **Storage**: Varies by tier (500MB - 50GB)

## Security and Compliance

### Data Handling
- **Public Data Only**: All data from public APIs and filings
- **Rate Limiting**: Respectful API usage
- **Error Handling**: Graceful failure and retry mechanisms
- **Logging**: Comprehensive audit trails

### Access Control
- **No Authentication Required**: Public data sources
- **Local Storage**: All data stored locally
- **Privacy**: No personal or proprietary data collected