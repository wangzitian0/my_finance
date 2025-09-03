#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCF Engine RAG Orchestrator

Main orchestrator that coordinates between ETL's data retrieval capabilities
and dcf_engine's answer generation to provide complete Graph RAG functionality.

This module:
- Coordinates query processing, data retrieval, and answer generation
- Manages the interaction between ETL (data layer) and dcf_engine (business layer)
- Provides the main entry point for Graph RAG queries
- Handles error cases and fallback responses
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from neomodel import db

from common.graph_rag_schema import (
    DEFAULT_EMBEDDING_CONFIG,
    GraphRAGQuery,
    GraphRAGResponse,
    QueryIntent,
    SemanticSearchResult,
)
from dcf_engine.graph_rag_engine import AnswerContext, AnswerGenerator, QueryProcessor
from ETL.semantic_retrieval import SemanticRetriever

logger = logging.getLogger(__name__)


class GraphRAGOrchestrator:
    """
    Main orchestrator for the Graph RAG system.

    This class coordinates between:
    - ETL layer: Data integration and semantic retrieval
    - DCF Engine layer: Query processing and answer generation

    Provides a unified interface for Graph RAG operations.
    """

    def __init__(
        self,
        data_dir: Path,
        neo4j_url: str = "bolt://localhost:7687",
        neo4j_username: str = "neo4j",
        neo4j_password: str = "password",
    ):
        """
        Initialize the Graph RAG orchestrator.

        Args:
            data_dir: Directory containing processed data and embeddings
            neo4j_url: Neo4j database URL
            neo4j_username: Neo4j username
            neo4j_password: Neo4j password
        """
        self.data_dir = Path(data_dir)
        self.neo4j_url = neo4j_url
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password

        # Initialize components
        self.query_processor = QueryProcessor()
        self.answer_generator = AnswerGenerator()
        self.semantic_retriever = None

        # Setup connections
        self._setup_neo4j_connection()
        self._setup_semantic_retriever()

        logger.info("Graph RAG orchestrator initialized successfully")

    def _setup_neo4j_connection(self):
        """Setup Neo4j database connection."""
        try:
            from neomodel import config

            config.DATABASE_URL = f"{self.neo4j_url}"
            db.set_connection(
                url=self.neo4j_url, username=self.neo4j_username, password=self.neo4j_password
            )

            # Test connection
            db.cypher_query("RETURN 1 as test")
            logger.info("Neo4j connection established")

        except Exception as e:
            logger.error(f"Failed to setup Neo4j connection: {e}")
            logger.warning("Graph database queries will be disabled")

    def _setup_semantic_retriever(self):
        """Setup semantic retriever with embeddings."""
        try:
            embeddings_path = self.data_dir / "stage_03_load" / "embeddings"

            if embeddings_path.exists():
                self.semantic_retriever = SemanticRetriever(
                    embeddings_path, DEFAULT_EMBEDDING_CONFIG
                )
                logger.info("Semantic retriever initialized with embeddings")
            else:
                logger.warning(f"Embeddings not found at {embeddings_path}")
                logger.warning("Semantic search will be limited")

        except Exception as e:
            logger.error(f"Failed to setup semantic retriever: {e}")
            logger.warning("Semantic search will be disabled")

    def answer_question(self, question: str) -> GraphRAGResponse:
        """
        Answer a natural language question using Graph RAG.

        Args:
            question: User's natural language question

        Returns:
            Structured response with answer and supporting information
        """
        try:
            logger.info(f"Processing question: {question}")

            # Step 1: Process query to extract intent and entities
            structured_query = self.query_processor.process_query(question)
            logger.debug(
                f"Query intent: {structured_query.intent}, "
                f"entities: {structured_query.entities}"
            )

            # Step 2: Retrieve data from graph database
            graph_results = self._query_graph_database(structured_query)

            # Step 3: Retrieve semantic content
            semantic_results = self._retrieve_semantic_content(structured_query)

            # Step 4: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                graph_results, semantic_results, structured_query
            )

            # Step 5: Create context for answer generation
            answer_context = AnswerContext(
                graph_results=graph_results,
                semantic_results=semantic_results,
                query_intent=structured_query.intent,
                extracted_entities=structured_query.entities,
                confidence_score=confidence_score,
            )

            # Step 6: Generate answer
            response = self.answer_generator.generate_answer(answer_context)

            logger.info(f"Generated answer with confidence: {response.confidence_score:.2f}")
            return response

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return self._generate_error_response(question, str(e))

    def _query_graph_database(self, query: GraphRAGQuery) -> Dict[str, Any]:
        """
        Query the Neo4j graph database for structured data.

        Args:
            query: Structured query object

        Returns:
            Graph query results
        """
        results = {}

        try:
            if not query.cypher_query:
                logger.debug("No Cypher query generated")
                return results

            logger.debug(f"Executing Cypher query: {query.cypher_query}")

            # Execute Cypher query
            cypher_results, meta = db.cypher_query(query.cypher_query)

            # Process results based on query intent
            if query.intent == QueryIntent.DCF_VALUATION:
                results["dcf_valuation"] = self._process_dcf_results(cypher_results)
            elif query.intent == QueryIntent.FINANCIAL_COMPARISON:
                results["financial_comparison"] = self._process_comparison_results(cypher_results)
            elif query.intent == QueryIntent.RISK_ANALYSIS:
                results["risk_analysis"] = self._process_risk_results(cypher_results)
            else:
                results["general"] = cypher_results

            logger.debug(f"Graph query returned {len(cypher_results)} results")

        except Exception as e:
            logger.error(f"Graph database query failed: {e}")
            results["error"] = str(e)

        return results

    def _retrieve_semantic_content(self, query: GraphRAGQuery) -> List[SemanticSearchResult]:
        """
        Retrieve semantically relevant content using vector search.

        Args:
            query: Structured query object

        Returns:
            List of semantically relevant content
        """
        if not self.semantic_retriever:
            logger.warning("Semantic retriever not available")
            return []

        try:
            # Use vector query for semantic search
            search_query = query.vector_query or query.question

            # Apply content filters based on entities and intent
            content_filter = query.context_filter or {}

            # Perform semantic search
            semantic_results = self.semantic_retriever.retrieve_relevant_content(
                query=search_query, top_k=10, min_similarity=0.3, content_filter=content_filter
            )

            logger.debug(f"Semantic search returned {len(semantic_results)} results")
            return semantic_results

        except Exception as e:
            logger.error(f"Semantic retrieval failed: {e}")
            raise RuntimeError(f"Semantic retrieval failed: {e}") from e

    def _calculate_confidence_score(
        self,
        graph_results: Dict[str, Any],
        semantic_results: List[SemanticSearchResult],
        query: GraphRAGQuery,
    ) -> float:
        """
        Calculate confidence score based on available data quality.

        Args:
            graph_results: Results from graph database
            semantic_results: Results from semantic search
            query: Original query

        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0

        # Base score for having any results
        if graph_results or semantic_results:
            score += 0.2

        # Score for structured data availability
        if graph_results and "error" not in graph_results:
            score += 0.3

        # Score for semantic search results
        if semantic_results:
            avg_similarity = sum(r.similarity_score for r in semantic_results) / len(
                semantic_results
            )
            score += min(0.3, avg_similarity * 0.5)  # Max 0.3 from similarity

        # Score for entity extraction success
        if query.entities:
            score += 0.1

        # Score for intent confidence
        if query.intent != QueryIntent.GENERAL_INFO:
            score += 0.1

        return min(1.0, score)  # Cap at 1.0

    def _process_dcf_results(self, cypher_results: List) -> Dict[str, Any]:
        """Process DCF valuation results from Cypher query."""
        if not cypher_results:
            return {}

        # Assuming first result contains DCF data
        if cypher_results and len(cypher_results[0]) > 0:
            dcf_node = cypher_results[0][0]

            return {
                "intrinsic_value": getattr(dcf_node, "intrinsic_value", 0),
                "current_price": getattr(dcf_node, "current_price", 0),
                "discount_rate": getattr(dcf_node, "discount_rate", 0.1),
                "terminal_growth_rate": getattr(dcf_node, "terminal_growth_rate", 0.03),
                "valuation_date": getattr(dcf_node, "valuation_date", None),
                "confidence_score": getattr(dcf_node, "confidence_score", None),
            }

        return {}

    def _process_comparison_results(self, cypher_results: List) -> Dict[str, Any]:
        """Process financial comparison results from Cypher query."""
        if not cypher_results:
            return {}

        comparison_data = {"companies": [], "metrics": [], "periods": []}

        for result in cypher_results:
            if len(result) >= 4:  # ticker1, ticker2, metrics1, metrics2
                ticker1, ticker2, m1, m2 = result[0], result[1], result[2], result[3]

                comparison_data["companies"].extend([ticker1, ticker2])
                comparison_data["metrics"].extend(
                    [self._extract_metrics(m1), self._extract_metrics(m2)]
                )

        return comparison_data

    def _process_risk_results(self, cypher_results: List) -> Dict[str, Any]:
        """Process risk analysis results from Cypher query."""
        risk_data = {"risk_documents": [], "risk_factors": []}

        for result in cypher_results:
            if result:  # DocumentChunk node
                chunk = result[0]
                risk_data["risk_documents"].append(
                    {
                        "content": getattr(chunk, "content", ""),
                        "document_type": getattr(chunk, "content_type", ""),
                        "parent_document": getattr(chunk, "parent_document", ""),
                    }
                )

        return risk_data

    def _extract_metrics(self, metrics_node) -> Dict[str, Any]:
        """Extract financial metrics from a node."""
        if not metrics_node:
            return {}

        return {
            "revenue": getattr(metrics_node, "revenue", None),
            "net_income": getattr(metrics_node, "net_income", None),
            "free_cash_flow": getattr(metrics_node, "free_cash_flow", None),
            "total_debt": getattr(metrics_node, "total_debt", None),
            "shareholders_equity": getattr(metrics_node, "shareholders_equity", None),
            "report_date": getattr(metrics_node, "report_date", None),
        }

    def _generate_error_response(self, question: str, error_message: str) -> GraphRAGResponse:
        """Generate error response when processing fails."""
        return GraphRAGResponse(
            answer=f"I apologize, but I encountered an error processing your question: '{question}'. "
            f"Please try rephrasing your question or ask about specific companies from the "
            f"Magnificent 7 (AAPL, MSFT, AMZN, GOOGL, META, TSLA, NFLX).",
            confidence_score=0.0,
            sources=[],
            reasoning_steps=[
                "Query processing started",
                f"Error encountered: {error_message}",
                "Generated fallback response",
            ],
            cypher_results={},
            metadata={"error": True, "error_message": error_message, "original_question": question},
        )

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health information."""
        status = {
            "neo4j_connected": False,
            "semantic_retriever_available": False,
            "embeddings_loaded": False,
            "total_documents": 0,
            "total_embeddings": 0,
        }

        # Check Neo4j connection
        try:
            db.cypher_query("RETURN 1")
            status["neo4j_connected"] = True
        except:
            pass

        # Check semantic retriever
        if self.semantic_retriever:
            status["semantic_retriever_available"] = True

            # Get document count
            if hasattr(self.semantic_retriever, "document_metadata"):
                status["total_documents"] = len(self.semantic_retriever.document_metadata)

            # Get embeddings count
            if (
                hasattr(self.semantic_retriever, "vector_index")
                and self.semantic_retriever.vector_index
            ):
                status["total_embeddings"] = self.semantic_retriever.vector_index.ntotal
                status["embeddings_loaded"] = True

        return status

    def test_query(
        self, test_question: str = "What is the DCF valuation for Apple?"
    ) -> Dict[str, Any]:
        """
        Run a test query to verify system functionality.

        Args:
            test_question: Question to test with

        Returns:
            Test results and system information
        """
        logger.info(f"Running test query: {test_question}")

        test_results = {
            "test_question": test_question,
            "system_status": self.get_system_status(),
            "query_processing": {},
            "response": None,
            "success": False,
        }

        try:
            # Test query processing
            structured_query = self.query_processor.process_query(test_question)
            test_results["query_processing"] = {
                "intent_detected": structured_query.intent.value,
                "entities_extracted": structured_query.entities,
                "cypher_generated": bool(structured_query.cypher_query),
                "vector_query_generated": bool(structured_query.vector_query),
            }

            # Test full pipeline
            response = self.answer_question(test_question)
            test_results["response"] = {
                "answer_generated": bool(response.answer),
                "confidence_score": response.confidence_score,
                "sources_found": len(response.sources),
                "reasoning_steps": len(response.reasoning_steps),
            }

            test_results["success"] = True
            logger.info("Test query completed successfully")

        except Exception as e:
            test_results["error"] = str(e)
            logger.error(f"Test query failed: {e}")

        return test_results
