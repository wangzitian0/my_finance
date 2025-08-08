#!/usr/bin/env python3
"""
Strategy Validation and Testing Framework

This module provides comprehensive validation tools for investment strategies,
including DCF analysis, backtesting, benchmark comparison, and report generation.
"""

from .validator import StrategyValidator

__version__ = "1.0.0"
__all__ = ["StrategyValidator"]