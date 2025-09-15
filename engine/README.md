# Graph-RAG Investment Analysis Engine

**Business Purpose**: Transform Neo4j knowledge graph data into actionable investment strategies and professional reports using Graph-RAG enhanced reasoning.

## Data Flow

```
Neo4j Knowledge Graph + LLM + Templates → Investment Strategies & Reports
```

The engine represents the core reasoning layer of the investment analysis system, taking processed data from the ETL pipeline and generating concrete investment insights.

## Module Structure

### Core Components

#### graph_rag/
**Purpose**: Intelligent information retrieval from Neo4j knowledge graph
- Hybrid search combining graph traversal + vector similarity
- Context-aware retrieval for investment analysis
- Entity relationship reasoning
- Relevance scoring and ranking

#### llm/
**Purpose**: Language model integration for analysis generation
- Prompt template management for financial analysis
- Structured output parsing (JSON, financial metrics)
- Context window management for large documents
- Model routing (GPT-4, DeepSeek, local models)

#### strategy/
**Purpose**: Quantitative investment strategy generation
- DCF (Discounted Cash Flow) calculations
- Valuation models and financial metrics
- Investment recommendation algorithms
- Risk assessment and scenario analysis

#### reports/
**Purpose**: Professional investment report generation
- Executive summary creation
- Financial charts and visualizations
- Multi-format export (PDF, HTML, JSON)
- Dashboard data preparation

## Business Integration

### Input Sources
- **ETL Module**: Processes raw data → Neo4j knowledge graph
- **Common Templates**: Financial analysis prompt templates
- **Market Data**: Real-time pricing and financial metrics

### Output Consumers
- **Evaluation Module**: Strategy backtesting and validation
- **Build Data**: Report storage in `stage_04_query_results/`
- **Decision Makers**: Investment committee consumption

## Key Features

### Graph-RAG Enhancement
- **Contextual Retrieval**: Semantic search enhanced with graph relationships
- **Evidence-Based Analysis**: SEC filing citations and management guidance
- **Competitive Intelligence**: Peer company analysis and sector trends
- **Risk Factor Analysis**: Regulatory disclosures and risk assessment

### Quantitative Analysis
- **Multi-Stage DCF Models**: Terminal value calculation with sensitivity analysis
- **WACC Calculation**: Risk-adjusted discount rates
- **Scenario Modeling**: Bull/base/bear case valuations
- **Risk-Adjusted Returns**: Portfolio optimization considerations

### Professional Reporting
- **Executive Summaries**: Key insights and recommendations
- **Supporting Evidence**: SEC filing citations and data sources
- **Visualization**: Financial charts and trend analysis
- **Compliance**: Regulatory disclosure requirements

## Configuration

### LLM Configuration
```yaml
# common/config/llm/configs/
default_model: "gpt-4"
fallback_model: "deepseek"
context_window: 8192
temperature: 0.1
```

### Graph-RAG Settings
```yaml
# common/config/graph_rag.yml
vector_similarity_threshold: 0.7
max_retrieval_documents: 10
enable_multi_hop: true
relationship_depth: 3
```

### Strategy Parameters
```yaml
# common/config/strategy.yml
dcf_projection_years: 5
terminal_growth_rate: 0.025
risk_free_rate: 0.04
market_premium: 0.06
```

## Issue #256 Implementation

This module consolidates the core reasoning capabilities that were previously scattered across different directories:

**Before**: `analysis/` contained mixed evaluation and strategy logic
**After**: Clear separation:
- `engine/` - Strategy generation from current data
- `evaluation/` - Strategy testing against historical data

This separation enables:
- **Independent Validation**: Unbiased strategy evaluation
- **Clear Business Logic**: Focused responsibility per module
- **Scalable Architecture**: Easier to maintain and extend
- **Professional Workflow**: Matches investment industry practices

## Usage Examples

### Basic DCF Calculation
```python
from engine.strategy.dcf_calculator import DCFCalculator, DCFInputs
from engine.graph_rag.retriever import GraphRAGRetriever

# Retrieve company context
retriever = GraphRAGRetriever(neo4j_config, vector_config)
context = retriever.retrieve(company="AAPL", analysis_type="financial_metrics")

# Calculate valuation
calculator = DCFCalculator()
dcf_inputs = DCFInputs(...)
results = calculator.calculate_dcf(dcf_inputs, context)

print(f"Intrinsic Value: ${results.intrinsic_value_per_share}")
```

### Investment Report Generation
```python
from engine.reports.report_generator import ReportGenerator

generator = ReportGenerator()
report = generator.create_investment_report(
    company="AAPL",
    dcf_results=results,
    graph_context=context
)

# Export to multiple formats
report.export_pdf("reports/AAPL_analysis.pdf")
report.export_html("dashboards/AAPL_dashboard.html")
```

## Development Guidelines

### Testing Strategy
- **Unit Tests**: Individual component validation
- **Integration Tests**: Cross-component workflow testing  
- **End-to-End Tests**: Complete analysis pipeline validation
- **Mock Data**: Consistent test datasets across components

### Performance Targets
- **Retrieval Response**: <2 seconds for Graph-RAG queries
- **DCF Calculation**: <500ms for complete valuation
- **Report Generation**: <10 seconds for comprehensive reports
- **Memory Usage**: <2GB for typical analysis workload

### Quality Standards
- **Input Validation**: Comprehensive parameter checking
- **Error Handling**: Graceful degradation and recovery
- **Logging**: Detailed audit trail for compliance
- **Documentation**: Business logic explanation with examples

---

**Issue #256**: Business-oriented restructuring for clear Graph-RAG investment analysis pipeline
**Integration**: Uses DirectoryManager for all file paths and centralized configuration
**Governance**: Follows CLAUDE.md policies for development and deployment standards