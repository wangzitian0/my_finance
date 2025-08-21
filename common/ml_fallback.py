#!/usr/bin/env python3
"""
ML Fallback Module
Provides fallback implementations for ML functionality when containers are not available
"""
import logging
import hashlib
from typing import List, Dict, Any, Optional

# Avoid numpy import due to circular import issues in pixi environment
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Create a simple array-like class
    class SimpleArray:
        def __init__(self, data):
            self.data = data
            self.shape = (len(data), len(data[0]) if data else 0)
    np = None

logger = logging.getLogger(__name__)

class FallbackEmbeddings:
    """Simple fallback for sentence embeddings using text hashing"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        logger.warning("Using fallback embeddings - ML container not available")
    
    def encode(self, texts: List[str]):
        """Generate simple hash-based embeddings"""
        embeddings = []
        
        for text in texts:
            # Create a deterministic hash-based embedding
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Convert hex to numbers and normalize
            embedding = []
            for i in range(0, min(len(text_hash), self.dimension // 16)):
                chunk = text_hash[i*2:(i+1)*2]
                if chunk:  # Ensure chunk is not empty
                    embedding.append(int(chunk, 16) / 255.0 - 0.5)
                else:
                    embedding.append(0.0)
            
            # Pad to required dimension
            while len(embedding) < self.dimension:
                embedding.append(0.0)
                
            embeddings.append(embedding[:self.dimension])
        
        if NUMPY_AVAILABLE:
            return np.array(embeddings, dtype=np.float32)
        else:
            return SimpleArray(embeddings)
    
    def similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity based on common words"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

class MLService:
    """ML service that tries container first, falls back to simple implementation"""
    
    def __init__(self):
        self.container_available = False
        self.fallback_embeddings = None
        self._check_container()
    
    def get_sentence_embedding_dimension(self):
        """Get the dimension of sentence embeddings"""
        return 384  # Standard dimension for sentence transformers
    
    def _check_container(self):
        """Check if ML container is available"""
        try:
            # Try to import requests in pixi environment
            import subprocess
            result = subprocess.run([
                "curl", "-s", "http://localhost:8888/health"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                import json
                health = json.loads(result.stdout)
                self.container_available = health.get('ml_available', False)
                logger.info(f"ML container available via curl: {self.container_available}")
            else:
                logger.info(f"ML container check failed: {result.stderr}")
        except Exception as e:
            logger.info(f"ML container not available: {e}")
            
        if not self.container_available:
            self.fallback_embeddings = FallbackEmbeddings()
    
    def encode_texts(self, texts: List[str]):
        """Encode texts to embeddings"""
        if self.container_available:
            return self._encode_via_container(texts)
        else:
            logger.info("Using fallback embeddings")
            return self.fallback_embeddings.encode(texts)
    
    def _encode_via_container(self, texts: List[str]):
        """Encode via ML container using curl"""
        try:
            import subprocess
            import json
            import tempfile
            
            # Create temporary file with request data
            request_data = {"texts": texts}
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(request_data, f)
                temp_file = f.name
            
            try:
                result = subprocess.run([
                    "curl", "-s", "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "-d", f"@{temp_file}",
                    "http://localhost:8888/encode"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    response_data = json.loads(result.stdout)
                    embeddings = response_data["embeddings"]
                    if NUMPY_AVAILABLE:
                        return np.array(embeddings, dtype=np.float32)
                    else:
                        return SimpleArray(embeddings)
                else:
                    logger.error(f"Container encoding failed: {result.stderr}")
                    # Fall back to simple embeddings
                    if not self.fallback_embeddings:
                        self.fallback_embeddings = FallbackEmbeddings()
                    return self.fallback_embeddings.encode(texts)
            finally:
                import os
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"Container communication failed: {e}")
            # Fall back to simple embeddings
            if not self.fallback_embeddings:
                self.fallback_embeddings = FallbackEmbeddings()
            return self.fallback_embeddings.encode(texts)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity"""
        if self.container_available:
            return self._similarity_via_container(text1, text2)
        else:
            return self.fallback_embeddings.similarity(text1, text2)
    
    def _similarity_via_container(self, text1: str, text2: str) -> float:
        """Calculate similarity via ML container using curl"""
        try:
            import subprocess
            import json
            import tempfile
            
            # Create temporary file with request data
            request_data = {"text1": text1, "text2": text2}
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(request_data, f)
                temp_file = f.name
            
            try:
                result = subprocess.run([
                    "curl", "-s", "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "-d", f"@{temp_file}",
                    "http://localhost:8888/similarity"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    response_data = json.loads(result.stdout)
                    return response_data["similarity"]
                else:
                    logger.error(f"Container similarity failed: {result.stderr}")
                    return self.fallback_embeddings.similarity(text1, text2)
            finally:
                import os
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"Container communication failed: {e}")
            return self.fallback_embeddings.similarity(text1, text2)

# Global instance
_ml_service = None

def get_ml_service() -> MLService:
    """Get the global ML service instance"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service

def encode_texts(texts: List[str]):
    """Convenience function to encode texts"""
    return get_ml_service().encode_texts(texts)

def calculate_similarity(text1: str, text2: str) -> float:
    """Convenience function to calculate similarity"""
    return get_ml_service().calculate_similarity(text1, text2)