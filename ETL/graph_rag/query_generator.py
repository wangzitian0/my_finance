#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structured Query Generator for Graph RAG System

This module converts natural language questions into structured Cypher queries
for Neo4j graph database retrieval.
"""

import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Enumeration of supported query intents."""

    DCF_VALUATION = "dcf_valuation"
    FINANCIAL_COMPARISON = "financial_comparison"
    RISK_ANALYSIS = "risk_analysis"
    NEWS_IMPACT = "news_impact"
    SECTOR_ANALYSIS = "sector_analysis"
    GENERAL_INFO = "general_info"
    HISTORICAL_TRENDS = "historical_trends"


class StructuredQueryGenerator:
    """
    Converts natural language questions into structured Cypher queries
    and identifies query intentions for appropriate graph traversal.
    """

    def __init__(self):
        """Initialize the query generator with pattern matching rules."""

        # Intent classification patterns
        self.intent_patterns = {
            QueryIntent.DCF_VALUATION: [
                r"dcf|discounted cash flow|intrinsic value|valuation|fair value",
                r"what.*worth|how much.*value|estimate.*value",
                r"undervalued|overvalued|price target",
            ],
            QueryIntent.FINANCIAL_COMPARISON: [
                r"compare|comparison|versus|vs\.|against",
                r"better than|worse than|relative to",
                r"peer.*analysis|competitive.*position",
            ],
            QueryIntent.RISK_ANALYSIS: [
                r"risk|risks|risky|bankruptcy|volatile|volatility|danger",
                r"downside|threat|concern|warning",
                r"debt.*equity|leverage|solvency",
            ],
            QueryIntent.NEWS_IMPACT: [
                r"news|recent.*event|latest.*development|announcement",
                r"impact.*price|affect.*stock|influence.*valuation",
                r"market.*reaction|sentiment",
            ],
            QueryIntent.SECTOR_ANALYSIS: [
                r"sector|industry|peers|competitors",
                r"market.*share|industry.*trend",
                r"relative.*performance",
            ],
            QueryIntent.HISTORICAL_TRENDS: [
                r"trend|historical|over time|past.*year|growth",
                r"performance.*history|track record",
                r"revenue.*growth|earnings.*trend",
            ],
            QueryIntent.GENERAL_INFO: [
                r"what is|tell me about|information about|details about",
                r"company.*profile|business.*model|overview",
            ],
        }

        # Ticker extraction patterns
        self.ticker_patterns = [
            r"\b([A-Z]{1,5})\b",  # 1-5 uppercase letters
            r"ticker[:\s]+([A-Z]{1,5})",
            r"symbol[:\s]+([A-Z]{1,5})",
            r"stock[:\s]+([A-Z]{1,5})",
        ]

        # Company name to ticker mapping (Magnificent 7)
        self.company_ticker_map = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "amazon": "AMZN",
            "alphabet": "GOOGL",
            "google": "GOOGL",
            "meta": "META",
            "facebook": "META",
            "tesla": "TSLA",
            "netflix": "NFLX",
        }

    def generate_cypher_query(self, natural_question: str) -> Dict[str, Any]:
        """
        Convert natural language question to Cypher query.

        Args:
            natural_question: User's natural language query

        Returns:
            Dictionary containing Cypher query, intent, and metadata
        """
        # Classify the question intent
        intent = self.classify_question_intent(natural_question)

        # Extract ticker symbols from the question
        tickers = self.extract_tickers_from_question(natural_question)

        # Generate appropriate Cypher query based on intent
        cypher_query = ""
        params = {}

        if intent == QueryIntent.DCF_VALUATION:
            cypher_query, params = self.generate_dcf_query(natural_question, tickers)
        elif intent == QueryIntent.FINANCIAL_COMPARISON:
            cypher_query, params = self.generate_comparison_query(natural_question, tickers)
        elif intent == QueryIntent.RISK_ANALYSIS:
            cypher_query, params = self.generate_risk_query(natural_question, tickers)
        elif intent == QueryIntent.NEWS_IMPACT:
            cypher_query, params = self.generate_news_impact_query(natural_question, tickers)
        elif intent == QueryIntent.SECTOR_ANALYSIS:
            cypher_query, params = self.generate_sector_query(natural_question, tickers)
        elif intent == QueryIntent.HISTORICAL_TRENDS:
            cypher_query, params = self.generate_historical_query(natural_question, tickers)
        else:
            cypher_query, params = self.generate_general_query(natural_question, tickers)

        return {
            "cypher_query": cypher_query,
            "parameters": params,
            "intent": intent.value,
            "tickers": tickers,
            "original_question": natural_question,
            "generated_at": datetime.now().isoformat(),
        }

    def classify_question_intent(self, question: str) -> QueryIntent:
        """
        Classify the intent of a natural language question.

        Args:
            question: User's question

        Returns:
            Classified intent enum value
        """
        question_lower = question.lower()

        # Score each intent based on pattern matches
        intent_scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, question_lower))
                score += matches
            intent_scores[intent] = score

        # Return intent with highest score, default to GENERAL_INFO
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            if best_intent[1] > 0:
                return best_intent[0]

        return QueryIntent.GENERAL_INFO

    def extract_tickers_from_question(self, question: str) -> List[str]:
        """
        Extract ticker symbols from natural language question.

        Args:
            question: User's question

        Returns:
            List of identified ticker symbols
        """
        tickers = []
        question_lower = question.lower()

        # First, check for company names
        for company_name, ticker in self.company_ticker_map.items():
            if company_name in question_lower:
                tickers.append(ticker)

        # Then check for direct ticker patterns
        for pattern in self.ticker_patterns:
            matches = re.findall(pattern, question.upper())
            for match in matches:
                if match not in tickers and len(match) <= 5:
                    # Basic validation: exclude common English words
                    excluded_words = {
                        "THE",
                        "AND",
                        "FOR",
                        "ARE",
                        "BUT",
                        "NOT",
                        "YOU",
                        "ALL",
                        "CAN",
                        "HAD",
                        "HER",
                        "WAS",
                        "ONE",
                        "OUR",
                        "OUT",
                        "DAY",
                        "GET",
                        "HAS",
                        "HIM",
                        "HOW",
                        "NEW",
                        "NOW",
                        "OLD",
                        "SEE",
                        "TWO",
                        "WHO",
                        "BOY",
                        "DID",
                        "ITS",
                        "LET",
                        "PUT",
                        "SAY",
                        "SHE",
                        "TOO",
                        "USE",
                    }
                    if match not in excluded_words:
                        tickers.append(match)

        return list(set(tickers))  # Remove duplicates

    def generate_dcf_query(self, question: str, tickers: List[str]) -> tuple[str, Dict[str, Any]]:
        """Generate Cypher query for DCF valuation questions."""
        if not tickers:
            # Return query for all available DCF data
            cypher = """
            MATCH (s:Stock)-[:HAS_VALUATION]->(dcf:DCFValuation)
            WHERE dcf.valuation_date >= date() - duration({days: 90})
            OPTIONAL MATCH (s)-[:HAS_INFO]->(info:Info)
            OPTIONAL MATCH (s)-[:HAS_FILING]->(filing:SECFiling)
            WHERE filing.filing_date >= date() - duration({days: 365})
            RETURN s.ticker as ticker, dcf, info, 
                   collect(filing) as recent_filings
            ORDER BY dcf.valuation_date DESC
            LIMIT 10
            """
            params = {}
        else:
            ticker = tickers[0]  # Use first ticker for single company queries
            cypher = f"""
            MATCH (s:Stock {{ticker: $ticker}})
            OPTIONAL MATCH (s)-[:HAS_VALUATION]->(dcf:DCFValuation)
            WHERE dcf.valuation_date >= date() - duration({{days: 90}})
            OPTIONAL MATCH (s)-[:HAS_INFO]->(info:Info)
            OPTIONAL MATCH (s)-[:HAS_FILING]->(filing:SECFiling)
            WHERE filing.filing_date >= date() - duration({{days: 365}})
            OPTIONAL MATCH (s)-[:HAS_METRIC]->(metric:FinancialMetrics)
            WHERE metric.metric_date >= date() - duration({{days: 365}})
            RETURN s, dcf, info, 
                   collect(DISTINCT filing) as recent_filings,
                   collect(DISTINCT metric) as financial_metrics
            ORDER BY dcf.valuation_date DESC
            LIMIT 1
            """
            params = {"ticker": ticker}

        return cypher, params

    def generate_comparison_query(
        self, question: str, tickers: List[str]
    ) -> tuple[str, Dict[str, Any]]:
        """Generate Cypher query for financial comparison questions."""
        if len(tickers) >= 2:
            cypher = """
            MATCH (s:Stock)
            WHERE s.ticker IN $tickers
            OPTIONAL MATCH (s)-[:HAS_VALUATION]->(dcf:DCFValuation)
            WHERE dcf.valuation_date >= date() - duration({days: 90})
            OPTIONAL MATCH (s)-[:HAS_METRIC]->(metric:FinancialMetrics)
            WHERE metric.metric_date >= date() - duration({days: 365})
            OPTIONAL MATCH (s)-[:HAS_INFO]->(info:Info)
            RETURN s.ticker as ticker, dcf, 
                   collect(DISTINCT metric) as metrics, 
                   info
            ORDER BY s.ticker
            """
            params = {"tickers": tickers}
        else:
            # Compare with sector peers
            ticker = tickers[0] if tickers else "AAPL"
            cypher = f"""
            MATCH (s:Stock {{ticker: $ticker}})-[:HAS_INFO]->(info:Info)
            MATCH (peer:Stock)-[:HAS_INFO]->(peer_info:Info)
            WHERE peer_info.sector = info.sector AND peer.ticker <> s.ticker
            OPTIONAL MATCH (s)-[:HAS_VALUATION]->(s_dcf:DCFValuation)
            OPTIONAL MATCH (peer)-[:HAS_VALUATION]->(peer_dcf:DCFValuation)
            WHERE s_dcf.valuation_date >= date() - duration({{days: 90}})
              AND peer_dcf.valuation_date >= date() - duration({{days: 90}})
            RETURN s.ticker as target_ticker, s_dcf as target_dcf,
                   collect({{ticker: peer.ticker, dcf: peer_dcf}}) as peers
            LIMIT 1
            """
            params = {"ticker": ticker}

        return cypher, params

    def generate_risk_query(self, question: str, tickers: List[str]) -> tuple[str, Dict[str, Any]]:
        """Generate Cypher query for risk analysis questions."""
        ticker = tickers[0] if tickers else "AAPL"
        cypher = """
        MATCH (s:Stock {ticker: $ticker})
        OPTIONAL MATCH (s)-[:HAS_VALUATION]->(dcf:DCFValuation)
        WHERE dcf.valuation_date >= date() - duration({days: 90})
        OPTIONAL MATCH (s)-[:HAS_FILING]->(filing:SECFiling)
        WHERE filing.filing_date >= date() - duration({days: 365})
          AND filing.risk_factors IS NOT NULL
        OPTIONAL MATCH (s)-[:HAS_METRIC]->(metric:FinancialMetrics)
        WHERE metric.metric_date >= date() - duration({days: 365})
        RETURN s, dcf, 
               collect(DISTINCT {filing_type: filing.filing_type, 
                               risk_factors: filing.risk_factors,
                               filing_date: filing.filing_date}) as risk_info,
               collect(DISTINCT {debt_to_equity: metric.debt_to_equity,
                               current_ratio: metric.current_ratio,
                               metric_date: metric.metric_date}) as financial_health
        """
        params = {"ticker": ticker}
        return cypher, params

    def generate_news_impact_query(
        self, question: str, tickers: List[str]
    ) -> tuple[str, Dict[str, Any]]:
        """Generate Cypher query for news impact analysis."""
        ticker = tickers[0] if tickers else "AAPL"
        cypher = """
        MATCH (s:Stock {ticker: $ticker})
        OPTIONAL MATCH (s)-[:MENTIONED_IN]->(news:NewsEvent)
        WHERE news.published_date >= date() - duration({days: 30})
        OPTIONAL MATCH (s)-[:HAS_VALUATION]->(dcf:DCFValuation)
        WHERE dcf.valuation_date >= date() - duration({days: 90})
        OPTIONAL MATCH (news)-[:IMPACTS]->(dcf)
        RETURN s, 
               collect(DISTINCT {title: news.title,
                               published_date: news.published_date,
                               sentiment_score: news.sentiment_score,
                               impact_categories: news.impact_categories}) as recent_news,
               dcf
        ORDER BY news.published_date DESC
        """
        params = {"ticker": ticker}
        return cypher, params

    def generate_sector_query(
        self, question: str, tickers: List[str]
    ) -> tuple[str, Dict[str, Any]]:
        """Generate Cypher query for sector analysis."""
        ticker = tickers[0] if tickers else "AAPL"
        cypher = """
        MATCH (s:Stock {ticker: $ticker})-[:HAS_INFO]->(info:Info)
        MATCH (peer:Stock)-[:HAS_INFO]->(peer_info:Info)
        WHERE peer_info.sector = info.sector
        OPTIONAL MATCH (peer)-[:HAS_VALUATION]->(peer_dcf:DCFValuation)
        WHERE peer_dcf.valuation_date >= date() - duration({days: 90})
        RETURN info.sector as sector,
               collect({ticker: peer.ticker,
                       company_name: peer_info.longBusinessSummary,
                       dcf: peer_dcf}) as sector_companies
        """
        params = {"ticker": ticker}
        return cypher, params

    def generate_historical_query(
        self, question: str, tickers: List[str]
    ) -> tuple[str, Dict[str, Any]]:
        """Generate Cypher query for historical trend analysis."""
        ticker = tickers[0] if tickers else "AAPL"
        cypher = """
        MATCH (s:Stock {ticker: $ticker})
        OPTIONAL MATCH (s)-[:HAS_PRICE]->(price:PriceData)
        WHERE price.date >= date() - duration({days: 365})
        OPTIONAL MATCH (s)-[:HAS_METRIC]->(metric:FinancialMetrics)
        WHERE metric.metric_date >= date() - duration({days: 1095})  // 3 years
        RETURN s,
               collect(DISTINCT {date: price.date, close: price.close, volume: price.volume}) as price_history,
               collect(DISTINCT {metric_date: metric.metric_date,
                               revenue: metric.revenue,
                               net_income: metric.net_income,
                               free_cash_flow: metric.free_cash_flow}) as financial_history
        ORDER BY price.date DESC, metric.metric_date DESC
        """
        params = {"ticker": ticker}
        return cypher, params

    def generate_general_query(
        self, question: str, tickers: List[str]
    ) -> tuple[str, Dict[str, Any]]:
        """Generate Cypher query for general information requests."""
        if tickers:
            ticker = tickers[0]
            cypher = """
            MATCH (s:Stock {ticker: $ticker})
            OPTIONAL MATCH (s)-[:HAS_INFO]->(info:Info)
            OPTIONAL MATCH (s)-[:HAS_FAST_INFO]->(fast_info:FastInfo)
            OPTIONAL MATCH (s)-[:HAS_VALUATION]->(dcf:DCFValuation)
            WHERE dcf.valuation_date >= date() - duration({days: 90})
            RETURN s, info, fast_info, dcf
            """
            params = {"ticker": ticker}
        else:
            # Return general information about available stocks
            cypher = """
            MATCH (s:Stock)-[:HAS_INFO]->(info:Info)
            RETURN s.ticker as ticker, 
                   info.longBusinessSummary as description,
                   info.sector as sector,
                   info.industry as industry
            ORDER BY s.ticker
            LIMIT 10
            """
            params = {}

        return cypher, params
