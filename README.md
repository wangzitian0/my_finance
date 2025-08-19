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

```bash
# Setup (once)
p3 env setup

# Daily workflow
pixi shell                    # Enter environment (managed by pixi)
p3 e2e                        # Quick validation (end-to-end)
p3 refresh m7                 # Build test dataset with SEC filings
./p3 pr "Description" 81      # If p3 not in PATH, run local script
p3 clean                      # Clean local build artifacts
p3 shutdown-all               # Clean shutdown
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

- **`ETL/`** - Data Processing Pipeline: SEC document crawling, semantic embedding, data cleaning
- **`dcf_engine/`** - SEC-Enhanced DCF Engine: Semantic retrieval, citation management, valuation models
- **`graph_rag/`** - Graph Retrieval-Augmented Generation: SEC document semantic search, relevance ranking
- **`evaluation/`** - Evaluation Toolkit: Backtesting, LLM evaluation, performance analysis

### Supporting Components

- **`common/`** - Common Components: Module coordination, schema definition, build tracking
- **`infra/`** - Infrastructure: Pixi environment management, Ansible automation, Podman containers
- **`data/`** - Staged Data Storage: SEC documents, embedding vectors, build manifests
- **`spider/`** - Data Crawlers: SEC Edgar API, YFinance integration
- **`parser/`** - Document Parsing: SEC document structuring, financial data extraction

## Development Commands

### SEC-Enhanced DCF Operations
```bash
p3 refresh m7               # Build M7 dataset with SEC filings (336 documents)
p3 dcf-analysis             # Generate Pure LLM DCF reports
p3 backtest                 # Run historical performance test
```

### Development Tools
```bash
p3 format                   # Format code with black + isort
p3 lint                     # Code quality check with pylint
p3 typecheck                # Type checking with mypy
p3 test                     # Run test suite with pytest
p3 create-pr                # Create PR with automated M7 testing
```

### Environment Management (Pixi + Ansible)
```bash
p3 env setup               # Complete environment setup (Podman + Neo4j)
p3 env status              # Check environment health (all services)
p3 env start               # Start all services (Podman + Neo4j)
p3 env stop                # Stop services gracefully
p3 shutdown-all            # Complete shutdown with cleanup
p3 env reset               # Reset environment (destructive)
```

### Data Pipeline Operations
```bash
p3 refresh f2              # Fast build (2 tickers)
p3 refresh m7              # Magnificent 7 build (7 tickers + SEC data)
p3 refresh n100            # NASDAQ 100 build 
p3 refresh v3k             # Full VTI build (3500 tickers)
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
p3 env setup                 # Podman + Neo4j + Python ML stack + SEC data
```

**What gets installed**:
- **Podman machine** with Neo4j graph database
- **Python 3.12** with ML dependencies (PyTorch, scikit-learn, transformers)
- **SEC data pipeline** with semantic embedding capabilities
- **Development tools** (linting, formatting, testing)

**Verification**:
```bash
p3 env status                # Check all services
p3 build-m7                  # Test with Magnificent 7 dataset
```

**Troubleshooting**: Use `p3 env reset` for complete clean reset.

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
- **[Data Collection](spider/README.md)** - YFinance and SEC Edgar spiders
- **[Data Management](common/README.md)** - Metadata system and utilities  
- **[Build System](scripts/README.md)** - Dataset building and management
- **[Data Pipeline](data/README.md)** - ETL structure and four-tier dataset strategy

### Component Documentation
- **[ETL Processing](ETL/README.md)** - Data processing and transformation
- **[Graph RAG](graph_rag/README.md)** - Retrieval-augmented generation
- **[Local LLM](local_llm/README.md)** - Local language model integration# Test trigger
