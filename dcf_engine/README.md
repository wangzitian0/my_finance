# DCF Engine - Discounted Cash Flow Valuation Engine

Data-focused implementation of various DCF valuation strategies and logic.

## Component Structure

### Core Engine
- `validator.py` - Strategy validator
- `simple_m7_dcf.py` - Simplified M7 DCF calculation
- `m7_dcf_analysis.py` - M7 DCF analysis
- `generate_dcf_report.py` - DCF report generation

### Knowledge Graph
- `build_knowledge_base.py` - Knowledge base construction
- `demo_graph_rag.py` - Graph RAG demonstration
- `build_nasdaq100_simple.py` - NASDAQ100 simplified construction

### Strategy Validation
- `test_strategy_validation.py` - Strategy validation testing

### Documentation
- `dcf-engine.md` - DCF engine architecture documentation
- `STRATEGY_RELEASE_PROCESS.md` - Strategy release process

## Data Flow

```
DTS (Data Input) → DCF Engine (Strategy Calculation) → DTS (Result Output)
                     ↓
                Common (Schema Definition)
```

## Core Functionality

### DCF Valuation Calculation
- Multiple DCF model implementations
- Parameter sensitivity analysis  
- Scenario analysis and stress testing

### Strategy Validation
- Historical backtesting
- Statistical significance testing
- Risk metric calculation

### Knowledge Graph Enhancement
- Graph RAG queries
- Multi-source data fusion
- Intelligent reasoning analysis

## Usage

```bash
# Strategy validation
pixi run validate-strategy

# DCF analysis
python dcf_engine/m7_dcf_analysis.py

# Report generation
python dcf_engine/generate_dcf_report.py
```

## Design Principles

1. **Pure Calculation Logic**: No data I/O handling, focus on business logic
2. **Configurable Strategies**: Support for multiple DCF models and parameters
3. **Traceable Results**: Record calculation process and intermediate results
4. **Performance Optimization**: Support parallel computing and caching