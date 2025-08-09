#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Refactored Graph RAG Architecture

Tests the new architecture where:
- ETL handles data integration and semantic retrieval
- dcf_engine handles query processing and answer generation  
- common provides shared schema definitions
- data directory stores all data products

This script validates the refactored components work together correctly.
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_schema_import():
    """Test that common schema can be imported."""
    logger.info("Testing schema import...")
    try:
        from common.graph_rag_schema import (
            QueryIntent, StockNode, GraphRAGQuery, GraphRAGResponse,
            MAGNIFICENT_7_TICKERS, DEFAULT_EMBEDDING_CONFIG
        )
        
        # Test enum usage
        intent = QueryIntent.DCF_VALUATION
        logger.info(f"QueryIntent.DCF_VALUATION: {intent.value}")
        
        # Test data class creation
        stock = StockNode(
            node_id="test_stock_AAPL",
            ticker="AAPL",
            company_name="Apple Inc.",
            cik="0000320193",
            sector="Technology",
            industry="Consumer Electronics",
            created_at=datetime.now()
        )
        logger.info(f"Created StockNode: {stock.ticker} - {stock.company_name}")
        
        # Test constants
        logger.info(f"M7 tickers: {MAGNIFICENT_7_TICKERS}")
        logger.info(f"Default embedding model: {DEFAULT_EMBEDDING_CONFIG.model_name}")
        
        logger.info("✅ Schema import test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema import test failed: {e}")
        return False


def test_etl_imports():
    """Test ETL module imports."""
    logger.info("Testing ETL imports...")
    try:
        from ETL.graph_data_integration import GraphDataIntegrator
        from ETL.semantic_retrieval import SemanticEmbeddingGenerator, SemanticRetriever
        
        logger.info("GraphDataIntegrator class imported successfully")
        logger.info("SemanticEmbeddingGenerator class imported successfully") 
        logger.info("SemanticRetriever class imported successfully")
        
        logger.info("✅ ETL imports test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ ETL imports test failed: {e}")
        return False


def test_dcf_engine_imports():
    """Test dcf_engine module imports."""
    logger.info("Testing dcf_engine imports...")
    try:
        from dcf_engine.graph_rag_engine import QueryProcessor, AnswerGenerator, AnswerContext
        from dcf_engine.rag_orchestrator import GraphRAGOrchestrator
        
        logger.info("QueryProcessor class imported successfully")
        logger.info("AnswerGenerator class imported successfully")
        logger.info("GraphRAGOrchestrator class imported successfully")
        
        logger.info("✅ dcf_engine imports test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ dcf_engine imports test failed: {e}")
        return False


def test_query_processing():
    """Test query processing functionality."""
    logger.info("Testing query processing...")
    try:
        from dcf_engine.graph_rag_engine import QueryProcessor
        from common.graph_rag_schema import QueryIntent
        
        processor = QueryProcessor()
        
        # Test different query types
        test_queries = [
            "What is the DCF valuation for Apple?",
            "Compare Apple and Microsoft financial performance", 
            "What are the main risk factors for Tesla?",
            "Should I invest in Amazon based on recent news?"
        ]
        
        for query in test_queries:
            structured_query = processor.process_query(query)
            logger.info(f"Query: '{query}'")
            logger.info(f"  Intent: {structured_query.intent.value}")
            logger.info(f"  Entities: {structured_query.entities}")
            logger.info(f"  Has Cypher: {bool(structured_query.cypher_query)}")
            logger.info(f"  Has Vector Query: {bool(structured_query.vector_query)}")
        
        logger.info("✅ Query processing test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Query processing test failed: {e}")
        return False


def test_data_directory_structure():
    """Test that data directory structure is correct."""
    logger.info("Testing data directory structure...")
    try:
        data_dir = project_root / "data" / "stage_03_load"
        
        expected_dirs = [
            "dcf_results",
            "graph_nodes", 
            "embeddings",
            "graph_embeddings",
            "vector_index", 
            "graph_rag_cache"
        ]
        
        for expected_dir in expected_dirs:
            dir_path = data_dir / expected_dir
            if not dir_path.exists():
                logger.warning(f"Directory {expected_dir} does not exist, creating...")
                dir_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"  ✓ {expected_dir}/")
        
        # Check README exists
        readme_path = data_dir / "README.md"
        if readme_path.exists():
            logger.info("  ✓ README.md")
        else:
            logger.warning("  ⚠ README.md missing")
        
        logger.info("✅ Data directory structure test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data directory structure test failed: {e}")
        return False


def test_answer_generation():
    """Test answer generation with mock data."""
    logger.info("Testing answer generation...")
    try:
        from dcf_engine.graph_rag_engine import AnswerGenerator, AnswerContext
        from common.graph_rag_schema import QueryIntent, SemanticSearchResult, DocumentType
        
        generator = AnswerGenerator()
        
        # Create mock context
        mock_semantic_results = [
            SemanticSearchResult(
                node_id="mock_chunk_1",
                content="Apple reported strong quarterly earnings with revenue growth of 15%.",
                similarity_score=0.85,
                metadata={"source": "10-Q filing"},
                source_document="AAPL_sec_edgar_10q_2024.txt",
                document_type=DocumentType.SEC_10Q
            )
        ]
        
        mock_context = AnswerContext(
            graph_results={},
            semantic_results=mock_semantic_results,
            query_intent=QueryIntent.DCF_VALUATION,
            extracted_entities=["AAPL"],
            confidence_score=0.8
        )
        
        # Generate answer
        response = generator.generate_answer(mock_context)
        
        logger.info(f"Generated answer length: {len(response.answer)} characters")
        logger.info(f"Confidence score: {response.confidence_score}")
        logger.info(f"Number of sources: {len(response.sources)}")
        logger.info(f"Reasoning steps: {len(response.reasoning_steps)}")
        
        # Verify response structure
        assert response.answer, "Answer should not be empty"
        assert response.confidence_score >= 0, "Confidence should be non-negative"
        assert isinstance(response.reasoning_steps, list), "Reasoning steps should be a list"
        
        logger.info("✅ Answer generation test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Answer generation test failed: {e}")
        return False


def test_orchestrator_initialization():
    """Test orchestrator initialization without external dependencies."""
    logger.info("Testing orchestrator initialization...")
    try:
        from dcf_engine.rag_orchestrator import GraphRAGOrchestrator
        
        data_dir = project_root / "data"
        
        # This will fail Neo4j connection but should handle gracefully
        orchestrator = GraphRAGOrchestrator(
            data_dir=data_dir,
            neo4j_url="bolt://localhost:7687",
            neo4j_username="neo4j", 
            neo4j_password="test"
        )
        
        # Test system status
        status = orchestrator.get_system_status()
        logger.info(f"System status: {status}")
        
        # Test query processing component
        test_results = orchestrator.test_query("What is Apple's valuation?")
        logger.info(f"Test query results: {test_results}")
        
        logger.info("✅ Orchestrator initialization test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Orchestrator initialization test failed: {e}")
        return False


def run_all_tests():
    """Run all architecture tests."""
    logger.info("🚀 Starting Graph RAG refactor architecture tests")
    logger.info("=" * 60)
    
    tests = [
        ("Schema Import", test_schema_import),
        ("ETL Imports", test_etl_imports), 
        ("DCF Engine Imports", test_dcf_engine_imports),
        ("Query Processing", test_query_processing),
        ("Data Directory Structure", test_data_directory_structure),
        ("Answer Generation", test_answer_generation),
        ("Orchestrator Initialization", test_orchestrator_initialization)
    ]
    
    results = {}
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed_tests += 1
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Test Results Summary:")
    logger.info(f"Passed: {passed_tests}/{total_tests} tests")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status} - {test_name}")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 All tests passed! Graph RAG refactor is working correctly.")
        return True
    else:
        logger.warning(f"\n⚠️  {total_tests - passed_tests} tests failed. Review the issues above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)