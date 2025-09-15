#!/usr/bin/env python3
"""
Graph-Enhanced Retrieval Augmented Generation (Graph-RAG)

Advanced semantic search and knowledge retrieval system that combines:
- Neo4j graph database queries
- Vector similarity search
- Entity relationship reasoning
- Context-aware retrieval

This module enables the engine to perform intelligent retrieval from the
knowledge graph, combining structured graph relationships with semantic
vector search for comprehensive investment analysis.

Business Purpose:
Transform SEC filings and financial data stored in Neo4j into contextually
relevant information for investment decision making.

Key Components:
- Vector retrieval from financial document embeddings
- Graph traversal for entity relationships
- Hybrid search combining graph + vector similarity
- Context ranking and relevance scoring

Issue #256: Moved from analysis/ to engine/graph_rag/ to clarify that this
is part of the reasoning engine, not the evaluation/backtesting system.
"""

__version__ = "1.0.0"

try:
    from .graph_query import GraphQueryEngine
    from .hybrid_search import HybridSearchEngine
    from .retriever import GraphRAGRetriever
    from .vector_search import VectorSearchEngine

    __all__ = ["GraphRAGRetriever", "VectorSearchEngine", "GraphQueryEngine", "HybridSearchEngine"]
except ImportError:
    __all__ = []
