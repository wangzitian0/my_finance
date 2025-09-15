#!/usr/bin/env python3
"""
Performance Metrics and Analytics

Comprehensive performance measurement system for evaluating investment
strategy results from backtesting simulations.

Business Purpose:
Quantify strategy performance using industry-standard financial metrics
to enable objective strategy comparison and selection.

Key Metrics:
- Return Metrics: Total return, annualized return, CAGR
- Risk Metrics: Volatility, maximum drawdown, VaR, CVaR
- Risk-Adjusted: Sharpe ratio, Sortino ratio, Calmar ratio
- Benchmark Comparison: Alpha, beta, tracking error, information ratio
- Advanced: Tail ratio, Omega ratio, gain-pain ratio

Analytics Features:
- Rolling window analysis
- Regime-specific performance
- Sector/factor attribution
- Time-series decomposition
- Statistical significance testing

Output Integration:
- Feeds into evaluation/reporting/ for comprehensive reports
- Provides data for dashboard visualizations
- Supports strategy ranking and selection processes
"""

__version__ = "1.0.0"

try:
    from .drawdown_analysis import DrawdownAnalysis
    from .performance_calculator import PerformanceCalculator
    from .return_analytics import ReturnAnalytics
    from .risk_metrics import RiskMetrics
    from .statistical_tests import StatisticalTests

    __all__ = [
        "PerformanceCalculator",
        "RiskMetrics",
        "ReturnAnalytics",
        "DrawdownAnalysis",
        "StatisticalTests",
    ]
except ImportError:
    __all__ = []
