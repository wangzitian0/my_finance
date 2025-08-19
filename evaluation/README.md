# Evaluation - Evaluation Toolkit

Evaluation toolkit containing LLM template querying, strategy backtesting tool chain and performance evaluation framework.

## Component Structure

### Evaluation Documentation
- `evaluation.md` - Evaluation framework architecture documentation

### Environment Validation
- `validate_development_environment.py` - Development environment validation

## Features to Implement

### LLM Evaluation Tools
- [ ] `llm_templates/` - LLM prompt template library
- [ ] `llm_evaluator.py` - LLM response quality evaluator
- [ ] `prompt_manager.py` - Prompt manager

### Strategy Backtesting Framework
- [ ] `backtest_engine.py` - Backtesting engine
- [ ] `performance_metrics.py` - Performance metrics calculation
- [ ] `risk_analyzer.py` - Risk analyzer
- [ ] `benchmark_comparison.py` - Benchmark comparison tool

### Evaluation Reports
- [ ] `report_generator.py` - Evaluation report generator
- [ ] `visualization.py` - Result visualization tool
- [ ] `statistical_tests.py` - Statistical significance testing

## Evaluation Dimensions

### Strategy Performance Evaluation
- **Return Metrics**: Total return, annualized return, excess return
- **Risk Metrics**: Volatility, maximum drawdown, VaR, Sharpe ratio
- **Stability**: Win rate, profit-loss ratio, consecutive loss periods

### LLM Quality Evaluation  
- **Accuracy**: Similarity to benchmark answers
- **Consistency**: Stability of multiple query results
- **Reasoning Ability**: Completeness of logical reasoning chains
- **Timeliness**: Response time and throughput

### System Performance Evaluation
- **Computational Performance**: Execution time, memory usage
- **Data Quality**: Completeness, consistency, timeliness
- **User Experience**: Response speed, interface friendliness

## Usage

```bash
# Environment validation
python evaluation/validate_development_environment.py

# Strategy backtesting (to be implemented)
python evaluation/backtest_engine.py --strategy dcf --period 1y

# LLM evaluation (to be implemented)  
python evaluation/llm_evaluator.py --template dcf_analysis
```

## Design Principles

1. **Objective Quantification**: Use quantifiable metrics for evaluation
2. **Multi-dimensional**: Evaluate from multiple perspectives including performance, risk, stability
3. **Reproducible**: Standardized evaluation process with reproducible results
4. **Continuous Improvement**: Establish evaluation feedback loops