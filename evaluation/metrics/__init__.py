#!/usr/bin/env python3
"""
Professional Performance Metrics

Risk and return performance measurement framework for comprehensive
investment strategy evaluation and reporting.

Business Purpose:
Calculate and report institutional-grade performance metrics including
risk-adjusted returns, drawdown analysis, and volatility measurements.

Key Components:
- Risk-adjusted return calculations (Sharpe, Sortino, Calmar ratios)
- Drawdown analysis and risk assessment
- Volatility and correlation analysis
- Value at Risk (VaR) and Expected Shortfall calculations
- Performance persistence and consistency metrics
- Multi-period performance aggregation

Metrics Pipeline:
Strategy Returns + Market Data → Risk Calculations → Performance Report

This module provides comprehensive performance measurement capabilities
meeting institutional investment standards and regulatory requirements.
"""

__version__ = "1.0.0"

try:
    from .correlation_analyzer import CorrelationAnalyzer
    from .drawdown_analyzer import DrawdownAnalyzer
    from .performance_metrics import PerformanceMetrics
    from .risk_calculator import RiskCalculator
    from .var_calculator import VaRCalculator

    __all__ = [
        "PerformanceMetrics",
        "RiskCalculator",
        "DrawdownAnalyzer",
        "VaRCalculator",
        "CorrelationAnalyzer",
    ]
except ImportError:
    __all__ = []
