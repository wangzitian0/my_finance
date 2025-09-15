#!/usr/bin/env python3
"""
Benchmark Comparison and Analysis

Comprehensive benchmark comparison system for evaluating investment strategy
performance against market indices and peer strategies.

Business Purpose:
Provide context for strategy performance by comparing against relevant
benchmarks to determine if strategies add value over passive alternatives.

Benchmark Categories:
- Market Indices: S&P 500, NASDAQ, Russell 2000, sector ETFs
- Factor Benchmarks: Value, growth, momentum, quality factors
- Peer Strategies: Similar investment approaches and styles
- Risk-Free Rate: Treasury bonds for Sharpe ratio calculations
- Custom Benchmarks: User-defined comparison portfolios

Comparison Metrics:
- Relative performance (alpha generation)
- Risk-adjusted outperformance 
- Tracking error and correlation analysis
- Up/down market performance
- Factor exposure analysis
- Attribution analysis (security selection vs. sector allocation)

This module enables investors to understand whether strategies generated
by engine/ provide meaningful advantages over simpler alternatives.
"""

__version__ = "1.0.0"

try:
    from .benchmark_manager import BenchmarkManager
    from .comparison_engine import ComparisonEngine
    from .attribution_analysis import AttributionAnalysis
    from .factor_analysis import FactorAnalysis
    from .relative_performance import RelativePerformance

    __all__ = [
        "BenchmarkManager",
        "ComparisonEngine",
        "AttributionAnalysis",
        "FactorAnalysis",
        "RelativePerformance"
    ]
except ImportError:
    __all__ = []