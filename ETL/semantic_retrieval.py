#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL Semantic Retrieval Module

Handles vector embedding generation and semantic retrieval functionality.
This module is responsible for:
- Generating semantic embeddings from documents
- Creating and managing vector indexes
- Performing similarity-based content retrieval
- Managing embedding storage and caching

Part of Stage 3 (Load) in the ETL pipeline.
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import faiss
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    ML_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    ML_DEPENDENCIES_AVAILABLE = False
    print(f"ML dependencies not available: {e}")

from common.graph_rag_schema import (
    DEFAULT_EMBEDDING_CONFIG,
    DocumentChunkNode,
    DocumentType,
    ETLStageOutput,
    SemanticSearchResult,
    VectorEmbeddingConfig,
)

logger = logging.getLogger(__name__)


class SemanticEmbeddingGenerator:
    """
    Generates and manages semantic embeddings for financial documents.

    This class handles the creation of vector embeddings from text content
    and provides similarity-based retrieval capabilities.
    """

    def __init__(self, config: VectorEmbeddingConfig = None):
        """
        Initialize the semantic embedding generator.

        Args:
            config: Configuration for embedding generation
        """
        self.config = config or DEFAULT_EMBEDDING_CONFIG
        self.model = None
        self.vector_index = None
        self.document_metadata = {}
        self.setup_model()

    def setup_model(self):
        """Setup the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.config.model_name}")
            self.model = SentenceTransformer(self.config.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def generate_document_embeddings(self, data_dir: Path) -> ETLStageOutput.EmbeddingsOutput:
        """
        Generate embeddings for all documents in the data directory.

        Args:
            data_dir: Root directory containing document data

        Returns:
            EmbeddingsOutput with generation statistics
        """
        logger.info("Starting document embedding generation")

        embeddings_created = 0
        documents_processed = 0
        embedding_data = []

        try:
            # Process SEC documents
            sec_stats = self._process_sec_documents(data_dir, embedding_data)
            embeddings_created += sec_stats["embeddings"]
            documents_processed += sec_stats["documents"]

            # Process Yahoo Finance data
            yf_stats = self._process_yfinance_documents(data_dir, embedding_data)
            embeddings_created += yf_stats["embeddings"]
            documents_processed += yf_stats["documents"]

            # Build vector index
            if embedding_data:
                self._build_vector_index(embedding_data)

            # Save embeddings and metadata
            output_path = data_dir / "stage_03_load" / "embeddings"
            output_path.mkdir(parents=True, exist_ok=True)

            self._save_embeddings_data(embedding_data, output_path)

            logger.info(
                f"Embedding generation completed. Documents processed: {documents_processed}, "
                f"embeddings created: {embeddings_created}"
            )

            return ETLStageOutput.EmbeddingsOutput(
                embeddings_created=embeddings_created,
                documents_processed=documents_processed,
                model_used=self.config.model_name,
                dimension=self.config.dimension,
                output_path=str(output_path),
            )

        except Exception as e:
            logger.error(f"Failed to generate document embeddings: {e}")
            raise

    def _process_sec_documents(self, data_dir: Path, embedding_data: List[Dict]) -> Dict[str, int]:
        """Process SEC documents for embedding generation."""
        stats = {"embeddings": 0, "documents": 0}

        sec_dir = data_dir / "stage_01_extract" / "sec_edgar"
        if not sec_dir.exists():
            logger.warning(f"SEC directory not found: {sec_dir}")
            return stats

        # Find latest partition
        partitions = [d for d in sec_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        if not partitions:
            return stats

        latest_partition = max(partitions, key=lambda x: x.name)

        # Process each company's SEC files
        for company_dir in latest_partition.iterdir():
            if not company_dir.is_dir():
                continue

            ticker = company_dir.name
            if ticker.startswith("CIK_"):  # Skip CIK directories
                continue

            sec_files = list(company_dir.glob("*_sec_edgar_*.txt"))
            logger.info(f"Processing {len(sec_files)} SEC files for {ticker}")

            for sec_file in sec_files:
                try:
                    # Read and chunk document
                    with open(sec_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    chunks = self._chunk_document(content, sec_file.stem)

                    # Generate embeddings for chunks
                    for i, chunk in enumerate(chunks):
                        chunk_embedding = self._generate_chunk_embedding(chunk["content"])

                        # Create document chunk metadata
                        chunk_data = {
                            "node_id": f"chunk_{sec_file.stem}_{i}",
                            "document_id": sec_file.stem,
                            "chunk_index": i,
                            "content": chunk["content"],
                            "content_type": self._get_sec_document_type(sec_file.name),
                            "embedding_vector": chunk_embedding.tolist(),
                            "parent_document": sec_file.name,
                            "ticker": ticker,
                            "metadata": {
                                "file_path": str(sec_file),
                                "chunk_start": chunk["start"],
                                "chunk_end": chunk["end"],
                            },
                        }

                        embedding_data.append(chunk_data)
                        stats["embeddings"] += 1

                    stats["documents"] += 1

                except Exception as e:
                    logger.error(f"Failed to process SEC file {sec_file}: {e}")
                    continue

        return stats

    def _process_yfinance_documents(
        self, data_dir: Path, embedding_data: List[Dict]
    ) -> Dict[str, int]:
        """Process Yahoo Finance JSON documents for embedding generation."""
        stats = {"embeddings": 0, "documents": 0}

        yf_dir = data_dir / "stage_01_extract" / "yfinance"
        if not yf_dir.exists():
            logger.warning(f"YFinance directory not found: {yf_dir}")
            return stats

        # Find latest partition with data
        for partition_dir in sorted(yf_dir.iterdir(), reverse=True):
            if not partition_dir.is_dir() or not partition_dir.name.isdigit():
                continue

            # Process each ticker directory
            for ticker_dir in partition_dir.iterdir():
                if not ticker_dir.is_dir():
                    continue

                ticker = ticker_dir.name
                yf_files = list(ticker_dir.glob(f"{ticker}_yfinance_*.json"))

                if not yf_files:
                    continue

                logger.info(f"Processing {len(yf_files)} YFinance files for {ticker}")

                for yf_file in yf_files:
                    try:
                        with open(yf_file, "r") as f:
                            yf_data = json.load(f)

                        # Convert financial data to text for embedding
                        text_content = self._yfinance_to_text(yf_data, ticker)

                        if text_content:
                            chunk_embedding = self._generate_chunk_embedding(text_content)

                            chunk_data = {
                                "node_id": f"chunk_{yf_file.stem}",
                                "document_id": yf_file.stem,
                                "chunk_index": 0,
                                "content": text_content,
                                "content_type": DocumentType.YFINANCE_DATA.value,
                                "embedding_vector": chunk_embedding.tolist(),
                                "parent_document": yf_file.name,
                                "ticker": ticker,
                                "metadata": {
                                    "file_path": str(yf_file),
                                    "data_type": "yfinance_json",
                                },
                            }

                            embedding_data.append(chunk_data)
                            stats["embeddings"] += 1
                            stats["documents"] += 1

                    except Exception as e:
                        logger.error(f"Failed to process YFinance file {yf_file}: {e}")
                        continue

            # Process only the latest partition
            break

        return stats

    def _chunk_document(self, content: str, doc_id: str) -> List[Dict[str, Any]]:
        """
        Split document into chunks for embedding.

        Args:
            content: Document content
            doc_id: Document identifier

        Returns:
            List of document chunks with metadata
        """
        chunk_size = self.config.chunk_size
        chunk_overlap = self.config.chunk_overlap

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size
            chunk_text = content[start:end]

            # Try to break at sentence boundaries
            if end < len(content):
                last_period = chunk_text.rfind(".")
                last_newline = chunk_text.rfind("\n")
                break_point = max(last_period, last_newline)

                if break_point > start + chunk_size // 2:  # At least half the chunk size
                    end = start + break_point + 1
                    chunk_text = content[start:end]

            chunks.append({"content": chunk_text.strip(), "start": start, "end": end})

            start = end - chunk_overlap

        return chunks

    def _generate_chunk_embedding(self, text: str) -> np.ndarray:
        """Generate embedding vector for a text chunk."""
        try:
            # Clean text
            text = text.replace("\n", " ").replace("\r", " ").strip()
            if not text:
                return np.zeros(self.config.dimension)

            # Generate embedding
            embedding = self.model.encode([text])
            return embedding[0]

        except Exception as e:
            logger.error(f"Failed to generate embedding for text chunk: {e}")
            return np.zeros(self.config.dimension)

    def _get_sec_document_type(self, filename: str) -> str:
        """Extract SEC document type from filename."""
        if "_10k_" in filename:
            return DocumentType.SEC_10K.value
        elif "_10q_" in filename:
            return DocumentType.SEC_10Q.value
        elif "_8k_" in filename:
            return DocumentType.SEC_8K.value
        else:
            return "sec_unknown"

    def _yfinance_to_text(self, yf_data: Dict, ticker: str) -> str:
        """Convert Yahoo Finance JSON data to text for embedding."""
        try:
            text_parts = [f"Financial data for {ticker}:"]

            # Process different data types
            if isinstance(yf_data, dict):
                for key, value in yf_data.items():
                    if isinstance(value, (str, int, float)):
                        text_parts.append(f"{key}: {value}")
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, (str, int, float)):
                                text_parts.append(f"{key} {sub_key}: {sub_value}")

            return " ".join(text_parts)

        except Exception as e:
            logger.error(f"Failed to convert YFinance data to text: {e}")
            return ""

    def _build_vector_index(self, embedding_data: List[Dict]):
        """Build FAISS vector index for similarity search."""
        try:
            if not embedding_data:
                return

            # Extract embeddings
            embeddings = np.array([item["embedding_vector"] for item in embedding_data])

            # Create FAISS index
            dimension = embeddings.shape[1]
            self.vector_index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)

            # Normalize vectors for cosine similarity
            faiss.normalize_L2(embeddings)
            self.vector_index.add(embeddings)

            # Store metadata for retrieval
            self.document_metadata = {i: item for i, item in enumerate(embedding_data)}

            logger.info(f"Built vector index with {len(embedding_data)} embeddings")

        except Exception as e:
            logger.error(f"Failed to build vector index: {e}")
            raise

    def _save_embeddings_data(self, embedding_data: List[Dict], output_path: Path):
        """Save embeddings and metadata to disk."""
        try:
            # Save embeddings metadata
            metadata_file = output_path / "embeddings_metadata.json"
            with open(metadata_file, "w") as f:
                # Remove embedding vectors for metadata file (save space)
                metadata = []
                for item in embedding_data:
                    meta_item = item.copy()
                    meta_item["embedding_dimension"] = len(item["embedding_vector"])
                    del meta_item["embedding_vector"]  # Remove large vectors from metadata
                    metadata.append(meta_item)

                json.dump(metadata, f, indent=2, default=str)

            # Save embeddings separately
            embeddings_file = output_path / "embeddings_vectors.npy"
            embeddings = np.array([item["embedding_vector"] for item in embedding_data])
            np.save(embeddings_file, embeddings)

            # Save FAISS index if available
            if self.vector_index:
                index_file = output_path / "vector_index.faiss"
                faiss.write_index(self.vector_index, str(index_file))

            logger.info(f"Saved embeddings data to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save embeddings data: {e}")
            raise


class SemanticRetriever:
    """
    Performs semantic retrieval from vector embeddings.

    This class provides similarity-based search capabilities
    for the Graph RAG system.
    """

    def __init__(self, embeddings_path: Path, config: VectorEmbeddingConfig = None):
        """
        Initialize the semantic retriever.

        Args:
            embeddings_path: Path to saved embeddings data
            config: Embedding configuration
        """
        self.embeddings_path = embeddings_path
        self.config = config or DEFAULT_EMBEDDING_CONFIG
        self.model = None
        self.vector_index = None
        self.document_metadata = {}
        self.load_embeddings()

    def load_embeddings(self):
        """Load embeddings and vector index from disk."""
        try:
            # Load embedding model
            self.model = SentenceTransformer(self.config.model_name)

            # Load metadata
            metadata_file = self.embeddings_path / "embeddings_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata_list = json.load(f)
                self.document_metadata = {i: item for i, item in enumerate(metadata_list)}

            # Load FAISS index
            index_file = self.embeddings_path / "vector_index.faiss"
            if index_file.exists():
                self.vector_index = faiss.read_index(str(index_file))
                logger.info(f"Loaded vector index with {self.vector_index.ntotal} vectors")

        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            raise

    def retrieve_relevant_content(
        self,
        query: str,
        top_k: int = None,
        min_similarity: float = None,
        content_filter: Dict[str, Any] = None,
    ) -> List[SemanticSearchResult]:
        """
        Retrieve semantically relevant content for a query.

        Args:
            query: Search query text
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold
            content_filter: Filter criteria (e.g., ticker, document_type)

        Returns:
            List of relevant content with similarity scores
        """
        top_k = top_k or self.config.max_results
        min_similarity = min_similarity or self.config.similarity_threshold

        try:
            if not self.vector_index or not self.model:
                logger.error("Vector index or model not loaded")
                return []

            # Generate query embedding
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)

            # Search vector index
            scores, indices = self.vector_index.search(
                query_embedding, min(top_k * 2, self.vector_index.ntotal)
            )

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if score < min_similarity:
                    continue

                if idx in self.document_metadata:
                    metadata = self.document_metadata[idx]

                    # Apply content filter
                    if content_filter and not self._matches_filter(metadata, content_filter):
                        continue

                    result = SemanticSearchResult(
                        node_id=metadata["node_id"],
                        content=metadata["content"],
                        similarity_score=float(score),
                        metadata=metadata.get("metadata", {}),
                        source_document=metadata["parent_document"],
                        document_type=DocumentType(metadata["content_type"]),
                    )

                    results.append(result)

                    if len(results) >= top_k:
                        break

            logger.debug(f"Retrieved {len(results)} relevant content items for query")
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve relevant content: {e}")
            return []

    def _matches_filter(self, metadata: Dict[str, Any], content_filter: Dict[str, Any]) -> bool:
        """Check if metadata matches the content filter."""
        for key, value in content_filter.items():
            if key not in metadata:
                return False

            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False

        return True

    def get_similar_documents(self, document_id: str, top_k: int = 5) -> List[SemanticSearchResult]:
        """Find documents similar to a given document."""
        # Find the document's embedding
        for idx, metadata in self.document_metadata.items():
            if metadata["node_id"] == document_id:
                # Use the document's content as query
                return self.retrieve_relevant_content(
                    metadata["content"][:500],  # Use first 500 chars as query
                    top_k=top_k + 1,  # +1 to exclude self
                )[
                    1:
                ]  # Skip the first result (self)

        logger.warning(f"Document {document_id} not found")
        return []
