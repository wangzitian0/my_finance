#!/usr/bin/env python3
"""
ETL Data Loaders - Knowledge Graph Population

Professional data loading components for populating Neo4j knowledge graphs
with validated, structured financial data and relationships.

Business Purpose:
Transform processed financial data into a comprehensive knowledge graph
that enables sophisticated relationship analysis and Graph-RAG retrieval.

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

This module creates the foundational knowledge graph that engine/retrieval/
uses for intelligent retrieval and analysis.
"""

__version__ = "1.0.0"

try:
    from .bulk_importer import BulkImporter
    from .graph_loader import GraphLoader
    from .index_manager import IndexManager
    from .relationship_builder import RelationshipBuilder
    from .schema_manager import SchemaManager

    __all__ = [
        "GraphLoader",
        "SchemaManager",
        "BulkImporter",
        "RelationshipBuilder",
        "IndexManager",
    ]
except ImportError:
    __all__ = []