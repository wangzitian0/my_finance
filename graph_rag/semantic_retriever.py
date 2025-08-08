#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Retriever for Graph RAG System

This module handles semantic similarity search and content retrieval
based on vector embeddings and relevance scoring.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .semantic_embedding import SemanticEmbedding

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Data class for storing retrieval results."""

    content: str
    source: str
    document_type: str
    section: Optional[str]
    similarity_score: float
    relevance_score: float
    document_date: datetime
    metadata: Dict[str, Any]


class SemanticRetriever:
    """
    Handles semantic similarity search and intelligent content retrieval
    with relevance and recency-based ranking.
    """

    def __init__(
        self, semantic_embedding: SemanticEmbedding, vector_store: Optional[Any] = None
    ):
        """
        Initialize the semantic retriever.

        Args:
            semantic_embedding: SemanticEmbedding instance for generating query embeddings
            vector_store: Optional vector database (for future implementation with Chroma/Pinecone)
        """
        self.semantic_embedding = semantic_embedding
        self.vector_store = vector_store

    def retrieve_relevant_content(
        self,
        question: str,
        graph_data: Dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.3,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant content based on semantic similarity to the question.

        Args:
            question: User's natural language question
            graph_data: Retrieved data from Neo4j graph database
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of relevant content chunks ranked by relevance
        """
        if not self.semantic_embedding.model:
            logger.warning("Semantic embedding model not available")
            return []

        # Generate question embedding
        question_embedding = self.semantic_embedding.embed_text(question)
        if not question_embedding:
            logger.error("Failed to generate question embedding")
            return []

        # Extract and process content from graph data
        content_chunks = self._extract_content_from_graph_data(graph_data)

        if not content_chunks:
            logger.warning("No content chunks found in graph data")
            return []

        # Calculate similarity scores
        similar_chunks = []

        for chunk in content_chunks:
            if "embedding" in chunk and chunk["embedding"]:
                similarity = self.semantic_embedding.calculate_similarity(
                    question_embedding, chunk["embedding"]
                )

                if similarity >= min_similarity:
                    # Create retrieval result
                    result = RetrievalResult(
                        content=chunk["content"],
                        source=chunk.get("source", "unknown"),
                        document_type=chunk.get("document_type", "unknown"),
                        section=chunk.get("section"),
                        similarity_score=similarity,
                        relevance_score=0.0,  # Will be calculated below
                        document_date=chunk.get("document_date", datetime.now()),
                        metadata=chunk.get("metadata", {}),
                    )
                    similar_chunks.append(result)

        # Rank by relevance and recency
        ranked_chunks = self.rank_by_relevance_and_recency(similar_chunks, question)

        return ranked_chunks[:top_k]

    def _extract_content_from_graph_data(
        self, graph_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract embeddable content chunks from Neo4j graph query results.

        Args:
            graph_data: Results from Neo4j query

        Returns:
            List of content chunks with embeddings and metadata
        """
        content_chunks = []

        # Process SEC filings
        filings = graph_data.get("recent_filings", [])
        for filing in filings:
            if isinstance(filing, dict):
                # Extract sections with embeddings
                sections = {
                    "business_overview": filing.get("business_overview"),
                    "risk_factors": filing.get("risk_factors"),
                    "financial_statements": filing.get("financial_statements"),
                    "md_and_a": filing.get("md_and_a"),
                }

                for section_name, content in sections.items():
                    if content:
                        embedding_key = f"{section_name}_embedding"
                        embedding = filing.get(embedding_key)

                        if embedding:
                            content_chunks.append(
                                {
                                    "content": content,
                                    "embedding": embedding,
                                    "source": f"SEC Filing {filing.get('filing_type', 'Unknown')}",
                                    "document_type": "sec_filing",
                                    "section": section_name,
                                    "document_date": filing.get(
                                        "filing_date", datetime.now()
                                    ),
                                    "metadata": {
                                        "filing_type": filing.get("filing_type"),
                                        "accession_number": filing.get(
                                            "accession_number"
                                        ),
                                        "cik": filing.get("cik"),
                                    },
                                }
                            )

        # Process news events
        news_events = graph_data.get("recent_news", [])
        for news in news_events:
            if isinstance(news, dict):
                # Process title
                title = news.get("title")
                title_embedding = news.get("title_embedding")
                if title and title_embedding:
                    content_chunks.append(
                        {
                            "content": title,
                            "embedding": title_embedding,
                            "source": f"News: {news.get('source', 'Unknown')}",
                            "document_type": "news",
                            "section": "title",
                            "document_date": news.get("published_date", datetime.now()),
                            "metadata": {
                                "sentiment_score": news.get("sentiment_score"),
                                "impact_categories": news.get("impact_categories"),
                                "url": news.get("url"),
                            },
                        }
                    )

                # Process content
                content = news.get("content")
                content_embedding = news.get("content_embedding")
                if content and content_embedding:
                    content_chunks.append(
                        {
                            "content": content,
                            "embedding": content_embedding,
                            "source": f"News: {news.get('source', 'Unknown')}",
                            "document_type": "news",
                            "section": "content",
                            "document_date": news.get("published_date", datetime.now()),
                            "metadata": {
                                "sentiment_score": news.get("sentiment_score"),
                                "impact_categories": news.get("impact_categories"),
                                "url": news.get("url"),
                            },
                        }
                    )

        # Process document chunks (if any exist)
        doc_chunks = graph_data.get("document_chunks", [])
        for chunk in doc_chunks:
            if isinstance(chunk, dict) and chunk.get("embedding"):
                content_chunks.append(
                    {
                        "content": chunk.get("content", ""),
                        "embedding": chunk.get("embedding"),
                        "source": f"Document Chunk {chunk.get('chunk_index', 0)}",
                        "document_type": chunk.get("source_document_type", "unknown"),
                        "section": chunk.get("section_name"),
                        "document_date": chunk.get("created_at", datetime.now()),
                        "metadata": {
                            "chunk_index": chunk.get("chunk_index"),
                            "token_count": chunk.get("token_count"),
                            "keywords": chunk.get("relevance_keywords", []),
                        },
                    }
                )

        return content_chunks

    def rank_by_relevance_and_recency(
        self,
        chunks: List[RetrievalResult],
        question: str,
        recency_weight: float = 0.3,
        similarity_weight: float = 0.7,
    ) -> List[RetrievalResult]:
        """
        Rank content chunks by combined relevance and recency scores.

        Args:
            chunks: List of RetrievalResult objects
            question: Original question for keyword matching
            recency_weight: Weight for recency score (0-1)
            similarity_weight: Weight for similarity score (0-1)

        Returns:
            Ranked list of RetrievalResult objects
        """
        current_date = datetime.now()
        question_lower = question.lower()

        # Extract key terms from question for keyword relevance
        question_keywords = self._extract_keywords(question_lower)

        for chunk in chunks:
            # Calculate recency score (newer content gets higher score)
            if isinstance(chunk.document_date, datetime):
                days_old = (current_date - chunk.document_date).days
            else:
                days_old = 365  # Default to 1 year old if no date

            # Recency score decreases exponentially with age
            recency_score = max(0, 1 - (days_old / 365))  # 1 year decay to 0

            # Calculate keyword relevance boost
            content_lower = chunk.content.lower()
            keyword_matches = sum(
                1 for keyword in question_keywords if keyword in content_lower
            )
            keyword_boost = min(0.2, keyword_matches * 0.05)  # Max 20% boost

            # Calculate document type relevance
            type_boost = self._get_document_type_boost(chunk.document_type, question)

            # Calculate final relevance score
            base_score = (
                similarity_weight * chunk.similarity_score
                + recency_weight * recency_score
            )
            final_score = base_score + keyword_boost + type_boost

            chunk.relevance_score = min(1.0, final_score)  # Cap at 1.0

        # Sort by relevance score (descending)
        chunks.sort(key=lambda x: x.relevance_score, reverse=True)

        return chunks

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text for relevance calculation.

        Args:
            text: Input text

        Returns:
            List of important keywords
        """
        # Simple keyword extraction (can be enhanced with NLP libraries)
        import re

        # Remove common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "what",
            "when",
            "where",
            "why",
            "how",
            "which",
            "who",
            "whose",
        }

        # Extract words (alphanumeric, 3+ characters)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Filter out stop words and return unique keywords
        keywords = [word for word in words if word not in stop_words]

        return list(set(keywords))

    def _get_document_type_boost(self, document_type: str, question: str) -> float:
        """
        Calculate relevance boost based on document type and question context.

        Args:
            document_type: Type of document (sec_filing, news, etc.)
            question: Original question

        Returns:
            Relevance boost value (0-0.15)
        """
        question_lower = question.lower()

        # Document type relevance mapping
        type_relevance = {
            "sec_filing": {
                "keywords": [
                    "financial",
                    "filing",
                    "sec",
                    "10-k",
                    "10-q",
                    "risk",
                    "revenue",
                    "earnings",
                ],
                "boost": 0.1,
            },
            "news": {
                "keywords": [
                    "news",
                    "recent",
                    "latest",
                    "announcement",
                    "event",
                    "impact",
                ],
                "boost": 0.1,
            },
            "dcf_valuation": {
                "keywords": [
                    "valuation",
                    "dcf",
                    "value",
                    "worth",
                    "price",
                    "intrinsic",
                ],
                "boost": 0.15,
            },
        }

        boost_config = type_relevance.get(document_type, {"keywords": [], "boost": 0})

        # Check if question contains relevant keywords for this document type
        keyword_matches = sum(
            1 for keyword in boost_config["keywords"] if keyword in question_lower
        )

        if keyword_matches > 0:
            return boost_config["boost"]

        return 0.0

    def filter_by_date_range(
        self,
        results: List[RetrievalResult],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[RetrievalResult]:
        """
        Filter results by date range.

        Args:
            results: List of retrieval results
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Filtered list of results
        """
        if not start_date and not end_date:
            return results

        filtered_results = []

        for result in results:
            doc_date = result.document_date

            # Check date range
            if start_date and doc_date < start_date:
                continue
            if end_date and doc_date > end_date:
                continue

            filtered_results.append(result)

        return filtered_results

    def get_content_summary(self, results: List[RetrievalResult]) -> Dict[str, Any]:
        """
        Generate a summary of retrieved content for context building.

        Args:
            results: List of retrieval results

        Returns:
            Summary dictionary with content statistics and top sources
        """
        if not results:
            return {"total_results": 0}

        # Calculate statistics
        total_results = len(results)
        avg_similarity = sum(r.similarity_score for r in results) / total_results
        avg_relevance = sum(r.relevance_score for r in results) / total_results

        # Group by document type
        type_counts = {}
        for result in results:
            doc_type = result.document_type
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

        # Get date range
        dates = [
            r.document_date for r in results if isinstance(r.document_date, datetime)
        ]
        date_range = {
            "earliest": min(dates).isoformat() if dates else None,
            "latest": max(dates).isoformat() if dates else None,
        }

        return {
            "total_results": total_results,
            "avg_similarity_score": round(avg_similarity, 3),
            "avg_relevance_score": round(avg_relevance, 3),
            "document_types": type_counts,
            "date_range": date_range,
            "top_sources": [r.source for r in results[:3]],
        }
