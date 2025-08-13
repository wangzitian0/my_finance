#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Step Reasoning Processor for Graph RAG System

This module handles complex questions that require multi-step reasoning
and chains together multiple queries and analyses.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ReasoningStep:
    """Data class for storing individual reasoning steps."""

    step_number: int
    question: str
    query_type: str
    result: Dict[str, Any]
    confidence: float
    evidence: List[str]


@dataclass
class ReasoningChain:
    """Data class for storing complete reasoning chains."""

    original_question: str
    sub_questions: List[str]
    reasoning_steps: List[ReasoningStep]
    final_answer: str
    overall_confidence: float
    processing_metadata: Dict[str, Any]


class MultiStepReasoning:
    """
    Processes complex questions that require multiple reasoning steps
    and coordinated analysis across different data sources.
    """

    def __init__(self, query_generator, semantic_retriever, answer_generator, graph_client=None):
        """
        Initialize the multi-step reasoning processor.

        Args:
            query_generator: StructuredQueryGenerator instance
            semantic_retriever: SemanticRetriever instance
            answer_generator: IntelligentAnswerGenerator instance
            graph_client: Neo4j database client
        """
        self.query_generator = query_generator
        self.semantic_retriever = semantic_retriever
        self.answer_generator = answer_generator
        self.graph_client = graph_client

        # Patterns for identifying complex questions
        self.complex_question_patterns = [
            r"based on.*recent.*news|considering.*recent.*developments",
            r"compare.*and.*analyze|compare.*performance.*against",
            r"what.*impact.*on.*valuation|how.*affect.*price",
            r"trend.*analysis|historical.*comparison",
            r"comprehensive.*analysis|detailed.*assessment",
            r"multiple.*factors|various.*considerations",
        ]

    def process_complex_question(self, question: str) -> ReasoningChain:
        """
        Process a complex question through multi-step reasoning.

        Args:
            question: Complex user question requiring multi-step analysis

        Returns:
            ReasoningChain with complete analysis
        """
        logger.info(f"Processing complex question: {question}")

        # Step 1: Decompose the complex question
        sub_questions = self.decompose_question(question)
        logger.info(f"Decomposed into {len(sub_questions)} sub-questions")

        # Step 2: Process each sub-question
        reasoning_steps = []
        accumulated_context = {}

        for i, sub_question in enumerate(sub_questions, 1):
            logger.info(f"Processing sub-question {i}: {sub_question}")

            step_result = self.answer_sub_question(sub_question, accumulated_context, step_number=i)

            reasoning_steps.append(step_result)

            # Update accumulated context with new findings
            self._update_accumulated_context(accumulated_context, step_result)

        # Step 3: Synthesize final answer
        final_answer = self.synthesize_final_answer(question, reasoning_steps)

        # Step 4: Calculate overall confidence
        overall_confidence = self.calculate_overall_confidence(reasoning_steps)

        # Create reasoning chain
        reasoning_chain = ReasoningChain(
            original_question=question,
            sub_questions=sub_questions,
            reasoning_steps=reasoning_steps,
            final_answer=final_answer,
            overall_confidence=overall_confidence,
            processing_metadata={
                "steps_count": len(reasoning_steps),
                "processing_time": datetime.now().isoformat(),
                "complexity_score": self._assess_complexity(question, sub_questions),
            },
        )

        logger.info(f"Completed multi-step reasoning with confidence: {overall_confidence:.2f}")
        return reasoning_chain

    def decompose_question(self, complex_question: str) -> List[str]:
        """
        Decompose a complex question into sub-questions.

        Args:
            complex_question: The original complex question

        Returns:
            List of sub-questions in logical order
        """
        # Identify question type and decomposition strategy
        question_lower = complex_question.lower()

        # Pattern-based decomposition strategies
        if any(
            pattern in question_lower
            for pattern in ["recent news", "latest development", "recent event"]
        ):
            return self._decompose_news_impact_question(complex_question)
        elif any(pattern in question_lower for pattern in ["compare", "versus", "vs.", "against"]):
            return self._decompose_comparison_question(complex_question)
        elif any(pattern in question_lower for pattern in ["dcf", "valuation", "worth", "value"]):
            return self._decompose_valuation_question(complex_question)
        elif any(pattern in question_lower for pattern in ["trend", "historical", "over time"]):
            return self._decompose_trend_question(complex_question)
        else:
            return self._decompose_general_question(complex_question)

    def _decompose_news_impact_question(self, question: str) -> List[str]:
        """Decompose news impact questions."""
        # Extract ticker if present
        tickers = self.query_generator.extract_tickers_from_question(question)
        ticker = tickers[0] if tickers else "the company"

        return [
            f"What is the current valuation of {ticker}?",
            f"What recent news events have affected {ticker}?",
            f"How do these news events impact the financial outlook for {ticker}?",
            f"What adjustments should be made to the DCF model based on recent developments?",
        ]

    def _decompose_comparison_question(self, question: str) -> List[str]:
        """Decompose comparison questions."""
        tickers = self.query_generator.extract_tickers_from_question(question)

        if len(tickers) >= 2:
            ticker1, ticker2 = tickers[0], tickers[1]
            return [
                f"What are the key financial metrics for {ticker1}?",
                f"What are the key financial metrics for {ticker2}?",
                f"What are the current valuations for {ticker1} and {ticker2}?",
                f"How do the business models and risk profiles compare between {ticker1} and {ticker2}?",
            ]
        else:
            ticker = tickers[0] if tickers else "the company"
            return [
                f"What sector does {ticker} operate in?",
                f"Who are the main competitors of {ticker}?",
                f"How does {ticker} perform relative to its peers?",
                f"What are {ticker}'s competitive advantages?",
            ]

    def _decompose_valuation_question(self, question: str) -> List[str]:
        """Decompose DCF valuation questions."""
        tickers = self.query_generator.extract_tickers_from_question(question)
        ticker = tickers[0] if tickers else "the company"

        return [
            f"What are the current financial metrics for {ticker}?",
            f"What is the existing DCF valuation for {ticker}?",
            f"What are the key assumptions in the DCF model for {ticker}?",
            f"What risk factors should be considered in the valuation of {ticker}?",
        ]

    def _decompose_trend_question(self, question: str) -> List[str]:
        """Decompose trend analysis questions."""
        tickers = self.query_generator.extract_tickers_from_question(question)
        ticker = tickers[0] if tickers else "the company"

        return [
            f"What is the historical financial performance of {ticker}?",
            f"What are the key growth trends for {ticker}?",
            f"How has the market valuation of {ticker} changed over time?",
            f"What factors are driving the performance trends for {ticker}?",
        ]

    def _decompose_general_question(self, question: str) -> List[str]:
        """Decompose general complex questions."""
        tickers = self.query_generator.extract_tickers_from_question(question)
        ticker = tickers[0] if tickers else "the company"

        # Generic decomposition based on available data types
        return [
            f"What basic information is available about {ticker}?",
            f"What are the financial fundamentals of {ticker}?",
            f"What is the current valuation status of {ticker}?",
            f"What additional context is relevant for analyzing {ticker}?",
        ]

    def answer_sub_question(
        self, sub_question: str, accumulated_context: Dict[str, Any], step_number: int
    ) -> ReasoningStep:
        """
        Answer a single sub-question within the reasoning chain.

        Args:
            sub_question: The sub-question to answer
            accumulated_context: Context from previous reasoning steps
            step_number: Sequential step number

        Returns:
            ReasoningStep with the answer and evidence
        """
        try:
            # Generate appropriate query for the sub-question
            query_info = self.query_generator.generate_cypher_query(sub_question)

            # Execute graph query (mock implementation - would use real Neo4j client)
            graph_data = self._execute_graph_query(query_info, accumulated_context)

            # Retrieve relevant semantic content
            semantic_content = self.semantic_retriever.retrieve_relevant_content(
                sub_question, graph_data, top_k=3
            )

            # Generate answer for this sub-question
            answer_result = self.answer_generator.generate_answer(
                sub_question, query_info["intent"], graph_data, semantic_content
            )

            # Extract evidence sources
            evidence = self._extract_evidence(answer_result, graph_data, semantic_content)

            return ReasoningStep(
                step_number=step_number,
                question=sub_question,
                query_type=query_info["intent"],
                result=answer_result,
                confidence=answer_result.get("confidence_score", 0.5),
                evidence=evidence,
            )

        except Exception as e:
            logger.error(f"Error answering sub-question '{sub_question}': {e}")

            # Return fallback step
            return ReasoningStep(
                step_number=step_number,
                question=sub_question,
                query_type="error",
                result={"answer": f"Unable to process sub-question: {str(e)}"},
                confidence=0.0,
                evidence=[f"Error: {str(e)}"],
            )

    def _execute_graph_query(
        self, query_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute graph query (mock implementation).

        In a real implementation, this would:
        1. Connect to Neo4j database
        2. Execute the Cypher query
        3. Return structured results
        """
        # Mock data structure - replace with actual Neo4j execution
        mock_data = {
            "ticker": (
                query_info.get("tickers", ["AAPL"])[0] if query_info.get("tickers") else "AAPL"
            ),
            "company_info": {
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "employees": 164000,
            },
            "dcf_valuation": {
                "intrinsic_value": 185.50,
                "current_price": 175.25,
                "upside_downside": 0.058,
                "valuation_date": "2024-01-15",
                "confidence_score": 0.75,
            },
            "recent_filings": [
                {
                    "filing_type": "10-K",
                    "filing_date": "2024-01-01",
                    "business_overview": "Technology company focused on consumer electronics...",
                    "risk_factors": "Competitive market conditions, supply chain risks...",
                }
            ],
        }

        return mock_data

    def _update_accumulated_context(self, context: Dict[str, Any], step_result: ReasoningStep):
        """Update accumulated context with results from a reasoning step."""

        step_key = f"step_{step_result.step_number}"
        context[step_key] = {
            "question": step_result.question,
            "answer": step_result.result.get("answer", ""),
            "confidence": step_result.confidence,
            "evidence": step_result.evidence,
            "query_type": step_result.query_type,
        }

        # Extract key findings for use in subsequent steps
        result_data = step_result.result

        # Update ticker information
        if "ticker" in result_data:
            context["ticker"] = result_data["ticker"]

        # Update financial context
        if "dcf_valuation" in result_data:
            context["valuation_info"] = result_data["dcf_valuation"]

        # Update sector/industry context
        if "company_info" in result_data:
            context["company_context"] = result_data["company_info"]

    def synthesize_final_answer(
        self, original_question: str, reasoning_steps: List[ReasoningStep]
    ) -> str:
        """
        Synthesize a comprehensive final answer from all reasoning steps.

        Args:
            original_question: The original complex question
            reasoning_steps: List of completed reasoning steps

        Returns:
            Comprehensive final answer
        """
        answer_parts = [f"**Comprehensive Analysis: {original_question}**\n"]

        # Add executive summary
        answer_parts.append("**Executive Summary:**")

        # Extract key insights from each step
        key_insights = []
        for step in reasoning_steps:
            if step.confidence > 0.3:  # Only include confident insights
                # Extract first sentence or key finding from step answer
                step_answer = step.result.get("answer", "")
                if step_answer:
                    # Simple extraction - take first 100 characters or first sentence
                    insight = step_answer.split("\n")[0][:100]
                    if insight:
                        key_insights.append(f"- {insight}...")

        if key_insights:
            answer_parts.extend(key_insights)

        # Add detailed step-by-step analysis
        answer_parts.append(f"\n**Detailed Analysis:**")

        for i, step in enumerate(reasoning_steps, 1):
            answer_parts.append(f"\n**Step {i}: {step.question}**")
            answer_parts.append(step.result.get("answer", "No answer available"))

            if step.confidence < 0.5:
                answer_parts.append(
                    f"*Note: Lower confidence ({step.confidence:.2f}) - limited data available*"
                )

        # Add overall assessment
        overall_confidence = self.calculate_overall_confidence(reasoning_steps)
        answer_parts.append(f"\n**Overall Assessment:**")
        answer_parts.append(f"Analysis confidence: {overall_confidence:.1%}")

        if overall_confidence > 0.7:
            answer_parts.append("High confidence in analysis based on comprehensive data.")
        elif overall_confidence > 0.4:
            answer_parts.append("Moderate confidence - some data limitations noted.")
        else:
            answer_parts.append("Lower confidence due to limited available data.")

        # Add combined evidence sources
        all_evidence = []
        for step in reasoning_steps:
            all_evidence.extend(step.evidence)

        unique_evidence = list(set(all_evidence))
        if unique_evidence:
            answer_parts.append(f"\n**Evidence Sources:** {', '.join(unique_evidence[:5])}")

        return "\n".join(answer_parts)

    def calculate_overall_confidence(self, reasoning_steps: List[ReasoningStep]) -> float:
        """
        Calculate overall confidence score for the reasoning chain.

        Args:
            reasoning_steps: List of completed reasoning steps

        Returns:
            Overall confidence score (0-1)
        """
        if not reasoning_steps:
            return 0.0

        # Weight confidence by step importance (earlier steps often more foundational)
        total_weighted_confidence = 0.0
        total_weight = 0.0

        for i, step in enumerate(reasoning_steps):
            # Earlier steps get slightly higher weight
            weight = 1.0 + (0.1 * (len(reasoning_steps) - i))
            total_weighted_confidence += step.confidence * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        base_confidence = total_weighted_confidence / total_weight

        # Apply completeness penalty if some steps failed
        failed_steps = sum(1 for step in reasoning_steps if step.confidence < 0.1)
        completeness_factor = max(0.5, 1.0 - (failed_steps / len(reasoning_steps)))

        return base_confidence * completeness_factor

    def _assess_complexity(self, original_question: str, sub_questions: List[str]) -> float:
        """Assess the complexity of the original question."""

        complexity_indicators = [
            len(sub_questions),  # More sub-questions = higher complexity
            len(original_question.split()),  # Longer questions tend to be more complex
            sum(
                1
                for pattern in self.complex_question_patterns
                if any(p in original_question.lower() for p in pattern.split("|"))
            ),
        ]

        # Normalize to 0-1 scale
        complexity_score = min(1.0, sum(complexity_indicators) / 20.0)
        return complexity_score

    def _extract_evidence(
        self,
        answer_result: Dict[str, Any],
        graph_data: Dict[str, Any],
        semantic_content: List,
    ) -> List[str]:
        """Extract evidence sources from answer components."""

        evidence = []

        # From answer result
        sources = answer_result.get("data_sources", [])
        evidence.extend(sources)

        # From graph data
        if "ticker" in graph_data:
            evidence.append(f"Stock data for {graph_data['ticker']}")

        # From semantic content
        for content in semantic_content:
            if hasattr(content, "source"):
                evidence.append(content.source)

        return list(set(evidence))  # Remove duplicates

    def is_complex_question(self, question: str) -> bool:
        """
        Determine if a question requires multi-step reasoning.

        Args:
            question: User's question

        Returns:
            True if question is complex and needs multi-step processing
        """
        question_lower = question.lower()

        # Check for complexity indicators
        complexity_indicators = [
            # Multiple entities or comparisons
            len(self.query_generator.extract_tickers_from_question(question)) > 1,
            # Temporal complexity
            any(
                temporal in question_lower
                for temporal in ["recent", "latest", "trend", "historical", "over time"]
            ),
            # Causal relationships
            any(
                causal in question_lower
                for causal in ["impact", "affect", "influence", "because of", "due to"]
            ),
            # Multiple question types
            "?" in question and question.count("?") > 1,
            # Explicit complexity markers
            any(
                marker in question_lower
                for marker in [
                    "comprehensive",
                    "detailed",
                    "thorough",
                    "complete analysis",
                ]
            ),
            # Pattern matching
            any(
                pattern in question_lower
                for pattern in [
                    "based on",
                    "considering",
                    "taking into account",
                    "given that",
                    "compare and",
                    "analyze the relationship",
                    "how does this affect",
                ]
            ),
        ]

        # If multiple complexity indicators present, treat as complex
        return sum(complexity_indicators) >= 2
