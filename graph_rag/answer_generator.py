#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent Answer Generator for Graph RAG System

This module generates context-aware responses using graph data and semantic content
to provide comprehensive investment analysis answers.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .semantic_retriever import RetrievalResult

logger = logging.getLogger(__name__)


class IntelligentAnswerGenerator:
    """
    Generates intelligent, context-aware answers for investment analysis questions
    using structured graph data and semantic content retrieval.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the answer generator.

        Args:
            llm_client: Optional LLM client for advanced text generation
        """
        self.llm_client = llm_client

    def generate_answer(
        self,
        question: str,
        intent: str,
        graph_data: Dict[str, Any],
        semantic_content: List[RetrievalResult],
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive answer based on question intent and available data.

        Args:
            question: Original user question
            intent: Classified question intent
            graph_data: Structured data from Neo4j query
            semantic_content: Relevant content from semantic retrieval

        Returns:
            Dictionary containing the generated answer and metadata
        """
        # Build context from all available data
        context = self.build_context(graph_data, semantic_content)

        # Generate answer based on intent
        if intent == "dcf_valuation":
            answer = self.generate_dcf_analysis_answer(question, context)
        elif intent == "financial_comparison":
            answer = self.generate_comparison_answer(question, context)
        elif intent == "risk_analysis":
            answer = self.generate_risk_analysis_answer(question, context)
        elif intent == "news_impact":
            answer = self.generate_news_impact_answer(question, context)
        elif intent == "sector_analysis":
            answer = self.generate_sector_analysis_answer(question, context)
        elif intent == "historical_trends":
            answer = self.generate_historical_analysis_answer(question, context)
        else:
            answer = self.generate_general_answer(question, context)

        return {
            "answer": answer,
            "context_summary": context.get("summary", {}),
            "data_sources": context.get("sources", []),
            "confidence_score": self._calculate_confidence_score(context),
            "generated_at": datetime.now().isoformat(),
        }

    def build_context(
        self, graph_data: Dict[str, Any], semantic_content: List[RetrievalResult]
    ) -> Dict[str, Any]:
        """
        Build comprehensive context from graph data and semantic content.

        Args:
            graph_data: Structured data from Neo4j
            semantic_content: Retrieved semantic content

        Returns:
            Context dictionary with organized information
        """
        context = {
            "structured_data": {},
            "document_content": [],
            "sources": [],
            "summary": {},
        }

        # Process graph data
        self._process_graph_data(graph_data, context)

        # Process semantic content
        self._process_semantic_content(semantic_content, context)

        # Generate summary statistics
        context["summary"] = self._generate_context_summary(context)

        return context

    def _process_graph_data(self, graph_data: Dict[str, Any], context: Dict[str, Any]):
        """Process structured graph database results."""

        # Process stock information
        stock_info = graph_data.get("s", {}) or graph_data.get("stock", {})
        if stock_info:
            context["structured_data"]["stock"] = {
                "ticker": stock_info.get("ticker"),
                "period": stock_info.get("period"),
                "fetched_at": stock_info.get("fetched_at"),
            }

        # Process company info
        info = graph_data.get("info", {})
        if info:
            context["structured_data"]["company_info"] = {
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "business_summary": info.get("longBusinessSummary"),
                "employees": info.get("fullTimeEmployees"),
                "website": info.get("website"),
            }

        # Process DCF valuation
        dcf = graph_data.get("dcf", {})
        if dcf:
            context["structured_data"]["dcf_valuation"] = {
                "intrinsic_value": dcf.get("intrinsic_value"),
                "current_price": dcf.get("current_price"),
                "upside_downside": dcf.get("upside_downside"),
                "valuation_date": dcf.get("valuation_date"),
                "wacc": dcf.get("wacc"),
                "terminal_growth_rate": dcf.get("terminal_growth_rate"),
                "confidence_score": dcf.get("confidence_score"),
                "bankruptcy_probability": dcf.get("bankruptcy_probability"),
            }
            context["sources"].append(
                f"DCF Valuation ({dcf.get('valuation_date', 'Unknown date')})"
            )

        # Process financial metrics
        metrics = graph_data.get("financial_metrics", []) or graph_data.get(
            "metrics", []
        )
        if metrics:
            context["structured_data"]["financial_metrics"] = []
            for metric in metrics:
                if isinstance(metric, dict):
                    context["structured_data"]["financial_metrics"].append(
                        {
                            "metric_date": metric.get("metric_date"),
                            "revenue": metric.get("revenue"),
                            "net_income": metric.get("net_income"),
                            "free_cash_flow": metric.get("free_cash_flow"),
                            "roe": metric.get("roe"),
                            "debt_to_equity": metric.get("debt_to_equity"),
                            "data_source": metric.get("data_source"),
                        }
                    )
            context["sources"].append(f"Financial Metrics ({len(metrics)} periods)")

        # Process SEC filings
        filings = graph_data.get("recent_filings", [])
        if filings:
            context["structured_data"]["sec_filings"] = []
            for filing in filings:
                if isinstance(filing, dict):
                    context["structured_data"]["sec_filings"].append(
                        {
                            "filing_type": filing.get("filing_type"),
                            "filing_date": filing.get("filing_date"),
                            "accession_number": filing.get("accession_number"),
                        }
                    )
            context["sources"].append(f"SEC Filings ({len(filings)} documents)")

        # Process news events
        news = graph_data.get("recent_news", [])
        if news:
            context["structured_data"]["news_events"] = []
            for news_item in news:
                if isinstance(news_item, dict):
                    context["structured_data"]["news_events"].append(
                        {
                            "title": news_item.get("title"),
                            "published_date": news_item.get("published_date"),
                            "sentiment_score": news_item.get("sentiment_score"),
                            "impact_categories": news_item.get("impact_categories"),
                        }
                    )
            context["sources"].append(f"News Events ({len(news)} articles)")

    def _process_semantic_content(
        self, semantic_content: List[RetrievalResult], context: Dict[str, Any]
    ):
        """Process semantic retrieval results."""

        for result in semantic_content:
            context["document_content"].append(
                {
                    "content": result.content,
                    "source": result.source,
                    "document_type": result.document_type,
                    "section": result.section,
                    "similarity_score": result.similarity_score,
                    "relevance_score": result.relevance_score,
                    "document_date": (
                        result.document_date.isoformat()
                        if isinstance(result.document_date, datetime)
                        else str(result.document_date)
                    ),
                }
            )

            if result.source not in context["sources"]:
                context["sources"].append(result.source)

    def _generate_context_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for the context."""

        summary = {
            "data_quality": "unknown",
            "data_recency": "unknown",
            "content_diversity": 0,
            "total_sources": len(context["sources"]),
        }

        # Assess data quality based on available structured data
        structured_data = context["structured_data"]
        quality_indicators = [
            "dcf_valuation",
            "financial_metrics",
            "company_info",
            "sec_filings",
        ]
        available_indicators = sum(
            1 for indicator in quality_indicators if indicator in structured_data
        )

        if available_indicators >= 3:
            summary["data_quality"] = "high"
        elif available_indicators >= 2:
            summary["data_quality"] = "medium"
        else:
            summary["data_quality"] = "low"

        # Assess data recency
        dates = []
        if structured_data.get("dcf_valuation", {}).get("valuation_date"):
            dates.append(structured_data["dcf_valuation"]["valuation_date"])

        for content in context["document_content"]:
            if content.get("document_date"):
                dates.append(content["document_date"])

        if dates:
            try:
                latest_date = max(
                    (
                        datetime.fromisoformat(date.replace("Z", "+00:00"))
                        if isinstance(date, str)
                        else date
                    )
                    for date in dates
                )
                days_old = (datetime.now() - latest_date.replace(tzinfo=None)).days

                if days_old <= 30:
                    summary["data_recency"] = "very_recent"
                elif days_old <= 90:
                    summary["data_recency"] = "recent"
                elif days_old <= 365:
                    summary["data_recency"] = "moderately_recent"
                else:
                    summary["data_recency"] = "outdated"
            except:
                summary["data_recency"] = "unknown"

        # Calculate content diversity
        content_types = set()
        for content in context["document_content"]:
            content_types.add(content.get("document_type", "unknown"))
        summary["content_diversity"] = len(content_types)

        return summary

    def generate_dcf_analysis_answer(
        self, question: str, context: Dict[str, Any]
    ) -> str:
        """Generate DCF valuation analysis answer."""

        answer_parts = []

        # Check if we have DCF data
        dcf_data = context["structured_data"].get("dcf_valuation")
        if dcf_data:
            intrinsic_value = dcf_data.get("intrinsic_value")
            current_price = dcf_data.get("current_price")
            upside_downside = dcf_data.get("upside_downside")

            if intrinsic_value and current_price:
                answer_parts.append(f"**DCF Valuation Analysis:**")
                answer_parts.append(f"- Intrinsic Value: ${intrinsic_value:.2f}")
                answer_parts.append(f"- Current Price: ${current_price:.2f}")

                if upside_downside:
                    percentage = upside_downside * 100
                    if percentage > 0:
                        answer_parts.append(f"- Potential Upside: {percentage:.1f}%")
                    else:
                        answer_parts.append(
                            f"- Potential Downside: {abs(percentage):.1f}%"
                        )

                # Add key assumptions
                wacc = dcf_data.get("wacc")
                terminal_growth = dcf_data.get("terminal_growth_rate")
                if wacc:
                    answer_parts.append(f"- WACC: {wacc:.2f}%")
                if terminal_growth:
                    answer_parts.append(
                        f"- Terminal Growth Rate: {terminal_growth:.2f}%"
                    )
        else:
            answer_parts.append("**DCF Valuation Analysis:**")
            answer_parts.append(
                "No recent DCF valuation data is available for this company."
            )

        # Add financial context
        metrics = context["structured_data"].get("financial_metrics", [])
        if metrics:
            latest_metrics = max(metrics, key=lambda x: x.get("metric_date", ""))
            answer_parts.append(f"\n**Key Financial Metrics:**")

            if latest_metrics.get("revenue"):
                answer_parts.append(f"- Revenue: ${latest_metrics['revenue']:,.0f}")
            if latest_metrics.get("free_cash_flow"):
                answer_parts.append(
                    f"- Free Cash Flow: ${latest_metrics['free_cash_flow']:,.0f}"
                )
            if latest_metrics.get("roe"):
                answer_parts.append(f"- Return on Equity: {latest_metrics['roe']:.1f}%")

        # Add risk factors from semantic content
        risk_content = [
            c
            for c in context["document_content"]
            if c.get("section") == "risk_factors"
            or "risk" in c.get("source", "").lower()
        ]
        if risk_content:
            answer_parts.append(f"\n**Key Risk Considerations:**")
            # Summarize top risk factors (simplified)
            for risk in risk_content[:2]:  # Top 2 risk-related content pieces
                # Extract first sentence or first 100 characters
                content = (
                    risk["content"][:100] + "..."
                    if len(risk["content"]) > 100
                    else risk["content"]
                )
                answer_parts.append(f"- {content}")

        # Add data sources
        if context["sources"]:
            answer_parts.append(f"\n**Data Sources:** {', '.join(context['sources'])}")

        return "\n".join(answer_parts)

    def generate_comparison_answer(self, question: str, context: Dict[str, Any]) -> str:
        """Generate financial comparison answer."""

        answer_parts = ["**Financial Comparison Analysis:**"]

        # Check for multiple companies in structured data
        metrics = context["structured_data"].get("financial_metrics", [])
        if len(metrics) > 1:
            answer_parts.append("Comparing key financial metrics across companies:")

            # Group metrics by company (simplified approach)
            for metric in metrics:
                revenue = metric.get("revenue")
                roe = metric.get("roe")
                debt_to_equity = metric.get("debt_to_equity")

                metric_line = f"- Company metrics: "
                if revenue:
                    metric_line += f"Revenue ${revenue:,.0f}, "
                if roe:
                    metric_line += f"ROE {roe:.1f}%, "
                if debt_to_equity:
                    metric_line += f"D/E {debt_to_equity:.2f}"

                answer_parts.append(metric_line)

        # Add relevant semantic content for comparison context
        comparison_content = [
            c
            for c in context["document_content"]
            if any(
                word in c["content"].lower()
                for word in ["comparison", "versus", "competitive", "peer"]
            )
        ]

        if comparison_content:
            answer_parts.append(f"\n**Market Context:**")
            for content in comparison_content[:2]:
                summary = (
                    content["content"][:150] + "..."
                    if len(content["content"]) > 150
                    else content["content"]
                )
                answer_parts.append(f"- {summary}")

        return "\n".join(answer_parts)

    def generate_risk_analysis_answer(
        self, question: str, context: Dict[str, Any]
    ) -> str:
        """Generate risk analysis answer."""

        answer_parts = ["**Risk Analysis:**"]

        # Financial risk indicators
        metrics = context["structured_data"].get("financial_metrics", [])
        if metrics:
            latest_metrics = max(metrics, key=lambda x: x.get("metric_date", ""))
            debt_to_equity = latest_metrics.get("debt_to_equity")
            current_ratio = latest_metrics.get("current_ratio")

            if debt_to_equity or current_ratio:
                answer_parts.append("**Financial Risk Indicators:**")
                if debt_to_equity:
                    risk_level = (
                        "High"
                        if debt_to_equity > 2
                        else "Moderate" if debt_to_equity > 1 else "Low"
                    )
                    answer_parts.append(
                        f"- Debt-to-Equity: {debt_to_equity:.2f} ({risk_level} leverage)"
                    )
                if current_ratio:
                    liquidity = (
                        "Good"
                        if current_ratio > 1.5
                        else "Adequate" if current_ratio > 1 else "Poor"
                    )
                    answer_parts.append(
                        f"- Current Ratio: {current_ratio:.2f} ({liquidity} liquidity)"
                    )

        # DCF-based risk assessment
        dcf_data = context["structured_data"].get("dcf_valuation")
        if dcf_data:
            bankruptcy_prob = dcf_data.get("bankruptcy_probability")
            if bankruptcy_prob:
                answer_parts.append(f"- Bankruptcy Probability: {bankruptcy_prob:.1f}%")

        # Risk factors from filings
        risk_content = [
            c for c in context["document_content"] if c.get("section") == "risk_factors"
        ]
        if risk_content:
            answer_parts.append(f"\n**Key Risk Factors from SEC Filings:**")
            for risk in risk_content[:3]:
                # Extract key sentences (simplified)
                sentences = risk["content"].split(".")[:2]
                summary = ". ".join(sentences) + "."
                answer_parts.append(f"- {summary}")

        return "\n".join(answer_parts)

    def generate_news_impact_answer(
        self, question: str, context: Dict[str, Any]
    ) -> str:
        """Generate news impact analysis answer."""

        answer_parts = ["**Recent News Impact Analysis:**"]

        news_events = context["structured_data"].get("news_events", [])
        if news_events:
            # Sort by date (most recent first)
            sorted_news = sorted(
                news_events, key=lambda x: x.get("published_date", ""), reverse=True
            )

            answer_parts.append(
                f"**Recent News Events ({len(sorted_news)} articles):**"
            )

            for news in sorted_news[:5]:  # Top 5 most recent
                title = news.get("title", "No title")
                sentiment = news.get("sentiment_score", 0)
                date = news.get("published_date", "Unknown date")

                sentiment_label = (
                    "Positive"
                    if sentiment > 0.1
                    else "Negative" if sentiment < -0.1 else "Neutral"
                )
                answer_parts.append(f"- {title} ({date}) - {sentiment_label} sentiment")

                impact_categories = news.get("impact_categories", {})
                if impact_categories:
                    impacts = [
                        category
                        for category, relevance in impact_categories.items()
                        if relevance > 0.5
                    ]
                    if impacts:
                        answer_parts.append(f"  Impact areas: {', '.join(impacts)}")

        # Add relevant news content from semantic retrieval
        news_content = [
            c for c in context["document_content"] if c.get("document_type") == "news"
        ]
        if news_content:
            answer_parts.append(f"\n**Key News Highlights:**")
            for content in news_content[:3]:
                summary = (
                    content["content"][:120] + "..."
                    if len(content["content"]) > 120
                    else content["content"]
                )
                answer_parts.append(f"- {summary}")

        return "\n".join(answer_parts)

    def generate_sector_analysis_answer(
        self, question: str, context: Dict[str, Any]
    ) -> str:
        """Generate sector analysis answer."""

        answer_parts = ["**Sector Analysis:**"]

        company_info = context["structured_data"].get("company_info", {})
        sector = company_info.get("sector")
        industry = company_info.get("industry")

        if sector:
            answer_parts.append(f"**Sector:** {sector}")
        if industry:
            answer_parts.append(f"**Industry:** {industry}")

        # Add sector-relevant content from semantic retrieval
        sector_content = [
            c
            for c in context["document_content"]
            if any(
                word in c["content"].lower()
                for word in ["sector", "industry", "competitive", "market share"]
            )
        ]

        if sector_content:
            answer_parts.append(f"\n**Sector Insights:**")
            for content in sector_content[:3]:
                summary = (
                    content["content"][:150] + "..."
                    if len(content["content"]) > 150
                    else content["content"]
                )
                answer_parts.append(f"- {summary}")

        return "\n".join(answer_parts)

    def generate_historical_analysis_answer(
        self, question: str, context: Dict[str, Any]
    ) -> str:
        """Generate historical trend analysis answer."""

        answer_parts = ["**Historical Trend Analysis:**"]

        metrics = context["structured_data"].get("financial_metrics", [])
        if len(metrics) > 1:
            # Sort by date
            sorted_metrics = sorted(metrics, key=lambda x: x.get("metric_date", ""))

            answer_parts.append(
                f"**Financial Performance Trends ({len(sorted_metrics)} periods):**"
            )

            # Calculate trends for key metrics
            if len(sorted_metrics) >= 2:
                recent = sorted_metrics[-1]
                previous = sorted_metrics[-2]

                revenue_trend = self._calculate_trend(
                    previous.get("revenue"), recent.get("revenue")
                )
                if revenue_trend:
                    answer_parts.append(f"- Revenue trend: {revenue_trend}")

                fcf_trend = self._calculate_trend(
                    previous.get("free_cash_flow"), recent.get("free_cash_flow")
                )
                if fcf_trend:
                    answer_parts.append(f"- Free Cash Flow trend: {fcf_trend}")

        # Add historical context from semantic content
        historical_content = [
            c
            for c in context["document_content"]
            if any(
                word in c["content"].lower()
                for word in ["historical", "trend", "growth", "performance"]
            )
        ]

        if historical_content:
            answer_parts.append(f"\n**Historical Context:**")
            for content in historical_content[:2]:
                summary = (
                    content["content"][:150] + "..."
                    if len(content["content"]) > 150
                    else content["content"]
                )
                answer_parts.append(f"- {summary}")

        return "\n".join(answer_parts)

    def generate_general_answer(self, question: str, context: Dict[str, Any]) -> str:
        """Generate general information answer."""

        answer_parts = ["**Company Information:**"]

        # Basic company info
        company_info = context["structured_data"].get("company_info", {})
        stock_info = context["structured_data"].get("stock", {})

        if stock_info.get("ticker"):
            answer_parts.append(f"**Ticker:** {stock_info['ticker']}")

        if company_info.get("sector"):
            answer_parts.append(f"**Sector:** {company_info['sector']}")

        if company_info.get("industry"):
            answer_parts.append(f"**Industry:** {company_info['industry']}")

        if company_info.get("employees"):
            answer_parts.append(f"**Employees:** {company_info['employees']:,}")

        # Business summary
        business_summary = company_info.get("business_summary")
        if business_summary:
            summary = (
                business_summary[:200] + "..."
                if len(business_summary) > 200
                else business_summary
            )
            answer_parts.append(f"\n**Business Overview:**\n{summary}")

        # Add most relevant semantic content
        if context["document_content"]:
            top_content = sorted(
                context["document_content"],
                key=lambda x: x.get("relevance_score", 0),
                reverse=True,
            )

            if top_content:
                answer_parts.append(f"\n**Additional Information:**")
                for content in top_content[:2]:
                    summary = (
                        content["content"][:150] + "..."
                        if len(content["content"]) > 150
                        else content["content"]
                    )
                    answer_parts.append(f"- {summary}")

        return "\n".join(answer_parts)

    def _calculate_trend(
        self, previous_value: Optional[float], current_value: Optional[float]
    ) -> Optional[str]:
        """Calculate trend between two values."""

        if not previous_value or not current_value:
            return None

        change_percent = ((current_value - previous_value) / previous_value) * 100

        if change_percent > 5:
            return f"Increasing (+{change_percent:.1f}%)"
        elif change_percent < -5:
            return f"Decreasing ({change_percent:.1f}%)"
        else:
            return f"Stable ({change_percent:+.1f}%)"

    def _calculate_confidence_score(self, context: Dict[str, Any]) -> float:
        """Calculate confidence score based on data quality and availability."""

        score = 0.0

        # Data quality component (0-0.4)
        summary = context.get("summary", {})
        data_quality = summary.get("data_quality", "unknown")
        if data_quality == "high":
            score += 0.4
        elif data_quality == "medium":
            score += 0.25
        elif data_quality == "low":
            score += 0.1

        # Data recency component (0-0.3)
        data_recency = summary.get("data_recency", "unknown")
        if data_recency == "very_recent":
            score += 0.3
        elif data_recency == "recent":
            score += 0.2
        elif data_recency == "moderately_recent":
            score += 0.1

        # Content diversity component (0-0.2)
        content_diversity = summary.get("content_diversity", 0)
        score += min(0.2, content_diversity * 0.05)

        # Source count component (0-0.1)
        source_count = summary.get("total_sources", 0)
        score += min(0.1, source_count * 0.02)

        return min(1.0, score)  # Cap at 1.0

    def add_citations(self, answer: str, sources: List[str]) -> str:
        """Add citation information to the answer."""

        if not sources:
            return answer

        citations = "\n\n**Sources:**\n"
        for i, source in enumerate(sources, 1):
            citations += f"{i}. {source}\n"

        return answer + citations
