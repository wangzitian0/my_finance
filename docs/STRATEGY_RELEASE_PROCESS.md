# Strategy Release Process

## Overview

This document defines the release testing mechanism for the Financial Strategy Engine. Every release must include validation that the DCF strategies produce meaningful results and outperform market benchmarks.

## Critical Issues Addressed

### Previous Problems Identified:
1. **No strategy validation** - changes were made without testing actual investment performance
2. **Mock data in production** - DCF calculations used placeholder values
3. **No benchmark comparison** - no way to know if strategies work better than buying SPY
4. **No historical testing** - strategies weren't backtested against real market data
5. **No performance tracking** - no way to measure strategy improvement over time

### New Release Requirements:
Every release must now pass **Strategy Validation Gates** before deployment.

## Release Workflow

### 1. Pre-Release Validation (MANDATORY)

Before any code changes can be merged to main:

```bash
# Run complete strategy validation
pixi run validate-strategy

# Must achieve minimum scores:
# - Overall Score: ≥ 70/100  
# - Sharpe Ratio: ≥ 1.0
# - Benchmark Outperformance: ≥ 2/3 indices
```

### 2. Strategy Validation Gates

#### Gate 1: DCF Analysis Validation
- **Requirement**: All M7 stocks must have DCF valuations within ±30% of consensus estimates
- **Data Source**: Compare against Yahoo Finance analyst targets
- **Confidence**: Average confidence score ≥ 70%

#### Gate 2: Backtesting Performance  
- **Requirement**: 1-year backtest shows positive Sharpe ratio (≥ 1.0)
- **Max Drawdown**: Must not exceed -20%
- **Win Rate**: ≥ 55% of positions profitable

#### Gate 3: Benchmark Outperformance
- **Requirement**: Must outperform ≥ 2 of 3 benchmark indices (SPY, QQQ, VTI)
- **Time Period**: Rolling 1-year performance
- **Risk-Adjusted**: Sharpe ratio must exceed benchmark Sharpe

#### Gate 4: Risk Management
- **Portfolio Beta**: Between 0.8 - 1.3 (not too conservative or aggressive)
- **Sector Concentration**: No single sector > 50% weight
- **VaR (5%)**: Daily Value at Risk < 5%

### 3. Release Report Generation

Every successful validation generates reports stored in `data/reports/`:

```bash
# Generate validation report
pixi run generate-report

# Reports created:
# - strategy_validation_YYYYMMDD_HHMMSS.json (detailed metrics)
# - strategy_summary_YYYYMMDD_HHMMSS.md (executive summary)
```

### 4. Release Approval Process

#### Automated Checks (CI/CD)
- [ ] All validation gates passed
- [ ] Overall score ≥ 70/100
- [ ] No critical risk warnings
- [ ] Reports generated successfully

#### Manual Review Required
- [ ] Strategy logic changes reviewed by senior developer
- [ ] Performance degradation > 10% from previous release investigated  
- [ ] New risk factors identified and documented
- [ ] Validation report reviewed and approved

### 5. Post-Release Monitoring

#### Weekly Performance Tracking
```bash
# Run ongoing performance monitoring
pixi run benchmark      # Compare current performance vs benchmarks
pixi run backtest       # Update historical performance metrics
```

#### Monthly Strategy Review
- Compare actual results vs validation predictions
- Update strategy parameters if performance degrades
- Archive old validation reports (keep 2 years)

## Validation Report Structure

### Strategy Validation Report (`strategy_validation_*.json`)

```json
{
  "validation_timestamp": "2024-01-15T10:30:00",
  "strategy_name": "DCF Graph RAG Strategy",
  "version": "1.2.3",
  "overall_score": 82.5,
  "validation_results": {
    "dcf_analysis": {
      "stocks_analyzed": 7,
      "average_upside_pct": 12.3,
      "portfolio_bias": "BULLISH",
      "confidence_score": 0.78,
      "individual_analysis": {
        "AAPL": {
          "dcf_intrinsic_value": 185.50,
          "current_price": 175.20,
          "upside_downside_pct": 5.9,
          "recommendation": "BUY",
          "confidence_score": 0.82
        }
      }
    },
    "backtesting": {
      "total_return_pct": 18.5,
      "sharpe_ratio": 1.24,
      "max_drawdown": -12.3,
      "win_rate": 0.64
    },
    "benchmark_comparison": {
      "SPY": {"outperformed": true, "excess_return_pct": 3.2},
      "QQQ": {"outperformed": true, "excess_return_pct": 1.8},
      "VTI": {"outperformed": false, "excess_return_pct": -0.5}
    },
    "risk_analysis": {
      "portfolio_beta": 1.15,
      "sector_concentration_pct": 85.0,
      "value_at_risk_5pct": -4.2
    }
  }
}
```

### Strategy Summary Report (`strategy_summary_*.md`)

Human-readable executive summary with:
- Overall performance grade (A/B/C/D/F)
- Key recommendations (BUY/HOLD/SELL signals)
- Risk warnings
- Comparison with previous releases

## Emergency Procedures

### Strategy Failure (Score < 50)
1. **IMMEDIATE**: Stop all automated trading/recommendations
2. **INVESTIGATE**: Run diagnostics on data quality and model parameters
3. **ROLLBACK**: Revert to last known good strategy version
4. **FIX**: Address root cause before next release

### Performance Degradation (Score drops > 15 points)
1. **ALERT**: Notify strategy team of performance decline
2. **ANALYZE**: Compare current vs historical validation reports
3. **INVESTIGATE**: Check for data quality issues, market regime changes
4. **ADJUST**: Update model parameters or add new risk controls

## Integration with Development Workflow

### Updated CLAUDE.md Workflow

```bash
# OLD workflow (problematic):
git commit -m "feat: update DCF model"
git push

# NEW workflow (with validation):
git commit -m "feat: update DCF model"
pixi run validate-strategy    # MUST PASS before push
# ... only if validation passes:
git push
```

### CI/CD Integration

```yaml
# .github/workflows/strategy-validation.yml
on: [pull_request]
jobs:
  validate-strategy:
    runs-on: ubuntu-latest  
    steps:
      - uses: actions/checkout@v3
      - name: Setup Pixi
        # ... setup steps
      - name: Run Strategy Validation
        run: pixi run validate-strategy
      - name: Check Validation Score
        run: |
          SCORE=$(python -c "import json; print(json.load(open('data/reports/strategy_validation_*.json'))['overall_score'])")
          if (( $(echo "$SCORE < 70" | bc -l) )); then
            echo "Strategy validation failed: $SCORE < 70"
            exit 1
          fi
```

## Migration Plan

### Phase 1 (Current Release)
- [x] Implement strategy validation framework
- [x] Create report generation system  
- [x] Update README to focus on strategy engine purpose
- [x] Add validation commands to pixi.toml

### Phase 2 (Next Release)  
- [ ] Replace mock DCF calculations with real financial models
- [ ] Add automated CI/CD validation checks
- [ ] Implement real-time performance monitoring
- [ ] Create strategy performance dashboard

### Phase 3 (Future)
- [ ] Add machine learning model validation
- [ ] Implement A/B testing for strategy variants
- [ ] Add options strategies and risk management
- [ ] Create client-facing investment reports

## Success Metrics

### Short Term (3 months)
- All releases pass validation gates
- Strategy reports generated for every release  
- Performance tracking vs benchmarks established

### Medium Term (6 months)
- Strategy consistently outperforms benchmarks
- Risk-adjusted returns (Sharpe ratio) > 1.5
- Maximum drawdown < 15%

### Long Term (12 months)
- Strategy generates positive alpha vs market
- Client adoption and positive feedback
- Expansion to additional asset classes