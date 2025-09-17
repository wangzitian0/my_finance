#!/usr/bin/env python3
"""
Data Schemas and Validation Models
Moved from schemas/ → data/schemas.py (Issue #284)

Data models and validation schemas consolidated into single module.
"""

try:
    # Try to import from the existing schemas location
    from common.schemas.graph_rag_schema import *
except ImportError:
    # Fallback implementations for CI/testing environments
    from dataclasses import dataclass
    from datetime import datetime
    from enum import Enum
    from typing import Any, Dict, List, Optional, Union

    class QueryIntent(Enum):
        DCF_VALUATION = "dcf_valuation"
        FINANCIAL_COMPARISON = "financial_comparison"
        RISK_ANALYSIS = "risk_analysis"
        NEWS_IMPACT = "news_impact"
        INDUSTRY_ANALYSIS = "industry_analysis"
        HISTORICAL_TRENDS = "historical_trends"
        INVESTMENT_RECOMMENDATION = "investment_recommendation"
        GENERAL_INFO = "general_info"

    class DocumentType(Enum):
        SEC_10K = "10k"
        SEC_10Q = "10q"
        SEC_8K = "8k"
        NEWS_ARTICLE = "news"
        YFINANCE_DATA = "yfinance"
        DCF_RESULT = "dcf_result"

    @dataclass
    class VectorEmbeddingConfig:
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
        dimension: int = 384
        batch_size: int = 32
        max_length: int = 512

    @dataclass
    class GraphNodeSchema:
        node_id: str
        node_type: str
        properties: Dict[str, Any]

    @dataclass
    class StockNode:
        ticker: str
        company_name: str
        cik: Optional[str] = None
        sector: Optional[str] = None
        industry: Optional[str] = None

    @dataclass
    class SECFilingNode:
        filing_id: str
        ticker: str
        filing_type: str
        filing_date: datetime
        content: str

    @dataclass
    class DocumentChunkNode:
        chunk_id: str
        document_id: str
        content: str
        embedding: Optional[List[float]] = None

    @dataclass
    class DCFValuationNode:
        ticker: str
        valuation_date: datetime
        intrinsic_value: float
        current_price: float
        recommendation: str

    class RelationshipType(Enum):
        FILED_BY = "FILED_BY"
        CONTAINS = "CONTAINS"
        RELATED_TO = "RELATED_TO"
        SIMILAR_TO = "SIMILAR_TO"
        MENTIONS = "MENTIONS"

    @dataclass
    class GraphRelationship:
        source_id: str
        target_id: str
        relationship_type: RelationshipType
        properties: Dict[str, Any]

    @dataclass
    class SemanticSearchResult:
        node_id: str
        score: float
        content: str
        metadata: Dict[str, Any]

    @dataclass
    class GraphRAGQuery:
        query_text: str
        intent: QueryIntent
        max_results: int = 10
        score_threshold: float = 0.7

    @dataclass
    class GraphRAGResponse:
        query: GraphRAGQuery
        results: List[SemanticSearchResult]
        answer: str
        confidence: float

    # Constants
    MAGNIFICENT_7_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"]
    MAGNIFICENT_7_CIKS = ["0000320193", "0000789019", "0001652044", "0001018724", "0001045810", "0001318605", "0001326801"]
    DEFAULT_EMBEDDING_CONFIG = VectorEmbeddingConfig()

# Re-export all functionality for the new data module structure
__all__ = [
    'QueryIntent',
    'DocumentType',
    'VectorEmbeddingConfig',
    'GraphNodeSchema',
    'StockNode',
    'SECFilingNode',
    'DocumentChunkNode',
    'DCFValuationNode',
    'RelationshipType',
    'GraphRelationship',
    'SemanticSearchResult',
    'GraphRAGQuery',
    'GraphRAGResponse',
    'MAGNIFICENT_7_TICKERS',
    'MAGNIFICENT_7_CIKS',
    'DEFAULT_EMBEDDING_CONFIG',
]