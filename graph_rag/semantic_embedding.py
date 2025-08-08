#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Embedding Module for Graph RAG System

This module provides semantic embedding functionality using sentence transformers
to enable vector similarity search and content understanding.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning(
        "sentence-transformers not available. Install with: pip install sentence-transformers"
    )

logger = logging.getLogger(__name__)


class SemanticEmbedding:
    """
    Handles semantic embedding generation for documents and sections
    using sentence transformers models.
    """

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the semantic embedding system.

        Args:
            embedding_model: HuggingFace model identifier for sentence transformers
        """
        self.embedding_model_name = embedding_model
        self.model = None

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(embedding_model)
                logger.info(f"Loaded embedding model: {embedding_model}")
            except Exception as e:
                logger.error(f"Failed to load embedding model {embedding_model}: {e}")
                self.model = None
        else:
            logger.warning(
                "Sentence transformers not available. Embedding functionality disabled."
            )

    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text string.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding, or None if embedding fails
        """
        if not self.model or not text:
            return None

        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            return None

    def embed_document_sections(self, sec_filing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate semantic embeddings for SEC filing sections.

        Args:
            sec_filing: Dictionary containing SEC filing data with sections

        Returns:
            Dictionary with embeddings for each section
        """
        if not self.model:
            logger.warning("Embedding model not available")
            return {}

        # Define the sections we want to embed
        sections = {
            "business_overview": sec_filing.get("item_1", ""),
            "risk_factors": sec_filing.get("item_1a", ""),
            "financial_statements": sec_filing.get("item_8", ""),
            "md_and_a": sec_filing.get(
                "item_7", ""
            ),  # Management Discussion & Analysis
        }

        embeddings = {}

        for section_name, content in sections.items():
            if content and isinstance(content, str) and len(content.strip()) > 0:
                try:
                    # Split long content into chunks for better processing
                    chunks = self.chunk_text(content, max_length=512)

                    if chunks:
                        # Generate embeddings for all chunks
                        chunk_embeddings = []
                        for chunk in chunks:
                            chunk_embedding = self.embed_text(chunk)
                            if chunk_embedding:
                                chunk_embeddings.append(chunk_embedding)

                        if chunk_embeddings:
                            # Calculate aggregate embedding as mean of chunks
                            chunk_embeddings_array = np.array(chunk_embeddings)
                            aggregate_embedding = np.mean(
                                chunk_embeddings_array, axis=0
                            )

                            embeddings[section_name] = {
                                "chunks": chunks,
                                "chunk_embeddings": chunk_embeddings,
                                "aggregate_embedding": aggregate_embedding.tolist(),
                                "num_chunks": len(chunks),
                                "processing_timestamp": datetime.now().isoformat(),
                            }

                            logger.debug(
                                f"Generated embeddings for {section_name}: {len(chunks)} chunks"
                            )
                        else:
                            logger.warning(
                                f"Failed to generate chunk embeddings for {section_name}"
                            )
                    else:
                        logger.warning(f"No chunks generated for {section_name}")

                except Exception as e:
                    logger.error(f"Failed to process section {section_name}: {e}")
                    continue
            else:
                logger.debug(f"Skipping empty or invalid section: {section_name}")

        return embeddings

    def chunk_text(
        self, text: str, max_length: int = 512, overlap: int = 50
    ) -> List[str]:
        """
        Split text into overlapping chunks for better embedding processing.

        Args:
            text: Input text to chunk
            max_length: Maximum length of each chunk in characters
            overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if not text or len(text.strip()) == 0:
            return []

        text = text.strip()

        # If text is shorter than max_length, return as single chunk
        if len(text) <= max_length:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position
            end = start + max_length

            # If this would be the last chunk, include all remaining text
            if end >= len(text):
                chunk = text[start:]
                if chunk.strip():
                    chunks.append(chunk.strip())
                break

            # Try to find a good breaking point (sentence or word boundary)
            chunk_text = text[start:end]

            # Look for sentence boundaries
            sentence_endings = [". ", "! ", "? ", "\n\n"]
            best_break = -1

            for ending in sentence_endings:
                last_occurrence = chunk_text.rfind(ending)
                if last_occurrence > len(chunk_text) * 0.5:  # Must be in latter half
                    best_break = max(best_break, last_occurrence + len(ending))

            # If no good sentence break found, look for word boundaries
            if best_break == -1:
                last_space = chunk_text.rfind(" ")
                if last_space > len(chunk_text) * 0.7:  # Must be in latter 30%
                    best_break = last_space

            # If still no good break found, just use max_length
            if best_break == -1:
                best_break = max_length

            chunk = text[start : start + best_break].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = start + best_break - overlap
            if start < 0:
                start = best_break

        return chunks

    def embed_news_content(self, news_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embeddings for news event content.

        Args:
            news_event: Dictionary containing news event data

        Returns:
            Dictionary with title and content embeddings
        """
        if not self.model:
            return {}

        embeddings = {}

        # Embed title
        title = news_event.get("title", "")
        if title:
            title_embedding = self.embed_text(title)
            if title_embedding:
                embeddings["title_embedding"] = title_embedding

        # Embed content
        content = news_event.get("content", "")
        if content:
            # For news content, we may also want to chunk if it's very long
            if len(content) > 1000:
                chunks = self.chunk_text(content, max_length=512)
                chunk_embeddings = []
                for chunk in chunks:
                    chunk_embedding = self.embed_text(chunk)
                    if chunk_embedding:
                        chunk_embeddings.append(chunk_embedding)

                if chunk_embeddings:
                    # Use mean embedding for content
                    content_embedding = np.mean(chunk_embeddings, axis=0)
                    embeddings["content_embedding"] = content_embedding.tolist()
                    embeddings["content_chunks"] = chunks
            else:
                content_embedding = self.embed_text(content)
                if content_embedding:
                    embeddings["content_embedding"] = content_embedding

        return embeddings

    def calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        if not embedding1 or not embedding2:
            return 0.0

        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0

    def find_most_similar_chunks(
        self,
        query_embedding: List[float],
        document_chunks: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find the most similar document chunks to a query embedding.

        Args:
            query_embedding: Query vector
            document_chunks: List of document chunks with embeddings
            top_k: Number of top results to return

        Returns:
            List of most similar chunks with similarity scores
        """
        if not query_embedding or not document_chunks:
            return []

        chunk_similarities = []

        for chunk in document_chunks:
            chunk_embedding = chunk.get("embedding")
            if chunk_embedding:
                similarity = self.calculate_similarity(query_embedding, chunk_embedding)
                chunk_similarities.append(
                    {"chunk": chunk, "similarity_score": similarity}
                )

        # Sort by similarity score (descending)
        chunk_similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

        return chunk_similarities[:top_k]
