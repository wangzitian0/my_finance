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

# Lazy import ML service to avoid circular import issues
ML_DEPENDENCIES_AVAILABLE = False
ml_service = None
FAISS_AVAILABLE = False


def _get_ml_service():
    """Lazy initialization of ML service"""
    global ML_DEPENDENCIES_AVAILABLE, ml_service

    if ml_service is not None:
        return ml_service

    try:
        # Try to use ML service from Docker container
        from common.ml_fallback import get_ml_service

        ml_service = get_ml_service()
        ML_DEPENDENCIES_AVAILABLE = True
        logging.info("Using ML service for semantic retrieval")
        return ml_service
    except Exception as e:
        logging.warning(f"ML service not available: {e}")
        ML_DEPENDENCIES_AVAILABLE = False
        return None


# Check if we should skip all imports in dev mode
import os

SKIP_ML_IMPORTS = (
    os.environ.get("SKIP_DCF_ANALYSIS", "").lower() == "true"
    or os.environ.get("SKIP_SEMANTIC_RETRIEVAL", "").lower() == "true"
)

if SKIP_ML_IMPORTS:
    # In dev mode, skip all potentially problematic imports
    FAISS_AVAILABLE = False
    NUMPY_AVAILABLE = False
    faiss = None
    np = None
    logging.info("Skipping FAISS and NumPy imports (dev mode)")
else:
    # Try to import faiss, but don't fail if it's not available
    try:
        import faiss

        FAISS_AVAILABLE = True
        logging.info("FAISS available for vector indexing")
    except ImportError as e:
        FAISS_AVAILABLE = False
        logging.warning(f"FAISS not available, using simple vector search: {e}")
        faiss = None

    # Check numpy availability separately
    NUMPY_AVAILABLE = False
    np = None
    try:
        import numpy as np

        NUMPY_AVAILABLE = True
    except ImportError:
        NUMPY_AVAILABLE = False

from common.graph_rag_schema import (
    DEFAULT_EMBEDDING_CONFIG,
    DocumentChunkNode,
    DocumentType,
    ETLStageOutput,
    SemanticSearchResult,
    VectorEmbeddingConfig,
)

logger = logging.getLogger(__name__)


class SimpleVectorIndex:
    """Simple vector index fallback when FAISS is not available"""

    def __init__(self, dimension):
        self.dimension = dimension
        self.vectors = []
        self.ntotal = 0

    def add(self, vectors):
        """Add vectors to the index"""
        if hasattr(vectors, "tolist"):
            self.vectors.extend(vectors.tolist())
        else:
            self.vectors.extend(vectors)
        self.ntotal = len(self.vectors)

    def search(self, query_vectors, k):
        """Simple cosine similarity search"""
        if not self.vectors:
            return [], []

        # Simple dot product similarity
        results = []
        for query in query_vectors.tolist() if hasattr(query_vectors, "tolist") else query_vectors:
            similarities = []
            for idx, vec in enumerate(self.vectors):
                # Simple dot product
                similarity = sum(q * v for q, v in zip(query, vec))
                similarities.append((similarity, idx))

            # Sort by similarity and get top k
            similarities.sort(reverse=True)
            top_k = similarities[:k]

            distances = [sim for sim, _ in top_k]
            indices = [idx for _, idx in top_k]
            results.append((distances, indices))

        if results:
            return [results[0][0]], [results[0][1]]
        return [], []


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
        """Setup the ML service for embeddings."""
        try:
            service = _get_ml_service()
            if service:
                logger.info(f"Using ML fallback service for model: {self.config.model_name}")
                self.model = service  # Use our fallback service
                logger.info("ML service ready for embeddings")
            else:
                logger.warning("No ML service available, using simple fallback")
                self.model = None
        except Exception as e:
            logger.error(f"Failed to setup ML service: {e}")
            self.model = None

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

    def _generate_chunk_embedding(self, text: str):
        """Generate embedding vector for a text chunk."""
        try:
            # Clean text
            text = text.replace("\n", " ").replace("\r", " ").strip()
            if not text:
                return [0.0] * self.config.dimension

            # Generate embedding using ML service
            if self.model:
                embeddings = self.model.encode_texts([text])
                if hasattr(embeddings, "data"):  # SimpleArray from fallback
                    return embeddings.data[0]
                else:  # numpy array
                    return embeddings[0]
            else:
                # Simple fallback without ML service
                import hashlib

                text_hash = hashlib.md5(text.encode()).hexdigest()
                # Create simple embedding from hash
                embedding = []
                for i in range(min(len(text_hash), self.config.dimension // 16)):
                    chunk = text_hash[i * 2 : (i + 1) * 2]
                    if chunk:
                        embedding.append(int(chunk, 16) / 255.0 - 0.5)
                while len(embedding) < self.config.dimension:
                    embedding.append(0.0)
                return embedding[: self.config.dimension]

        except Exception as e:
            logger.error(f"Failed to generate embedding for text chunk: {e}")
            return [0.0] * self.config.dimension

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
            embeddings_list = [item["embedding_vector"] for item in embedding_data]

            # Get dimension
            if embeddings_list and len(embeddings_list[0]) > 0:
                dimension = len(embeddings_list[0])
            else:
                dimension = 384  # Default dimension

            # Create vector index
            if FAISS_AVAILABLE:
                # Use FAISS if available
                import numpy as np

                embeddings = np.array(embeddings_list)
                self.vector_index = faiss.IndexFlatIP(dimension)
                faiss.normalize_L2(embeddings)
                self.vector_index.add(embeddings)
            else:
                # Use simple fallback
                self.vector_index = SimpleVectorIndex(dimension)
                # Normalize vectors manually
                normalized = []
                for vec in embeddings_list:
                    norm = sum(v * v for v in vec) ** 0.5
                    if norm > 0:
                        normalized.append([v / norm for v in vec])
                    else:
                        normalized.append(vec)
                self.vector_index.add(normalized)

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
            embeddings_list = [item["embedding_vector"] for item in embedding_data]
            if NUMPY_AVAILABLE and np:
                embeddings = np.array(embeddings_list)
                np.save(embeddings_file, embeddings)
            else:
                embeddings = embeddings_list
                # Save as JSON when numpy not available
                import json

                with open(str(embeddings_file).replace(".npy", ".json"), "w") as f:
                    json.dump(embeddings, f)

            # Save vector index if available
            if self.vector_index and FAISS_AVAILABLE:
                index_file = output_path / "vector_index.faiss"
                faiss.write_index(self.vector_index, str(index_file))
            elif self.vector_index:
                # Save simple index as JSON
                index_file = output_path / "vector_index.json"
                with open(index_file, "w") as f:
                    json.dump(
                        {
                            "dimension": self.vector_index.dimension,
                            "vectors": self.vector_index.vectors,
                            "ntotal": self.vector_index.ntotal,
                        },
                        f,
                    )

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
            # Load ML service instead of direct model
            service = _get_ml_service()
            if service:
                logger.info(
                    f"Using ML fallback service for retrieval model: {self.config.model_name}"
                )
                self.model = service
            else:
                logger.warning("No ML service available for retrieval")
                self.model = None

            # Load metadata
            metadata_file = self.embeddings_path / "embeddings_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata_list = json.load(f)
                self.document_metadata = {i: item for i, item in enumerate(metadata_list)}

            # Load vector index
            if FAISS_AVAILABLE:
                index_file = self.embeddings_path / "vector_index.faiss"
                if index_file.exists():
                    self.vector_index = faiss.read_index(str(index_file))
                    logger.info(f"Loaded FAISS index with {self.vector_index.ntotal} vectors")
            else:
                # Load simple index from JSON
                index_file = self.embeddings_path / "vector_index.json"
                if index_file.exists():
                    with open(index_file, "r") as f:
                        index_data = json.load(f)
                    self.vector_index = SimpleVectorIndex(index_data["dimension"])
                    self.vector_index.vectors = index_data["vectors"]
                    self.vector_index.ntotal = index_data["ntotal"]
                    logger.info(f"Loaded simple index with {self.vector_index.ntotal} vectors")

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
        # Check if semantic retrieval should be skipped in dev mode
        import os

        if os.environ.get("SKIP_SEMANTIC_RETRIEVAL", "").lower() == "true":
            logger.info("Skipping semantic retrieval (dev mode)")
            return []

        top_k = top_k or self.config.max_results
        min_similarity = min_similarity or self.config.similarity_threshold

        try:
            if not self.vector_index or not self.model:
                logger.error(
                    f"Vector index or model not loaded - index: {self.vector_index is not None}, model: {self.model is not None}"
                )
                # In dev mode, return empty results instead of hanging
                if os.environ.get("SKIP_DCF_ANALYSIS", "").lower() == "true":
                    logger.info("Returning empty results due to dev mode")
                    return []
                # Try to initialize with simple defaults
                if not self.vector_index:
                    self.vector_index = SimpleVectorIndex(384)
                    logger.info("Created empty SimpleVectorIndex as fallback")
                return []

            # Generate query embedding using ML service
            if self.model:
                embeddings = self.model.encode_texts([query])
                if hasattr(embeddings, "data"):  # SimpleArray from fallback
                    if NUMPY_AVAILABLE and np:
                        query_embedding = np.array([embeddings.data[0]], dtype=np.float32)
                    else:
                        query_embedding = [embeddings.data[0]]
                else:  # numpy array
                    query_embedding = embeddings
            else:
                # Simple fallback
                import hashlib

                query_hash = hashlib.md5(query.encode()).hexdigest()
                embedding = []
                for i in range(min(len(query_hash), self.config.dimension // 16)):
                    chunk = query_hash[i * 2 : (i + 1) * 2]
                    if chunk:
                        embedding.append(int(chunk, 16) / 255.0 - 0.5)
                while len(embedding) < self.config.dimension:
                    embedding.append(0.0)
                if NUMPY_AVAILABLE and np:
                    query_embedding = np.array(
                        [embedding[: self.config.dimension]], dtype=np.float32
                    )
                else:
                    query_embedding = [embedding[: self.config.dimension]]
            # Normalize query embedding
            if FAISS_AVAILABLE:
                faiss.normalize_L2(query_embedding)
            else:
                # Manual normalization
                if isinstance(query_embedding, list):
                    for vec in query_embedding:
                        norm = sum(v * v for v in vec) ** 0.5
                        if norm > 0:
                            for i in range(len(vec)):
                                vec[i] /= norm

            # Search vector index
            scores, indices = self.vector_index.search(
                query_embedding, min(top_k * 2, self.vector_index.ntotal)
            )

            results = []
            # Handle empty results safely
            if len(scores) > 0 and len(indices) > 0 and len(scores[0]) > 0:
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
