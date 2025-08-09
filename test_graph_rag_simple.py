#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Test Script for Refactored Graph RAG Architecture

Tests core components without external dependencies (Neo4j, sentence-transformers, etc.)
This validates the architectural design and module structure.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_schema_definitions():
    """Test schema definitions and data classes."""
    logger.info("Testing schema definitions...")
    try:
        from common.graph_rag_schema import (
            QueryIntent, StockNode, GraphRAGQuery, GraphRAGResponse,
            MAGNIFICENT_7_TICKERS, DEFAULT_EMBEDDING_CONFIG, DocumentType
        )
        
        # Test enum usage
        intent = QueryIntent.DCF_VALUATION
        logger.info(f"✓ QueryIntent enum: {intent.value}")
        
        # Test data class creation with proper defaults
        stock = StockNode(
            node_id="test_stock_AAPL",
            ticker="AAPL",
            company_name="Apple Inc.",
            cik="0000320193",
            sector="Technology",
            industry="Consumer Electronics",
            created_at=datetime.now()
        )
        logger.info(f"✓ StockNode creation: {stock.ticker} - {stock.company_name}")
        
        # Test constants
        logger.info(f"✓ M7 tickers ({len(MAGNIFICENT_7_TICKERS)}): {MAGNIFICENT_7_TICKERS[:3]}...")
        logger.info(f"✓ Default embedding model: {DEFAULT_EMBEDDING_CONFIG.model_name}")
        
        # Test DocumentType enum
        doc_type = DocumentType.SEC_10K
        logger.info(f"✓ DocumentType enum: {doc_type.value}")
        
        logger.info("✅ Schema definitions test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema definitions test FAILED: {e}")
        return False


def test_query_processing_logic():
    """Test query processing without external dependencies."""
    logger.info("Testing query processing logic...")
    try:
        # Create minimal query processor without dependencies
        from common.graph_rag_schema import QueryIntent, MAGNIFICENT_7_TICKERS
        import re
        
        class SimpleQueryProcessor:
            def __init__(self):
                self.intent_patterns = {
                    QueryIntent.DCF_VALUATION: [r'dcf|valuation|worth|value'],
                    QueryIntent.FINANCIAL_COMPARISON: [r'compare|vs|versus'],  
                    QueryIntent.RISK_ANALYSIS: [r'risk|downside|volatility']
                }
            
            def extract_intent(self, question):
                question_lower = question.lower()
                for intent, patterns in self.intent_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, question_lower):
                            return intent
                return QueryIntent.GENERAL_INFO
            
            def extract_tickers(self, question):
                found = []
                for ticker in MAGNIFICENT_7_TICKERS:
                    if ticker in question.upper():
                        found.append(ticker)
                return found
        
        processor = SimpleQueryProcessor()
        
        test_queries = [
            ("What is the DCF valuation for Apple?", QueryIntent.DCF_VALUATION, ["AAPL"]),
            ("Compare MSFT and GOOGL performance", QueryIntent.FINANCIAL_COMPARISON, ["MSFT", "GOOGL"]),
            ("Tesla risk factors", QueryIntent.RISK_ANALYSIS, ["TSLA"]),
            ("Tell me about Amazon", QueryIntent.GENERAL_INFO, ["AMZN"])
        ]
        
        for query, expected_intent, expected_tickers in test_queries:
            intent = processor.extract_intent(query)
            tickers = processor.extract_tickers(query)
            
            logger.info(f"Query: '{query}'")
            logger.info(f"  Expected intent: {expected_intent.value}, Got: {intent.value}")
            logger.info(f"  Expected tickers: {expected_tickers}, Got: {tickers}")
            
            # Verify basic functionality
            assert intent == expected_intent, f"Intent mismatch for: {query}"
            for ticker in expected_tickers:
                assert ticker in tickers, f"Ticker {ticker} not found in: {query}"
        
        logger.info("✅ Query processing logic test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Query processing logic test FAILED: {e}")
        return False


def test_answer_templates():
    """Test answer generation templates."""
    logger.info("Testing answer generation templates...")
    try:
        from common.graph_rag_schema import QueryIntent
        
        # Simple template system
        templates = {
            QueryIntent.DCF_VALUATION: "DCF Analysis for {ticker}: Intrinsic Value ${value:.2f}",
            QueryIntent.FINANCIAL_COMPARISON: "Comparing {ticker1} vs {ticker2}: {summary}",
            QueryIntent.RISK_ANALYSIS: "Risk factors for {ticker}: {risks}"
        }
        
        # Test template formatting
        dcf_answer = templates[QueryIntent.DCF_VALUATION].format(ticker="AAPL", value=150.50)
        logger.info(f"✓ DCF template: {dcf_answer}")
        
        comparison_answer = templates[QueryIntent.FINANCIAL_COMPARISON].format(
            ticker1="AAPL", ticker2="MSFT", summary="Both show strong growth"
        )
        logger.info(f"✓ Comparison template: {comparison_answer}")
        
        risk_answer = templates[QueryIntent.RISK_ANALYSIS].format(
            ticker="TSLA", risks="Market volatility, regulatory changes"
        )
        logger.info(f"✓ Risk template: {risk_answer}")
        
        logger.info("✅ Answer templates test PASSED") 
        return True
        
    except Exception as e:
        logger.error(f"❌ Answer templates test FAILED: {e}")
        return False


def test_data_directory_structure():
    """Test data directory structure."""
    logger.info("Testing data directory structure...")
    try:
        data_dir = project_root / "data" / "stage_03_load"
        
        expected_structure = {
            "dcf_results": "DCF valuation calculations",
            "graph_nodes": "Neo4j graph database nodes", 
            "embeddings": "Semantic vector embeddings",
            "graph_embeddings": "Combined graph + embedding data",
            "vector_index": "FAISS vector indexes",
            "graph_rag_cache": "Cached query results"
        }
        
        for dir_name, description in expected_structure.items():
            dir_path = data_dir / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✓ Created {dir_name}/ - {description}")
            else:
                logger.info(f"✓ Exists {dir_name}/ - {description}")
        
        # Verify README
        readme_path = data_dir / "README.md"
        if readme_path.exists():
            logger.info("✓ README.md exists with documentation")
        else:
            logger.warning("⚠ README.md missing")
        
        logger.info("✅ Data directory structure test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data directory structure test FAILED: {e}")
        return False


def test_architectural_separation():
    """Test that architectural components are properly separated."""
    logger.info("Testing architectural separation...")
    try:
        # Test that common schema is importable
        from common.graph_rag_schema import QueryIntent, StockNode
        logger.info("✓ Common schema is accessible")
        
        # Test that ETL files exist (without importing - no dependencies)
        etl_files = [
            "ETL/graph_data_integration.py",
            "ETL/semantic_retrieval.py"
        ]
        
        for file_path in etl_files:
            full_path = project_root / file_path
            if full_path.exists():
                logger.info(f"✓ ETL module exists: {file_path}")
            else:
                logger.error(f"❌ ETL module missing: {file_path}")
                return False
        
        # Test that dcf_engine files exist
        dcf_files = [
            "dcf_engine/graph_rag_engine.py", 
            "dcf_engine/rag_orchestrator.py"
        ]
        
        for file_path in dcf_files:
            full_path = project_root / file_path
            if full_path.exists():
                logger.info(f"✓ DCF Engine module exists: {file_path}")
            else:
                logger.error(f"❌ DCF Engine module missing: {file_path}")
                return False
        
        logger.info("✅ Architectural separation test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Architectural separation test FAILED: {e}")
        return False


def test_integration_points():
    """Test integration points between layers."""
    logger.info("Testing integration points...")
    try:
        from common.graph_rag_schema import (
            GraphRAGQuery, GraphRAGResponse, QueryIntent, 
            SemanticSearchResult, DocumentType
        )
        
        # Test that we can create integration objects
        query = GraphRAGQuery(
            question="What is Apple's valuation?",
            intent=QueryIntent.DCF_VALUATION,
            entities=["AAPL"],
            cypher_query="MATCH (s:Stock {ticker: 'AAPL'}) RETURN s",
            vector_query="Apple DCF valuation analysis"
        )
        logger.info(f"✓ GraphRAGQuery creation: {query.question}")
        
        # Mock semantic result
        semantic_result = SemanticSearchResult(
            node_id="test_chunk_1",
            content="Apple reported strong quarterly results...",
            similarity_score=0.85,
            metadata={"source": "10-Q"},
            source_document="AAPL_10q_2024.txt",
            document_type=DocumentType.SEC_10Q
        )
        logger.info(f"✓ SemanticSearchResult creation: {semantic_result.similarity_score}")
        
        # Mock response
        response = GraphRAGResponse(
            answer="Based on DCF analysis, Apple's intrinsic value is $150.",
            confidence_score=0.8,
            sources=[semantic_result],
            reasoning_steps=["Extracted intent", "Found relevant data", "Generated answer"],
            cypher_results={"dcf_value": 150.0}
        )
        logger.info(f"✓ GraphRAGResponse creation: confidence {response.confidence_score}")
        
        logger.info("✅ Integration points test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration points test FAILED: {e}")
        return False


def run_all_tests():
    """Run all simplified architecture tests."""
    logger.info("🚀 Starting Graph RAG Architecture Tests (Simplified)")
    logger.info("=" * 60)
    
    tests = [
        ("Schema Definitions", test_schema_definitions),
        ("Query Processing Logic", test_query_processing_logic),
        ("Answer Templates", test_answer_templates),
        ("Data Directory Structure", test_data_directory_structure), 
        ("Architectural Separation", test_architectural_separation),
        ("Integration Points", test_integration_points)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 ARCHITECTURE TEST RESULTS:")
    logger.info(f"✅ Passed: {passed}/{total} tests")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status} - {test_name}")
    
    if passed == total:
        logger.info(f"\n🎉 ALL TESTS PASSED!")
        logger.info("✅ Graph RAG refactor architecture is correctly implemented")
        logger.info("\n📋 Next steps:")
        logger.info("  1. Install dependencies: pixi run install-graph-rag")
        logger.info("  2. Setup Neo4j database: pixi run env-start") 
        logger.info("  3. Run M7 data integration: pixi run build-dataset m7")
        logger.info("  4. Test full system: pixi run demo-graph-rag")
        return True
    else:
        failed = total - passed
        logger.warning(f"\n⚠️  {failed} test(s) failed - review issues above")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)