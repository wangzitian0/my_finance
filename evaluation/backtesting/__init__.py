#!/usr/bin/env python3
"""
Professional Backtesting Framework

Historical strategy simulation and performance analysis for validating
investment strategies against historical market data.

Business Purpose:
Rigorous historical validation of investment strategies to assess performance,
risk characteristics, and reliability before live deployment.

Key Components:
- Historical data management and preparation
- Strategy simulation with realistic execution assumptions
- Performance attribution and analysis
- Risk-adjusted return calculations
- Transaction cost and slippage modeling
- Portfolio rebalancing simulation

Backtesting Pipeline:
Strategy Rules + Historical Data → Simulation Engine → Performance Results

This module provides institutional-grade backtesting capabilities with
proper risk controls and realistic market assumptions.
"""

__version__ = "1.0.0"

try:
    from .backtest_engine import BacktestEngine
    from .historical_data import HistoricalDataManager
    from .performance_calculator import PerformanceCalculator
    from .transaction_simulator import TransactionSimulator

    __all__ = [
        "BacktestEngine",
        "HistoricalDataManager",
        "PerformanceCalculator",
        "TransactionSimulator",
    ]
except ImportError:
    __all__ = []
