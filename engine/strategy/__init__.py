#!/usr/bin/env python3
"""
Investment Strategy Generation Module

Core financial analysis and investment strategy generation using Graph-RAG
enhanced data. Contains DCF valuation models, financial calculations, and
investment recommendation logic.

Business Purpose:
Convert retrieved financial data and insights into actionable investment
strategies, valuations, and buy/hold/sell recommendations.

Key Components:
- DCF (Discounted Cash Flow) calculation engine
- Valuation models and financial metrics
- Investment recommendation algorithms
- Risk assessment and scoring
- Scenario analysis and sensitivity testing
- Portfolio allocation strategies

Data Flow:
Graph-RAG Context + LLM Analysis → Financial Calculations → Investment Strategies

This module takes the output from graph_rag/ and llm/ modules and applies
quantitative financial analysis to generate concrete investment recommendations.

Issue #256: Moved DCF calculation logic from analysis/components/ to
engine/strategy/ to clarify this is part of the strategy generation process,
not the evaluation/backtesting system.
"""

__version__ = "1.0.0"

try:
    from .dcf_calculator import DCFCalculator
    from .recommendation_engine import RecommendationEngine
    from .risk_assessment import RiskAssessment
    from .scenario_analysis import ScenarioAnalysis
    from .valuation_models import ValuationModels

    __all__ = [
        "DCFCalculator",
        "ValuationModels",
        "RiskAssessment",
        "RecommendationEngine",
        "ScenarioAnalysis",
    ]
except ImportError:
    __all__ = []
