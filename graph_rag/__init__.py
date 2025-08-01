#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graph RAG System for Financial Analysis

This package provides a comprehensive Graph RAG (Retrieval-Augmented Generation)
system for intelligent financial analysis and investment research.
"""

from .semantic_embedding import SemanticEmbedding
from .query_generator import StructuredQueryGenerator, QueryIntent
from .semantic_retriever import SemanticRetriever, RetrievalResult
from .answer_generator import IntelligentAnswerGenerator
from .reasoning_processor import MultiStepReasoning, ReasoningChain, ReasoningStep

__version__ = "1.0.0"
__author__ = "Graph RAG Financial Analysis System"

__all__ = [
    'SemanticEmbedding',
    'StructuredQueryGenerator', 
    'QueryIntent',
    'SemanticRetriever',
    'RetrievalResult', 
    'IntelligentAnswerGenerator',
    'MultiStepReasoning',
    'ReasoningChain',
    'ReasoningStep',
    'GraphRAGSystem'
]


class GraphRAGSystem:
    """
    Main Graph RAG system that integrates all components for
    end-to-end financial question answering.
    """
    
    def __init__(self, neo4j_client=None, embedding_model='sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize the complete Graph RAG system.
        
        Args:
            neo4j_client: Neo4j database client
            embedding_model: Sentence transformer model name
        """
        # Initialize core components
        self.semantic_embedding = SemanticEmbedding(embedding_model)
        self.query_generator = StructuredQueryGenerator()
        self.semantic_retriever = SemanticRetriever(self.semantic_embedding)
        self.answer_generator = IntelligentAnswerGenerator()
        self.reasoning_processor = MultiStepReasoning(
            self.query_generator,
            self.semantic_retriever, 
            self.answer_generator,
            neo4j_client
        )
        
        self.neo4j_client = neo4j_client
        
    def answer_question(self, question: str) -> dict:
        """
        Answer a financial question using the complete Graph RAG pipeline.
        
        Args:
            question: User's natural language question
            
        Returns:
            Dictionary containing answer and metadata
        """
        # Check if question requires multi-step reasoning
        if self.reasoning_processor.is_complex_question(question):
            # Use multi-step reasoning for complex questions
            reasoning_chain = self.reasoning_processor.process_complex_question(question)
            
            return {
                'answer': reasoning_chain.final_answer,
                'reasoning_type': 'multi_step',
                'confidence': reasoning_chain.overall_confidence,
                'steps': len(reasoning_chain.reasoning_steps),
                'sub_questions': reasoning_chain.sub_questions,
                'metadata': reasoning_chain.processing_metadata
            }
        else:
            # Use single-step processing for simple questions
            return self._process_simple_question(question)
    
    def _process_simple_question(self, question: str) -> dict:
        """Process simple questions with single-step reasoning."""
        
        # Generate structured query
        query_info = self.query_generator.generate_cypher_query(question)
        
        # Execute graph query (mock - replace with real Neo4j execution)
        graph_data = self._execute_mock_query(query_info)
        
        # Retrieve semantic content
        semantic_content = self.semantic_retriever.retrieve_relevant_content(
            question, graph_data, top_k=5
        )
        
        # Generate answer
        answer_result = self.answer_generator.generate_answer(
            question,
            query_info['intent'],
            graph_data,
            semantic_content
        )
        
        return {
            'answer': answer_result['answer'],
            'reasoning_type': 'single_step',
            'confidence': answer_result['confidence_score'],
            'intent': query_info['intent'],
            'sources': answer_result['data_sources'],
            'metadata': {
                'query_type': query_info['intent'],
                'tickers': query_info.get('tickers', []),
                'semantic_results': len(semantic_content)
            }
        }
    
    def _execute_mock_query(self, query_info: dict) -> dict:
        """Mock query execution - replace with real Neo4j implementation."""
        
        ticker = query_info.get('tickers', ['AAPL'])[0] if query_info.get('tickers') else 'AAPL'
        
        return {
            'ticker': ticker,
            'company_info': {
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'business_summary': f'{ticker} is a leading technology company...',
                'employees': 150000
            },
            'dcf_valuation': {
                'intrinsic_value': 180.0,
                'current_price': 175.0,
                'upside_downside': 0.029,
                'valuation_date': '2024-01-15',
                'confidence_score': 0.8
            },
            'financial_metrics': [
                {
                    'metric_date': '2023-12-31',
                    'revenue': 394328000000,
                    'net_income': 99803000000,
                    'free_cash_flow': 84726000000,
                    'roe': 26.4,
                    'debt_to_equity': 1.73
                }
            ]
        }