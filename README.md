# Financial Strategy Engine

**A Graph RAG-powered DCF valuation and investment analysis system**

## What This Does

This system analyzes financial data to generate:
- **SEC Filing-Enhanced DCF Valuations**: Intrinsic value calculations backed by official SEC filings
- **Investment Recommendations**: Buy/Hold/Sell decisions with regulatory-backed confidence scores  
- **Risk Analysis**: Multi-factor risk assessments using SEC risk factor disclosures
- **Strategy Validation**: Performance tracking against market benchmarks
- **Graph RAG Integration**: Semantic retrieval of SEC filing data for DCF assumptions

## Quick Start

### ⚡ Unified p3 Command System

All operations use the unified `p3` command interface:

```bash
# Setup (once)
p3 env-setup                   # Complete environment setup

# Daily workflow  
p3 activate                    # Enter pixi environment
p3 e2e                         # Quick validation (end-to-end)
p3 build m7                    # Build test dataset with SEC filings
p3 create-pr "Description" 111 # Create PR with automated testing
p3 clean                       # Clean local build artifacts
p3 shutdown-all                # Clean shutdown
```

### 🔧 Shell Integration (Optional)

Add to your `~/.zshrc` for tab completion:
```bash
# Simple one-line setup
source /path/to/my_finance/scripts/p3-completion.zsh
```

Then enjoy tab completion:
```bash
p3 <TAB>           # Shows all available commands
p3 build <TAB>     # Shows scope options (f2/m7/n100/v3k)
p3 env-<TAB>       # Shows environment commands
```

## System Architecture

### Data Flow Architecture
```
SEC Edgar + YFinance → ETL → Graph RAG → DCF Engine → Evaluation
        ↓                ↓       ↓          ↓          ↓
   SEC Filing Data   Data Layer Semantic   Strategy  Backtesting
                                Retrieval  Engine    Evaluation
```

### Core Components

- **`ETL/`** - Data Processing Pipeline: SEC/YFinance spiders, document parsing, semantic embedding, data cleaning
- **`dcf_engine/`** - SEC-Enhanced DCF Engine: Semantic retrieval, citation management, valuation models
- **`graph_rag/`** - Graph Retrieval-Augmented Generation: SEC document semantic search, relevance ranking
- **`evaluation/`** - Evaluation Toolkit: Backtesting, LLM evaluation, performance analysis

### Supporting Components

- **`common/`** - Common Components: Module coordination, schema definition, build tracking
- **`infra/`** - Infrastructure: Pixi environment management, Ansible automation, Podman containers
- **`data/`** - Staged Data Storage: SEC documents, embedding vectors, build manifests
- **`scripts/`** - Utility Scripts: Build management, configuration updates, system maintenance
- **`templates/`** - Template System: DCF prompts, configuration templates, standardized formats
- **`tests/`** - Test Suite: Unit tests, integration tests, end-to-end validation

## Unified Command Interface

### 🎯 All Commands Through p3

**The system provides a unified `p3` command interface** that routes all operations through the proper environment:

### 📊 Analysis & Reporting
```bash
p3 build m7                 # Build M7 dataset with SEC filings (336 documents)
p3 fast-build f2            # Fast build with DeepSeek 1.5b (development)
p3 dcf-analysis             # Generate Pure LLM DCF reports
p3 generate-report          # Generate comprehensive analysis reports
p3 backtest                 # Run historical performance test
```

### 🛠️ Development Tools
```bash
p3 format                   # Format code with black + isort
p3 lint                     # Code quality check with pylint  
p3 typecheck                # Type checking with mypy
p3 test                     # Run test suite with pytest
p3 e2e                      # End-to-end validation (F2 fast mode)
p3 create-pr "Title" ISSUE  # Create PR with automated testing
```

### 🌐 Environment Management
```bash
p3 env-setup               # Complete environment setup (Podman + Neo4j)
p3 env-status              # Check environment health (all services)
p3 env-start               # Start all services (Podman + Neo4j)
p3 env-stop                # Stop services gracefully  
p3 shutdown-all            # Complete shutdown with cleanup
p3 env-reset               # Reset environment (destructive)
```

### 📈 Scope-Based Data Pipeline
```bash
# Build commands support scope parameters:
p3 build f2                # Fast build (2 companies) - development
p3 build m7                # Magnificent 7 (7 companies) - standard/PR testing
p3 build n100              # NASDAQ 100 (validation testing)
p3 build v3k               # VTI 3500+ (production testing)

# Fast build variants (with DeepSeek 1.5b):
p3 fast-build f2           # Accelerated F2 build for development
p3 fast-build m7           # Accelerated M7 build for testing
```

### 💡 Command Discovery

```bash
p3 --help                  # Complete command documentation
p3 status                  # Quick environment health check
p3 <invalid-command>       # Shows available commands
p3 build --help            # Scope-specific help
```

## SEC-Enhanced Strategy Reports

Each validation run generates comprehensive reports with SEC filing citations:
- **SEC-Backed DCF Valuations**: Intrinsic value calculations with regulatory backing
- **Cited Investment Recommendations**: Buy/Hold/Sell with SEC filing support
- **Risk Assessment**: Factor analysis using SEC risk factor disclosures
- **Management Guidance Integration**: Forward-looking assumptions from 10-K/10-Q filings
- **Build Tracking**: Complete lineage of data sources and processing steps

## Graph RAG Architecture

```
SEC Edgar API → Document Parser → Semantic Embeddings → Vector Search → DCF Engine
     ↓              ↓                     ↓                  ↓            ↓
 10-K/10-Q/8-K   Text Extract      Sentence Transformers   FAISS     Cited Analysis
   Filings      Financial Data        384-dim Vectors    Similarity  SEC References
```

### Data Flow Pipeline

```
Stage 0: Original Data Collection (SEC Edgar + YFinance)
    ↓
Stage 1: Document Extraction (SEC filings, financial statements)
    ↓  
Stage 2: Data Transformation (text processing, embedding generation)
    ↓
Stage 3: Graph Loading (Neo4j nodes, vector indices, semantic cache)
    ↓
Stage 99: Build Management (timestamped releases, validation reports)
```

## Installation Details

**Prerequisites**: 
- **Pixi** ([install guide](https://pixi.sh/latest/)) - Cross-platform package manager
- **Docker/Podman** - Container runtime for Neo4j database

**Complete Setup**:
```bash
# Clone repository
git clone https://github.com/wangzitian0/my_finance.git
cd my_finance

# One-command setup (installs everything)
p3 env-setup                 # Podman + Neo4j + Python ML stack + SEC data
```

**What gets installed**:
- **Podman machine** with Neo4j graph database
- **Python 3.12** with ML dependencies (PyTorch, scikit-learn, transformers)
- **SEC data pipeline** with semantic embedding capabilities
- **Development tools** (linting, formatting, testing)

**Verification**:
```bash
p3 env-status                # Check all services
p3 build-m7                  # Test with Magnificent 7 dataset
```

**Troubleshooting**: Use `p3 env-reset` for complete clean reset.

## SEC Filing Integration

This system uniquely integrates SEC filing data directly into DCF valuations:

### Available SEC Data
- **Magnificent 7 Companies**: 336 SEC documents (10-K, 10-Q, 8-K filings)
- **Document Types**: Annual reports, quarterly filings, current reports
- **Date Range**: 2017-2025 comprehensive filing coverage
- **Processing**: Semantic embedding with 384-dimensional vectors

### Key Features
- **Regulatory Backing**: All DCF assumptions cite official SEC filings
- **Semantic Search**: Natural language queries across financial documents
- **Citation Management**: Transparent source attribution for compliance
- **Template System**: Standardized integration patterns for reproducibility

### Usage Examples
```bash
# Generate SEC-enhanced DCF report
p3 dcf-analysis

# View SEC integration templates
ls data/stage_99_build/sec_integration_examples/
ls data/stage_99_build/sec_recall_examples/
```

### Templates Included
- **SEC Integration Template**: `dcf_engine/sec_integration_template.py`
- **SEC Recall Usage Example**: `dcf_engine/sec_recall_usage_example.py`
- **Implementation Guide**: Complete production-ready examples
- **Citation Standards**: Compliance-ready reference formatting

## Documentation

### Architecture & Design
- **[Architecture Documentation](docs/README.md)** - System architecture and design documents
- **[ETL Structure Design](docs/ETL_STRUCTURE_DESIGN.md)** - Data pipeline architecture
- **[Project Roadmap](docs/PROJECT_ROADMAP.md)** - Development plan and milestones

### Implementation Guides
- **[Data Processing](ETL/README.md)** - Complete ETL pipeline with SEC/YFinance spiders and parsers
- **[Data Management](common/README.md)** - Metadata system and utilities  
- **[Build System](scripts/README.md)** - Dataset building and management
- **[Data Pipeline](data/README.md)** - ETL structure and four-tier dataset strategy

### Component Documentation
- **[Graph RAG](graph_rag/README.md)** - Retrieval-augmented generation
- **[DCF Engine](dcf_engine/README.md)** - SEC-enhanced valuation engine
- **[Evaluation](evaluation/README.md)** - Backtesting and performance analysis
- **[Infrastructure](infra/README.md)** - Environment setup and deployment
- **[Testing](tests/README.md)** - Test suite and validation
