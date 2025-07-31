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
- **Python 3.12+**
- **Conda** (recommended for cross-platform consistency)
- **8GB+ RAM** (16GB+ recommended for full datasets)

### 1. Environment Setup
```bash
git clone git@github.com:wangzitian0/my_finance.git
cd my_finance

# Cross-platform setup with conda
conda create -n finance python=3.12 openjdk=17 -c conda-forge
conda activate finance
pip install pipenv
pipenv install

# Alternative: Automated setup (requires sudo)
ansible-playbook ansible/init.yml --ask-become-pass
```

### 2. Data Management
```bash
# Activate environment
pipenv shell

# Three-tier data strategy:
python manage.py build m7           # Tier 1: Stable test (500MB, git-tracked)
python manage.py build nasdaq100    # Tier 2: Extended (5GB, buildable) 
python manage.py build us-all       # Tier 3: Complete (50GB, buildable)

# Management commands
python manage.py status             # Check current data status
python manage.py validate           # Validate data integrity
```

### 3. Database and Analysis
```bash
# Start Neo4j database
ansible-playbook ansible/setup.yml

# Run data collection jobs
python run_job.py                          # Default M7 dataset
python run_job.py yfinance_nasdaq100.yml   # NASDAQ100 prices
python run_job.py sec_edgar_m7.yml         # SEC filings

# Future: DCF analysis (Phase 1 development)
# python -m dcf.analyze --ticker AAPL
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
# Install development dependencies
pipenv install --dev
pipenv shell

# Find Python interpreter path for IDE configuration
pipenv --py
```

### Architecture

**Three-Tier Data Strategy**: M7 (git-tracked) → NASDAQ100 (buildable) → US-ALL (buildable)

**Core Components**: Data spiders, Neo4j graph database, SEC parsing, management tools

See [docs/architecture.md](docs/architecture.md) for detailed architecture and component documentation.

### Git Workflow

**MANDATORY**: All changes must be associated with GitHub Issues. See [docs/development-setup.md](docs/development-setup.md) for complete workflow details.

```bash
git checkout -b feature/description-fixes-N
git commit -m "Brief description\n\nFixes #issue-number"
gh pr create --title "Feature - Fixes #issue-number" --body "Summary"
```

### Testing

Validation through manual testing and output verification. See [docs/data-validation.md](docs/data-validation.md) for testing procedures.

## 📋 Development Roadmap

**Phase 1**: MVP Core (DCF + Graph RAG)
**Phase 2**: Complete System (Web Interface + Scaling)
**Phase 3**: Production Optimization

See [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md) for detailed roadmap and milestones.

## 🤝 Contributing

1. **Create Issue**: Describe the feature or bug with appropriate labels (P0/P1/P2, MVP, etc.)
2. **Create Branch**: `git checkout -b feature/description-fixes-N`
3. **Develop**: Follow existing patterns, use pipenv for dependencies
4. **Test**: Verify data collection and processing functionality
5. **PR**: Link to issue, ensure all commits reference issue numbers

**Branch Naming**: `feature/`, `bugfix/`, `refactor/` + `description-fixes-N`

## 📚 Documentation

### Core Documentation
- [**Architecture**](docs/architecture.md) - System design and component details
- [**Development Setup**](docs/development-setup.md) - Complete development workflow
- [**Data Schema**](docs/data-schema.md) - Database models and data structures
- [**Project Roadmap**](docs/PROJECT_ROADMAP.md) - Detailed development phases

### Technical Documentation
- [**DCF Engine**](docs/dcf-engine.md) - Valuation calculation system
- [**Graph RAG**](docs/graph-rag.md) - Knowledge graph and semantic search
- [**Data Validation**](docs/data-validation.md) - Testing and quality assurance
- [**CI Strategy**](docs/ci-strategy.md) - Continuous integration approach

### Operations
- [**Deployment**](docs/deployment.md) - Production deployment guide
- [**Monitoring**](docs/monitoring.md) - System monitoring and observability
- [**API Documentation**](docs/api-docs.md) - API endpoints and usage

## 📊 Performance

**Hardware**: 4+ CPU cores, 16GB+ RAM, SSD storage recommended  
**Data Sizes**: M7 (~500MB), NASDAQ100 (~5GB), US-ALL (~50GB)

See [docs/deployment.md](docs/deployment.md) for detailed performance requirements.

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **Data Repository**: [my_finance_data](https://github.com/wangzitian0/my_finance_data) (git submodule)
- **Issue Tracking**: [GitHub Issues](https://github.com/wangzitian0/my_finance/issues)
- **Documentation Index**: All technical details available in [docs/](docs/) directory

---

**Built with ❤️ for intelligent investment analysis**