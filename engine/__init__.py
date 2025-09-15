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
- graph_rag/: Graph-enhanced Retrieval Augmented Generation
- llm/: Language model integration and prompt management
- strategy/: Investment strategy generation (DCF calculations, valuation models)
- reports/: Investment report generation and formatting

Issue #256: Consolidates graph-RAG functionality from analysis/ and creates
clear business separation between data processing (ETL) and reasoning (engine).
"""

__version__ = "1.0.0"

# Core engine components
__all__ = ["graph_rag", "llm", "strategy", "reports"]

# Import engine components when available
try:
    from . import graph_rag
except ImportError:
    graph_rag = None

try:
    from . import llm
except ImportError:
    llm = None

try:
    from . import strategy
except ImportError:
    strategy = None

try:
    from . import reports
except ImportError:
    reports = None
