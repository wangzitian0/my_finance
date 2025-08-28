#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Graph RAG System

This script tests the complete Graph RAG implementation with sample queries
and validates the system's functionality.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging using centralized directory management
from common.core.directory_manager import directory_manager
from graph_rag import GraphRAGSystem
from graph_rag.data_ingestion import GraphRAGDataIngestion
from graph_rag.semantic_embedding import SemanticEmbedding

# Ensure logs directory exists
log_dir = directory_manager.get_logs_path()
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "graph_rag_test.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(str(log_file)), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class GraphRAGTester:
    """
    Comprehensive tester for the Graph RAG system.
    """

    def __init__(self):
        """Initialize the tester with sample data and test queries."""

        # Initialize Graph RAG system
        logger.info("Initializing Graph RAG system...")
        self.graph_rag = GraphRAGSystem()

        # Test queries for different scenarios
        self.test_queries = {
            "simple_dcf_query": "What is the DCF valuation for Apple?",
            "comparison_query": "Compare Apple and Microsoft financial performance",
            "risk_analysis_query": "What are the main risk factors for Tesla?",
            "news_impact_query": "How do recent news events affect Netflix stock price?",
            "complex_reasoning_query": "Based on recent financial performance and market conditions, should I invest in Amazon?",
            "sector_analysis_query": "How does Meta perform compared to other technology companies?",
            "historical_trend_query": "What are the revenue growth trends for Google over the past 3 years?",
        }

        # Expected results structure for validation
        self.expected_result_keys = [
            "answer",
            "reasoning_type",
            "confidence",
            "metadata",
        ]

    def run_comprehensive_test(self) -> dict:
        """
        Run comprehensive tests of the Graph RAG system.

        Returns:
            Dictionary with test results and statistics
        """
        logger.info("Starting comprehensive Graph RAG system test")

        test_results = {
            "start_time": datetime.now().isoformat(),
            "system_initialization": {},
            "embedding_functionality": {},
            "query_generation": {},
            "answer_generation": {},
            "reasoning_capability": {},
            "overall_stats": {},
            "errors": [],
        }

        try:
            # Test 1: System Initialization
            logger.info("Test 1: System Initialization")
            test_results["system_initialization"] = self.test_system_initialization()

            # Test 2: Embedding Functionality
            logger.info("Test 2: Embedding Functionality")
            test_results["embedding_functionality"] = self.test_embedding_functionality()

            # Test 3: Query Generation
            logger.info("Test 3: Query Generation")
            test_results["query_generation"] = self.test_query_generation()

            # Test 4: Answer Generation
            logger.info("Test 4: Answer Generation")
            test_results["answer_generation"] = self.test_answer_generation()

            # Test 5: Reasoning Capability
            logger.info("Test 5: Reasoning Capability")
            test_results["reasoning_capability"] = self.test_reasoning_capability()

            # Calculate overall statistics
            test_results["overall_stats"] = self.calculate_overall_stats(test_results)

        except Exception as e:
            error_msg = f"Critical error during testing: {str(e)}"
            logger.error(error_msg)
            test_results["errors"].append(error_msg)

        test_results["end_time"] = datetime.now().isoformat()
        logger.info("Comprehensive test completed")

        return test_results

    def test_system_initialization(self) -> dict:
        """Test system initialization and component loading."""
        results = {
            "graph_rag_initialized": False,
            "embedding_model_loaded": False,
            "components_available": {},
            "errors": [],
        }

        try:
            # Check Graph RAG system initialization
            if self.graph_rag:
                results["graph_rag_initialized"] = True
                logger.info("✓ Graph RAG system initialized successfully")

            # Check embedding model
            if self.graph_rag.semantic_embedding.model:
                results["embedding_model_loaded"] = True
                logger.info("✓ Embedding model loaded successfully")
            else:
                logger.warning(
                    "⚠ Embedding model not loaded (sentence-transformers may not be installed)"
                )

            # Check individual components
            components = {
                "semantic_embedding": self.graph_rag.semantic_embedding,
                "query_generator": self.graph_rag.query_generator,
                "semantic_retriever": self.graph_rag.semantic_retriever,
                "answer_generator": self.graph_rag.answer_generator,
                "reasoning_processor": self.graph_rag.reasoning_processor,
            }

            for component_name, component in components.items():
                if component:
                    results["components_available"][component_name] = True
                    logger.info(f"✓ {component_name} initialized")
                else:
                    results["components_available"][component_name] = False
                    logger.error(f"✗ {component_name} failed to initialize")

        except Exception as e:
            error_msg = f"System initialization test failed: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)

        return results

    def test_embedding_functionality(self) -> dict:
        """Test semantic embedding generation."""
        results = {
            "text_embedding_success": False,
            "document_embedding_success": False,
            "similarity_calculation_success": False,
            "embeddings_generated": 0,
            "errors": [],
        }

        try:
            embedding_system = self.graph_rag.semantic_embedding

            # Test simple text embedding
            test_text = "Apple Inc. is a technology company that designs and manufactures consumer electronics."
            embedding = embedding_system.embed_text(test_text)

            if embedding and len(embedding) > 0:
                results["text_embedding_success"] = True
                results["embeddings_generated"] += 1
                logger.info(f"✓ Text embedding generated (dimension: {len(embedding)})")
            else:
                logger.warning("⚠ Text embedding generation failed or returned empty")

            # Test document section embedding
            mock_sec_filing = {
                "item_1": "Business overview: Apple Inc. designs, manufactures and markets smartphones...",
                "item_1a": "Risk factors: The company faces intense competition in the smartphone market...",
                "item_7": "Management discussion: Revenue increased by 8% year-over-year...",
                "item_8": "Financial statements: Net income was $99.8 billion for fiscal 2023...",
            }

            doc_embeddings = embedding_system.embed_document_sections(mock_sec_filing)

            if doc_embeddings and len(doc_embeddings) > 0:
                results["document_embedding_success"] = True
                results["embeddings_generated"] += len(doc_embeddings)
                logger.info(f"✓ Document embeddings generated for {len(doc_embeddings)} sections")
            else:
                logger.warning("⚠ Document embedding generation failed")

            # Test similarity calculation
            if embedding:
                test_text_2 = "Microsoft Corporation develops software and cloud services."
                embedding_2 = embedding_system.embed_text(test_text_2)

                if embedding_2:
                    similarity = embedding_system.calculate_similarity(embedding, embedding_2)
                    if similarity is not None:
                        results["similarity_calculation_success"] = True
                        logger.info(
                            f"✓ Similarity calculation successful (score: {similarity:.3f})"
                        )
                    else:
                        logger.warning("⚠ Similarity calculation returned None")

        except Exception as e:
            error_msg = f"Embedding functionality test failed: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)

        return results

    def test_query_generation(self) -> dict:
        """Test structured query generation from natural language."""
        results = {
            "queries_generated": 0,
            "intents_classified": {},
            "tickers_extracted": {},
            "cypher_queries_valid": 0,
            "errors": [],
        }

        try:
            query_generator = self.graph_rag.query_generator

            for query_name, test_query in self.test_queries.items():
                try:
                    # Generate structured query
                    query_result = query_generator.generate_cypher_query(test_query)

                    if query_result:
                        results["queries_generated"] += 1

                        # Track intent classification
                        intent = query_result.get("intent", "unknown")
                        results["intents_classified"][query_name] = intent

                        # Track ticker extraction
                        tickers = query_result.get("tickers", [])
                        results["tickers_extracted"][query_name] = tickers

                        # Validate Cypher query structure
                        cypher_query = query_result.get("cypher_query", "")
                        if cypher_query and "MATCH" in cypher_query:
                            results["cypher_queries_valid"] += 1

                        logger.info(f"✓ {query_name}: Intent={intent}, Tickers={tickers}")

                except Exception as e:
                    error_msg = f"Query generation failed for {query_name}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)

        except Exception as e:
            error_msg = f"Query generation test failed: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)

        return results

    def test_answer_generation(self) -> dict:
        """Test answer generation with mock data."""
        results = {
            "answers_generated": 0,
            "answer_quality_scores": {},
            "confidence_scores": {},
            "errors": [],
        }

        try:
            # Test simple questions first
            simple_queries = ["simple_dcf_query", "risk_analysis_query"]

            for query_name in simple_queries:
                try:
                    test_query = self.test_queries[query_name]

                    # Use the Graph RAG system to answer
                    answer_result = self.graph_rag.answer_question(test_query)

                    if answer_result and "answer" in answer_result:
                        results["answers_generated"] += 1

                        # Record confidence score
                        confidence = answer_result.get("confidence", 0)
                        results["confidence_scores"][query_name] = confidence

                        # Simple quality assessment
                        answer_text = answer_result["answer"]
                        quality_score = self.assess_answer_quality(answer_text, test_query)
                        results["answer_quality_scores"][query_name] = quality_score

                        logger.info(
                            f"✓ {query_name}: Generated answer (confidence: {confidence:.2f}, quality: {quality_score:.2f})"
                        )
                        logger.debug(f"Answer preview: {answer_text[:100]}...")

                except Exception as e:
                    error_msg = f"Answer generation failed for {query_name}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)

        except Exception as e:
            error_msg = f"Answer generation test failed: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)

        return results

    def test_reasoning_capability(self) -> dict:
        """Test multi-step reasoning for complex questions."""
        results = {
            "complex_questions_processed": 0,
            "reasoning_steps_generated": {},
            "final_answers_quality": {},
            "errors": [],
        }

        try:
            # Test complex questions that should trigger multi-step reasoning
            complex_queries = ["complex_reasoning_query", "comparison_query"]

            for query_name in complex_queries:
                try:
                    test_query = self.test_queries[query_name]

                    # Check if question is identified as complex
                    is_complex = self.graph_rag.reasoning_processor.is_complex_question(test_query)

                    if is_complex:
                        logger.info(f"✓ {query_name} correctly identified as complex")

                        # Process the complex question
                        answer_result = self.graph_rag.answer_question(test_query)

                        if answer_result:
                            results["complex_questions_processed"] += 1

                            # Record reasoning steps if available
                            if answer_result.get("reasoning_type") == "multi_step":
                                steps = answer_result.get("steps", 0)
                                results["reasoning_steps_generated"][query_name] = steps
                                logger.info(
                                    f"✓ {query_name}: Multi-step reasoning with {steps} steps"
                                )

                            # Assess answer quality
                            answer_text = answer_result.get("answer", "")
                            quality = self.assess_answer_quality(answer_text, test_query)
                            results["final_answers_quality"][query_name] = quality
                    else:
                        logger.info(
                            f"- {query_name} not identified as complex (will use simple processing)"
                        )

                except Exception as e:
                    error_msg = f"Reasoning test failed for {query_name}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)

        except Exception as e:
            error_msg = f"Reasoning capability test failed: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)

        return results

    def assess_answer_quality(self, answer_text: str, original_question: str) -> float:
        """
        Simple answer quality assessment.

        Args:
            answer_text: Generated answer
            original_question: Original question

        Returns:
            Quality score between 0 and 1
        """
        if not answer_text or len(answer_text.strip()) == 0:
            return 0.0

        quality_score = 0.0

        # Length check (answers should be substantial but not too long)
        if 50 <= len(answer_text) <= 2000:
            quality_score += 0.3
        elif len(answer_text) > 20:
            quality_score += 0.1

        # Structure check (look for markdown formatting)
        if "**" in answer_text or "##" in answer_text:
            quality_score += 0.2

        # Content relevance (simple keyword matching)
        question_lower = original_question.lower()
        answer_lower = answer_text.lower()

        relevant_keywords = [
            "dcf",
            "valuation",
            "financial",
            "analysis",
            "risk",
            "company",
            "revenue",
            "profit",
            "investment",
            "stock",
            "price",
            "market",
        ]

        keyword_matches = sum(
            1
            for keyword in relevant_keywords
            if keyword in question_lower and keyword in answer_lower
        )

        if keyword_matches > 0:
            quality_score += min(0.3, keyword_matches * 0.1)

        # Data sources mentioned
        if "source" in answer_lower or "filing" in answer_lower or "data" in answer_lower:
            quality_score += 0.2

        return min(1.0, quality_score)

    def calculate_overall_stats(self, test_results: dict) -> dict:
        """Calculate overall testing statistics."""

        stats = {
            "total_tests_run": 0,
            "successful_tests": 0,
            "total_errors": 0,
            "success_rate": 0.0,
            "system_health": "unknown",
        }

        # Count successful tests
        test_categories = [
            "system_initialization",
            "embedding_functionality",
            "query_generation",
            "answer_generation",
            "reasoning_capability",
        ]

        for category in test_categories:
            if category in test_results:
                stats["total_tests_run"] += 1

                category_results = test_results[category]
                category_errors = len(category_results.get("errors", []))
                stats["total_errors"] += category_errors

                # Consider test successful if it has some positive results and few errors
                if category_errors == 0 and self._has_positive_results(category_results):
                    stats["successful_tests"] += 1

        # Calculate success rate
        if stats["total_tests_run"] > 0:
            stats["success_rate"] = stats["successful_tests"] / stats["total_tests_run"]

        # Determine system health
        if stats["success_rate"] >= 0.8:
            stats["system_health"] = "excellent"
        elif stats["success_rate"] >= 0.6:
            stats["system_health"] = "good"
        elif stats["success_rate"] >= 0.4:
            stats["system_health"] = "fair"
        else:
            stats["system_health"] = "poor"

        return stats

    def _has_positive_results(self, category_results: dict) -> bool:
        """Check if a test category has positive results."""

        positive_indicators = [
            "graph_rag_initialized",
            "text_embedding_success",
            "queries_generated",
            "answers_generated",
            "complex_questions_processed",
        ]

        for indicator in positive_indicators:
            if category_results.get(indicator):
                return True

        # Check for numeric indicators > 0
        numeric_indicators = ["embeddings_generated", "cypher_queries_valid"]

        for indicator in numeric_indicators:
            if category_results.get(indicator, 0) > 0:
                return True

        return False

    def save_test_report(self, test_results: dict, filename: str = None):
        """Save detailed test report to file."""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"graph_rag_test_report_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(test_results, f, indent=2, default=str)

            logger.info(f"Test report saved to {filename}")

        except Exception as e:
            logger.error(f"Failed to save test report: {e}")

    def print_test_summary(self, test_results: dict):
        """Print a summary of test results."""

        print("\n" + "=" * 60)
        print("GRAPH RAG SYSTEM TEST SUMMARY")
        print("=" * 60)

        overall_stats = test_results.get("overall_stats", {})

        print(f"Total Tests Run: {overall_stats.get('total_tests_run', 0)}")
        print(f"Successful Tests: {overall_stats.get('successful_tests', 0)}")
        print(f"Total Errors: {overall_stats.get('total_errors', 0)}")
        print(f"Success Rate: {overall_stats.get('success_rate', 0):.1%}")
        print(f"System Health: {overall_stats.get('system_health', 'unknown').upper()}")

        print("\nDETAILED RESULTS:")
        print("-" * 40)

        # System initialization
        init_results = test_results.get("system_initialization", {})
        print(f"System Initialization: {'✓' if init_results.get('graph_rag_initialized') else '✗'}")
        print(f"Embedding Model: {'✓' if init_results.get('embedding_model_loaded') else '⚠'}")

        # Embedding functionality
        embed_results = test_results.get("embedding_functionality", {})
        print(f"Text Embeddings: {'✓' if embed_results.get('text_embedding_success') else '✗'}")
        print(
            f"Document Embeddings: {'✓' if embed_results.get('document_embedding_success') else '✗'}"
        )

        # Query generation
        query_results = test_results.get("query_generation", {})
        queries_generated = query_results.get("queries_generated", 0)
        print(f"Query Generation: {queries_generated} queries processed")

        # Answer generation
        answer_results = test_results.get("answer_generation", {})
        answers_generated = answer_results.get("answers_generated", 0)
        print(f"Answer Generation: {answers_generated} answers generated")

        # Reasoning capability
        reasoning_results = test_results.get("reasoning_capability", {})
        complex_processed = reasoning_results.get("complex_questions_processed", 0)
        print(f"Complex Reasoning: {complex_processed} complex questions processed")

        print("\n" + "=" * 60)


def main():
    """Main function to run Graph RAG system tests."""

    print("Graph RAG System Testing")
    print("=" * 50)

    try:
        # Initialize tester
        tester = GraphRAGTester()

        # Run comprehensive tests
        test_results = tester.run_comprehensive_test()

        # Print summary
        tester.print_test_summary(test_results)

        # Save detailed report
        tester.save_test_report(test_results)

        # Return appropriate exit code
        overall_stats = test_results.get("overall_stats", {})
        success_rate = overall_stats.get("success_rate", 0)

        if success_rate >= 0.8:
            print("\n🎉 Graph RAG system is working excellently!")
            return 0
        elif success_rate >= 0.6:
            print("\n✅ Graph RAG system is working well with minor issues.")
            return 0
        elif success_rate >= 0.4:
            print("\n⚠️ Graph RAG system has some issues that need attention.")
            return 1
        else:
            print("\n❌ Graph RAG system has significant issues.")
            return 2

    except Exception as e:
        logger.error(f"Critical error during testing: {e}")
        print(f"\n💥 Critical error: {e}")
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
