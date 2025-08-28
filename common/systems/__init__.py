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

# Import specific items from graph_rag_schema to avoid wildcard imports
from .graph_rag_schema import (
    DEFAULT_EMBEDDING_CONFIG,
    MAGNIFICENT_7_CIKS,
    MAGNIFICENT_7_TICKERS,
    DCFValuationNode,
    DocumentChunkNode,
    DocumentType,
    GraphNodeSchema,
    GraphRAGQuery,
    GraphRAGResponse,
    GraphRelationship,
    QueryIntent,
    RelationshipType,
    SECFilingNode,
    SemanticSearchResult,
    StockNode,
    VectorEmbeddingConfig,
)
from .metadata_manager import MetadataManager
from .quality_reporter import QualityReporter, setup_quality_reporter

__all__ = [
    # Build and quality systems
    "BuildTracker",
    "QualityReporter",
    "setup_quality_reporter",
    # Preserved systems
    "MetadataManager",
    # Graph RAG schema
    "QueryIntent",
    "DocumentType",
    "VectorEmbeddingConfig",
    "GraphNodeSchema",
    "StockNode",
    "SECFilingNode",
    "DocumentChunkNode",
    "DCFValuationNode",
    "RelationshipType",
    "GraphRelationship",
    "SemanticSearchResult",
    "GraphRAGQuery",
    "GraphRAGResponse",
    "MAGNIFICENT_7_TICKERS",
    "MAGNIFICENT_7_CIKS",
    "DEFAULT_EMBEDDING_CONFIG",
]
