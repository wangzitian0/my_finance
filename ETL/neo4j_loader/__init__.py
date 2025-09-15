#!/usr/bin/env python3
"""
Neo4j Knowledge Graph Loader

Specialized data loading system for populating Neo4j graph database with
processed financial data, creating the knowledge graph foundation for
Graph-RAG analysis.

Business Purpose:
Transform processed SEC filings, financial metrics, and market data into
a structured knowledge graph that enables sophisticated investment analysis.

Key Components:
- Graph schema management (nodes, relationships, properties)
- Bulk data loading with transaction optimization
- Incremental updates and upsert operations
- Data consistency validation
- Graph indexing and query optimization
- Schema evolution and migration support

Graph Structure:
- Company nodes with financial metrics
- Document nodes for SEC filings  
- Relationship links (ownership, sector, competitors)
- Embedding properties for vector search
- Temporal relationships for time-series analysis

Data Flow:
Processed Data → Graph Transformation → Neo4j Bulk Load → Knowledge Graph

This module creates the foundational knowledge graph that engine/graph_rag/
uses for intelligent retrieval and analysis.
"""

__version__ = "1.0.0"

try:
    from .graph_loader import GraphLoader
    from .schema_manager import SchemaManager
    from .bulk_importer import BulkImporter
    from .relationship_builder import RelationshipBuilder
    from .index_manager import IndexManager

    __all__ = [
        "GraphLoader",
        "SchemaManager",
        "BulkImporter",
        "RelationshipBuilder", 
        "IndexManager"
    ]
except ImportError:
    __all__ = []