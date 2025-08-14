#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCF Engine Graph RAG Module

Handles question answering and response generation using Graph RAG.
This module is responsible for:
- Natural language query processing and intent recognition
- Question template matching and parameter extraction
- LLM-based answer generation using retrieved context
- Structured response formatting and reporting

This is the business logic layer that uses ETL's data integration and retrieval.
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from neomodel import db

from common.graph_rag_schema import (
    CYPHER_TEMPLATES,
    MAGNIFICENT_7_TICKERS,
    DocumentType,
    GraphRAGQuery,
    GraphRAGResponse,
    QueryIntent,
    SemanticSearchResult,
)

logger = logging.getLogger(__name__)


class AnswerTemplate(Enum):
    """Templates for different types of financial answers."""

    DCF_VALUATION = "dcf_valuation"
    FINANCIAL_COMPARISON = "financial_comparison"
    RISK_ANALYSIS = "risk_analysis"
    INVESTMENT_RECOMMENDATION = "investment_recommendation"
    GENERAL_FINANCIAL = "general_financial"


@dataclass
class AnswerContext:
    """Context information for answer generation."""

    graph_results: Dict[str, Any]
    semantic_results: List[SemanticSearchResult]
    query_intent: QueryIntent
    extracted_entities: List[str]
    confidence_score: float = 0.0


class QueryProcessor:
    """
    Processes natural language queries and extracts structured information.

    This class handles intent recognition, entity extraction, and
    query transformation for the Graph RAG system.
    """

    def __init__(self):
        """Initialize the query processor."""
        self.intent_patterns = self._build_intent_patterns()
        self.entity_patterns = self._build_entity_patterns()

    def _build_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
        """Build regex patterns for intent recognition."""
        return {
            QueryIntent.DCF_VALUATION: [
                r"dcf\s+valuation|discounted\s+cash\s+flow|intrinsic\s+value",
                r"what.*worth|fair\s+value|valuation\s+of",
                r"dcf.*analysis|valuation.*model",
            ],
            QueryIntent.FINANCIAL_COMPARISON: [
                r"compare.*financial|compare.*performance",
                r"(vs|versus|against).*financial",
                r"difference.*between.*performance",
            ],
            QueryIntent.RISK_ANALYSIS: [
                r"risk.*factor|risk.*analysis|main.*risk",
                r"what.*risk|potential.*risk|downside.*risk",
                r"volatility|uncertainty|challenges",
            ],
            QueryIntent.NEWS_IMPACT: [
                r"news.*impact|recent.*news|latest.*news",
                r"market.*reaction|news.*affect|headline.*impact",
            ],
            QueryIntent.INVESTMENT_RECOMMENDATION: [
                r"should.*invest|investment.*recommendation",
                r"buy.*hold.*sell|investment.*advice",
                r"good.*investment|invest.*in",
            ],
            QueryIntent.HISTORICAL_TRENDS: [
                r"trend|historical.*performance|past.*years",
                r"growth.*rate|revenue.*trend|earnings.*trend",
            ],
            QueryIntent.INDUSTRY_ANALYSIS: [
                r"industry.*analysis|sector.*performance",
                r"compared.*to.*industry|industry.*average",
            ],
        }

    def _build_entity_patterns(self) -> Dict[str, str]:
        """Build patterns for entity extraction."""
        ticker_pattern = "|".join(MAGNIFICENT_7_TICKERS)
        company_names = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "AMZN": "Amazon",
            "GOOGL": "Google|Alphabet",
            "META": "Meta|Facebook",
            "TSLA": "Tesla",
            "NFLX": "Netflix",
        }

        name_pattern = "|".join([names for names in company_names.values()])

        return {
            "tickers": f"\\b({ticker_pattern})\\b",
            "company_names": f"\\b({name_pattern})\\b",
            "financial_metrics": r"\\b(revenue|profit|earnings|cash flow|debt|equity|ROE|ROA|margin)\\b",
            "time_periods": r"\\b(year|years|quarter|quarters|month|months|Q[1-4]|20\d{2})\\b",
        }

    def process_query(self, question: str) -> GraphRAGQuery:
        """
        Process natural language query into structured format.

        Args:
            question: User's natural language question

        Returns:
            Structured GraphRAGQuery object
        """
        logger.debug(f"Processing query: {question}")

        # Extract intent
        intent = self._extract_intent(question)

        # Extract entities
        entities = self._extract_entities(question)

        # Generate Cypher query if applicable
        cypher_query = self._generate_cypher_query(intent, entities)

        # Generate vector search query
        vector_query = self._generate_vector_query(question, intent)

        return GraphRAGQuery(
            question=question,
            intent=intent,
            entities=entities,
            cypher_query=cypher_query,
            vector_query=vector_query,
            context_filter=self._build_context_filter(entities, intent),
        )

    def _extract_intent(self, question: str) -> QueryIntent:
        """Extract query intent from natural language."""
        question_lower = question.lower()

        # Score each intent based on pattern matches
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, question_lower))
                score += matches

            if score > 0:
                intent_scores[intent] = score

        # Return highest scoring intent, default to GENERAL_INFO
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]

        return QueryIntent.GENERAL_INFO

    def _extract_entities(self, question: str) -> List[str]:
        """Extract entities (tickers, company names, etc.) from question."""
        entities = []

        # Extract tickers
        ticker_matches = re.findall(self.entity_patterns["tickers"], question.upper())
        entities.extend(ticker_matches)

        # Extract company names and map to tickers
        name_matches = re.findall(self.entity_patterns["company_names"], question, re.IGNORECASE)
        for name in name_matches:
            ticker = self._company_name_to_ticker(name.lower())
            if ticker and ticker not in entities:
                entities.append(ticker)

        return entities

    def _company_name_to_ticker(self, company_name: str) -> Optional[str]:
        """Map company name to ticker symbol."""
        name_to_ticker = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "amazon": "AMZN",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "meta": "META",
            "facebook": "META",
            "tesla": "TSLA",
            "netflix": "NFLX",
        }
        return name_to_ticker.get(company_name)

    def _generate_cypher_query(self, intent: QueryIntent, entities: List[str]) -> Optional[str]:
        """Generate Cypher query based on intent and entities."""
        if intent not in CYPHER_TEMPLATES:
            return None

        template = CYPHER_TEMPLATES[intent]

        # Simple parameter substitution
        if intent == QueryIntent.DCF_VALUATION and entities:
            return template.replace("$ticker", f"'{entities[0]}'")
        elif intent == QueryIntent.FINANCIAL_COMPARISON and len(entities) >= 2:
            return template.replace("$ticker1", f"'{entities[0]}'").replace(
                "$ticker2", f"'{entities[1]}'"
            )
        elif intent == QueryIntent.RISK_ANALYSIS and entities:
            return template.replace("$ticker", f"'{entities[0]}'")

        return template

    def _generate_vector_query(self, question: str, intent: QueryIntent) -> str:
        """Generate optimized query for vector search."""
        # Clean and optimize the question for semantic search
        query = question.lower()

        # Add intent-specific keywords
        intent_keywords = {
            QueryIntent.DCF_VALUATION: " DCF valuation intrinsic value",
            QueryIntent.RISK_ANALYSIS: " risk factors downside uncertainty",
            QueryIntent.FINANCIAL_COMPARISON: " financial performance comparison",
            QueryIntent.NEWS_IMPACT: " news market impact recent events",
        }

        if intent in intent_keywords:
            query += intent_keywords[intent]

        return query

    def _build_context_filter(self, entities: List[str], intent: QueryIntent) -> Dict[str, Any]:
        """Build context filter for retrieval."""
        context_filter = {}

        if entities:
            context_filter["ticker"] = entities

        # Document type filters based on intent
        if intent == QueryIntent.DCF_VALUATION:
            context_filter["content_type"] = [
                DocumentType.SEC_10K.value,
                DocumentType.YFINANCE_DATA.value,
                DocumentType.DCF_RESULT.value,
            ]
        elif intent == QueryIntent.RISK_ANALYSIS:
            context_filter["content_type"] = [
                DocumentType.SEC_10K.value,
                DocumentType.SEC_10Q.value,
            ]

        return context_filter


class AnswerGenerator:
    """
    Generates intelligent answers using retrieved context.

    This class formats responses based on query intent and
    combines graph and semantic search results.
    """

    def __init__(self):
        """Initialize the answer generator."""
        self.templates = self._load_answer_templates()

    def _load_answer_templates(self) -> Dict[QueryIntent, str]:
        """Load answer templates for different query types."""
        return {
            QueryIntent.DCF_VALUATION: """
Based on the DCF analysis, here are the valuation details for {ticker}:

**Intrinsic Value**: ${intrinsic_value:.2f}
**Current Price**: ${current_price:.2f} 
**Discount Rate**: {discount_rate:.1%}
**Terminal Growth Rate**: {terminal_growth_rate:.1%}

**Valuation Summary**: 
{valuation_summary}

**Key Assumptions**:
{assumptions}

**Sources**: {sources}
            """.strip(),
            QueryIntent.FINANCIAL_COMPARISON: """
**Financial Performance Comparison**:

{comparison_table}

**Key Insights**:
{insights}

**Performance Summary**:
{summary}

**Sources**: {sources}
            """.strip(),
            QueryIntent.RISK_ANALYSIS: """
**Risk Analysis for {ticker}**:

**Primary Risk Factors**:
{risk_factors}

**Risk Level**: {risk_level}

**Mitigation Strategies**:
{mitigation_strategies}

**Sources**: {sources}
            """.strip(),
            QueryIntent.INVESTMENT_RECOMMENDATION: """
**Investment Recommendation for {ticker}**:

**Recommendation**: {recommendation}
**Confidence Level**: {confidence_level}

**Supporting Analysis**:
{analysis}

**Key Considerations**:
{considerations}

**Risk Assessment**: {risk_assessment}

**Sources**: {sources}
            """.strip(),
        }

    def generate_answer(self, context: AnswerContext) -> GraphRAGResponse:
        """
        Generate structured answer from context.

        Args:
            context: Context with graph and semantic search results

        Returns:
            Structured GraphRAGResponse
        """
        try:
            logger.debug(f"Generating answer for intent: {context.query_intent}")

            # Generate answer based on intent
            if context.query_intent == QueryIntent.DCF_VALUATION:
                answer = self._generate_dcf_answer(context)
            elif context.query_intent == QueryIntent.FINANCIAL_COMPARISON:
                answer = self._generate_comparison_answer(context)
            elif context.query_intent == QueryIntent.RISK_ANALYSIS:
                answer = self._generate_risk_answer(context)
            elif context.query_intent == QueryIntent.INVESTMENT_RECOMMENDATION:
                answer = self._generate_investment_answer(context)
            else:
                answer = self._generate_general_answer(context)

            # Generate reasoning steps
            reasoning_steps = self._generate_reasoning_steps(context)

            return GraphRAGResponse(
                answer=answer,
                confidence_score=context.confidence_score,
                sources=context.semantic_results,
                reasoning_steps=reasoning_steps,
                cypher_results=context.graph_results,
                metadata={
                    "query_intent": context.query_intent.value,
                    "entities_found": context.extracted_entities,
                    "sources_used": len(context.semantic_results),
                },
            )

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return self._generate_fallback_response(context)

    def _generate_dcf_answer(self, context: AnswerContext) -> str:
        """Generate DCF valuation answer."""
        if not context.extracted_entities:
            return "I need a specific company ticker to provide DCF valuation analysis."

        ticker = context.extracted_entities[0]

        # Check for DCF data in graph results
        dcf_data = context.graph_results.get("dcf_valuation", {})

        if dcf_data:
            template = self.templates[QueryIntent.DCF_VALUATION]
            return template.format(
                ticker=ticker,
                intrinsic_value=dcf_data.get("intrinsic_value", 0),
                current_price=dcf_data.get("current_price", 0),
                discount_rate=dcf_data.get("discount_rate", 0.1),
                terminal_growth_rate=dcf_data.get("terminal_growth_rate", 0.03),
                valuation_summary=self._create_valuation_summary(dcf_data),
                assumptions=self._extract_dcf_assumptions(context.semantic_results),
                sources=self._format_sources(context.semantic_results),
            )
        else:
            # Generate answer from semantic results
            relevant_content = self._extract_relevant_content(context.semantic_results)
            return f"""
**DCF Valuation Analysis for {ticker}**:

Based on available financial data and SEC filings:

{relevant_content}

**Note**: Detailed DCF calculation requires access to current financial models. 
The above analysis is based on available disclosure documents and market data.

**Sources**: {self._format_sources(context.semantic_results)}
            """.strip()

    def _generate_comparison_answer(self, context: AnswerContext) -> str:
        """Generate financial comparison answer."""
        if len(context.extracted_entities) < 2:
            return "I need at least two companies to perform a financial comparison."

        ticker1, ticker2 = context.extracted_entities[0], context.extracted_entities[1]

        relevant_content = self._extract_relevant_content(context.semantic_results)

        return f"""
**Financial Comparison: {ticker1} vs {ticker2}**

{relevant_content}

**Analysis Summary**:
Based on the available financial data, here are the key differences between {ticker1} and {ticker2}.

**Sources**: {self._format_sources(context.semantic_results)}
        """.strip()

    def _generate_risk_answer(self, context: AnswerContext) -> str:
        """Generate risk analysis answer."""
        if not context.extracted_entities:
            return "I need a specific company to provide risk analysis."

        ticker = context.extracted_entities[0]
        risk_content = self._extract_risk_content(context.semantic_results)

        template = self.templates[QueryIntent.RISK_ANALYSIS]
        return template.format(
            ticker=ticker,
            risk_factors=risk_content["factors"],
            risk_level=risk_content["level"],
            mitigation_strategies=risk_content["mitigation"],
            sources=self._format_sources(context.semantic_results),
        )

    def _generate_investment_answer(self, context: AnswerContext) -> str:
        """Generate investment recommendation answer."""
        if not context.extracted_entities:
            return "I need a specific company to provide investment recommendations."

        ticker = context.extracted_entities[0]

        # Analyze context for recommendation
        recommendation_data = self._analyze_investment_context(context)

        template = self.templates[QueryIntent.INVESTMENT_RECOMMENDATION]
        return template.format(
            ticker=ticker,
            recommendation=recommendation_data["recommendation"],
            confidence_level=recommendation_data["confidence"],
            analysis=recommendation_data["analysis"],
            considerations=recommendation_data["considerations"],
            risk_assessment=recommendation_data["risk_assessment"],
            sources=self._format_sources(context.semantic_results),
        )

    def _generate_general_answer(self, context: AnswerContext) -> str:
        """Generate general financial answer."""
        relevant_content = self._extract_relevant_content(context.semantic_results)

        if not relevant_content:
            return "I couldn't find specific information to answer your question. Please try rephrasing or asking about specific companies from the Magnificent 7 (AAPL, MSFT, AMZN, GOOGL, META, TSLA, NFLX)."

        return f"""
**Financial Analysis**:

{relevant_content}

**Sources**: {self._format_sources(context.semantic_results)}
        """.strip()

    def _extract_relevant_content(self, semantic_results: List[SemanticSearchResult]) -> str:
        """Extract and summarize relevant content from semantic results."""
        if not semantic_results:
            return "No relevant information found."

        # Take top 3 most relevant results
        top_results = semantic_results[:3]

        content_parts = []
        for i, result in enumerate(top_results, 1):
            # Truncate content to reasonable length
            content = result.content[:500] + "..." if len(result.content) > 500 else result.content
            content_parts.append(
                f"**Source {i}** (Similarity: {result.similarity_score:.2f}):\n{content}"
            )

        return "\n\n".join(content_parts)

    def _extract_risk_content(self, semantic_results: List[SemanticSearchResult]) -> Dict[str, str]:
        """Extract risk-related content from semantic results."""
        risk_factors = []

        for result in semantic_results[:5]:  # Top 5 results
            content = result.content.lower()
            if any(
                keyword in content for keyword in ["risk", "uncertainty", "volatility", "challenge"]
            ):
                risk_factors.append(
                    result.content[:200] + "..." if len(result.content) > 200 else result.content
                )

        return {
            "factors": "\n".join(f"• {factor}" for factor in risk_factors[:5]),
            "level": "Moderate to High" if len(risk_factors) > 3 else "Moderate",
            "mitigation": "Diversification, regular monitoring, and staying informed about market conditions.",
        }

    def _analyze_investment_context(self, context: AnswerContext) -> Dict[str, str]:
        """Analyze context to generate investment recommendation."""
        # Simple heuristic-based recommendation
        positive_signals = 0
        negative_signals = 0

        for result in context.semantic_results:
            content_lower = result.content.lower()

            # Positive indicators
            if any(
                word in content_lower
                for word in ["growth", "profit", "revenue increase", "strong performance"]
            ):
                positive_signals += 1

            # Negative indicators
            if any(word in content_lower for word in ["loss", "decline", "risk", "challenges"]):
                negative_signals += 1

        # Generate recommendation
        if positive_signals > negative_signals:
            recommendation = "POSITIVE - Consider for investment"
            confidence = "Medium-High"
        elif negative_signals > positive_signals:
            recommendation = "CAUTIOUS - Requires further analysis"
            confidence = "Medium"
        else:
            recommendation = "NEUTRAL - Mixed signals"
            confidence = "Medium"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "analysis": f"Found {positive_signals} positive and {negative_signals} negative indicators in recent data.",
            "considerations": "Consider your risk tolerance, investment timeline, and portfolio diversification.",
            "risk_assessment": "Standard market risks apply. Monitor quarterly reports and market conditions.",
        }

    def _create_valuation_summary(self, dcf_data: Dict) -> str:
        """Create valuation summary from DCF data."""
        intrinsic = dcf_data.get("intrinsic_value", 0)
        current = dcf_data.get("current_price", 0)

        if current > 0:
            discount_premium = ((intrinsic - current) / current) * 100
            if discount_premium > 10:
                return f"Stock appears undervalued by approximately {discount_premium:.1f}%"
            elif discount_premium < -10:
                return f"Stock appears overvalued by approximately {abs(discount_premium):.1f}%"
            else:
                return "Stock appears fairly valued relative to DCF model"

        return "Valuation analysis based on discounted cash flow model"

    def _extract_dcf_assumptions(self, semantic_results: List[SemanticSearchResult]) -> str:
        """Extract DCF assumptions from semantic search results."""
        assumptions = []

        for result in semantic_results:
            if "cash flow" in result.content.lower() or "revenue" in result.content.lower():
                # Extract relevant financial assumptions
                content = (
                    result.content[:150] + "..." if len(result.content) > 150 else result.content
                )
                assumptions.append(f"• {content}")

        if not assumptions:
            assumptions = [
                "• Standard DCF assumptions apply",
                "• Market-based discount rate",
                "• Conservative growth estimates",
            ]

        return "\n".join(assumptions[:3])

    def _format_sources(self, semantic_results: List[SemanticSearchResult]) -> str:
        """Format source citations."""
        if not semantic_results:
            return "No sources available"

        sources = []
        seen_sources = set()

        for result in semantic_results[:5]:  # Top 5 sources
            source = result.source_document
            if source not in seen_sources:
                sources.append(source)
                seen_sources.add(source)

        return ", ".join(sources)

    def _generate_reasoning_steps(self, context: AnswerContext) -> List[str]:
        """Generate reasoning steps for transparency."""
        steps = [
            f"1. Identified query intent as: {context.query_intent.value}",
        ]

        if context.extracted_entities:
            steps.append(f"2. Extracted entities: {', '.join(context.extracted_entities)}")

        if context.graph_results:
            steps.append(f"3. Retrieved structured data from graph database")

        if context.semantic_results:
            steps.append(
                f"4. Found {len(context.semantic_results)} relevant documents via semantic search"
            )

        steps.append(f"5. Generated contextual answer using appropriate template")

        return steps

    def _generate_fallback_response(self, context: AnswerContext) -> GraphRAGResponse:
        """Generate fallback response when answer generation fails."""
        return GraphRAGResponse(
            answer="I apologize, but I encountered an issue processing your query. Please try rephrasing your question or ask about specific companies from the Magnificent 7.",
            confidence_score=0.0,
            sources=[],
            reasoning_steps=["Failed to generate answer due to processing error"],
            cypher_results={},
            metadata={"error": "answer_generation_failed"},
        )
