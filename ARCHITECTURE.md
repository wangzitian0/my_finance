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
- **Visualization**: Result presentation and reporting

### 🔧 Common - Common Components
**Responsibility**: Manage module interactions, define schemas and shared utilities
- **Schema Definition**: Unified data models across components
- **Utility Functions**: Shared tools and helper functions
- **Module Coordination**: Inter-component communication
- **Configuration Management**: Centralized config handling

### 🏗️ Infra - Infrastructure
**Responsibility**: Environment management, containerized deployment, monitoring & alerting
- **Environment Management**: Ansible automated deployment
- **Containerization**: Service management using Podman
- **Database**: Neo4j graph database management
- **Monitoring**: System status and performance monitoring

### 🧪 Tests - Testing Framework
**Responsibility**: Quality assurance through comprehensive testing
- **Unit Testing**: Component-level testing
- **Integration Testing**: Cross-component validation
- **End-to-End Testing**: Full pipeline validation
- **Performance Testing**: Load and stress testing

### 🧠 Graph RAG - Knowledge Graph & RAG
**Responsibility**: Intelligent query processing and reasoning
- **Graph Database**: Knowledge representation in Neo4j
- **Semantic Retrieval**: Context-aware information retrieval
- **LLM Integration**: Natural language query processing
- **Reasoning Engine**: Intelligent analysis and insights

## Key Design Principles

1. **Separation of Concerns**: Each component has a clear, single responsibility
2. **Data Flow Driven**: Architecture follows natural data processing flow
3. **Modular Design**: Components are loosely coupled, highly cohesive
4. **Scalable**: Architecture supports horizontal and vertical scaling
5. **Testable**: Each component can be tested independently
6. **Configuration Driven**: Behavior controlled through external configuration
7. **Performance Oriented**: Optimized for financial data processing workloads

## Integration Patterns

- **Data Pipeline**: ETL → DTS → DCF Engine → Evaluation
- **Knowledge Enhancement**: Graph RAG integrated across all analysis components
- **Configuration**: Common component provides centralized configuration
- **Infrastructure**: Infra component supports all other components
- **Quality Assurance**: Tests component validates all functionality

This architecture ensures clean separation of concerns while maintaining efficient data flow for financial analysis and DCF valuation workflows.