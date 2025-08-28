#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph RAG Schema Definitions

Centralized schema definitions for Graph RAG system including:
- Neo4j node and relationship models
- Vector embedding configurations
- Query intent classifications
- Data structure interfaces

This file is used by both ETL (data layer) and dcf_engine (business layer)
to ensure consistent data models across the system.

Issue #184: Moved to systems/ as part of library restructuring
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class QueryIntent(Enum):
    """Intent classification for user queries."""

    DCF_VALUATION = "dcf_valuation"
    FINANCIAL_COMPARISON = "financial_comparison"
    RISK_ANALYSIS = "risk_analysis"
    NEWS_IMPACT = "news_impact"
    INDUSTRY_ANALYSIS = "industry_analysis"
    HISTORICAL_TRENDS = "historical_trends"
    INVESTMENT_RECOMMENDATION = "investment_recommendation"
    GENERAL_INFO = "general_info"


class DocumentType(Enum):
    """Types of documents in the system."""

    SEC_10K = "10k"
    SEC_10Q = "10q"
    SEC_8K = "8k"
    NEWS_ARTICLE = "news"
    YFINANCE_DATA = "yfinance"
    DCF_RESULT = "dcf_result"


@dataclass
class VectorEmbeddingConfig:
    """Configuration for vector embeddings."""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    dimension: int = 384
    similarity_threshold: float = 0.3
    max_results: int = 10


@dataclass
class GraphNodeSchema:
    """Base schema for graph nodes."""

    node_id: str = ""
    node_type: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class StockNode(GraphNodeSchema):
    """Stock company node schema."""

    node_type: str = "Stock"
    ticker: str = ""
    company_name: str = ""
    cik: str = ""
    sector: str = ""
    industry: str = ""
    market_cap: Optional[float] = None


@dataclass
class SECFilingNode(GraphNodeSchema):
    """SEC filing document node schema."""

    node_type: str = "SECFiling"
    accession_number: str = ""
    filing_type: Optional[DocumentType] = None
    filing_date: Optional[datetime] = None
    period_end_date: Optional[datetime] = None
    company_cik: str = ""
    document_url: Optional[str] = None


@dataclass
class DocumentChunkNode(GraphNodeSchema):
    """Document chunk node for semantic search."""

    node_type: str = "DocumentChunk"
    document_id: str = ""
    chunk_index: int = 0
    content: str = ""
    content_type: Optional[DocumentType] = None
    embedding_vector: Optional[List[float]] = None
    parent_document: str = ""


@dataclass
class DCFValuationNode(GraphNodeSchema):
    """DCF valuation result node schema."""

    node_type: str = "DCFValuation"
    ticker: str = ""
    valuation_date: Optional[datetime] = None
    intrinsic_value: float = 0.0
    current_price: Optional[float] = None
    discount_rate: float = 0.1
    terminal_growth_rate: float = 0.03
    confidence_score: Optional[float] = None


@dataclass
class NewsEventNode(GraphNodeSchema):
    """News event node schema."""

    node_type: str = "NewsEvent"
    headline: str = ""
    publication_date: Optional[datetime] = None
    source: str = ""
    sentiment_score: Optional[float] = None
    impact_score: Optional[float] = None
    mentioned_tickers: List[str] = None

    def __post_init__(self):
        if self.mentioned_tickers is None:
            self.mentioned_tickers = []


@dataclass
class FinancialMetricsNode(GraphNodeSchema):
    """Financial metrics node schema."""

    node_type: str = "FinancialMetrics"
    ticker: str = ""
    report_date: Optional[datetime] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    free_cash_flow: Optional[float] = None
    total_debt: Optional[float] = None
    shareholders_equity: Optional[float] = None


class RelationshipType(Enum):
    """Types of relationships between nodes."""

    HAS_FILING = "HAS_FILING"
    MENTIONED_IN = "MENTIONED_IN"
    HAS_VALUATION = "HAS_VALUATION"
    HAS_METRIC = "HAS_METRIC"
    IMPACTS = "IMPACTS"
    USES = "USES"
    CHUNK_OF = "CHUNK_OF"
    SIMILAR_TO = "SIMILAR_TO"


@dataclass
class GraphRelationship:
    """Graph relationship schema."""

    source_node: str = ""
    target_node: str = ""
    relationship_type: Optional[RelationshipType] = None
    properties: Optional[Dict[str, Any]] = None
    weight: Optional[float] = None
    created_at: Optional[datetime] = None


@dataclass
class SemanticSearchResult:
    """Result from semantic search."""

    node_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    source_document: str
    document_type: DocumentType


@dataclass
class GraphRAGQuery:
    """Query structure for Graph RAG system."""

    question: str
    intent: QueryIntent
    entities: List[str]  # Extracted tickers, company names, etc.
    cypher_query: Optional[str] = None
    vector_query: Optional[str] = None
    context_filter: Optional[Dict[str, Any]] = None


@dataclass
class GraphRAGResponse:
    """Response structure from Graph RAG system."""

    answer: str
    confidence_score: float
    sources: List[SemanticSearchResult]
    reasoning_steps: List[str]
    cypher_results: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ETLStageOutput:
    """Interface for ETL stage outputs related to Graph RAG."""

    @dataclass
    class GraphNodesOutput:
        """Output from graph nodes creation stage."""

        nodes_created: int
        relationships_created: int
        node_types: Dict[str, int]
        output_path: str

    @dataclass
    class EmbeddingsOutput:
        """Output from embeddings generation stage."""

        embeddings_created: int
        documents_processed: int
        model_used: str
        dimension: int
        output_path: str

    @dataclass
    class VectorIndexOutput:
        """Output from vector index creation stage."""

        index_size: int
        index_type: str
        search_ready: bool
        output_path: str


# Configuration constants
MAGNIFICENT_7_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NFLX"]

MAGNIFICENT_7_CIKS = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "AMZN": "0001018724",
    "GOOGL": "0001652044",
    "META": "0001326801",
    "TSLA": "0001318605",
    "NFLX": "0001065280",
}

DEFAULT_EMBEDDING_CONFIG = VectorEmbeddingConfig()

# Neo4j Cypher query templates
CYPHER_TEMPLATES = {
    QueryIntent.DCF_VALUATION: """
        MATCH (s:Stock {ticker: $ticker})-[:HAS_VALUATION]->(dcf:DCFValuation)
        RETURN dcf
        ORDER BY dcf.valuation_date DESC
        LIMIT 1
    """,
    QueryIntent.FINANCIAL_COMPARISON: """
        MATCH (s1:Stock {ticker: $ticker1})-[:HAS_METRIC]->(m1:FinancialMetrics)
        MATCH (s2:Stock {ticker: $ticker2})-[:HAS_METRIC]->(m2:FinancialMetrics)
        WHERE m1.report_date = m2.report_date
        RETURN s1.ticker, s2.ticker, m1, m2
        ORDER BY m1.report_date DESC
        LIMIT 5
    """,
    QueryIntent.RISK_ANALYSIS: """
        MATCH (s:Stock {ticker: $ticker})-[:HAS_FILING]->(f:SECFiling)
        WHERE f.filing_type = '10K' OR f.filing_type = '10Q'
        MATCH (f)-[:CHUNK_OF]-(c:DocumentChunk)
        WHERE c.content CONTAINS 'risk' OR c.content CONTAINS 'uncertainty'
        RETURN c
        ORDER BY f.filing_date DESC
        LIMIT 10
    """,
}
