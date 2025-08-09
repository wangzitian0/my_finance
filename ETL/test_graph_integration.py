#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL Graph Integration Module Tests

Tests for graph data integration and semantic retrieval functionality.
Tests run without external dependencies (Neo4j, sentence-transformers).
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.graph_rag_schema import (
    StockNode, SECFilingNode, DocumentType, MAGNIFICENT_7_CIKS
)


def test_stock_node_creation():
    """Test creating stock nodes from M7 data."""
    ticker = "AAPL"
    cik = MAGNIFICENT_7_CIKS[ticker]
    
    stock_node = StockNode(
        node_id=f"stock_{ticker}",
        ticker=ticker,
        company_name="Apple Inc.", 
        cik=cik,
        sector="Technology",
        industry="Consumer Electronics",
        created_at=datetime.now()
    )
    
    assert stock_node.ticker == "AAPL"
    assert stock_node.cik == "0000320193"
    assert stock_node.node_type == "Stock"


def test_sec_filing_node_creation():
    """Test creating SEC filing nodes."""
    filing_node = SECFilingNode(
        node_id="sec_AAPL_123456",
        accession_number="0000320193-24-000123",
        filing_type=DocumentType.SEC_10K,
        filing_date=datetime.now(),
        company_cik="0000320193",
        created_at=datetime.now()
    )
    
    assert filing_node.filing_type == DocumentType.SEC_10K
    assert filing_node.accession_number == "0000320193-24-000123"
    assert filing_node.node_type == "SECFiling"


def test_sec_filename_parsing():
    """Test parsing SEC filenames for metadata."""
    filename = "AAPL_sec_edgar_10k_250810-005935_0000320193-24-000123.txt"
    
    # Simple parsing logic
    parts = filename.split('_')
    ticker = parts[0]
    filing_type = parts[3] 
    accession = parts[5] if len(parts) > 5 else parts[4]
    
    assert ticker == "AAPL"
    assert filing_type == "10k"
    assert "0000320193-24-000123" in accession


def test_document_chunking():
    """Test document chunking functionality."""
    content = "This is a test document. " * 100  # Create long content
    chunk_size = 100
    chunk_overlap = 20
    
    def chunk_document(content, chunk_size, chunk_overlap):
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk_text = content[start:end]
            
            chunks.append({
                'content': chunk_text.strip(),
                'start': start,
                'end': end
            })
            
            start = end - chunk_overlap
            
        return chunks
    
    chunks = chunk_document(content, chunk_size, chunk_overlap)
    
    assert len(chunks) > 1
    assert len(chunks[0]['content']) <= chunk_size
    assert chunks[0]['start'] == 0


def test_yfinance_to_text_conversion():
    """Test converting Yahoo Finance JSON to text."""
    yf_data = {
        "symbol": "AAPL",
        "regularMarketPrice": 150.25,
        "marketCap": 2500000000000,
        "trailingEps": 6.05,
        "forwardPE": 25.8
    }
    
    def yfinance_to_text(data, ticker):
        text_parts = [f"Financial data for {ticker}:"]
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (str, int, float)):
                    text_parts.append(f"{key}: {value}")
        
        return " ".join(text_parts)
    
    text = yfinance_to_text(yf_data, "AAPL")
    
    assert "AAPL" in text
    assert "150.25" in text
    assert "marketCap" in text


def test_integration_statistics():
    """Test integration statistics calculation."""
    stats = {
        'nodes_created': 0,
        'relationships_created': 0,
        'node_types': {}
    }
    
    def update_stats(main_stats, new_stats):
        for key, value in new_stats.items():
            if key == 'node_types':
                if 'node_types' not in main_stats:
                    main_stats['node_types'] = {}
                for node_type, count in value.items():
                    main_stats['node_types'][node_type] = main_stats['node_types'].get(node_type, 0) + count
            else:
                main_stats[key] = main_stats.get(key, 0) + value
    
    # Simulate adding stats
    new_stats = {
        'nodes_created': 5,
        'relationships_created': 3,
        'node_types': {'Stock': 1, 'SECFiling': 4}
    }
    
    update_stats(stats, new_stats)
    
    assert stats['nodes_created'] == 5
    assert stats['relationships_created'] == 3
    assert stats['node_types']['Stock'] == 1
    assert stats['node_types']['SECFiling'] == 4


def test_mock_vector_embedding():
    """Test mock vector embedding generation."""
    import numpy as np
    
    def mock_generate_embedding(text, dimension=384):
        """Mock embedding generation for testing."""
        # Simple hash-based mock embedding
        hash_val = hash(text) % (2**31)
        np.random.seed(hash_val)
        return np.random.random(dimension)
    
    text1 = "Apple reported strong earnings"
    text2 = "Microsoft revenue growth"
    
    embedding1 = mock_generate_embedding(text1)
    embedding2 = mock_generate_embedding(text2)
    
    assert len(embedding1) == 384
    assert len(embedding2) == 384
    assert not np.array_equal(embedding1, embedding2)  # Different texts should have different embeddings


def test_semantic_search_simulation():
    """Test semantic search simulation."""
    # Mock document database
    documents = [
        {"id": "doc1", "content": "Apple financial results", "embedding": [0.8, 0.2, 0.1]},
        {"id": "doc2", "content": "Microsoft earnings report", "embedding": [0.2, 0.8, 0.1]},
        {"id": "doc3", "content": "Apple revenue growth", "embedding": [0.7, 0.3, 0.2]}
    ]
    
    def cosine_similarity(vec1, vec2):
        """Simple cosine similarity calculation."""
        import numpy as np
        vec1, vec2 = np.array(vec1), np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def search_similar(query_embedding, documents, top_k=2):
        similarities = []
        for doc in documents:
            similarity = cosine_similarity(query_embedding, doc["embedding"])
            similarities.append((doc, similarity))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    query_embedding = [0.8, 0.2, 0.1]  # Similar to Apple documents
    results = search_similar(query_embedding, documents, top_k=2)
    
    assert len(results) == 2
    assert "Apple" in results[0][0]["content"]  # Most similar should be Apple-related
    assert results[0][1] > results[1][1]  # First result should be more similar


def run_all_tests():
    """Run all ETL module tests."""
    test_functions = [
        test_stock_node_creation,
        test_sec_filing_node_creation,
        test_sec_filename_parsing,
        test_document_chunking,
        test_yfinance_to_text_conversion,
        test_integration_statistics,
        test_mock_vector_embedding,
        test_semantic_search_simulation
    ]
    
    passed = 0
    total = len(test_functions)
    
    print("🧪 Running ETL Graph Integration Tests")
    print("=" * 50)
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)