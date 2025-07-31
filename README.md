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

## Installation and Setup

This project uses a hybrid approach for environment management to ensure both flexibility and consistency across platforms (Linux, macOS, Windows).

- **[Pixi](https://pixi.sh/)**: Manages all **application-level dependencies** (Python packages, etc.) in a cross-platform manner. It provides the core development environment.
- **[Ansible](https://www.ansible.com/)**: Manages all **system-level setup** (installing and configuring services like Neo4j). It prepares the machine for the application to run.

### Prerequisites

1.  **Pixi**: Install Pixi by following the [official instructions](https://pixi.sh/latest/).
2.  **Ansible**: Pixi will automatically install Ansible into the project environment, so no separate installation is needed.
3.  **Docker (Optional, Recommended)**: For the simplest setup, install [Docker Desktop](https://www.docker.com/products/docker-desktop/). The setup script will automatically use Docker for Neo4j if it's available.

### Setup Instructions

With Pixi installed, setting up the entire development environment is a single command. This command runs an Ansible playbook that intelligently handles system-level setup (like Neo4j) and then uses Pixi to install all application dependencies.

```bash
# This command will:
# 1. Install system dependencies like Neo4j (using Docker if available, otherwise manually).
# 2. Install all Python packages specified in pixi.toml.
# 3. Initialize data submodules.
pixi run setup-env
```

The `setup-env` task will prompt for a `sudo` password on Linux if it needs to perform a manual installation of Neo4j in `/opt`. On macOS, manual installation happens in the user's home directory and does not require `sudo`.

### Data Persistence

To ensure that your database data is not lost when the Docker container is removed or recreated, this project uses a **local bind mount**. The setup script automatically creates a `neo4j` directory inside the local `./data` folder and mounts it into the container.

-   `./data/neo4j/data`: Stores all the graph data.
-   `./data/neo4j/logs`: Stores Neo4j log files.

Because this data lives directly on your filesystem (within the project structure), it's easy to inspect, back up, or even move. The `.gitignore` file has been configured to **exclude the `/data/neo4j/` directory** from version control.

- **Reset the Database (Deletes all local data!)**:
  The `neo4j-remove` task has been configured to be destructive for easy resetting of the environment. It will not only stop and remove the container but also **permanently delete the local `./data/neo4j` directory**.

  ```bash
  # WARNING: This will delete all your local Neo4j data.
  pixi run neo4j-remove
  ```
  After running this, the next `pixi run setup-env` will recreate the directories and start a fresh, empty database.

## Development Environment

### Activating the Environment

To activate the shell with all the tools and dependencies ready to use, run:
```bash
pixi shell
```

### Key Management Tasks

The `pixi.toml` file contains a standardized set of tasks for managing the project.

#### Neo4j Database

The setup script handles the installation. Once set up, you can manage the Neo4j service with the following commands:

- **Start Neo4j**:
  ```bash
  pixi run neo4j-start
  ```
- **Check Status**:
  ```bash
  pixi run neo4j-status
  ```
- **Stop Neo4j**:
  ```bash
  pixi run neo4j-stop
  ```
- **Restart Neo4j**:
  ```bash
  pixi run neo4j-restart
  ```
- **Forcibly Kill Neo4j (if it gets stuck)**:
  ```bash
  pixi run neo4j-kill
  ```

#### Data and Application

- **Check Data Status**: See which datasets (M7, NASDAQ100, etc.) are downloaded.
  ```bash
  pixi run status
  ```
- **Build a Test Dataset**: Download data for the "Magnificent 7" stocks.
  ```bash
  pixi run build-m7
  ```
- **Run a Data Collection Job**:
  ```bash
  # Run the default job
  pixi run run-job
  # Run a specific job
  pixi run python run_job.py --config-path data/config/yfinance_nasdaq100.yml
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