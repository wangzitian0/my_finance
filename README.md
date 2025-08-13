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
pixi run setup-env

# Daily workflow
pixi shell                    # Enter environment
pixi run env-status           # Check environment health
pixi run build-m7             # Build test dataset with SEC filings
pixi run validate-strategy    # Run strategy validation
pixi run generate-report      # Create validation report with SEC citations
pixi run shutdown-all         # Clean shutdown
```

## 系统架构

### 数据流架构
```
SEC Edgar + YFinance → ETL → Graph RAG → DCF Engine → Evaluation
        ↓                ↓       ↓          ↓          ↓
   SEC Filing Data    数据层  语义检索   策略引擎   回测评估
```

### 核心组件

- **`ETL/`** - 数据处理管道：SEC文档爬虫、语义嵌入、数据清洗
- **`dcf_engine/`** - SEC增强DCF引擎：语义检索、引用管理、估值模型
- **`graph_rag/`** - 图形检索增强生成：SEC文档语义搜索、相关性排序
- **`evaluation/`** - 评估工具集：回测、LLM评估、性能分析

### 支撑组件

- **`common/`** - 公共组件：模块协调、Schema定义、构建追踪
- **`infra/`** - 基础设施：Pixi环境管理、Ansible自动化、Podman容器
- **`data/`** - 分阶段数据存储：SEC文档、嵌入向量、构建清单
- **`spider/`** - 数据爬虫：SEC Edgar API、YFinance集成
- **`parser/`** - 文档解析：SEC文档结构化、财务数据提取

## Development Commands

### SEC-Enhanced DCF Operations
```bash
pixi run build-m7             # Build M7 dataset with SEC filings (336 documents)
pixi run validate-strategy    # Run SEC-backed DCF validation suite
pixi run generate-report      # Create validation report with SEC citations
pixi run dcf-analysis         # Generate Pure LLM DCF reports
pixi run backtest             # Run historical performance test
```

### Development Tools
```bash
pixi run format              # Format code with black + isort
pixi run lint                # Code quality check with pylint
pixi run typecheck           # Type checking with mypy
pixi run test                # Run test suite with pytest
pixi run create-pr           # Create PR with automated M7 testing
```

### Environment Management (Pixi + Ansible)
```bash
pixi run setup-env           # Complete environment setup (Podman + Neo4j)
pixi run env-status          # Check environment health (all services)
pixi run env-start           # Start all services (Podman + Neo4j)
pixi run env-stop            # Stop services gracefully
pixi run shutdown-all        # Complete shutdown with cleanup
pixi run env-reset           # Reset environment (destructive)
```

### Data Pipeline Operations
```bash
pixi run build-dataset f2    # Fast build (2 tickers)
pixi run build-dataset m7    # Magnificent 7 build (7 tickers + SEC data)
pixi run build-dataset n100  # NASDAQ 100 build 
pixi run build-dataset v3k   # Full VTI build (3500 tickers)
pixi run create-build        # Create timestamped build
pixi run release-build       # Promote build to release
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
pixi run setup-env           # Podman + Neo4j + Python ML stack + SEC data
```

**What gets installed**:
- **Podman machine** with Neo4j graph database
- **Python 3.12** with ML dependencies (PyTorch, scikit-learn, transformers)
- **SEC data pipeline** with semantic embedding capabilities
- **Development tools** (linting, formatting, testing)

**Verification**:
```bash
pixi run env-status          # Check all services
pixi run build-m7            # Test with Magnificent 7 dataset
```

**Troubleshooting**: Use `pixi run env-reset` for complete clean reset.

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
pixi run dcf-analysis

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
