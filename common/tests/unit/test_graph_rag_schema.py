#!/usr/bin/env python3
"""
Unit tests for graph_rag_schema.py - Graph RAG Schema Definitions
Tests schema classes, enums, and configuration constants.
"""

from datetime import datetime
from typing import List

import pytest

from common.schemas.graph_rag_schema import (
    QueryIntent,
    DocumentType,
    VectorEmbeddingConfig,
    GraphNodeSchema,
    StockNode,
    SECFilingNode,
    DocumentChunkNode,
    DCFValuationNode,
    NewsEventNode,
    FinancialMetricsNode,
    RelationshipType,
    GraphRelationship,
    SemanticSearchResult,
    GraphRAGQuery,
    GraphRAGResponse,
    ETLStageOutput,
    MAGNIFICENT_7_TICKERS,
    MAGNIFICENT_7_CIKS,
    DEFAULT_EMBEDDING_CONFIG,
    CYPHER_TEMPLATES
)


@pytest.mark.schemas
class TestEnums:
    """Test enum definitions."""
    
    def test_query_intent_values(self):
        """Test QueryIntent enum values."""
        assert QueryIntent.DCF_VALUATION.value == "dcf_valuation"
        assert QueryIntent.FINANCIAL_COMPARISON.value == "financial_comparison"
        assert QueryIntent.RISK_ANALYSIS.value == "risk_analysis"
        assert QueryIntent.NEWS_IMPACT.value == "news_impact"
        assert QueryIntent.INDUSTRY_ANALYSIS.value == "industry_analysis"
        assert QueryIntent.HISTORICAL_TRENDS.value == "historical_trends"
        assert QueryIntent.INVESTMENT_RECOMMENDATION.value == "investment_recommendation"
        assert QueryIntent.GENERAL_INFO.value == "general_info"
        
    def test_document_type_values(self):
        """Test DocumentType enum values."""
        assert DocumentType.SEC_10K.value == "10k"
        assert DocumentType.SEC_10Q.value == "10q"
        assert DocumentType.SEC_8K.value == "8k"
        assert DocumentType.NEWS_ARTICLE.value == "news"
        assert DocumentType.YFINANCE_DATA.value == "yfinance"
        assert DocumentType.DCF_RESULT.value == "dcf_result"
        
    def test_relationship_type_values(self):
        """Test RelationshipType enum values."""
        assert RelationshipType.HAS_FILING.value == "HAS_FILING"
        assert RelationshipType.MENTIONED_IN.value == "MENTIONED_IN"
        assert RelationshipType.HAS_VALUATION.value == "HAS_VALUATION"
        assert RelationshipType.HAS_METRIC.value == "HAS_METRIC"
        assert RelationshipType.IMPACTS.value == "IMPACTS"
        assert RelationshipType.USES.value == "USES"
        assert RelationshipType.CHUNK_OF.value == "CHUNK_OF"
        assert RelationshipType.SIMILAR_TO.value == "SIMILAR_TO"


@pytest.mark.schemas
class TestVectorEmbeddingConfig:
    """Test VectorEmbeddingConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = VectorEmbeddingConfig()
        
        assert config.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.chunk_size == 512
        assert config.chunk_overlap == 50
        assert config.dimension == 384
        assert config.similarity_threshold == 0.3
        assert config.max_results == 10
        
    def test_custom_config(self):
        """Test custom configuration values."""
        config = VectorEmbeddingConfig(
            model_name="custom-model",
            chunk_size=1024,
            chunk_overlap=100,
            dimension=768,
            similarity_threshold=0.5,
            max_results=20
        )
        
        assert config.model_name == "custom-model"
        assert config.chunk_size == 1024
        assert config.chunk_overlap == 100
        assert config.dimension == 768
        assert config.similarity_threshold == 0.5
        assert config.max_results == 20


@pytest.mark.schemas
class TestGraphNodeSchema:
    """Test base GraphNodeSchema dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        node = GraphNodeSchema()
        
        assert node.node_id == ""
        assert node.node_type == ""
        assert node.created_at is None
        assert node.updated_at is None
        assert node.metadata is None
        
    def test_custom_values(self):
        """Test custom values."""
        now = datetime.now()
        metadata = {"key": "value"}
        
        node = GraphNodeSchema(
            node_id="test-123",
            node_type="TestNode",
            created_at=now,
            updated_at=now,
            metadata=metadata
        )
        
        assert node.node_id == "test-123"
        assert node.node_type == "TestNode"
        assert node.created_at == now
        assert node.updated_at == now
        assert node.metadata == metadata


@pytest.mark.schemas
class TestStockNode:
    """Test StockNode dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        stock = StockNode()
        
        assert stock.node_type == "Stock"
        assert stock.ticker == ""
        assert stock.company_name == ""
        assert stock.cik == ""
        assert stock.sector == ""
        assert stock.industry == ""
        assert stock.market_cap is None
        
    def test_stock_node_creation(self):
        """Test creating stock node with values."""
        stock = StockNode(
            node_id="aapl-001",
            ticker="AAPL",
            company_name="Apple Inc.",
            cik="0000320193",
            sector="Technology",
            industry="Consumer Electronics",
            market_cap=3000000000000.0
        )
        
        assert stock.node_type == "Stock"
        assert stock.ticker == "AAPL"
        assert stock.company_name == "Apple Inc."
        assert stock.cik == "0000320193"
        assert stock.sector == "Technology"
        assert stock.industry == "Consumer Electronics"
        assert stock.market_cap == 3000000000000.0


@pytest.mark.schemas
class TestSECFilingNode:
    """Test SECFilingNode dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        filing = SECFilingNode()
        
        assert filing.node_type == "SECFiling"
        assert filing.accession_number == ""
        assert filing.filing_type is None
        assert filing.filing_date is None
        assert filing.period_end_date is None
        assert filing.company_cik == ""
        assert filing.document_url is None
        
    def test_sec_filing_creation(self):
        """Test creating SEC filing node."""
        filing_date = datetime(2024, 1, 15)
        period_end = datetime(2023, 12, 31)
        
        filing = SECFilingNode(
            node_id="filing-001",
            accession_number="0000320193-24-000006",
            filing_type=DocumentType.SEC_10K,
            filing_date=filing_date,
            period_end_date=period_end,
            company_cik="0000320193",
            document_url="https://sec.gov/..."
        )
        
        assert filing.node_type == "SECFiling"
        assert filing.accession_number == "0000320193-24-000006"
        assert filing.filing_type == DocumentType.SEC_10K
        assert filing.filing_date == filing_date
        assert filing.period_end_date == period_end
        assert filing.company_cik == "0000320193"
        assert filing.document_url == "https://sec.gov/..."


@pytest.mark.schemas
class TestDocumentChunkNode:
    """Test DocumentChunkNode dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        chunk = DocumentChunkNode()
        
        assert chunk.node_type == "DocumentChunk"
        assert chunk.document_id == ""
        assert chunk.chunk_index == 0
        assert chunk.content == ""
        assert chunk.content_type is None
        assert chunk.embedding_vector is None
        assert chunk.parent_document == ""
        
    def test_document_chunk_creation(self):
        """Test creating document chunk node."""
        embedding = [0.1, 0.2, 0.3]
        
        chunk = DocumentChunkNode(
            node_id="chunk-001",
            document_id="doc-123",
            chunk_index=5,
            content="This is a chunk of text content.",
            content_type=DocumentType.SEC_10K,
            embedding_vector=embedding,
            parent_document="filing-001"
        )
        
        assert chunk.node_type == "DocumentChunk"
        assert chunk.document_id == "doc-123"
        assert chunk.chunk_index == 5
        assert chunk.content == "This is a chunk of text content."
        assert chunk.content_type == DocumentType.SEC_10K
        assert chunk.embedding_vector == embedding
        assert chunk.parent_document == "filing-001"


@pytest.mark.schemas
class TestDCFValuationNode:
    """Test DCFValuationNode dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        dcf = DCFValuationNode()
        
        assert dcf.node_type == "DCFValuation"
        assert dcf.ticker == ""
        assert dcf.valuation_date is None
        assert dcf.intrinsic_value == 0.0
        assert dcf.current_price is None
        assert dcf.discount_rate == 0.1
        assert dcf.terminal_growth_rate == 0.03
        assert dcf.confidence_score is None
        
    def test_dcf_valuation_creation(self):
        """Test creating DCF valuation node."""
        valuation_date = datetime(2024, 1, 15)
        
        dcf = DCFValuationNode(
            node_id="dcf-001",
            ticker="AAPL",
            valuation_date=valuation_date,
            intrinsic_value=185.50,
            current_price=180.25,
            discount_rate=0.12,
            terminal_growth_rate=0.025,
            confidence_score=0.85
        )
        
        assert dcf.node_type == "DCFValuation"
        assert dcf.ticker == "AAPL"
        assert dcf.valuation_date == valuation_date
        assert dcf.intrinsic_value == 185.50
        assert dcf.current_price == 180.25
        assert dcf.discount_rate == 0.12
        assert dcf.terminal_growth_rate == 0.025
        assert dcf.confidence_score == 0.85


@pytest.mark.schemas
class TestNewsEventNode:
    """Test NewsEventNode dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        news = NewsEventNode()
        
        assert news.node_type == "NewsEvent"
        assert news.headline == ""
        assert news.publication_date is None
        assert news.source == ""
        assert news.sentiment_score is None
        assert news.impact_score is None
        assert news.mentioned_tickers == []
        
    def test_news_event_creation(self):
        """Test creating news event node."""
        pub_date = datetime(2024, 1, 15)
        tickers = ["AAPL", "MSFT"]
        
        news = NewsEventNode(
            node_id="news-001",
            headline="Apple Reports Strong Q1 Results",
            publication_date=pub_date,
            source="Reuters",
            sentiment_score=0.8,
            impact_score=0.6,
            mentioned_tickers=tickers
        )
        
        assert news.node_type == "NewsEvent"
        assert news.headline == "Apple Reports Strong Q1 Results"
        assert news.publication_date == pub_date
        assert news.source == "Reuters"
        assert news.sentiment_score == 0.8
        assert news.impact_score == 0.6
        assert news.mentioned_tickers == tickers
        
    def test_news_event_post_init(self):
        """Test __post_init__ method initializes mentioned_tickers."""
        news = NewsEventNode(mentioned_tickers=None)
        assert news.mentioned_tickers == []
        
        news = NewsEventNode(mentioned_tickers=["AAPL"])
        assert news.mentioned_tickers == ["AAPL"]


@pytest.mark.schemas
class TestFinancialMetricsNode:
    """Test FinancialMetricsNode dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        metrics = FinancialMetricsNode()
        
        assert metrics.node_type == "FinancialMetrics"
        assert metrics.ticker == ""
        assert metrics.report_date is None
        assert metrics.revenue is None
        assert metrics.net_income is None
        assert metrics.free_cash_flow is None
        assert metrics.total_debt is None
        assert metrics.shareholders_equity is None
        
    def test_financial_metrics_creation(self):
        """Test creating financial metrics node."""
        report_date = datetime(2023, 12, 31)
        
        metrics = FinancialMetricsNode(
            node_id="metrics-001",
            ticker="AAPL",
            report_date=report_date,
            revenue=394328000000,
            net_income=96995000000,
            free_cash_flow=84726000000,
            total_debt=123000000000,
            shareholders_equity=74000000000
        )
        
        assert metrics.node_type == "FinancialMetrics"
        assert metrics.ticker == "AAPL"
        assert metrics.report_date == report_date
        assert metrics.revenue == 394328000000
        assert metrics.net_income == 96995000000
        assert metrics.free_cash_flow == 84726000000
        assert metrics.total_debt == 123000000000
        assert metrics.shareholders_equity == 74000000000


@pytest.mark.schemas
class TestGraphRelationship:
    """Test GraphRelationship dataclass."""
    
    def test_default_values(self):
        """Test default values."""
        rel = GraphRelationship()
        
        assert rel.source_node == ""
        assert rel.target_node == ""
        assert rel.relationship_type is None
        assert rel.properties is None
        assert rel.weight is None
        assert rel.created_at is None
        
    def test_graph_relationship_creation(self):
        """Test creating graph relationship."""
        created_at = datetime.now()
        properties = {"confidence": 0.9}
        
        rel = GraphRelationship(
            source_node="stock-001",
            target_node="filing-001",
            relationship_type=RelationshipType.HAS_FILING,
            properties=properties,
            weight=1.0,
            created_at=created_at
        )
        
        assert rel.source_node == "stock-001"
        assert rel.target_node == "filing-001"
        assert rel.relationship_type == RelationshipType.HAS_FILING
        assert rel.properties == properties
        assert rel.weight == 1.0
        assert rel.created_at == created_at


@pytest.mark.schemas
class TestSemanticSearchResult:
    """Test SemanticSearchResult dataclass."""
    
    def test_semantic_search_result_creation(self):
        """Test creating semantic search result."""
        metadata = {"chunk_index": 5, "relevance": "high"}
        
        result = SemanticSearchResult(
            node_id="chunk-001",
            content="This is relevant content",
            similarity_score=0.85,
            metadata=metadata,
            source_document="filing-001",
            document_type=DocumentType.SEC_10K
        )
        
        assert result.node_id == "chunk-001"
        assert result.content == "This is relevant content"
        assert result.similarity_score == 0.85
        assert result.metadata == metadata
        assert result.source_document == "filing-001"
        assert result.document_type == DocumentType.SEC_10K


@pytest.mark.schemas
class TestGraphRAGQuery:
    """Test GraphRAGQuery dataclass."""
    
    def test_graph_rag_query_creation(self):
        """Test creating Graph RAG query."""
        entities = ["AAPL", "Apple Inc."]
        context_filter = {"date_range": "2024"}
        
        query = GraphRAGQuery(
            question="What is Apple's DCF valuation?",
            intent=QueryIntent.DCF_VALUATION,
            entities=entities,
            cypher_query="MATCH (s:Stock {ticker: 'AAPL'}) RETURN s",
            vector_query="Apple DCF valuation analysis",
            context_filter=context_filter
        )
        
        assert query.question == "What is Apple's DCF valuation?"
        assert query.intent == QueryIntent.DCF_VALUATION
        assert query.entities == entities
        assert query.cypher_query == "MATCH (s:Stock {ticker: 'AAPL'}) RETURN s"
        assert query.vector_query == "Apple DCF valuation analysis"
        assert query.context_filter == context_filter


@pytest.mark.schemas
class TestGraphRAGResponse:
    """Test GraphRAGResponse dataclass."""
    
    def test_graph_rag_response_creation(self):
        """Test creating Graph RAG response."""
        sources = [
            SemanticSearchResult(
                node_id="chunk-001",
                content="Apple's revenue is growing",
                similarity_score=0.9,
                metadata={},
                source_document="filing-001",
                document_type=DocumentType.SEC_10K
            )
        ]
        reasoning_steps = ["Step 1: Retrieved SEC filings", "Step 2: Analyzed revenue"]
        cypher_results = {"valuation": 185.50}
        metadata = {"query_time": 0.5}
        
        response = GraphRAGResponse(
            answer="Apple's intrinsic value is $185.50 per share",
            confidence_score=0.85,
            sources=sources,
            reasoning_steps=reasoning_steps,
            cypher_results=cypher_results,
            metadata=metadata
        )
        
        assert response.answer == "Apple's intrinsic value is $185.50 per share"
        assert response.confidence_score == 0.85
        assert response.sources == sources
        assert response.reasoning_steps == reasoning_steps
        assert response.cypher_results == cypher_results
        assert response.metadata == metadata


@pytest.mark.schemas
class TestETLStageOutput:
    """Test ETLStageOutput nested classes."""
    
    def test_graph_nodes_output(self):
        """Test GraphNodesOutput creation."""
        node_types = {"Stock": 7, "SECFiling": 21}
        
        output = ETLStageOutput.GraphNodesOutput(
            nodes_created=28,
            relationships_created=45,
            node_types=node_types,
            output_path="/data/nodes"
        )
        
        assert output.nodes_created == 28
        assert output.relationships_created == 45
        assert output.node_types == node_types
        assert output.output_path == "/data/nodes"
        
    def test_embeddings_output(self):
        """Test EmbeddingsOutput creation."""
        output = ETLStageOutput.EmbeddingsOutput(
            embeddings_created=1000,
            documents_processed=50,
            model_used="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384,
            output_path="/data/embeddings"
        )
        
        assert output.embeddings_created == 1000
        assert output.documents_processed == 50
        assert output.model_used == "sentence-transformers/all-MiniLM-L6-v2"
        assert output.dimension == 384
        assert output.output_path == "/data/embeddings"
        
    def test_vector_index_output(self):
        """Test VectorIndexOutput creation."""
        output = ETLStageOutput.VectorIndexOutput(
            index_size=1000,
            index_type="FAISS",
            search_ready=True,
            output_path="/data/index"
        )
        
        assert output.index_size == 1000
        assert output.index_type == "FAISS"
        assert output.search_ready is True
        assert output.output_path == "/data/index"


@pytest.mark.schemas
class TestConstants:
    """Test module constants."""
    
    def test_magnificent_7_tickers(self):
        """Test Magnificent 7 tickers constant."""
        expected_tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NFLX"]
        assert MAGNIFICENT_7_TICKERS == expected_tickers
        assert len(MAGNIFICENT_7_TICKERS) == 7
        
    def test_magnificent_7_ciks(self):
        """Test Magnificent 7 CIKs constant."""
        expected_ciks = {
            "AAPL": "0000320193",
            "MSFT": "0000789019",
            "AMZN": "0001018724",
            "GOOGL": "0001652044",
            "META": "0001326801",
            "TSLA": "0001318605",
            "NFLX": "0001065280",
        }
        
        assert MAGNIFICENT_7_CIKS == expected_ciks
        assert len(MAGNIFICENT_7_CIKS) == 7
        
        # Verify all tickers have corresponding CIKs
        for ticker in MAGNIFICENT_7_TICKERS:
            assert ticker in MAGNIFICENT_7_CIKS
            assert MAGNIFICENT_7_CIKS[ticker].startswith("00")
            assert len(MAGNIFICENT_7_CIKS[ticker]) == 10
            
    def test_default_embedding_config(self):
        """Test default embedding configuration constant."""
        assert isinstance(DEFAULT_EMBEDDING_CONFIG, VectorEmbeddingConfig)
        assert DEFAULT_EMBEDDING_CONFIG.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert DEFAULT_EMBEDDING_CONFIG.dimension == 384
        
    def test_cypher_templates(self):
        """Test Cypher query templates."""
        assert QueryIntent.DCF_VALUATION in CYPHER_TEMPLATES
        assert QueryIntent.FINANCIAL_COMPARISON in CYPHER_TEMPLATES
        assert QueryIntent.RISK_ANALYSIS in CYPHER_TEMPLATES
        
        # Check DCF valuation template
        dcf_template = CYPHER_TEMPLATES[QueryIntent.DCF_VALUATION]
        assert "MATCH (s:Stock {ticker: $ticker})" in dcf_template
        assert "DCFValuation" in dcf_template
        assert "ORDER BY dcf.valuation_date DESC" in dcf_template
        
        # Check financial comparison template
        comp_template = CYPHER_TEMPLATES[QueryIntent.FINANCIAL_COMPARISON]
        assert "$ticker1" in comp_template
        assert "$ticker2" in comp_template
        assert "FinancialMetrics" in comp_template
        
        # Check risk analysis template
        risk_template = CYPHER_TEMPLATES[QueryIntent.RISK_ANALYSIS]
        assert "SECFiling" in risk_template
        assert "DocumentChunk" in risk_template
        assert "risk" in risk_template.lower()


@pytest.mark.integration
class TestSchemaIntegration:
    """Integration tests for schema interactions."""
    
    def test_complete_graph_schema_workflow(self):
        """Test complete schema workflow."""
        # Create a stock node
        stock = StockNode(
            node_id="aapl-001",
            ticker="AAPL",
            company_name="Apple Inc.",
            cik=MAGNIFICENT_7_CIKS["AAPL"]
        )
        
        # Create a filing node
        filing = SECFilingNode(
            node_id="filing-001",
            accession_number="0000320193-24-000006",
            filing_type=DocumentType.SEC_10K,
            company_cik=stock.cik
        )
        
        # Create a relationship
        relationship = GraphRelationship(
            source_node=stock.node_id,
            target_node=filing.node_id,
            relationship_type=RelationshipType.HAS_FILING
        )
        
        # Create a document chunk
        chunk = DocumentChunkNode(
            node_id="chunk-001",
            document_id=filing.node_id,
            content="Apple's revenue grew significantly...",
            content_type=DocumentType.SEC_10K,
            parent_document=filing.node_id
        )
        
        # Create DCF valuation
        dcf = DCFValuationNode(
            node_id="dcf-001",
            ticker=stock.ticker,
            intrinsic_value=185.50
        )
        
        # Create search result
        search_result = SemanticSearchResult(
            node_id=chunk.node_id,
            content=chunk.content,
            similarity_score=0.9,
            metadata={"source": "10K"},
            source_document=filing.node_id,
            document_type=DocumentType.SEC_10K
        )
        
        # Create query and response
        query = GraphRAGQuery(
            question="What is Apple's DCF valuation?",
            intent=QueryIntent.DCF_VALUATION,
            entities=[stock.ticker]
        )
        
        response = GraphRAGResponse(
            answer=f"Apple's intrinsic value is ${dcf.intrinsic_value}",
            confidence_score=0.85,
            sources=[search_result],
            reasoning_steps=["Retrieved SEC filing", "Calculated DCF"]
        )
        
        # Verify all objects are properly created and linked
        assert stock.node_type == "Stock"
        assert filing.company_cik == stock.cik
        assert relationship.source_node == stock.node_id
        assert relationship.target_node == filing.node_id
        assert chunk.parent_document == filing.node_id
        assert dcf.ticker == stock.ticker
        assert search_result.document_type == filing.filing_type
        assert query.intent == QueryIntent.DCF_VALUATION
        assert str(dcf.intrinsic_value) in response.answer