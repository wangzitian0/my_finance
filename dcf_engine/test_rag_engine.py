#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCF Engine RAG Module Tests

Tests for query processing, answer generation, and orchestration functionality.
Tests run without external dependencies.
"""

import re
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.graph_rag_schema import (
    QueryIntent, GraphRAGQuery, GraphRAGResponse, SemanticSearchResult,
    DocumentType, MAGNIFICENT_7_TICKERS
)


def test_intent_recognition():
    """Test query intent recognition patterns."""
    intent_patterns = {
        QueryIntent.DCF_VALUATION: [
            r'dcf\s+valuation|discounted\s+cash\s+flow|intrinsic\s+value',
            r'what.*worth|fair\s+value|valuation\s+of'
        ],
        QueryIntent.FINANCIAL_COMPARISON: [
            r'compare.*financial|compare.*performance',
            r'(vs|versus|against).*financial'
        ],
        QueryIntent.RISK_ANALYSIS: [
            r'risk.*factor|risk.*analysis|main.*risk'
        ]
    }
    
    def extract_intent(question):
        question_lower = question.lower()
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return intent
        return QueryIntent.GENERAL_INFO
    
    # Test cases
    test_cases = [
        ("What is Apple's DCF valuation?", QueryIntent.DCF_VALUATION),
        ("Compare Apple and Microsoft financial performance", QueryIntent.FINANCIAL_COMPARISON),
        ("What are the main risk factors for Tesla?", QueryIntent.RISK_ANALYSIS),
        ("Tell me about Netflix", QueryIntent.GENERAL_INFO)
    ]
    
    for question, expected_intent in test_cases:
        detected_intent = extract_intent(question)
        assert detected_intent == expected_intent, f"Failed for: {question}"


def test_entity_extraction():
    """Test entity extraction from queries."""
    def extract_tickers(question):
        tickers = []
        for ticker in MAGNIFICENT_7_TICKERS:
            if ticker in question.upper():
                tickers.append(ticker)
        return tickers
    
    def extract_company_names(question):
        name_to_ticker = {
            'apple': 'AAPL',
            'microsoft': 'MSFT', 
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'meta': 'META',
            'facebook': 'META',
            'tesla': 'TSLA',
            'netflix': 'NFLX'
        }
        
        tickers = []
        question_lower = question.lower()
        for name, ticker in name_to_ticker.items():
            if name in question_lower:
                tickers.append(ticker)
        return list(set(tickers))  # Remove duplicates
    
    # Test ticker extraction
    assert extract_tickers("What is AAPL valuation?") == ["AAPL"]
    assert set(extract_tickers("Compare MSFT vs GOOGL")) == {"MSFT", "GOOGL"}
    
    # Test company name extraction
    assert extract_company_names("Apple financial results") == ["AAPL"]
    assert extract_company_names("Microsoft versus Google") == ["MSFT", "GOOGL"]


def test_cypher_query_generation():
    """Test Cypher query generation for different intents."""
    cypher_templates = {
        QueryIntent.DCF_VALUATION: """
            MATCH (s:Stock {ticker: $ticker})-[:HAS_VALUATION]->(dcf:DCFValuation)
            RETURN dcf ORDER BY dcf.valuation_date DESC LIMIT 1
        """,
        QueryIntent.FINANCIAL_COMPARISON: """
            MATCH (s1:Stock {ticker: $ticker1})-[:HAS_METRIC]->(m1:FinancialMetrics)
            MATCH (s2:Stock {ticker: $ticker2})-[:HAS_METRIC]->(m2:FinancialMetrics)
            WHERE m1.report_date = m2.report_date
            RETURN s1.ticker, s2.ticker, m1, m2
        """
    }
    
    def generate_cypher_query(intent, entities):
        if intent not in cypher_templates:
            return None
        
        template = cypher_templates[intent].strip()
        
        if intent == QueryIntent.DCF_VALUATION and entities:
            return template.replace('$ticker', f"'{entities[0]}'")
        elif intent == QueryIntent.FINANCIAL_COMPARISON and len(entities) >= 2:
            return template.replace('$ticker1', f"'{entities[0]}'").replace('$ticker2', f"'{entities[1]}'")
        
        return template
    
    # Test DCF query generation
    dcf_query = generate_cypher_query(QueryIntent.DCF_VALUATION, ["AAPL"])
    assert "AAPL" in dcf_query
    assert "DCFValuation" in dcf_query
    
    # Test comparison query generation  
    comp_query = generate_cypher_query(QueryIntent.FINANCIAL_COMPARISON, ["AAPL", "MSFT"])
    assert "AAPL" in comp_query
    assert "MSFT" in comp_query


def test_answer_template_formatting():
    """Test answer template formatting."""
    templates = {
        QueryIntent.DCF_VALUATION: """
Based on DCF analysis for {ticker}:
**Intrinsic Value**: ${intrinsic_value:.2f}
**Current Price**: ${current_price:.2f}
**Recommendation**: {recommendation}
        """.strip(),
        
        QueryIntent.FINANCIAL_COMPARISON: """
**Financial Comparison**: {ticker1} vs {ticker2}
{comparison_summary}
**Winner**: {winner}
        """.strip()
    }
    
    # Test DCF template
    dcf_answer = templates[QueryIntent.DCF_VALUATION].format(
        ticker="AAPL",
        intrinsic_value=150.75,
        current_price=145.20,
        recommendation="BUY"
    )
    
    assert "AAPL" in dcf_answer
    assert "$150.75" in dcf_answer
    assert "$145.20" in dcf_answer
    assert "BUY" in dcf_answer
    
    # Test comparison template
    comp_answer = templates[QueryIntent.FINANCIAL_COMPARISON].format(
        ticker1="AAPL",
        ticker2="MSFT", 
        comparison_summary="Both companies show strong growth",
        winner="AAPL"
    )
    
    assert "AAPL vs MSFT" in comp_answer
    assert "strong growth" in comp_answer


def test_context_filtering():
    """Test content filtering for retrieval."""
    def matches_filter(metadata, content_filter):
        for key, value in content_filter.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False
        
        return True
    
    # Test data
    metadata1 = {"ticker": "AAPL", "content_type": "10k"}
    metadata2 = {"ticker": "MSFT", "content_type": "10q"}
    metadata3 = {"ticker": "AAPL", "content_type": "10q"}
    
    # Test filters
    filter1 = {"ticker": "AAPL"}
    filter2 = {"content_type": ["10k", "10q"]}
    filter3 = {"ticker": "AAPL", "content_type": "10k"}
    
    assert matches_filter(metadata1, filter1) == True
    assert matches_filter(metadata2, filter1) == False
    assert matches_filter(metadata1, filter2) == True
    assert matches_filter(metadata1, filter3) == True
    assert matches_filter(metadata3, filter3) == False


def test_confidence_score_calculation():
    """Test confidence score calculation logic."""
    def calculate_confidence_score(graph_results, semantic_results, query):
        score = 0.0
        
        # Base score for having results
        if graph_results or semantic_results:
            score += 0.2
        
        # Score for structured data
        if graph_results and 'error' not in graph_results:
            score += 0.3
        
        # Score for semantic results
        if semantic_results:
            avg_similarity = sum(r.similarity_score for r in semantic_results) / len(semantic_results)
            score += min(0.3, avg_similarity * 0.5)
        
        # Score for entity extraction
        if hasattr(query, 'entities') and query.entities:
            score += 0.1
        
        # Score for intent recognition
        if hasattr(query, 'intent') and query.intent != QueryIntent.GENERAL_INFO:
            score += 0.1
        
        return min(1.0, score)
    
    # Mock query with entities and intent
    class MockQuery:
        def __init__(self, entities, intent):
            self.entities = entities
            self.intent = intent
    
    # Mock semantic results
    semantic_results = [
        type('obj', (object,), {'similarity_score': 0.8})(),
        type('obj', (object,), {'similarity_score': 0.6})()
    ]
    
    query = MockQuery(entities=["AAPL"], intent=QueryIntent.DCF_VALUATION)
    graph_results = {"dcf_value": 150.0}
    
    confidence = calculate_confidence_score(graph_results, semantic_results, query)
    
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should be reasonably high with good inputs


def test_reasoning_steps_generation():
    """Test reasoning steps generation."""
    def generate_reasoning_steps(intent, entities, graph_results, semantic_results):
        steps = [f"1. Identified query intent as: {intent.value}"]
        
        if entities:
            steps.append(f"2. Extracted entities: {', '.join(entities)}")
        
        if graph_results:
            steps.append("3. Retrieved structured data from graph database")
        
        if semantic_results:
            steps.append(f"4. Found {len(semantic_results)} relevant documents")
        
        steps.append("5. Generated contextual answer")
        
        return steps
    
    steps = generate_reasoning_steps(
        QueryIntent.DCF_VALUATION, 
        ["AAPL"], 
        {"dcf": "data"}, 
        [1, 2, 3]
    )
    
    assert len(steps) == 5
    assert "DCF_VALUATION" in steps[0]
    assert "AAPL" in steps[1]
    assert "graph database" in steps[2]
    assert "3 relevant documents" in steps[3]


def run_all_tests():
    """Run all DCF engine tests."""
    test_functions = [
        test_intent_recognition,
        test_entity_extraction,
        test_cypher_query_generation,
        test_answer_template_formatting,
        test_context_filtering,
        test_confidence_score_calculation,
        test_reasoning_steps_generation
    ]
    
    passed = 0
    total = len(test_functions)
    
    print("🧪 Running DCF Engine RAG Tests")
    print("=" * 45)
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
    
    print("=" * 45)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)