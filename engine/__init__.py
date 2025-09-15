#!/usr/bin/env python3
"""
Graph-RAG Investment Analysis Engine

Core reasoning engine that transforms Neo4j knowledge graph data into investment
strategies and reports using Graph-RAG and LLM integration.

Business Logic Flow:
Neo4j Knowledge Graph + LLM + Templates → Investment Strategies & Reports

This module represents the heart of the investment analysis system, taking
processed data from ETL pipelines and Neo4j graphs and generating actionable
investment insights.

Components:
- retrieval/: Graph-enhanced Retrieval Augmented Generation (professional terminology)
- reasoning/: Language model integration and prompt management (professional terminology)
- valuation/: Investment strategy generation (DCF calculations, valuation models) (professional terminology)
- reporting/: Investment report generation and formatting (professional terminology)

Issue #256: Consolidates graph-RAG functionality from analysis/ and creates
clear business separation between data processing (ETL) and reasoning (engine).
"""

__version__ = "1.0.0"

# Core engine components
__all__ = ["retrieval", "reasoning", "valuation", "reporting"]

# Import engine components when available
try:
    from . import retrieval
except ImportError:
    retrieval = None

try:
    from . import reasoning
except ImportError:
    reasoning = None

try:
    from . import valuation
except ImportError:
    valuation = None

try:
    from . import reporting
except ImportError:
    reporting = None
