#!/usr/bin/env python3
"""
Strategy Validation and Testing Framework

This module provides comprehensive validation tools for investment strategies,
including DCF analysis, backtesting, benchmark comparison, and report generation.
"""

try:
    from .validator import StrategyValidator

    __all__ = ["StrategyValidator"]
except ImportError:
    __all__ = []

__version__ = "1.0.0"
