# My Finance DCF Analysis Tool

A comprehensive **Graph RAG-powered DCF valuation system** that leverages SEC filings and multi-source financial data to perform intelligent investment analysis with automated parameter determination.

## 🚀 Features

- **📊 DCF Valuation Engine**: Automated discounted cash flow analysis with bankruptcy probability assessment
- **🕸️ Graph RAG System**: Neo4j-powered knowledge graph with semantic search capabilities  
- **📋 SEC Filing Integration**: Automated collection and parsing of 10-K, 10-Q, and 8-K filings
- **🔄 Multi-Source Data Validation**: Yahoo Finance, SEC Edgar, and extensible data pipeline
- **🎯 Zero-Config Design**: Knowledge-driven parameter determination without manual configuration
- **📱 Mobile-Friendly Web Interface**: Responsive design for investment analysis on-the-go
- **⚡ Layered Data Management**: Smart 3-tier architecture optimizing for development and production

## 🏗️ Architecture Overview

### Three-Tier Data Management Strategy
- **Tier 1 (M7)**: Magnificent 7 companies - stable test dataset (~500MB, git-tracked)
- **Tier 2 (NASDAQ100)**: Extended validation dataset (~5GB, buildable)  
- **Tier 3 (US-ALL)**: Complete US stock universe (~50GB, buildable)

### Core Components
- **Data Collection**: `spider/` - Yahoo Finance and SEC Edgar data acquisition
- **Graph Database**: `ETL/` - Neo4j models and import scripts using neomodel ORM
- **Document Parsing**: `parser/` - SEC filing XML/SGML processing with BeautifulSoup
- **RAG Pipeline**: Graph-powered retrieval with semantic embedding search
- **Web Interface**: Mobile-responsive DCF analysis dashboard

## 🛠️ Quick Start

### Prerequisites
- **8GB+ RAM** (16GB+ recommended)
- **Internet connection** (for conda installation)
- **Bash-compatible shell** (macOS/Linux/WSL)

### 1. Automated Cross-Platform Setup
```bash
git clone git@github.com:wangzitian0/my_finance.git
cd my_finance

# One-command cross-platform setup (no sudo required!)
ansible-playbook ansible/init.yml
```

**What this does:**
- ✅ Installs Miniconda (if not present)  
- ✅ Creates `finance` conda environment with Python 3.12 + OpenJDK 17
- ✅ Installs all Python dependencies via conda + pip
- ✅ Downloads and configures Neo4j with proper Java environment
- ✅ Sets up git submodules and project structure

### 2. Activate Environment & Build Knowledge Base
```bash
# Activate the finance conda environment
source activate-finance.sh

# Build stable test dataset (M7 companies)
python manage.py build m7

# Check data status
python manage.py status

# Optional: Build extended datasets
python manage.py build nasdaq100    # ~5GB download
python manage.py build us-all       # ~50GB download
```

### 3. Start Analysis
```bash
# Start Neo4j database (from project root)
./neo4j/bin/neo4j-service start

# Verify Neo4j is running
./neo4j/bin/neo4j-service status

# Run DCF analysis (coming in Phase 1)
python -m dcf.analyze --ticker AAPL
```

## 📊 Data Management

### Management Commands
```bash
python manage.py build m7           # Build core test dataset
python manage.py validate           # Validate data integrity  
python manage.py status             # Show current status
python manage.py clean nasdaq100    # Clean old data (keep 30 days)
python manage.py setup              # Initial project setup
```

### Data Collection Jobs
```bash
# Individual data collection
python run_job.py                          # Default M7 dataset
python run_job.py yfinance_nasdaq100.yml   # NASDAQ100 prices
python run_job.py sec_edgar_m7.yml         # M7 SEC filings
```

## 🎯 Target Companies

### Magnificent 7 (Core Test Set)
- **Apple (AAPL)** - CIK: 0000320193
- **Microsoft (MSFT)** - CIK: 0000789019  
- **Amazon (AMZN)** - CIK: 0001018724
- **Alphabet (GOOGL)** - CIK: 0001652044
- **Meta (META)** - CIK: 0001326801
- **Tesla (TSLA)** - CIK: 0001318605
- **Netflix (NFLX)** - CIK: 0001065280

## 🗂️ Project Structure

```
my_finance/
├── dcf/                    # DCF valuation engine (Phase 1)
├── rag/                    # Graph RAG system (Phase 1)  
├── web/                    # Web interface (Phase 2)
├── spider/                 # Data collection spiders
│   ├── yfinance_spider.py  # Yahoo Finance data
│   └── sec_edgar_spider.py # SEC Edgar filings
├── ETL/                    # Neo4j database layer
│   ├── models.py           # Graph database models
│   └── import_data.py      # Data import scripts
├── parser/                 # Document processing
│   ├── sec_parser.py       # SEC filing parser
│   └── rcts.py             # Advanced text processing
├── data/                   # Data directory (git submodule)
│   ├── config/             # Job configurations
│   ├── original/           # Raw collected data
│   └── log/                # Build and processing logs
├── ansible/                # Environment automation
├── docs/                   # Documentation
├── build_knowledge_base.py # Layered data builder
└── manage.py               # Management interface
```

## 🔧 Development

### Environment Setup
```bash
# Activate conda environment (always first!)
source activate-finance.sh

# All development tools are pre-installed:
# - Python 3.12, OpenJDK 17, pipenv
# - black, isort, pylint, mypy, pytest

# Find Python path for IDE setup
conda info --envs
# Use: ~/miniconda3/envs/finance/bin/python
```

### Code Quality
```bash
# Activate environment first
source activate-finance.sh

# Format and lint (all tools pre-installed)
black .
isort .
pylint src/
mypy src/

# Run tests (when available)
pytest tests/ -v --cov=src/
```

### Cross-Platform Benefits
- **✅ No platform-specific package managers** (apt/homebrew/yum)
- **✅ Consistent Python + Java versions** across macOS/Linux/Windows
- **✅ Isolated environment** - no system pollution
- **✅ Reproducible builds** - same conda environment everywhere
- **✅ Easy CI/CD integration** - single conda environment file

### GoLand Integration
Create commits with clickable PR links:
```bash
git commit -m "Feature description

Fixes #issue-number

PR: https://github.com/wangzitian0/my_finance/pull/TBD"
```

## 📋 Development Roadmap

### Phase 1: MVP Core Capabilities (4-6 weeks)
- [ ] **Issue #20**: Extend Neo4j schema for SEC filings and DCF calculations
- [ ] **Issue #21**: Implement Graph RAG pipeline with semantic search  
- [ ] **Issue #22**: Build basic DCF valuation engine with parameter extraction

### Phase 2: Complete System (6-8 weeks)
- [ ] Mobile-responsive web interface
- [ ] Advanced Graph RAG with multi-hop reasoning
- [ ] Real-time data updates and monitoring
- [ ] Comprehensive DCF scenario analysis

### Phase 3: Production Optimization (Continuous)
- [ ] Performance optimization and caching
- [ ] Advanced analytics and reporting
- [ ] API endpoints for external integration

## 🤝 Contributing

This project follows GitHub flow with mandatory issue association:

1. **Create Issue**: Describe the feature or bug
2. **Create Branch**: `git checkout -b feature/description-fixes-N`  
3. **Develop**: Follow existing code patterns and conventions
4. **Test**: Ensure data collection and processing work correctly
5. **PR**: Link to issue with descriptive summary

### Branch Naming Convention
- `feature/description-fixes-N` - New features
- `bugfix/description-fixes-N` - Bug fixes  
- `refactor/description-fixes-N` - Code refactoring

## 📊 Performance

### Recommended Hardware
- **CPU**: 4+ cores for parallel data processing
- **RAM**: 16GB+ for large dataset handling
- **Storage**: SSD for optimal Neo4j performance
- **Network**: Stable connection for SEC Edgar API access

### Data Size Estimates
- **M7 Dataset**: ~500MB (7 companies, 3 years of data)
- **NASDAQ100**: ~5GB (100 companies, 3 years of data)  
- **US-ALL**: ~50GB (8000+ companies, 3 years of data)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **Data Repository**: [my_finance_data](https://github.com/wangzitian0/my_finance_data) (git submodule)
- **SEC Parser Library**: Enhanced XML/SGML processing for financial documents
- **Graph RAG Framework**: Neo4j-powered semantic search and reasoning

---

**Built with ❤️ for intelligent investment analysis**
** END **
