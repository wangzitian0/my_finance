#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common Schema Module Tests

Tests for graph RAG schema definitions and data structures.
"""

import pytest
from datetime import datetime
from typing import List

from graph_rag_schema import (
    QueryIntent, StockNode, SECFilingNode, DocumentChunkNode,
    GraphRAGQuery, GraphRAGResponse, SemanticSearchResult,
    MAGNIFICENT_7_TICKERS, DEFAULT_EMBEDDING_CONFIG, DocumentType
)


def test_query_intent_enum():
    """Test QueryIntent enum values."""
    assert QueryIntent.DCF_VALUATION.value == "dcf_valuation"
    assert QueryIntent.FINANCIAL_COMPARISON.value == "financial_comparison"
    assert QueryIntent.RISK_ANALYSIS.value == "risk_analysis"
    

def test_stock_node_creation():
    """Test StockNode data class creation."""
    stock = StockNode(
        node_id="stock_AAPL",
        ticker="AAPL", 
        company_name="Apple Inc.",
        cik="0000320193",
        sector="Technology",
        industry="Consumer Electronics",
        created_at=datetime.now()
    )
    
    assert stock.node_type == "Stock"
    assert stock.ticker == "AAPL"
    assert stock.company_name == "Apple Inc."
    assert stock.cik == "0000320193"


def test_sec_filing_node_creation():
    """Test SECFilingNode data class creation."""
    filing = SECFilingNode(
        node_id="sec_AAPL_123456",
        accession_number="0000320193-24-000123",
        filing_type=DocumentType.SEC_10K,
        filing_date=datetime.now(),
        company_cik="0000320193",
        created_at=datetime.now()
    )
    
    assert filing.node_type == "SECFiling"
    assert filing.accession_number == "0000320193-24-000123"
    assert filing.filing_type == DocumentType.SEC_10K


def test_document_chunk_node_creation():
    """Test DocumentChunkNode data class creation."""
    chunk = DocumentChunkNode(
        node_id="chunk_test_1",
        document_id="test_doc",
        chunk_index=0,
        content="Test content for semantic search",
        content_type=DocumentType.SEC_10K,
        parent_document="test_doc.txt",
        created_at=datetime.now()
    )
    
    assert chunk.node_type == "DocumentChunk"
    assert chunk.chunk_index == 0
    assert "semantic search" in chunk.content


def test_graph_rag_query_creation():
    """Test GraphRAGQuery data class creation."""
    query = GraphRAGQuery(
        question="What is Apple's DCF valuation?",
        intent=QueryIntent.DCF_VALUATION,
        entities=["AAPL"],
        cypher_query="MATCH (s:Stock {ticker: 'AAPL'}) RETURN s",
        vector_query="Apple DCF valuation"
    )
    
    assert query.intent == QueryIntent.DCF_VALUATION
    assert "AAPL" in query.entities
    assert query.cypher_query is not None


def test_semantic_search_result_creation():
    """Test SemanticSearchResult data class creation."""
    result = SemanticSearchResult(
        node_id="chunk_1",
        content="Apple reported strong earnings...",
        similarity_score=0.85,
        metadata={"source": "10-Q"},
        source_document="AAPL_10q.txt",
        document_type=DocumentType.SEC_10Q
    )
    
    assert result.similarity_score == 0.85
    assert result.document_type == DocumentType.SEC_10Q
    assert result.metadata["source"] == "10-Q"


def test_graph_rag_response_creation():
    """Test GraphRAGResponse data class creation."""
    response = GraphRAGResponse(
        answer="Apple's intrinsic value is $150",
        confidence_score=0.8,
        sources=[],
        reasoning_steps=["Step 1", "Step 2"],
        cypher_results={"value": 150}
    )
    
    assert response.confidence_score == 0.8
    assert len(response.reasoning_steps) == 2
    assert response.cypher_results["value"] == 150


def test_magnificent_7_constants():
    """Test M7 constants are properly defined."""
    assert len(MAGNIFICENT_7_TICKERS) == 7
    assert "AAPL" in MAGNIFICENT_7_TICKERS
    assert "MSFT" in MAGNIFICENT_7_TICKERS
    assert "GOOGL" in MAGNIFICENT_7_TICKERS


def test_default_embedding_config():
    """Test default embedding configuration."""
    config = DEFAULT_EMBEDDING_CONFIG
    
    assert config.model_name == "sentence-transformers/all-MiniLM-L6-v2"
    assert config.chunk_size == 512
    assert config.dimension == 384
    assert config.similarity_threshold == 0.3


if __name__ == "__main__":
    # Run tests directly
    import sys
    
    test_functions = [
        test_query_intent_enum,
        test_stock_node_creation,
        test_sec_filing_node_creation,
        test_document_chunk_node_creation,
        test_graph_rag_query_creation,
        test_semantic_search_result_creation,
        test_graph_rag_response_creation,
        test_magnificent_7_constants,
        test_default_embedding_config
    ]
    
    passed = 0
    total = len(test_functions)
    
    print("🧪 Running Common Schema Tests")
    print("=" * 40)
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    sys.exit(0 if passed == total else 1)