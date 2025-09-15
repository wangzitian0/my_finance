#!/usr/bin/env python3
"""
Professional Valuation Models

DCF (Discounted Cash Flow) calculations and comprehensive valuation models
for generating intrinsic value estimates and investment recommendations.

Business Purpose:
Professional-grade valuation methodologies backed by SEC filings to produce
reliable intrinsic value estimates and buy/hold/sell recommendations.

Key Components:
- DCF (Discounted Cash Flow) calculation engine
- Multiple valuation model implementations
- Risk-adjusted discount rate calculations
- Sensitivity analysis and scenario modeling
- Comparable company analysis (Comps)
- Investment recommendation generation

Valuation Pipeline:
Financial Data + Market Context → DCF Models → Intrinsic Value → Investment Decision

This module provides institutional-grade valuation capabilities with full
regulatory backing and transparent methodologies.

Integration Points:
- Inputs: Analyzed financial data from reasoning/
- Processing: Professional valuation methodologies
- Outputs: Investment recommendations for reporting/
"""

__version__ = "1.0.0"

try:
    from .comps_analyzer import CompsAnalyzer
    from .dcf_calculator import DCFCalculator
    from .recommendation_engine import RecommendationEngine
    from .risk_adjuster import RiskAdjuster
    from .valuation_engine import ValuationEngine

    __all__ = [
        "ValuationEngine",
        "DCFCalculator",
        "RiskAdjuster",
        "CompsAnalyzer",
        "RecommendationEngine",
    ]
except ImportError:
    __all__ = []
