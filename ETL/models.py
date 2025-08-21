# ETL/models.py
from datetime import datetime

# Avoid numpy import due to circular import issues in pixi environment
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
from neomodel import (
    ArrayProperty,
    BooleanProperty,
    DateTimeProperty,
    FloatProperty,
    IntegerProperty,
    JSONProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
)


class Info(StructuredNode):
    address1 = StringProperty()
    city = StringProperty()
    state = StringProperty()
    zip = StringProperty()
    country = StringProperty()
    phone = StringProperty()
    website = StringProperty()
    industry = StringProperty()
    industryKey = StringProperty()
    industryDisp = StringProperty()
    sector = StringProperty()
    sectorKey = StringProperty()
    sectorDisp = StringProperty()
    longBusinessSummary = StringProperty()
    fullTimeEmployees = IntegerProperty()
    companyOfficers = JSONProperty()  # Store company officers array information


class FastInfo(StructuredNode):
    currency = StringProperty()
    dayHigh = FloatProperty()
    dayLow = FloatProperty()
    exchange = StringProperty()
    fiftyDayAverage = FloatProperty()
    lastPrice = FloatProperty()
    lastVolume = IntegerProperty()


class PriceData(StructuredNode):
    # Historical stock price data, each record corresponds to one date
    date = DateTimeProperty()
    open = FloatProperty()
    high = FloatProperty()
    low = FloatProperty()
    close = FloatProperty()
    volume = IntegerProperty()


class Recommendations(StructuredNode):
    period = JSONProperty()  # e.g. {"0": "0m", "1": "-1m", ...}
    strongBuy = JSONProperty()
    buy = JSONProperty()
    hold = JSONProperty()
    sell = JSONProperty()
    strongSell = JSONProperty()


class Sustainability(StructuredNode):
    esgScores = JSONProperty()  # Store ESG score data


class SECFiling(StructuredNode):
    filing_type = StringProperty(required=True)  # 10-K, 10-Q, 8-K
    filing_date = DateTimeProperty(required=True)
    period_end_date = DateTimeProperty()
    cik = StringProperty(required=True)
    accession_number = StringProperty(unique_index=True)
    document_url = StringProperty()

    # Parsed content sections
    business_overview = StringProperty()
    risk_factors = StringProperty()
    financial_statements = StringProperty()
    md_and_a = StringProperty()  # Management Discussion & Analysis

    # Raw content for full-text search
    raw_content = StringProperty()

    # Semantic embeddings for sections (stored as JSON arrays)
    business_overview_embedding = JSONProperty()
    risk_factors_embedding = JSONProperty()
    financial_statements_embedding = JSONProperty()
    md_and_a_embedding = JSONProperty()

    # Processing metadata
    processed_at = DateTimeProperty()
    parsing_success = BooleanProperty(default=False)


class NewsEvent(StructuredNode):
    title = StringProperty(required=True)
    content = StringProperty()
    published_date = DateTimeProperty(required=True)
    source = StringProperty()  # Reuters, Bloomberg, etc.
    url = StringProperty()

    # Sentiment analysis
    sentiment_score = FloatProperty()  # -1 to 1
    sentiment_label = StringProperty()  # positive, negative, neutral

    # Content embeddings
    title_embedding = JSONProperty()
    content_embedding = JSONProperty()

    # Impact categorization
    impact_categories = JSONProperty()  # revenue, costs, risk, growth
    relevance_score = FloatProperty()

    # Processing metadata
    processed_at = DateTimeProperty()


class DCFValuation(StructuredNode):
    valuation_date = DateTimeProperty(required=True)
    intrinsic_value = FloatProperty(required=True)
    current_price = FloatProperty(required=True)
    upside_downside = FloatProperty()  # (intrinsic_value - current_price) / current_price

    # Key DCF parameters
    revenue_growth_rate = FloatProperty()
    operating_margin = FloatProperty()
    tax_rate = FloatProperty()
    wacc = FloatProperty()  # Weighted Average Cost of Capital
    terminal_growth_rate = FloatProperty()

    # Valuation components
    dcf_value = FloatProperty()
    terminal_value = FloatProperty()
    net_cash = FloatProperty()
    shares_outstanding = IntegerProperty()

    # Risk assessment
    bankruptcy_probability = FloatProperty()
    volatility = FloatProperty()

    # Sensitivity analysis results
    sensitivity_analysis = JSONProperty()

    # Confidence metrics
    confidence_score = FloatProperty()
    data_quality_score = FloatProperty()


class FinancialMetrics(StructuredNode):
    metric_date = DateTimeProperty(required=True)
    period_type = StringProperty()  # annual, quarterly

    # Income Statement
    revenue = FloatProperty()
    gross_profit = FloatProperty()
    operating_income = FloatProperty()
    net_income = FloatProperty()
    eps = FloatProperty()

    # Balance Sheet
    total_assets = FloatProperty()
    total_debt = FloatProperty()
    cash_and_equivalents = FloatProperty()
    shareholders_equity = FloatProperty()

    # Cash Flow
    operating_cash_flow = FloatProperty()
    free_cash_flow = FloatProperty()
    capex = FloatProperty()

    # Ratios
    roe = FloatProperty()  # Return on Equity
    roa = FloatProperty()  # Return on Assets
    debt_to_equity = FloatProperty()
    current_ratio = FloatProperty()

    # Extracted from SEC filings or calculated
    data_source = StringProperty()  # sec_filing, calculated, yahoo_finance


class DocumentChunk(StructuredNode):
    content = StringProperty(required=True)
    chunk_index = IntegerProperty(required=True)
    token_count = IntegerProperty()

    # Source information
    source_document_type = StringProperty()  # sec_filing, news, report
    section_name = StringProperty()

    # Semantic embedding
    embedding = JSONProperty()  # Vector representation

    # Metadata
    created_at = DateTimeProperty(default_now=True)
    relevance_keywords = ArrayProperty(StringProperty())


class Stock(StructuredNode):
    ticker = StringProperty(unique_index=True)
    period = StringProperty()
    interval = StringProperty()
    fetched_at = DateTimeProperty()

    # Existing relationships
    info = RelationshipTo(Info, "HAS_INFO")
    fast_info = RelationshipTo(FastInfo, "HAS_FAST_INFO")
    prices = RelationshipTo(PriceData, "HAS_PRICE")
    recommendations = RelationshipTo(Recommendations, "HAS_RECOMMENDATIONS")
    sustainability = RelationshipTo(Sustainability, "HAS_SUSTAINABILITY")

    # Graph RAG relationships
    filings = RelationshipTo(SECFiling, "HAS_FILING")
    news = RelationshipTo(NewsEvent, "MENTIONED_IN")
    valuations = RelationshipTo(DCFValuation, "HAS_VALUATION")
    metrics = RelationshipTo(FinancialMetrics, "HAS_METRIC")
    document_chunks = RelationshipTo(DocumentChunk, "HAS_CHUNK")


# Additional relationship definitions for Graph RAG
class SECFilingRelationships:
    # SEC Filings can contain financial metrics
    SECFiling.financial_metrics = RelationshipTo(FinancialMetrics, "CONTAINS")
    SECFiling.document_chunks = RelationshipTo(DocumentChunk, "HAS_CHUNK")


class NewsEventRelationships:
    # News can impact DCF valuations
    NewsEvent.impacts_valuation = RelationshipTo(DCFValuation, "IMPACTS")
    NewsEvent.document_chunks = RelationshipTo(DocumentChunk, "HAS_CHUNK")


class DCFValuationRelationships:
    # DCF valuations use financial metrics
    DCFValuation.uses_metrics = RelationshipTo(FinancialMetrics, "USES")
    # News events can provide forecast adjustments
    DCFValuation.influenced_by_news = RelationshipFrom(NewsEvent, "IMPACTS")
