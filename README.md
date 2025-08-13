# Financial Strategy Engine

**A Graph RAG-powered DCF valuation and investment analysis system**

## What This Does

This system analyzes financial data to generate:
- **DCF Valuations**: Intrinsic value calculations for stocks
- **Investment Recommendations**: Buy/Hold/Sell decisions with confidence scores  
- **Risk Analysis**: Multi-factor risk assessments
- **Strategy Validation**: Performance tracking against market benchmarks

## Quick Start

```bash
# Setup (once)  
p3 env-setup                 # Install Podman, Neo4j, dependencies

# Daily workflow with P3 system
pixi shell                   # Enter environment
p3 build                     # Fast F2 build & analysis  
p3 dcf-m7                    # Full M7 DCF analysis
p3 release                   # Create release
p3 env-stop                  # Clean shutdown

# Additional commands (if needed)
p3 validate-strategy         # Legacy strategy validation
p3 generate-report           # Legacy report generation  
```

### P3 Alias System 🚀

Use short commands for faster development:

```bash
# Core Development
p3 build          # Fast build (F2)
p3 test           # Run tests
p3 lint           # Code formatting
p3 clean          # Cleanup builds
p3 status         # Environment status

# DCF Analysis  
p3 dcf            # Quick DCF analysis
p3 dcf-f2         # Fast 2-company test
p3 dcf-m7         # Full Magnificent 7

# Environment (Ansible)
p3 env-start      # Start services
p3 env-stop       # Stop services  
p3 env-status     # Check environment
p3 env-reset      # Reset environment

# Release Management
p3 release        # Create release
p3 pr             # Create pull request
```

> **📖 Complete Commands**: See [CLAUDE.md](CLAUDE.md) for full command reference and development workflows.

## 系统架构

### 数据流架构
```
ETL → DTS → DCF Engine → Evaluation
 ↓     ↓        ↓          ↓
爬虫  数据层   策略引擎   回测评估
```

### 核心组件

- **`ETL/`** - 数据处理管道：爬虫、数据清洗、结构化处理
- **`dts/`** - 数据传输服务：抽象数据I/O，屏蔽存储细节
- **`dcf_engine/`** - DCF估值引擎：策略逻辑、模型计算
- **`evaluation/`** - 评估工具集：回测、LLM评估、性能分析

### 支撑组件

- **`common/`** - 公共组件：模块协调、Schema定义、工具库
- **`infra/`** - 基础设施：环境管理、部署、监控
- **`data/`** - 数据存储：样例数据、配置文档 
- **`tests/`** - 测试框架：单元测试、集成测试

## Essential Commands

### Core Operations
```bash
p3 build-m7                  # Build M7 dataset with DCF analysis
p3 validate-strategy         # Run strategy validation (legacy)
p3 generate-report           # Create validation report (legacy)  
p3 update-stock-lists        # Update NASDAQ-100 and VTI stock lists
```

### Development & Testing
```bash
p3 dcf-f2                    # Fast 2-company DCF test
p3 dcf-m7                    # Full M7 DCF analysis
p3 lint                      # Format & check code quality
p3 test                      # Run complete test suite
```

### Environment
```bash
p3 status                    # Check environment health
p3 env-status                # Detailed environment status  
p3 env-stop                  # Stop all services
```

> **⚙️ Advanced Commands**: See [CLAUDE.md](CLAUDE.md) for complete command reference, development workflows, and testing strategies.

## Strategy Reports

Each validation run generates reports stored in `data/reports/`:
- **Strategy Performance**: Returns, volatility, Sharpe ratio
- **Stock Analysis**: Individual DCF valuations and recommendations  
- **Risk Assessment**: Factor exposures and risk metrics
- **Benchmark Comparison**: Performance vs market indices

## Architecture

```
Data Sources → Neo4j Graph → Strategy Engine → Validation → Reports
    ↓              ↓              ↓              ↓         ↓
  YFinance      Companies     DCF Models    Backtesting  JSON/HTML
  SEC Edgar     Financials    Risk Engine   Benchmarks   Dashboards
```

## Installation Details

**Prerequisites**: Docker, Pixi ([install guide](https://pixi.sh/latest/))

**Full Setup**:
```bash
p3 env-setup                 # Installs Podman, Neo4j, dependencies
```

This creates a complete environment with Podman containers, Neo4j graph database, and all Python dependencies isolated in Pixi.

**Troubleshooting**: Use `p3 env-reset` to start fresh if needed.

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
- **[Local LLM](local_llm/README.md)** - Local language model integration