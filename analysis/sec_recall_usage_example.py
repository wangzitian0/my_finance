#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEC Recall Usage Example Template

This template demonstrates how to use SEC filing data retrieval (recall)
in DCF reports, showing the complete workflow from semantic search to
final report generation with proper citations.

Issue #75 requirement 6: Create example template showing SEC recall usage
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SECRecallUsageExample:
    """
    Example template demonstrating SEC filing recall usage in DCF reports.

    This class shows the complete workflow:
    1. Semantic search on SEC filings
    2. Content recall and ranking
    3. Integration into DCF analysis
    4. Proper citation and reference management
    """

    def __init__(self):
        """Initialize the SEC recall usage example."""
        logger.info("📚 SEC Recall Usage Example initialized")

    def demonstrate_semantic_search_workflow(self, ticker: str = "AAPL") -> Dict[str, Any]:
        """
        Demonstrate the complete semantic search and recall workflow.

        Args:
            ticker: Stock ticker to demonstrate with

        Returns:
            Complete workflow results with examples
        """
        logger.info(f"🔍 Demonstrating semantic search workflow for {ticker}")

        workflow_results = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "workflow_steps": {},
            "final_dcf_integration": {},
        }

        # Step 1: Define DCF-specific search queries
        dcf_queries = self._create_dcf_search_queries(ticker)
        workflow_results["workflow_steps"]["search_queries"] = dcf_queries

        # Step 2: Simulate semantic search results
        search_results = self._simulate_semantic_search(ticker, dcf_queries)
        workflow_results["workflow_steps"]["search_results"] = search_results

        # Step 3: Rank and filter results by DCF relevance
        ranked_results = self._rank_results_by_dcf_relevance(search_results)
        workflow_results["workflow_steps"]["ranked_results"] = ranked_results

        # Step 4: Extract actionable DCF insights
        dcf_insights = self._extract_dcf_insights(ranked_results)
        workflow_results["workflow_steps"]["dcf_insights"] = dcf_insights

        # Step 5: Create cited DCF analysis
        cited_analysis = self._create_cited_dcf_analysis(ticker, dcf_insights)
        workflow_results["final_dcf_integration"] = cited_analysis

        logger.info(f"✅ Workflow demonstration completed for {ticker}")
        return workflow_results

    def _create_dcf_search_queries(self, ticker: str) -> List[Dict[str, Any]]:
        """Create DCF-specific search queries with explanations."""
        queries = [
            {
                "query": f"{ticker} revenue growth outlook guidance",
                "dcf_purpose": "Revenue Growth Projections",
                "explanation": "Search for management guidance on future revenue growth to inform 5-year projections",
                "expected_sources": [
                    "10-K Business section",
                    "10-Q MD&A",
                    "Earnings call transcripts",
                ],
                "dcf_component": "top_line_growth",
            },
            {
                "query": f"{ticker} free cash flow capital expenditures capex",
                "dcf_purpose": "Free Cash Flow Modeling",
                "explanation": "Find historical cash flow patterns and future CapEx plans for FCF projections",
                "expected_sources": ["10-K Cash Flow Statement", "10-Q Financial Statements"],
                "dcf_component": "free_cash_flow",
            },
            {
                "query": f"{ticker} operating margin efficiency cost structure",
                "dcf_purpose": "Profitability Trends",
                "explanation": "Analyze margin trends and cost structure for profit margin projections",
                "expected_sources": ["10-K MD&A", "10-Q Operating Results"],
                "dcf_component": "operating_margins",
            },
            {
                "query": f"{ticker} risk factors competition regulatory",
                "dcf_purpose": "Risk Assessment for Discount Rate",
                "explanation": "Identify business risks that affect the discount rate (WACC) calculation",
                "expected_sources": ["10-K Risk Factors section", "10-Q Risk Updates"],
                "dcf_component": "discount_rate",
            },
            {
                "query": f"{ticker} long term strategy innovation investment",
                "dcf_purpose": "Terminal Value Assumptions",
                "explanation": "Understand long-term strategy for terminal growth rate estimation",
                "expected_sources": ["10-K Business Strategy", "Shareholder Letters"],
                "dcf_component": "terminal_value",
            },
        ]

        logger.info(f"📋 Created {len(queries)} DCF-specific search queries")
        return queries

    def _simulate_semantic_search(
        self, ticker: str, queries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Simulate semantic search results for demonstration.

        In production, this would call the actual semantic retrieval system.
        """
        logger.info(f"🔍 Simulating semantic search for {ticker}")

        # Simulate realistic SEC filing search results
        simulated_results = []

        for i, query_info in enumerate(queries):
            # Generate realistic SEC filing matches
            for doc_idx in range(2):  # 2 documents per query
                result = {
                    "query_id": i,
                    "query_text": query_info["query"],
                    "dcf_purpose": query_info["dcf_purpose"],
                    "document_id": f"{ticker}_sec_edgar_10k_2024{doc_idx + 1}.txt",
                    "similarity_score": 0.85 - (doc_idx * 0.1),  # Decreasing relevance
                    "content_excerpt": self._generate_realistic_content_excerpt(
                        ticker, query_info["dcf_component"]
                    ),
                    "filing_type": "10-K" if doc_idx == 0 else "10-Q",
                    "filing_date": f"2024-{(i + 1) * 2:02d}-15",
                    "section": self._get_relevant_section(query_info["dcf_component"]),
                    "metadata": {
                        "ticker": ticker,
                        "cik": "0000320193",  # Apple's CIK
                        "extraction_method": "semantic_search",
                        "relevance_keywords": self._get_relevance_keywords(
                            query_info["dcf_component"]
                        ),
                    },
                }
                simulated_results.append(result)

        logger.info(f"📄 Generated {len(simulated_results)} simulated search results")
        return simulated_results

    def _generate_realistic_content_excerpt(self, ticker: str, dcf_component: str) -> str:
        """Generate realistic SEC filing content excerpts for demonstration."""

        excerpts = {
            "top_line_growth": f"""Our revenue for fiscal 2024 was $383.3 billion, an increase of 2% compared to fiscal 2023. 
            We expect continued growth in our Services business, driven by our expanding installed base and increased engagement 
            across our platforms. iPhone revenue is expected to benefit from our AI capabilities and the transition to 5G. 
            Looking forward, we anticipate revenue growth in the range of 5-8% annually over the next three years.""",
            "free_cash_flow": f"""Operating cash flow for fiscal 2024 was $118.3 billion compared to $111.4 billion in fiscal 2023. 
            Free cash flow was $93.2 billion compared to $84.7 billion in the prior year. Capital expenditures were $25.1 billion, 
            primarily for data centers, retail stores, and manufacturing equipment. We expect CapEx to be approximately $27-30 billion 
            annually to support our growth initiatives and AI infrastructure investments.""",
            "operating_margins": f"""Gross margin was 46.2% compared to 44.1% in the prior year, reflecting favorable product mix 
            and cost management initiatives. Operating margin improved to 30.6% from 29.8%, demonstrating our operational efficiency. 
            We continue to focus on optimizing our cost structure while investing in innovation and growth opportunities.""",
            "discount_rate": f"""Our business faces risks including intense competition in the technology industry, rapidly changing 
            technology and customer preferences, and potential supply chain disruptions. Regulatory changes, particularly regarding 
            privacy and antitrust, could impact our operations. Economic downturns may affect consumer demand for our products.""",
            "terminal_value": f"""Our long-term strategy focuses on creating the best products and services that enrich people's lives. 
            We continue to invest in artificial intelligence, augmented reality, and autonomous systems. Our commitment to innovation 
            and our expanding ecosystem position us for sustainable long-term growth beyond traditional hardware cycles.""",
        }

        return excerpts.get(
            dcf_component, f"Relevant {ticker} financial information for {dcf_component} analysis."
        )

    def _get_relevant_section(self, dcf_component: str) -> str:
        """Get the relevant SEC filing section for each DCF component."""

        section_mapping = {
            "top_line_growth": "Management Discussion and Analysis (MD&A)",
            "free_cash_flow": "Consolidated Statements of Cash Flows",
            "operating_margins": "Consolidated Statements of Operations",
            "discount_rate": "Risk Factors",
            "terminal_value": "Business Strategy and Outlook",
        }

        return section_mapping.get(dcf_component, "General Business Information")

    def _get_relevance_keywords(self, dcf_component: str) -> List[str]:
        """Get relevance keywords for each DCF component."""

        keyword_mapping = {
            "top_line_growth": ["revenue", "growth", "guidance", "outlook", "sales"],
            "free_cash_flow": ["cash flow", "capex", "capital expenditures", "operating cash"],
            "operating_margins": ["margin", "profitability", "operating income", "efficiency"],
            "discount_rate": ["risk", "competition", "regulatory", "uncertainty"],
            "terminal_value": ["strategy", "long-term", "innovation", "growth"],
        }

        return keyword_mapping.get(dcf_component, ["financial", "business"])

    def _rank_results_by_dcf_relevance(
        self, search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank search results by DCF relevance with detailed scoring."""
        logger.info("📊 Ranking results by DCF relevance")

        for result in search_results:
            # Calculate DCF relevance score
            dcf_score = self._calculate_dcf_relevance_score(result)
            result["dcf_relevance_score"] = dcf_score
            result["ranking_explanation"] = self._generate_ranking_explanation(result)

        # Sort by DCF relevance score (descending)
        ranked_results = sorted(
            search_results, key=lambda x: x["dcf_relevance_score"], reverse=True
        )

        # Add ranking position
        for i, result in enumerate(ranked_results):
            result["dcf_rank"] = i + 1
            result["selection_rationale"] = self._generate_selection_rationale(result, i + 1)

        logger.info(f"📈 Ranked {len(ranked_results)} results by DCF relevance")
        return ranked_results

    def _calculate_dcf_relevance_score(self, result: Dict[str, Any]) -> float:
        """Calculate a DCF-specific relevance score."""

        base_similarity = result["similarity_score"]

        # Boost scores based on DCF component importance
        component_weights = {
            "top_line_growth": 1.2,  # Revenue is critical
            "free_cash_flow": 1.3,  # FCF is the foundation of DCF
            "operating_margins": 1.1,  # Important for projections
            "discount_rate": 1.0,  # Risk assessment
            "terminal_value": 0.9,  # Long-term assumptions
        }

        # Document type preference (10-K > 10-Q > 8-K)
        doc_type_weights = {
            "10-K": 1.1,  # Annual comprehensive data
            "10-Q": 1.0,  # Quarterly updates
            "8-K": 0.9,  # Event-driven information
        }

        # Recency bonus (newer filings are more relevant)
        filing_year = int(result["filing_date"].split("-")[0])
        recency_bonus = 1.0 + (filing_year - 2020) * 0.05  # 5% bonus per year since 2020

        # Calculate weighted score
        component_weight = component_weights.get(result["query_text"].split()[-1], 1.0)
        doc_weight = doc_type_weights.get(result["filing_type"], 1.0)

        dcf_score = base_similarity * component_weight * doc_weight * recency_bonus

        return round(dcf_score, 3)

    def _generate_ranking_explanation(self, result: Dict[str, Any]) -> str:
        """Generate explanation for the ranking decision."""

        explanations = []

        # Similarity score explanation
        if result["similarity_score"] > 0.9:
            explanations.append("High semantic similarity to DCF query")
        elif result["similarity_score"] > 0.8:
            explanations.append("Good semantic match with DCF requirements")
        else:
            explanations.append("Moderate relevance to DCF analysis")

        # Document type explanation
        if result["filing_type"] == "10-K":
            explanations.append("Annual 10-K provides comprehensive data")
        elif result["filing_type"] == "10-Q":
            explanations.append("Quarterly 10-Q offers recent updates")

        # DCF component explanation
        component_explanations = {
            "top_line_growth": "Critical for revenue projection modeling",
            "free_cash_flow": "Essential for DCF valuation foundation",
            "operating_margins": "Important for profitability assumptions",
            "discount_rate": "Relevant for risk assessment in WACC",
            "terminal_value": "Useful for long-term growth assumptions",
        }

        dcf_component = result.get("dcf_purpose", "").lower().replace(" ", "_")
        if dcf_component in component_explanations:
            explanations.append(component_explanations[dcf_component])

        return "; ".join(explanations)

    def _generate_selection_rationale(self, result: Dict[str, Any], rank: int) -> str:
        """Generate rationale for selecting this result in DCF analysis."""

        if rank <= 3:
            priority = "High Priority"
            rationale = "Should be included in primary DCF analysis"
        elif rank <= 6:
            priority = "Medium Priority"
            rationale = "Valuable for supporting analysis and validation"
        else:
            priority = "Low Priority"
            rationale = "May be useful for comprehensive risk assessment"

        return f"{priority}: {rationale} (Rank #{rank}, Score: {result['dcf_relevance_score']})"

    def _extract_dcf_insights(self, ranked_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract actionable DCF insights from ranked search results."""
        logger.info("💡 Extracting actionable DCF insights")

        # Group results by DCF component
        dcf_insights = {
            "revenue_projections": {
                "insights": [],
                "confidence_level": "High",
                "supporting_documents": [],
            },
            "cash_flow_modeling": {
                "insights": [],
                "confidence_level": "High",
                "supporting_documents": [],
            },
            "margin_analysis": {
                "insights": [],
                "confidence_level": "Medium",
                "supporting_documents": [],
            },
            "risk_assessment": {
                "insights": [],
                "confidence_level": "Medium",
                "supporting_documents": [],
            },
            "terminal_assumptions": {
                "insights": [],
                "confidence_level": "Low",
                "supporting_documents": [],
            },
        }

        # Process top-ranked results
        for result in ranked_results[:8]:  # Use top 8 results
            insight = self._create_dcf_insight_from_result(result)

            # Map to DCF component
            component_mapping = {
                "Revenue Growth Projections": "revenue_projections",
                "Free Cash Flow Modeling": "cash_flow_modeling",
                "Profitability Trends": "margin_analysis",
                "Risk Assessment for Discount Rate": "risk_assessment",
                "Terminal Value Assumptions": "terminal_assumptions",
            }

            dcf_component = component_mapping.get(result["dcf_purpose"], "revenue_projections")
            dcf_insights[dcf_component]["insights"].append(insight)
            dcf_insights[dcf_component]["supporting_documents"].append(result["document_id"])

        # Calculate confidence levels based on number of supporting documents
        for component, data in dcf_insights.items():
            doc_count = len(data["supporting_documents"])
            if doc_count >= 3:
                data["confidence_level"] = "High"
            elif doc_count >= 2:
                data["confidence_level"] = "Medium"
            else:
                data["confidence_level"] = "Low"

        logger.info(f"💡 Extracted insights for {len(dcf_insights)} DCF components")
        return dcf_insights

    def _create_dcf_insight_from_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured DCF insight from a search result."""

        return {
            "insight_summary": f"SEC filing provides {result['dcf_purpose'].lower()} data",
            "content_preview": result["content_excerpt"][:200] + "...",
            "full_content": result["content_excerpt"],
            "source_citation": f"{result['document_id']} ({result['filing_type']}, {result['filing_date']})",
            "relevance_score": result["dcf_relevance_score"],
            "dcf_application": self._generate_dcf_application(result),
            "quantitative_data": self._extract_quantitative_data(result["content_excerpt"]),
            "qualitative_factors": self._extract_qualitative_factors(result["content_excerpt"]),
        }

    def _generate_dcf_application(self, result: Dict[str, Any]) -> str:
        """Generate specific DCF application guidance."""

        applications = {
            "Revenue Growth Projections": "Use for 5-year revenue growth rate assumptions and segment-specific projections",
            "Free Cash Flow Modeling": "Apply to FCF margin assumptions and CapEx guidance for future years",
            "Profitability Trends": "Incorporate into operating margin projections and cost structure analysis",
            "Risk Assessment for Discount Rate": "Factor into risk premium calculation for WACC estimation",
            "Terminal Value Assumptions": "Use for long-term growth rate and sustainability assessments",
        }

        return applications.get(result["dcf_purpose"], "Apply to relevant DCF modeling assumptions")

    def _extract_quantitative_data(self, content: str) -> List[str]:
        """Extract quantitative data points from content (simplified simulation)."""

        # In production, this would use NLP/regex to extract actual numbers
        quantitative_examples = [
            "Revenue: $383.3 billion (+2% YoY)",
            "Free Cash Flow: $93.2 billion",
            "Operating Margin: 30.6%",
            "CapEx: $25.1 billion",
        ]

        return [
            q
            for q in quantitative_examples
            if any(word in content.lower() for word in q.lower().split())
        ]

    def _extract_qualitative_factors(self, content: str) -> List[str]:
        """Extract qualitative factors from content (simplified simulation)."""

        qualitative_examples = [
            "Services business growth driver",
            "AI capabilities expected to boost iPhone sales",
            "Supply chain risk factors identified",
            "Regulatory compliance requirements",
        ]

        return [q for q in qualitative_examples if len(q.split()) <= 6]  # Simple filter

    def _create_cited_dcf_analysis(
        self, ticker: str, dcf_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a complete DCF analysis with proper SEC filing citations."""
        logger.info(f"📄 Creating cited DCF analysis for {ticker}")

        cited_analysis = {
            "ticker": ticker,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "methodology": "SEC Filing-Enhanced DCF Valuation",
            "executive_summary": self._create_executive_summary(ticker, dcf_insights),
            "dcf_components": {},
            "citations": {},
            "confidence_assessment": {},
            "recommendations": {},
        }

        # Create detailed DCF component analysis
        for component, insights in dcf_insights.items():
            if insights["insights"]:  # Only include components with data
                cited_analysis["dcf_components"][component] = {
                    "analysis": self._create_component_analysis(component, insights),
                    "supporting_evidence": insights["supporting_documents"],
                    "confidence_level": insights["confidence_level"],
                    "key_assumptions": self._generate_key_assumptions(component, insights),
                }

        # Create citation index
        all_citations = set()
        for insights in dcf_insights.values():
            for insight in insights["insights"]:
                all_citations.add(insight["source_citation"])

        cited_analysis["citations"] = {
            "total_sources": len(all_citations),
            "source_list": sorted(list(all_citations)),
            "citation_note": "All data sourced from official SEC filings to ensure regulatory compliance and accuracy",
        }

        # Overall confidence assessment
        cited_analysis["confidence_assessment"] = self._assess_overall_confidence(dcf_insights)

        # Investment recommendations
        cited_analysis["recommendations"] = self._generate_sec_backed_recommendations(
            ticker, dcf_insights
        )

        logger.info(f"📄 Completed cited DCF analysis with {len(all_citations)} SEC citations")
        return cited_analysis

    def _create_executive_summary(self, ticker: str, dcf_insights: Dict[str, Any]) -> str:
        """Create an executive summary of the SEC-enhanced DCF analysis."""

        # Count available insights
        total_insights = sum(len(insights["insights"]) for insights in dcf_insights.values())
        high_confidence_components = sum(
            1 for insights in dcf_insights.values() if insights["confidence_level"] == "High"
        )

        summary = f"""
SEC Filing-Enhanced DCF Analysis for {ticker}

This valuation analysis incorporates {total_insights} insights extracted from recent SEC filings 
to provide regulatory-backed financial projections. {high_confidence_components} of 5 DCF components 
have high-confidence data support from official filings.

Key findings from SEC data:
• Revenue growth projections supported by management guidance in recent 10-K/10-Q filings
• Free cash flow modeling based on historical patterns and disclosed CapEx plans
• Risk assessment incorporates specific business risks identified in SEC risk factor disclosures
• Assumptions are backed by quantitative data from audited financial statements

This approach ensures that DCF assumptions are grounded in official, audited company disclosures
rather than analyst estimates or market speculation.
        """.strip()

        return summary

    def _create_component_analysis(self, component: str, insights: Dict[str, Any]) -> str:
        """Create detailed analysis for each DCF component."""

        component_descriptions = {
            "revenue_projections": f"""
Revenue Growth Analysis:
Based on {len(insights['insights'])} SEC filing insights, management guidance suggests sustained growth 
in core business segments. Key drivers include expanding services revenue, international market penetration, 
and new product category development. Confidence level: {insights['confidence_level']}.
            """,
            "cash_flow_modeling": f"""
Free Cash Flow Projections:
Historical FCF patterns from SEC filings show strong cash generation capability. 
Management's disclosed CapEx plans provide visibility into future investment requirements.
Confidence level: {insights['confidence_level']}.
            """,
            "margin_analysis": f"""
Operating Margin Trends:
SEC filing data reveals margin expansion initiatives and cost structure optimization.
Management focus on operational efficiency supports margin sustainability assumptions.
Confidence level: {insights['confidence_level']}.
            """,
            "risk_assessment": f"""
Business Risk Evaluation:
SEC risk factor disclosures identify key risks including competitive pressures, regulatory changes,
and supply chain vulnerabilities. These factors inform discount rate adjustments.
Confidence level: {insights['confidence_level']}.
            """,
            "terminal_assumptions": f"""
Long-term Growth Assumptions:
Management's strategic outlook from SEC filings supports terminal growth rate estimates.
Innovation investments and market expansion plans indicate sustainable competitive advantages.
Confidence level: {insights['confidence_level']}.
            """,
        }

        return component_descriptions.get(
            component, f"Analysis for {component} based on SEC filing data."
        ).strip()

    def _generate_key_assumptions(self, component: str, insights: Dict[str, Any]) -> List[str]:
        """Generate key assumptions for each DCF component."""

        assumption_templates = {
            "revenue_projections": [
                "5-year revenue CAGR: 6-8% based on management guidance",
                "Services revenue growth: 10-12% annually",
                "International expansion contributes 30% of growth",
            ],
            "cash_flow_modeling": [
                "FCF margin: 24-26% of revenue",
                "CapEx: 6-7% of revenue annually",
                "Working capital neutral to growth",
            ],
            "margin_analysis": [
                "Operating margin expansion: 50bps annually",
                "Gross margin stability: 46-48%",
                "SG&A leverage: -25bps annually",
            ],
            "risk_assessment": [
                "Risk-free rate: 4.5%",
                "Market risk premium: 6.0%",
                "Company-specific risk premium: 1.0%",
            ],
            "terminal_assumptions": [
                "Terminal growth rate: 2.5%",
                "Terminal FCF margin: 25%",
                "Sustainable competitive moat",
            ],
        }

        return assumption_templates.get(component, ["Assumptions based on SEC filing analysis"])

    def _assess_overall_confidence(self, dcf_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall confidence in the DCF analysis."""

        confidence_scores = [insights["confidence_level"] for insights in dcf_insights.values()]
        confidence_mapping = {"High": 3, "Medium": 2, "Low": 1}

        avg_confidence = sum(confidence_mapping[level] for level in confidence_scores) / len(
            confidence_scores
        )

        if avg_confidence >= 2.5:
            overall_confidence = "High"
            rationale = "Strong SEC filing support across multiple DCF components"
        elif avg_confidence >= 1.5:
            overall_confidence = "Medium"
            rationale = "Adequate SEC filing support with some data gaps"
        else:
            overall_confidence = "Low"
            rationale = "Limited SEC filing support, requires additional assumptions"

        return {
            "overall_level": overall_confidence,
            "rationale": rationale,
            "component_breakdown": confidence_scores,
            "recommendation": (
                "Proceed with DCF analysis"
                if avg_confidence >= 2.0
                else "Supplement with additional research"
            ),
        }

    def _generate_sec_backed_recommendations(
        self, ticker: str, dcf_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate investment recommendations backed by SEC filing analysis."""

        return {
            "investment_thesis": f"SEC filing analysis supports {ticker} as a fundamentally strong investment",
            "key_strengths": [
                "Consistent revenue growth trajectory documented in filings",
                "Strong free cash flow generation with prudent capital allocation",
                "Transparent risk disclosure and management mitigation strategies",
            ],
            "risk_considerations": [
                "Competitive pressures in core markets as disclosed in risk factors",
                "Regulatory oversight may impact future growth optionality",
                "Supply chain dependencies highlighted in recent 10-Q filings",
            ],
            "valuation_range": "SEC data supports intrinsic value range of $160-190 per share",
            "recommendation": "BUY with price target based on SEC-enhanced DCF model",
            "monitoring_points": [
                "Quarterly revenue guidance updates in 10-Q filings",
                "CapEx adjustments disclosed in earnings releases",
                "New risk factor additions in annual 10-K updates",
            ],
        }

    def save_example_templates(self, ticker: str = "AAPL") -> Dict[str, str]:
        """Save comprehensive example templates for SEC recall usage."""
        logger.info(f"💾 Saving SEC recall usage examples for {ticker}")

        # Create examples directory
        examples_dir = Path("data/stage_99_build/sec_recall_examples")
        examples_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        try:
            # 1. Complete workflow demonstration
            workflow_results = self.demonstrate_semantic_search_workflow(ticker)
            workflow_file = examples_dir / f"sec_recall_workflow_{ticker}.json"
            with open(workflow_file, "w", encoding="utf-8") as f:
                json.dump(workflow_results, f, indent=2, ensure_ascii=False)
            saved_files["workflow"] = str(workflow_file)

            # 2. DCF integration example
            dcf_integration = workflow_results["final_dcf_integration"]
            dcf_file = examples_dir / f"sec_cited_dcf_analysis_{ticker}.json"
            with open(dcf_file, "w", encoding="utf-8") as f:
                json.dump(dcf_integration, f, indent=2, ensure_ascii=False)
            saved_files["dcf_analysis"] = str(dcf_file)

            # 3. Usage guide
            usage_guide = self._create_usage_guide()
            guide_file = examples_dir / "SEC_Recall_Usage_Guide.md"
            with open(guide_file, "w", encoding="utf-8") as f:
                f.write(usage_guide)
            saved_files["usage_guide"] = str(guide_file)

            # 4. Code implementation example
            code_example = self._create_code_implementation_example()
            code_file = examples_dir / "implementation_example.py"
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code_example)
            saved_files["code_example"] = str(code_file)

            logger.info(f"✅ SEC recall examples saved:")
            for example_type, file_path in saved_files.items():
                logger.info(f"   - {example_type}: {file_path}")

        except Exception as e:
            logger.error(f"❌ Error saving examples: {e}")

        return saved_files

    def _create_usage_guide(self) -> str:
        """Create a comprehensive usage guide for SEC recall in DCF reports."""

        return """# SEC Recall Usage Guide for DCF Reports

This guide demonstrates how to effectively use SEC filing recall in DCF valuation analysis.

## Overview

SEC recall refers to the process of retrieving and citing specific information from SEC filings to support DCF valuation assumptions. This approach provides:

1. **Regulatory Backing**: All assumptions are grounded in official company disclosures
2. **Transparency**: Clear citation trail for all valuation inputs
3. **Accuracy**: Data comes from audited financial statements
4. **Compliance**: Meets investment research standards for source documentation

## Complete Workflow

### Step 1: Query Formulation
Create DCF-specific search queries that target relevant financial information:

```python
dcf_queries = [
    {
        'query': 'AAPL revenue growth outlook guidance',
        'dcf_purpose': 'Revenue Growth Projections',
        'target_sections': ['MD&A', 'Business Outlook']
    },
    {
        'query': 'AAPL free cash flow capital expenditures',
        'dcf_purpose': 'Free Cash Flow Modeling', 
        'target_sections': ['Cash Flow Statement', 'CapEx Discussion']
    }
]
```

### Step 2: Semantic Search Execution
Execute semantic search against SEC filing corpus:

```python
from ETL.semantic_retrieval import SemanticRetriever

retriever = SemanticRetriever(embeddings_path)
results = []

for query_info in dcf_queries:
    search_results = retriever.retrieve_relevant_content(
        query=query_info['query'],
        top_k=5,
        min_similarity=0.75,
        content_filter={'ticker': 'AAPL', 'document_type': ['sec_10k', 'sec_10q']}
    )
    results.extend(search_results)
```

### Step 3: Result Ranking and Filtering
Rank results by DCF relevance:

```python
def calculate_dcf_relevance_score(result, dcf_purpose):
    base_score = result.similarity_score
    
    # Component-specific weights
    weights = {
        'Revenue Growth Projections': 1.2,
        'Free Cash Flow Modeling': 1.3,
        'Risk Assessment': 1.0
    }
    
    # Document type preferences
    doc_weights = {'10-K': 1.1, '10-Q': 1.0, '8-K': 0.9}
    
    return base_score * weights[dcf_purpose] * doc_weights[result.doc_type]
```

### Step 4: Insight Extraction
Extract actionable DCF insights:

```python
def extract_dcf_insights(ranked_results):
    insights = {
        'revenue_projections': [],
        'cash_flow_modeling': [],
        'risk_assessment': []
    }
    
    for result in ranked_results[:10]:  # Top 10 results
        insight = {
            'content': result.content,
            'citation': f"{result.source_document} ({result.filing_date})",
            'dcf_application': generate_dcf_application(result),
            'quantitative_data': extract_numbers(result.content),
            'confidence_score': result.dcf_relevance_score
        }
        
        # Map to appropriate DCF component
        component = map_to_dcf_component(result.dcf_purpose)
        insights[component].append(insight)
    
    return insights
```

### Step 5: Citation Management
Maintain proper citations throughout the analysis:

```python
def create_citation_index(insights):
    citations = {}
    citation_counter = 1
    
    for component, component_insights in insights.items():
        for insight in component_insights:
            source = insight['citation']
            if source not in citations:
                citations[source] = f"[{citation_counter}]"
                citation_counter += 1
    
    return citations
```

### Step 6: DCF Integration
Integrate SEC insights into DCF model:

```python
def integrate_sec_data_into_dcf(insights, citations):
    dcf_assumptions = {}
    
    # Revenue projections
    if insights['revenue_projections']:
        revenue_data = insights['revenue_projections'][0]
        dcf_assumptions['revenue_growth'] = {
            'assumption': '6-8% annual growth',
            'source': revenue_data['citation'],
            'rationale': revenue_data['dcf_application'],
            'citation_ref': citations[revenue_data['citation']]
        }
    
    # Cash flow modeling
    if insights['cash_flow_modeling']:
        cf_data = insights['cash_flow_modeling'][0]
        dcf_assumptions['fcf_margin'] = {
            'assumption': '24-26% of revenue',
            'source': cf_data['citation'],
            'rationale': cf_data['dcf_application'],
            'citation_ref': citations[cf_data['citation']]
        }
    
    return dcf_assumptions
```

## Best Practices

### 1. Query Design
- **Be Specific**: Target exact DCF components (revenue growth, not just revenue)
- **Use Company Context**: Include ticker symbol for precise results
- **Multiple Angles**: Create several queries per DCF component

### 2. Result Selection
- **Prioritize Recent Filings**: 10-K > 10-Q > 8-K for comprehensiveness
- **Check Filing Dates**: Ensure data is current and relevant
- **Verify Content Quality**: Review extracted content for completeness

### 3. Citation Standards
- **Document Source**: Always include filing type and date
- **Section Reference**: Specify the relevant section when possible
- **Maintain Index**: Keep consistent citation numbering

### 4. Assumption Validation
- **Cross-Reference**: Verify assumptions across multiple filings
- **Consistency Check**: Ensure data consistency across time periods
- **Confidence Assessment**: Rate confidence based on data quality

## Example Implementation

### Complete DCF Component Analysis

```python
def create_sec_backed_dcf_component(ticker, component_name, sec_insights):
    \"\"\"Create a complete DCF component with SEC backing.\"\"\"
    
    return {
        'component': component_name,
        'ticker': ticker,
        'assumptions': extract_assumptions(sec_insights),
        'supporting_evidence': [
            {
                'insight': insight['content'][:200] + '...',
                'source': insight['citation'],
                'relevance': insight['dcf_application']
            }
            for insight in sec_insights[:3]  # Top 3 insights
        ],
        'confidence_level': assess_confidence(sec_insights),
        'methodology_note': f'Assumptions derived from SEC filing analysis using semantic recall'
    }
```

### Final Report Generation

```python
def generate_sec_enhanced_dcf_report(ticker, dcf_components, citations):
    \"\"\"Generate complete DCF report with SEC citations.\"\"\"
    
    report = f\"\"\"
# SEC Filing-Enhanced DCF Analysis: {ticker}

## Executive Summary
This DCF valuation incorporates insights from {len(citations)} SEC filings to ensure 
all assumptions are backed by official company disclosures.

## DCF Components

### Revenue Projections
{dcf_components['revenue']['assumptions']}
Source: {dcf_components['revenue']['supporting_evidence'][0]['source']}

### Free Cash Flow Modeling  
{dcf_components['cash_flow']['assumptions']}
Source: {dcf_components['cash_flow']['supporting_evidence'][0]['source']}

## Citations
\"\"\"
    
    for i, (source, ref) in enumerate(citations.items(), 1):
        report += f\"\\n{ref} {source}\"
    
    report += \"\\n\\n*All data sourced from official SEC filings*\"
    
    return report
```

## Quality Assurance

### 1. Data Validation
- Verify numerical data against original filings
- Check for data consistency across periods
- Validate calculation methodologies

### 2. Citation Accuracy
- Ensure all citations are complete and accurate
- Verify filing dates and document types
- Check section references when available

### 3. Assumption Reasonableness
- Compare assumptions to industry benchmarks
- Validate against historical company performance
- Assess consistency with management guidance

## Troubleshooting

### Common Issues

1. **No Results Found**
   - Broaden search terms
   - Check ticker symbol accuracy
   - Verify SEC data availability

2. **Low Relevance Scores**
   - Refine query specificity
   - Adjust similarity thresholds
   - Review DCF component mapping

3. **Missing Quantitative Data**
   - Target financial statement sections
   - Use multiple queries per component
   - Supplement with MD&A sections

4. **Citation Formatting Issues**
   - Standardize citation format
   - Include all required elements
   - Maintain consistent numbering

---

**Issue #75 Requirement 6**: ✅ Example template showing SEC recall usage completed.
"""

    def _create_code_implementation_example(self) -> str:
        """Create a complete code implementation example."""

        return '''#!/usr/bin/env python3
"""
SEC Recall Implementation Example

This script demonstrates how to implement SEC filing recall
in a production DCF analysis system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import your actual semantic retrieval system
from ETL.semantic_retrieval import SemanticRetriever
from common.graph_rag_schema import DEFAULT_EMBEDDING_CONFIG

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
                query=query_info['query'],
                top_k=5,
                min_similarity=0.75,
                content_filter={
                    'ticker': ticker.upper(),
                    'document_type': ['sec_10k', 'sec_10q', 'sec_8k']
                }
            )
            
            # Add query context to results
            for result in results:
                result.dcf_purpose = query_info['dcf_purpose']
                result.dcf_component = query_info['component']
            
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
                'query': f'{ticker} revenue growth rate guidance outlook management',
                'dcf_purpose': 'Revenue Growth Projections',
                'component': 'revenue_modeling'
            },
            {
                'query': f'{ticker} free cash flow generation capital expenditures capex',
                'dcf_purpose': 'Free Cash Flow Analysis',
                'component': 'cash_flow_modeling'
            },
            {
                'query': f'{ticker} operating margin profitability cost structure efficiency',
                'dcf_purpose': 'Margin Analysis',
                'component': 'profitability_trends'
            },
            {
                'query': f'{ticker} risk factors competition regulatory market risks',
                'dcf_purpose': 'Risk Assessment',
                'component': 'risk_analysis'
            },
            {
                'query': f'{ticker} long term strategy competitive advantage moat',
                'dcf_purpose': 'Terminal Value Analysis',
                'component': 'terminal_assumptions'
            }
        ]
    
    def _rank_by_dcf_relevance(self, results: List) -> List:
        """Rank results by DCF-specific relevance scoring."""
        
        # Component importance weights
        component_weights = {
            'revenue_modeling': 1.3,      # Most critical
            'cash_flow_modeling': 1.4,    # Core of DCF
            'profitability_trends': 1.1,
            'risk_analysis': 1.0,
            'terminal_assumptions': 0.9
        }
        
        # Document type weights
        doc_type_weights = {
            'sec_10k': 1.2,    # Most comprehensive
            'sec_10q': 1.0,    # Regular updates
            'sec_8k': 0.8      # Event-driven
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
            'revenue_modeling': [],
            'cash_flow_modeling': [],
            'profitability_trends': [],
            'risk_analysis': [],
            'terminal_assumptions': []
        }
        
        # Process top results
        for result in ranked_results[:15]:  # Top 15 results
            insight = {
                'content': result.content,
                'source_document': result.source_document,
                'document_type': result.document_type.value,
                'similarity_score': result.similarity_score,
                'dcf_relevance_score': result.dcf_relevance_score,
                'metadata': result.metadata,
                'filing_date': self._extract_filing_date(result.source_document),
                'quantitative_data': self._extract_quantitative_data(result.content),
                'key_phrases': self._extract_key_phrases(result.content)
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
            parts = source_document.split('_')
            for part in parts:
                if len(part) >= 8 and part[:6].isdigit():
                    date_str = part[:8]
                    if date_str.startswith('20'):
                        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        except:
            pass
        return "Unknown"
    
    def _extract_quantitative_data(self, content: str) -> List[str]:
        """Extract quantitative data from content using regex."""
        import re
        
        # Patterns for financial data
        patterns = [
            r'\\$[0-9]+\\.?[0-9]*\\s*(?:billion|million|trillion)',  # Dollar amounts
            r'[0-9]+\\.?[0-9]*%',                                    # Percentages
            r'[0-9]+\\.?[0-9]*\\s*(?:CAGR|growth|margin)',          # Growth rates
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
            'revenue growth', 'cash flow', 'operating margin', 'capital expenditures',
            'free cash flow', 'working capital', 'discount rate', 'terminal value',
            'competitive advantage', 'market share', 'risk factors', 'guidance'
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
        self, 
        ticker: str, 
        dcf_insights: Dict[str, List[Dict]], 
        citations: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create the final SEC-enhanced DCF analysis."""
        
        return {
            'ticker': ticker,
            'analysis_date': datetime.now().isoformat(),
            'methodology': 'SEC Filing-Enhanced DCF Valuation',
            'data_sources': {
                'total_sec_documents': len(citations),
                'filing_types': self._get_filing_types(dcf_insights),
                'date_range': self._get_date_range(dcf_insights)
            },
            'dcf_components': self._create_dcf_component_analysis(dcf_insights, citations),
            'citations': citations,
            'executive_summary': self._create_executive_summary(ticker, dcf_insights),
            'confidence_assessment': self._assess_confidence(dcf_insights),
            'next_steps': self._generate_next_steps(dcf_insights)
        }
    
    def _get_filing_types(self, dcf_insights: Dict[str, List[Dict]]) -> List[str]:
        """Get list of filing types used in analysis."""
        
        filing_types = set()
        for component_insights in dcf_insights.values():
            for insight in component_insights:
                filing_types.add(insight['document_type'])
        
        return sorted(list(filing_types))
    
    def _get_date_range(self, dcf_insights: Dict[str, List[Dict]]) -> str:
        """Get date range of filings used."""
        
        dates = []
        for component_insights in dcf_insights.values():
            for insight in component_insights:
                if insight['filing_date'] != 'Unknown':
                    dates.append(insight['filing_date'])
        
        if dates:
            dates.sort()
            return f"{dates[0]} to {dates[-1]}"
        return "Unknown"
    
    def _create_dcf_component_analysis(
        self, 
        dcf_insights: Dict[str, List[Dict]], 
        citations: Dict[str, str]
    ) -> Dict[str, Dict]:
        """Create detailed analysis for each DCF component."""
        
        component_analysis = {}
        
        for component, insights in dcf_insights.items():
            if insights:  # Only include components with data
                component_analysis[component] = {
                    'insights_count': len(insights),
                    'average_relevance': sum(i['dcf_relevance_score'] for i in insights) / len(insights),
                    'key_findings': [i['content'][:150] + '...' for i in insights[:3]],
                    'supporting_sources': [
                        {
                            'document': insight['source_document'],
                            'citation': citations.get(
                                f"{insight['source_document']} ({insight['filing_date']})", 
                                '[Unknown]'
                            ),
                            'relevance_score': insight['dcf_relevance_score']
                        }
                        for insight in insights[:5]  # Top 5 sources
                    ],
                    'quantitative_data': self._aggregate_quantitative_data(insights),
                    'confidence_level': self._assess_component_confidence(insights)
                }
        
        return component_analysis
    
    def _aggregate_quantitative_data(self, insights: List[Dict]) -> List[str]:
        """Aggregate quantitative data from insights."""
        
        all_data = []
        for insight in insights:
            all_data.extend(insight['quantitative_data'])
        
        # Remove duplicates and return top 10
        unique_data = list(dict.fromkeys(all_data))  # Preserves order
        return unique_data[:10]
    
    def _assess_component_confidence(self, insights: List[Dict]) -> str:
        """Assess confidence level for a DCF component."""
        
        if len(insights) >= 3 and all(i['dcf_relevance_score'] > 0.8 for i in insights[:3]):
            return 'High'
        elif len(insights) >= 2 and any(i['dcf_relevance_score'] > 0.75 for i in insights):
            return 'Medium'
        else:
            return 'Low'
    
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
        
        confidence_scores = {'High': 3, 'Medium': 2, 'Low': 1}
        avg_score = sum(confidence_scores[c] for c in component_confidences) / len(component_confidences)
        
        if avg_score >= 2.5:
            overall = 'High'
        elif avg_score >= 1.5:
            overall = 'Medium'
        else:
            overall = 'Low'
        
        return {
            'overall_confidence': overall,
            'component_breakdown': component_confidences,
            'recommendation': 'Proceed with DCF' if avg_score >= 2.0 else 'Supplement with additional research'
        }
    
    def _generate_next_steps(self, dcf_insights: Dict[str, List[Dict]]) -> List[str]:
        """Generate next steps for the DCF analysis."""
        
        next_steps = [
            'Implement DCF model using extracted SEC filing assumptions',
            'Validate quantitative assumptions against historical performance',
            'Conduct sensitivity analysis on key variables'
        ]
        
        # Component-specific next steps
        if not dcf_insights.get('revenue_modeling'):
            next_steps.append('Supplement revenue projections with additional market research')
        
        if not dcf_insights.get('risk_analysis'):
            next_steps.append('Enhance risk assessment with industry and macroeconomic factors')
        
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
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Production SEC recall example saved to: {output_file}")
    print(f"📊 Analysis summary:")
    print(f"   - Ticker: {analysis['ticker']}")
    print(f"   - SEC Documents: {analysis['data_sources']['total_sec_documents']}")
    print(f"   - DCF Components: {len(analysis['dcf_components'])}")
    print(f"   - Overall Confidence: {analysis['confidence_assessment']['overall_confidence']}")


if __name__ == "__main__":
    main()
'''


def main():
    """Demonstrate SEC recall usage examples."""
    print("🧪 SEC Recall Usage Example Demo")
    print("=" * 50)

    # Initialize example system
    example = SECRecallUsageExample()

    try:
        # Demonstrate complete workflow
        print(f"\n📋 Demonstrating SEC recall workflow for AAPL")
        workflow_results = example.demonstrate_semantic_search_workflow("AAPL")

        # Save all example templates
        print(f"\n💾 Saving example templates")
        saved_files = example.save_example_templates("AAPL")

        print(f"\n✅ SEC recall usage examples completed!")
        print(f"📁 Examples saved to: data/stage_99_build/sec_recall_examples/")
        print(f"\n📊 Workflow Summary:")
        print(f"   - Search queries: {len(workflow_results['workflow_steps']['search_queries'])}")
        print(f"   - Search results: {len(workflow_results['workflow_steps']['search_results'])}")
        print(f"   - DCF insights: {len(workflow_results['workflow_steps']['dcf_insights'])}")
        print(f"   - Final analysis: {len(workflow_results['final_dcf_integration'])} components")

        return True

    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
