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
pixi run setup-env

# Daily workflow
pixi shell                    # Enter environment
pixi run validate-strategy    # Run strategy validation
pixi run generate-report      # Create validation report
pixi run shutdown-all         # Clean shutdown
```

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

## Development Commands

### Strategy Operations
```bash
pixi run validate-strategy    # Run strategy validation suite
pixi run generate-report      # Create validation report  
pixi run backtest            # Run historical performance test
pixi run benchmark           # Compare against market indices
```

### Development Tools
```bash
pixi run build-m7            # Build test dataset
pixi run format              # Format code
pixi run lint                # Code quality check
pixi run test                # Run test suite
```

### Environment Management
```bash
pixi run env-status          # Check environment health
pixi run env-start           # Start services
pixi run shutdown-all        # Stop all services
```

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
pixi run setup-env           # Installs Minikube, Neo4j, dependencies
```

This creates a complete environment with Kubernetes, Neo4j graph database, and all Python dependencies isolated in Pixi.

**Troubleshooting**: Use `pixi run env-reset` to start fresh if needed.

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