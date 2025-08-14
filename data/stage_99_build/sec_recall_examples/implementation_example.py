#!/usr/bin/env python3
"""
SEC Recall Implementation Example

This script demonstrates how to implement SEC filing recall
in a production DCF analysis system.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from common.graph_rag_schema import DEFAULT_EMBEDDING_CONFIG
# Import your actual semantic retrieval system
from ETL.semantic_retrieval import SemanticRetriever

logger = logging.getLogger(__name__)


class ProductionSECRecall:
    """Production implementation of SEC filing recall for DCF analysis."""

    def __init__(self, embeddings_path: Path):
        """Initialize with actual semantic retrieval system."""
        self.retriever = SemanticRetriever(embeddings_path, DEFAULT_EMBEDDING_CONFIG)
        self.citation_counter = 1
        self.citation_index = {}

    def perform_dcf_sec_recall(self, ticker: str) -> Dict[str, Any]:
        """Perform complete SEC recall for DCF analysis."""

        logger.info(f"🔍 Starting SEC recall for {ticker} DCF analysis")

        # Step 1: Define DCF search queries
        queries = self._create_dcf_queries(ticker)

        # Step 2: Execute semantic search
        all_results = []
        for query_info in queries:
            results = self.retriever.retrieve_relevant_content(
                query=query_info["query"],
                top_k=5,
                min_similarity=0.75,
                content_filter={
                    "ticker": ticker.upper(),
                    "document_type": ["sec_10k", "sec_10q", "sec_8k"],
                },
            )

            # Add query context to results
            for result in results:
                result.dcf_purpose = query_info["dcf_purpose"]
                result.dcf_component = query_info["component"]

            all_results.extend(results)

        # Step 3: Rank by DCF relevance
        ranked_results = self._rank_by_dcf_relevance(all_results)

        # Step 4: Extract insights
        dcf_insights = self._extract_dcf_insights(ranked_results)

        # Step 5: Create citations
        citations = self._create_citation_index(dcf_insights)

        # Step 6: Generate final analysis
        final_analysis = self._create_final_analysis(ticker, dcf_insights, citations)

        logger.info(f"✅ SEC recall completed for {ticker}")
        return final_analysis

    def _create_dcf_queries(self, ticker: str) -> List[Dict[str, str]]:
        """Create production-ready DCF search queries."""

        return [
            {
                "query": f"{ticker} revenue growth rate guidance outlook management",
                "dcf_purpose": "Revenue Growth Projections",
                "component": "revenue_modeling",
            },
            {
                "query": f"{ticker} free cash flow generation capital expenditures capex",
                "dcf_purpose": "Free Cash Flow Analysis",
                "component": "cash_flow_modeling",
            },
            {
                "query": f"{ticker} operating margin profitability cost structure efficiency",
                "dcf_purpose": "Margin Analysis",
                "component": "profitability_trends",
            },
            {
                "query": f"{ticker} risk factors competition regulatory market risks",
                "dcf_purpose": "Risk Assessment",
                "component": "risk_analysis",
            },
            {
                "query": f"{ticker} long term strategy competitive advantage moat",
                "dcf_purpose": "Terminal Value Analysis",
                "component": "terminal_assumptions",
            },
        ]

    def _rank_by_dcf_relevance(self, results: List) -> List:
        """Rank results by DCF-specific relevance scoring."""

        # Component importance weights
        component_weights = {
            "revenue_modeling": 1.3,  # Most critical
            "cash_flow_modeling": 1.4,  # Core of DCF
            "profitability_trends": 1.1,
            "risk_analysis": 1.0,
            "terminal_assumptions": 0.9,
        }

        # Document type weights
        doc_type_weights = {
            "sec_10k": 1.2,  # Most comprehensive
            "sec_10q": 1.0,  # Regular updates
            "sec_8k": 0.8,  # Event-driven
        }

        for result in results:
            # Calculate DCF relevance score
            base_score = result.similarity_score
            component_weight = component_weights.get(result.dcf_component, 1.0)
            doc_weight = doc_type_weights.get(result.document_type.value, 1.0)

            result.dcf_relevance_score = base_score * component_weight * doc_weight

        # Sort by DCF relevance
        return sorted(results, key=lambda x: x.dcf_relevance_score, reverse=True)

    def _extract_dcf_insights(self, ranked_results: List) -> Dict[str, List[Dict]]:
        """Extract structured DCF insights from search results."""

        insights = {
            "revenue_modeling": [],
            "cash_flow_modeling": [],
            "profitability_trends": [],
            "risk_analysis": [],
            "terminal_assumptions": [],
        }

        # Process top results
        for result in ranked_results[:15]:  # Top 15 results
            insight = {
                "content": result.content,
                "source_document": result.source_document,
                "document_type": result.document_type.value,
                "similarity_score": result.similarity_score,
                "dcf_relevance_score": result.dcf_relevance_score,
                "metadata": result.metadata,
                "filing_date": self._extract_filing_date(result.source_document),
                "quantitative_data": self._extract_quantitative_data(result.content),
                "key_phrases": self._extract_key_phrases(result.content),
            }

            # Add to appropriate component
            component = result.dcf_component
            if component in insights:
                insights[component].append(insight)

        return insights

    def _extract_filing_date(self, source_document: str) -> str:
        """Extract filing date from document name."""
        # Example: AAPL_sec_edgar_10k_250810-005935_0000320193-24-000123.txt
        try:
            # Look for YYYYMMDD pattern in filename
            parts = source_document.split("_")
            for part in parts:
                if len(part) >= 8 and part[:6].isdigit():
                    date_str = part[:8]
                    if date_str.startswith("20"):
                        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        except:
            pass
        return "Unknown"

    def _extract_quantitative_data(self, content: str) -> List[str]:
        """Extract quantitative data from content using regex."""
        import re

        # Patterns for financial data
        patterns = [
            r"\$[0-9]+\.?[0-9]*\s*(?:billion|million|trillion)",  # Dollar amounts
            r"[0-9]+\.?[0-9]*%",  # Percentages
            r"[0-9]+\.?[0-9]*\s*(?:CAGR|growth|margin)",  # Growth rates
        ]

        quantitative_data = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            quantitative_data.extend(matches[:3])  # Limit to 3 matches per pattern

        return quantitative_data[:10]  # Max 10 quantitative points

    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key financial phrases from content."""

        # Key financial phrases for DCF
        key_phrases = [
            "revenue growth",
            "cash flow",
            "operating margin",
            "capital expenditures",
            "free cash flow",
            "working capital",
            "discount rate",
            "terminal value",
            "competitive advantage",
            "market share",
            "risk factors",
            "guidance",
        ]

        found_phrases = []
        content_lower = content.lower()

        for phrase in key_phrases:
            if phrase in content_lower:
                found_phrases.append(phrase)

        return found_phrases[:5]  # Limit to 5 key phrases

    def _create_citation_index(self, dcf_insights: Dict[str, List[Dict]]) -> Dict[str, str]:
        """Create a citation index for all sources."""

        citations = {}

        for component_insights in dcf_insights.values():
            for insight in component_insights:
                source = f"{insight['source_document']} ({insight['filing_date']})"
                if source not in citations:
                    citations[source] = f"[{self.citation_counter}]"
                    self.citation_counter += 1

        return citations

    def _create_final_analysis(
        self, ticker: str, dcf_insights: Dict[str, List[Dict]], citations: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create the final SEC-enhanced DCF analysis."""

        return {
            "ticker": ticker,
            "analysis_date": datetime.now().isoformat(),
            "methodology": "SEC Filing-Enhanced DCF Valuation",
            "data_sources": {
                "total_sec_documents": len(citations),
                "filing_types": self._get_filing_types(dcf_insights),
                "date_range": self._get_date_range(dcf_insights),
            },
            "dcf_components": self._create_dcf_component_analysis(dcf_insights, citations),
            "citations": citations,
            "executive_summary": self._create_executive_summary(ticker, dcf_insights),
            "confidence_assessment": self._assess_confidence(dcf_insights),
            "next_steps": self._generate_next_steps(dcf_insights),
        }

    def _get_filing_types(self, dcf_insights: Dict[str, List[Dict]]) -> List[str]:
        """Get list of filing types used in analysis."""

        filing_types = set()
        for component_insights in dcf_insights.values():
            for insight in component_insights:
                filing_types.add(insight["document_type"])

        return sorted(list(filing_types))

    def _get_date_range(self, dcf_insights: Dict[str, List[Dict]]) -> str:
        """Get date range of filings used."""

        dates = []
        for component_insights in dcf_insights.values():
            for insight in component_insights:
                if insight["filing_date"] != "Unknown":
                    dates.append(insight["filing_date"])

        if dates:
            dates.sort()
            return f"{dates[0]} to {dates[-1]}"
        return "Unknown"

    def _create_dcf_component_analysis(
        self, dcf_insights: Dict[str, List[Dict]], citations: Dict[str, str]
    ) -> Dict[str, Dict]:
        """Create detailed analysis for each DCF component."""

        component_analysis = {}

        for component, insights in dcf_insights.items():
            if insights:  # Only include components with data
                component_analysis[component] = {
                    "insights_count": len(insights),
                    "average_relevance": sum(i["dcf_relevance_score"] for i in insights)
                    / len(insights),
                    "key_findings": [i["content"][:150] + "..." for i in insights[:3]],
                    "supporting_sources": [
                        {
                            "document": insight["source_document"],
                            "citation": citations.get(
                                f"{insight['source_document']} ({insight['filing_date']})",
                                "[Unknown]",
                            ),
                            "relevance_score": insight["dcf_relevance_score"],
                        }
                        for insight in insights[:5]  # Top 5 sources
                    ],
                    "quantitative_data": self._aggregate_quantitative_data(insights),
                    "confidence_level": self._assess_component_confidence(insights),
                }

        return component_analysis

    def _aggregate_quantitative_data(self, insights: List[Dict]) -> List[str]:
        """Aggregate quantitative data from insights."""

        all_data = []
        for insight in insights:
            all_data.extend(insight["quantitative_data"])

        # Remove duplicates and return top 10
        unique_data = list(dict.fromkeys(all_data))  # Preserves order
        return unique_data[:10]

    def _assess_component_confidence(self, insights: List[Dict]) -> str:
        """Assess confidence level for a DCF component."""

        if len(insights) >= 3 and all(i["dcf_relevance_score"] > 0.8 for i in insights[:3]):
            return "High"
        elif len(insights) >= 2 and any(i["dcf_relevance_score"] > 0.75 for i in insights):
            return "Medium"
        else:
            return "Low"

    def _create_executive_summary(self, ticker: str, dcf_insights: Dict[str, List[Dict]]) -> str:
        """Create executive summary of the analysis."""

        total_insights = sum(len(insights) for insights in dcf_insights.values())
        components_with_data = len([c for c in dcf_insights.values() if c])

        return f"""
SEC Filing-Enhanced DCF Analysis for {ticker}

This analysis extracted {total_insights} relevant insights from recent SEC filings 
across {components_with_data} DCF components. The analysis ensures all valuation 
assumptions are grounded in official company disclosures and audited financial data.

Key strengths of this approach:
• Regulatory compliance through official SEC filing sources
• Transparent citation trail for all assumptions
• Reduced reliance on analyst estimates or market speculation
• Comprehensive coverage of business fundamentals and risks

The resulting DCF model provides a robust, well-documented valuation framework
suitable for institutional investment analysis and regulatory review.
        """.strip()

    def _assess_confidence(self, dcf_insights: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Assess overall confidence in the analysis."""

        component_confidences = []
        for insights in dcf_insights.values():
            if insights:
                component_confidences.append(self._assess_component_confidence(insights))

        confidence_scores = {"High": 3, "Medium": 2, "Low": 1}
        avg_score = sum(confidence_scores[c] for c in component_confidences) / len(
            component_confidences
        )

        if avg_score >= 2.5:
            overall = "High"
        elif avg_score >= 1.5:
            overall = "Medium"
        else:
            overall = "Low"

        return {
            "overall_confidence": overall,
            "component_breakdown": component_confidences,
            "recommendation": (
                "Proceed with DCF" if avg_score >= 2.0 else "Supplement with additional research"
            ),
        }

    def _generate_next_steps(self, dcf_insights: Dict[str, List[Dict]]) -> List[str]:
        """Generate next steps for the DCF analysis."""

        next_steps = [
            "Implement DCF model using extracted SEC filing assumptions",
            "Validate quantitative assumptions against historical performance",
            "Conduct sensitivity analysis on key variables",
        ]

        # Component-specific next steps
        if not dcf_insights.get("revenue_modeling"):
            next_steps.append("Supplement revenue projections with additional market research")

        if not dcf_insights.get("risk_analysis"):
            next_steps.append("Enhance risk assessment with industry and macroeconomic factors")

        return next_steps


def main():
    """Demonstrate production SEC recall implementation."""

    # Initialize with actual embeddings path
    embeddings_path = Path("data/stage_03_load/embeddings")

    if not embeddings_path.exists():
        print("❌ Embeddings not found. Run semantic embedding generation first.")
        return

    # Create SEC recall system
    sec_recall = ProductionSECRecall(embeddings_path)

    # Perform SEC recall for AAPL
    analysis = sec_recall.perform_dcf_sec_recall("AAPL")

    # Save results
    output_file = Path("data/stage_99_build/production_sec_recall_example.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"✅ Production SEC recall example saved to: {output_file}")
    print(f"📊 Analysis summary:")
    print(f"   - Ticker: {analysis['ticker']}")
    print(f"   - SEC Documents: {analysis['data_sources']['total_sec_documents']}")
    print(f"   - DCF Components: {len(analysis['dcf_components'])}")
    print(f"   - Overall Confidence: {analysis['confidence_assessment']['overall_confidence']}")


if __name__ == "__main__":
    main()
