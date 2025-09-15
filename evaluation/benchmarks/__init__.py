#!/usr/bin/env python3
"""
Professional Benchmark Analysis

Market comparison and attribution analysis for evaluating investment strategy
performance relative to market benchmarks and peer comparisons.

Business Purpose:
Comprehensive benchmark analysis to assess strategy performance in context,
identify sources of alpha, and evaluate risk-adjusted returns.

Key Components:
- Market benchmark data management (S&P 500, NASDAQ, etc.)
- Peer group analysis and comparison
- Performance attribution analysis
- Risk-adjusted performance metrics
- Sector and style analysis
- Alpha and beta decomposition

Benchmark Pipeline:
Strategy Returns + Market Data → Attribution Analysis → Performance Assessment

This module provides institutional-grade benchmark analysis with comprehensive
market context and performance attribution capabilities.
"""

__version__ = "1.0.0"

try:
    from .benchmark_manager import BenchmarkManager
    from .attribution_analyzer import AttributionAnalyzer
    from .peer_comparator import PeerComparator
    from .alpha_calculator import AlphaCalculator

    __all__ = [
        "BenchmarkManager",
        "AttributionAnalyzer",
        "PeerComparator", 
        "AlphaCalculator",
    ]
except ImportError:
    __all__ = []