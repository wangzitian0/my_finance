# DCF Engine Strategies

This directory contains different DCF (Discounted Cash Flow) valuation strategies and calculation approaches.

## Purpose

Implementation of various DCF calculation strategies:
- Traditional DCF models
- SEC-enhanced DCF with document integration
- Multi-model ensemble approaches
- LLM-powered analysis strategies

## Strategy Types

### Core DCF Models
- **Traditional DCF**: Standard discounted cash flow calculations
- **Enhanced DCF**: SEC document-informed adjustments
- **Multi-Model DCF**: Ensemble approaches combining multiple methods
- **Graph RAG DCF**: Graph-enhanced retrieval-augmented generation

### Integration Strategies
- **SEC Document Integration**: Incorporating 10-K/10-Q/8-K insights
- **News Sentiment**: Market sentiment and news impact analysis
- **Peer Comparison**: Industry and peer-relative valuation
- **Risk Adjustment**: Dynamic risk assessment and incorporation

## Key Components

1. **Calculation Engines**: Core DCF computation logic
2. **Data Integration**: Multi-source data combination strategies
3. **Risk Models**: Risk assessment and adjustment mechanisms
4. **Validation Logic**: Model validation and quality checks

## Usage

Strategies are utilized by:
- `dcf_engine/pure_llm_dcf.py` - Main DCF orchestration
- `dcf_engine/build_knowledge_base.py` - Knowledge base construction
- Graph RAG system for enhanced analysis
- Build system for automated valuation workflows

## Architecture

### Strategy Pattern
Each strategy implements a common interface:
- Data input standardization
- Calculation methodology
- Output formatting
- Quality metrics and validation

### Extensibility
- New strategies can be added modularly
- Common utilities shared across strategies
- Configuration-driven strategy selection
- Performance and accuracy benchmarking

## Development

When adding new strategies:
1. Follow the established strategy interface pattern
2. Include comprehensive testing and validation
3. Document methodology and assumptions
4. Provide benchmarking against existing strategies
5. Ensure SEC compliance for document usage

## Quality Assurance

- **Backtesting**: Historical performance validation
- **Peer Review**: Cross-validation with traditional models
- **Documentation**: Clear methodology explanation
- **Monitoring**: Performance tracking and quality metrics