# Project Architecture

## Refactored Top-Level Directory Architecture

Clear layered architecture based on data flow and separation of responsibilities:

```
my_finance/
├── ETL/           # Data processing pipeline: web scrapers, data processing & cleaning
├── dts/           # Data transfer service: abstract data I/O, storage abstraction
├── dcf_engine/    # DCF valuation engine: strategy logic, model calculations
├── evaluation/    # Evaluation toolkit: backtesting, LLM evaluation, performance analysis
├── common/        # Common components: module coordination, schema definitions, utilities
├── infra/         # Infrastructure: environment management, deployment, monitoring
├── data/          # Data storage: sample data, configuration documents
├── tests/         # Testing framework: unit tests, integration tests
└── graph_rag/     # Graph RAG components: intelligent queries and reasoning
```

## Data Flow Architecture

```
Raw Data Sources → ETL → DTS → DCF Engine → Evaluation
    ↓        ↓         ↓        ↓           ↓
  YFinance  Spider   Data Layer Strategy Engine Backtesting
  SEC Edgar Parsing   Cache    Model Calc   Performance
            Cleaning  Abstract Risk Analysis LLM Evaluation
```

## Core Component Responsibilities

### 📊 ETL - Data Processing Pipeline
**Responsibility**: Web scraping, data processing & cleaning from raw data to structured output
- **Data Collection**: YFinance, SEC Edgar spiders
- **Data Parsing**: Document parsing, format conversion
- **Data Cleaning**: Quality checks, standardization
- **Data Building**: Multi-tier dataset construction

### 🔌 DTS - Data Transfer Service  
**Responsibility**: Data import/export with online databases, abstracting infrastructure details for dcf_engine
- **Data Abstraction**: Unified data access interface
- **Multi-source Adaptation**: Support for Neo4j, MySQL, Redis, etc.
- **Cache Management**: Intelligent caching for performance
- **Connection Pool**: Optimized database connection usage

### 🎯 DCF Engine - Valuation Engine
**Responsibility**: Data input/output focused, concentrate on strategy logic
- **DCF Calculation**: Multiple valuation model implementations
- **Strategy Validation**: Historical backtesting, statistical testing
- **Knowledge Graph**: Graph RAG enhanced analysis
- **Result Generation**: Report and analysis output

### 📈 Evaluation - Evaluation Toolkit
**Responsibility**: LLM templates, strategy backtesting toolkit, performance evaluation
- **Strategy Backtesting**: Historical performance validation
- **LLM Evaluation**: Prompt and response quality assessment
- **Performance Metrics**: Return, risk, stability analysis
- **可视化**: 结果展示和报告

### 🔧 Common - 公共组件
**职责**: 管理模块交互，定义Schema和共享工具
- **Schema定义**: 数据结构标准
- **模块协调**: 组件间通信
- **工具库**: 日志、配置、工具函数
- **元数据管理**: 数据血缘和生命周期

### 🏗️ Infra - 基础设施
**职责**: 全局性基础设施，环境和部署
- **环境管理**: Docker、K8s、数据库
- **部署自动化**: Ansible、CI/CD
- **开发工具**: Git工具、代码质量
- **监控运维**: 系统监控、日志管理

## 设计原则

### 1. 数据流清晰
- **单向数据流**: ETL → DTS → DCF Engine → Evaluation
- **责任分离**: 每个组件专注自己的核心职责
- **接口标准化**: 通过common定义标准接口

### 2. 模块解耦
- **独立部署**: 每个组件可独立开发和部署
- **接口抽象**: 通过DTS抽象数据访问
- **配置驱动**: 行为通过配置文件控制

### 3. 可扩展性
- **水平扩展**: 支持多实例部署
- **插件化**: 支持新增数据源和策略
- **版本管理**: 组件版本独立管理

### 4. 运维友好
- **监控完整**: 全链路监控和告警
- **日志结构化**: 便于分析和调试
- **自动化**: 部署、测试、运维自动化

## 使用场景

### 开发人员
```bash
# 数据处理
p3 build run m7              # ETL数据构建
pixi run metadata-rebuild      # 元数据管理

# 策略开发  
pixi run dcf-analysis          # DCF分析
pixi run validate-strategy     # 策略验证

# 环境管理
p3 env status            # 环境检查
p3 shutdown-all          # 服务关闭
```

### 运维人员
```bash
# 部署管理
ansible-playbook infra/ansible/setup.yml
kubectl apply -f infra/k8s/

# 监控运维
python infra/env_status.py
python infra/monitoring.py
```

### 研究人员
```bash
# 策略评估
python evaluation/backtest_engine.py
python evaluation/llm_evaluator.py

# 数据分析
python dcf_engine/demo_graph_rag.py
python graph_rag/semantic_retriever.py
```

## 升级优势

1. **架构清晰**: 一级目录直接体现业务流程
2. **职责明确**: 每个组件专注核心功能  
3. **易于理解**: 新人可快速理解项目结构
4. **便于维护**: 模块化降低维护成本
5. **扩展友好**: 支持新增功能和组件