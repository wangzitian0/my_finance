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

## Strategy Engine Components

### 1. Data Collection Layer
- **M7 Dataset**: Magnificent 7 stocks (tracked in git for testing)
- **NASDAQ100**: Extended dataset for validation
- **US-ALL**: Full market coverage

### 2. Analysis Engine  
- **DCF Calculator**: Discounted cash flow valuation models
- **Graph RAG**: Multi-step reasoning for complex analysis
- **Risk Engine**: Factor-based risk assessment

### 3. Validation System
- **Backtesting**: Historical performance validation
- **Benchmark Comparison**: vs S&P 500, sector indices
- **Strategy Reports**: Stored in `data/reports/` for analysis

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