#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinLang Financial Embeddings Integration

Integrates FinLang/finance-embeddings-investopedia for specialized financial text embeddings
optimized for investment and financial analysis use cases.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available. Install with: pip install sentence-transformers")

logger = logging.getLogger(__name__)


class FinLangEmbedding:
    """
    FinLang specialized financial embeddings for DCF and investment analysis.
    
    This class provides financial domain-specific embeddings optimized for:
    - Financial statement analysis
    - Investment research documents
    - Market intelligence reports
    - DCF valuation components
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize FinLang embedding system.
        
        Args:
            config_path: Path to configuration file, defaults to debug config
        """
        self.config = self._load_config(config_path)
        self.model = None
        self.model_name = self.config.get('embedding', {}).get('model_name', 'FinLang/finance-embeddings-investopedia')
        
        # Debug and logging setup
        self.debug_mode = self.config.get('dcf_generation', {}).get('debug_mode', True)
        self.log_embeddings = self.config.get('logging', {}).get('log_embeddings', False)
        self.debug_dir = Path("data/llm_debug")
        
        self._initialize_model()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = "data/llm_debug/configs/ollama_config.yml"
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'embedding': {
                'model_name': 'FinLang/finance-embeddings-investopedia',
                'device': 'cpu',
                'batch_size': 32,
                'max_length': 512
            },
            'dcf_generation': {
                'debug_mode': True
            },
            'logging': {
                'log_embeddings': False
            }
        }
    
    def _initialize_model(self):
        """Initialize the FinLang embedding model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error("sentence-transformers not available")
            return
            
        try:
            logger.info(f"Loading FinLang embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("FinLang embedding model loaded successfully")
            
            if self.debug_mode:
                self._save_model_info()
                
        except Exception as e:
            logger.error(f"Failed to load FinLang embedding model: {e}")
            logger.info("Falling back to general financial embedding model")
            try:
                # Fallback to a more general financial model
                fallback_model = "sentence-transformers/all-MiniLM-L6-v2"
                self.model = SentenceTransformer(fallback_model)
                logger.info(f"Loaded fallback model: {fallback_model}")
            except Exception as fallback_error:
                logger.error(f"Fallback model also failed: {fallback_error}")
                self.model = None
    
    def _save_model_info(self):
        """Save model information for debugging."""
        if not self.model:
            return
            
        model_info = {
            'model_name': self.model_name,
            'model_dimension': self.model.get_sentence_embedding_dimension(),
            'max_seq_length': getattr(self.model, 'max_seq_length', 'unknown'),
            'loaded_at': datetime.now().isoformat(),
            'device': str(self.model.device) if hasattr(self.model, 'device') else 'unknown'
        }
        
        debug_file = self.debug_dir / "logs" / "finlang_model_info.json"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, indent=2)
        
        logger.debug(f"Model info saved to: {debug_file}")

    def embed_financial_text(self, text: str, text_type: str = "general") -> Optional[List[float]]:
        """
        Generate financial domain-specific embedding for text.
        
        Args:
            text: Input financial text
            text_type: Type of financial text (dcf, risk, market, earnings, etc.)
            
        Returns:
            Financial embedding vector or None if failed
        """
        if not self.model or not text:
            return None
            
        try:
            # Preprocess financial text for better embeddings
            processed_text = self._preprocess_financial_text(text, text_type)
            
            embedding = self.model.encode(processed_text)
            embedding_list = embedding.tolist()
            
            if self.log_embeddings:
                self._log_embedding_info(text, text_type, embedding_list)
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Failed to generate financial embedding: {e}")
            return None
    
    def _preprocess_financial_text(self, text: str, text_type: str) -> str:
        """
        Preprocess financial text to optimize for FinLang embeddings.
        
        Args:
            text: Raw financial text
            text_type: Type of financial content
            
        Returns:
            Preprocessed text optimized for financial embeddings
        """
        # Add financial context prefixes to improve embedding quality
        financial_prefixes = {
            'dcf': 'DCF Valuation Analysis: ',
            'risk': 'Financial Risk Assessment: ',
            'earnings': 'Earnings Analysis: ',
            'market': 'Market Intelligence: ',
            'financial_statement': 'Financial Statement Analysis: ',
            'investment': 'Investment Analysis: ',
            'general': 'Financial Analysis: '
        }
        
        prefix = financial_prefixes.get(text_type, financial_prefixes['general'])
        
        # Clean and standardize the text
        cleaned_text = text.strip()
        
        # Add financial context
        if not cleaned_text.startswith(prefix):
            processed_text = prefix + cleaned_text
        else:
            processed_text = cleaned_text
            
        return processed_text
    
    def _log_embedding_info(self, text: str, text_type: str, embedding: List[float]):
        """Log embedding information for debugging."""
        embedding_info = {
            'timestamp': datetime.now().isoformat(),
            'text_type': text_type,
            'text_length': len(text),
            'text_preview': text[:100] + "..." if len(text) > 100 else text,
            'embedding_dimension': len(embedding),
            'embedding_norm': float(np.linalg.norm(embedding)),
            'embedding_sample': embedding[:5]  # First 5 dimensions for debugging
        }
        
        log_file = self.debug_dir / "logs" / "embedding_log.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(embedding_info) + '\n')

    def embed_dcf_components(self, dcf_data: Dict[str, Any]) -> Dict[str, List[float]]:
        """
        Generate embeddings for different DCF analysis components.
        
        Args:
            dcf_data: Dictionary containing DCF analysis components
            
        Returns:
            Dictionary with embeddings for each component
        """
        embeddings = {}
        
        # Define DCF components and their text types
        dcf_components = {
            'company_overview': 'investment',
            'financial_performance': 'financial_statement',
            'cash_flow_analysis': 'dcf',
            'valuation_assumptions': 'dcf',
            'risk_factors': 'risk',
            'market_analysis': 'market',
            'investment_thesis': 'investment'
        }
        
        for component, text_type in dcf_components.items():
            if component in dcf_data and dcf_data[component]:
                text_content = str(dcf_data[component])
                embedding = self.embed_financial_text(text_content, text_type)
                if embedding:
                    embeddings[component] = embedding
                    
        return embeddings

    def find_similar_financial_content(
        self, 
        query_text: str, 
        document_embeddings: List[Dict[str, Any]], 
        top_k: int = 5,
        query_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Find financial documents most similar to query using FinLang embeddings.
        
        Args:
            query_text: Financial query text
            document_embeddings: List of documents with embeddings
            top_k: Number of top results to return
            query_type: Type of financial query (dcf, risk, etc.)
            
        Returns:
            List of most similar documents with similarity scores
        """
        if not self.model or not query_text or not document_embeddings:
            return []
            
        # Generate query embedding
        query_embedding = self.embed_financial_text(query_text, query_type)
        if not query_embedding:
            return []
            
        similarities = []
        
        for doc in document_embeddings:
            if 'embedding' not in doc:
                continue
                
            doc_embedding = doc['embedding']
            similarity = self._calculate_cosine_similarity(query_embedding, doc_embedding)
            
            similarities.append({
                'document': doc,
                'similarity_score': similarity,
                'query_type': query_type
            })
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        if self.debug_mode:
            self._save_similarity_debug(query_text, query_type, similarities[:top_k])
        
        return similarities[:top_k]
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return float(dot_product / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _save_similarity_debug(self, query: str, query_type: str, results: List[Dict]):
        """Save similarity search results for debugging."""
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'query_type': query_type,
            'num_results': len(results),
            'top_similarities': [
                {
                    'similarity': result['similarity_score'],
                    'doc_preview': str(result['document']).get('content', '')[:100] if isinstance(result['document'], dict) else str(result['document'])[:100]
                }
                for result in results[:3]
            ]
        }
        
        debug_file = self.debug_dir / "logs" / "similarity_debug.jsonl"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(debug_info) + '\n')

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.model:
            return {'status': 'not_loaded', 'model_name': self.model_name}
            
        return {
            'status': 'loaded',
            'model_name': self.model_name,
            'embedding_dimension': self.model.get_sentence_embedding_dimension(),
            'max_sequence_length': getattr(self.model, 'max_seq_length', 'unknown'),
            'device': str(self.model.device) if hasattr(self.model, 'device') else 'unknown'
        }

    def test_embedding_quality(self, test_texts: List[str]) -> Dict[str, Any]:
        """
        Test embedding quality with sample financial texts.
        
        Args:
            test_texts: List of sample financial texts
            
        Returns:
            Quality assessment results
        """
        if not self.model:
            return {'status': 'model_not_available'}
            
        results = {
            'status': 'completed',
            'test_count': len(test_texts),
            'embeddings_generated': 0,
            'average_dimension': 0,
            'sample_similarities': []
        }
        
        embeddings = []
        for text in test_texts:
            embedding = self.embed_financial_text(text, 'general')
            if embedding:
                embeddings.append(embedding)
                results['embeddings_generated'] += 1
        
        if embeddings:
            results['average_dimension'] = len(embeddings[0])
            
            # Calculate pairwise similarities for first few embeddings
            for i in range(min(3, len(embeddings))):
                for j in range(i + 1, min(3, len(embeddings))):
                    similarity = self._calculate_cosine_similarity(embeddings[i], embeddings[j])
                    results['sample_similarities'].append({
                        'text1_preview': test_texts[i][:50],
                        'text2_preview': test_texts[j][:50],
                        'similarity': similarity
                    })
        
        # Save test results
        if self.debug_mode:
            test_file = self.debug_dir / "logs" / "embedding_quality_test.json"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        
        return results