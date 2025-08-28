#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Specialized system modules for the common library.

This module provides refactored system components:
- BuildTracker: Refactored build execution tracking
- QualityReporter: Refactored quality reporting system
- MetadataManager: Metadata tracking (preserved)
- GraphRAGSchema: Graph RAG schema definitions (preserved)

Issue #184: Core library restructuring - Systems refactoring
"""

from .build_tracker import BuildTracker
from .quality_reporter import QualityReporter, setup_quality_reporter
from .metadata_manager import MetadataManager
# Import specific items from graph_rag_schema to avoid wildcard imports
from .graph_rag_schema import (
    QueryIntent, DocumentType, VectorEmbeddingConfig, GraphNodeSchema,
    StockNode, SECFilingNode, DocumentChunkNode, DCFValuationNode,
    RelationshipType, GraphRelationship, SemanticSearchResult,
    GraphRAGQuery, GraphRAGResponse, MAGNIFICENT_7_TICKERS,
    MAGNIFICENT_7_CIKS, DEFAULT_EMBEDDING_CONFIG
)

__all__ = [
    # Build and quality systems
    "BuildTracker",
    "QualityReporter", 
    "setup_quality_reporter",
    # Preserved systems
    "MetadataManager",
    # Graph RAG schema
    "QueryIntent", "DocumentType", "VectorEmbeddingConfig", "GraphNodeSchema",
    "StockNode", "SECFilingNode", "DocumentChunkNode", "DCFValuationNode",
    "RelationshipType", "GraphRelationship", "SemanticSearchResult",
    "GraphRAGQuery", "GraphRAGResponse", "MAGNIFICENT_7_TICKERS",
    "MAGNIFICENT_7_CIKS", "DEFAULT_EMBEDDING_CONFIG"
]