#!/usr/bin/env python3
"""
Investment Analysis Reasoning Engine

Language model integration and reasoning components for financial analysis,
combining retrieved data with advanced reasoning to generate investment insights.

Business Purpose:
Apply sophisticated financial reasoning to retrieved data, generating DCF analyses,
risk assessments, and investment recommendations with regulatory backing.

Key Components:
- Large Language Model integration (OpenAI, Claude, etc.)
- Financial reasoning prompt templates
- Multi-step reasoning workflows
- Risk assessment frameworks
- Regulatory compliance validation
- Investment thesis generation

Reasoning Pipeline:
Retrieved Data + Context → LLM Reasoning → Investment Analysis → Validation

This module transforms raw financial data into actionable investment insights
through advanced reasoning and analysis frameworks.

Integration Points:
- Inputs: Retrieved financial data from retrieval/
- Processing: LLM-enhanced financial analysis
- Outputs: Investment insights for valuation/ and reporting/
"""

__version__ = "1.0.0"

try:
    from .llm_client import LLMClient
    from .prompt_manager import PromptManager
    from .reasoning_engine import ReasoningEngine
    from .risk_analyzer import RiskAnalyzer
    from .thesis_generator import ThesisGenerator

    __all__ = [
        "ReasoningEngine",
        "LLMClient",
        "PromptManager",
        "RiskAnalyzer",
        "ThesisGenerator",
    ]
except ImportError:
    __all__ = []
