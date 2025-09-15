#!/usr/bin/env python3
"""
Investment Analysis Retrieval System

Graph-RAG (Retrieval Augmented Generation) system for extracting relevant
financial information from Neo4j knowledge graphs to support investment analysis.

Business Purpose:
Intelligent information retrieval combining semantic search with graph traversal
to provide contextually relevant data for DCF valuations and investment decisions.

Key Components:
- Hybrid semantic and graph-based retrieval
- Vector similarity search using embeddings
- Graph traversal for relationship discovery
- Context-aware query processing
- Multi-modal data integration (text, metrics, documents)
- Relevance scoring and ranking

Retrieval Pipeline:
Query → Vector Search + Graph Traversal → Context Assembly → Ranked Results

This system bridges the gap between raw knowledge graphs and actionable
investment insights by providing intelligent, context-aware data retrieval.

Integration Points:
- Inputs: User queries, investment analysis requests
- Data Sources: Neo4j knowledge graph, vector embeddings
- Outputs: Contextually relevant financial data for reasoning/
"""

__version__ = "1.0.0"

try:
    from .context_assembler import ContextAssembler
    from .graph_retriever import GraphRetriever
    from .query_processor import QueryProcessor
    from .rag_system import GraphRAGSystem
    from .vector_search import VectorSearch

    __all__ = [
        "GraphRAGSystem",
        "GraphRetriever",
        "VectorSearch",
        "ContextAssembler",
        "QueryProcessor",
    ]
except ImportError:
    __all__ = []
