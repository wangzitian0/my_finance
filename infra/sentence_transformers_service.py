#!/usr/bin/env python3
"""
Sentence Transformers Microservice
Provides ML embedding services via HTTP API to avoid dependency conflicts
"""
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Any
import traceback

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import torch
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    ML_ERROR = str(e)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SentenceTransformersHandler(BaseHTTPRequestHandler):
    """HTTP handler for sentence transformers requests"""
    
    def __init__(self, *args, **kwargs):
        self.model = None
        if ML_AVAILABLE:
            try:
                # Load the standard sentence transformer model
                self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                logger.info("✅ Sentence transformer model loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                self.model = None
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests for embeddings"""
        if not ML_AVAILABLE:
            self._send_error_response(500, f"ML dependencies not available: {ML_ERROR}")
            return
            
        if not self.model:
            self._send_error_response(500, "Model not loaded")
            return
            
        try:
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/encode':
                self._handle_encode(request_data)
            elif self.path == '/similarity':
                self._handle_similarity(request_data)
            else:
                self._send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            logger.error(traceback.format_exc())
            self._send_error_response(500, str(e))
    
    def do_GET(self):
        """Handle GET requests for health check"""
        if self.path == '/health':
            self._send_json_response({
                "status": "healthy" if (ML_AVAILABLE and self.model) else "unhealthy",
                "ml_available": ML_AVAILABLE,
                "model_loaded": self.model is not None,
                "model_info": "sentence-transformers/all-MiniLM-L6-v2" if self.model else None
            })
        else:
            self._send_error_response(404, "Endpoint not found")
    
    def _handle_encode(self, request_data: Dict[str, Any]):
        """Handle text encoding to embeddings"""
        texts = request_data.get('texts', [])
        if not texts:
            self._send_error_response(400, "No texts provided")
            return
            
        logger.info(f"Encoding {len(texts)} texts")
        embeddings = self.model.encode(texts)
        
        # Convert numpy arrays to lists for JSON serialization
        embeddings_list = embeddings.tolist()
        
        self._send_json_response({
            "embeddings": embeddings_list,
            "count": len(embeddings_list),
            "dimension": len(embeddings_list[0]) if embeddings_list else 0
        })
    
    def _handle_similarity(self, request_data: Dict[str, Any]):
        """Handle similarity computation between texts"""
        text1 = request_data.get('text1')
        text2 = request_data.get('text2')
        
        if not text1 or not text2:
            self._send_error_response(400, "Both text1 and text2 required")
            return
            
        embeddings = self.model.encode([text1, text2])
        
        # Calculate cosine similarity
        from numpy.linalg import norm
        similarity = np.dot(embeddings[0], embeddings[1]) / (norm(embeddings[0]) * norm(embeddings[1]))
        
        self._send_json_response({
            "similarity": float(similarity),
            "text1_length": len(text1),
            "text2_length": len(text2)
        })
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        response = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    def _send_error_response(self, status_code: int, message: str):
        """Send error response"""
        self._send_json_response({"error": message}, status_code)
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(format % args)

def main():
    """Start the sentence transformers service"""
    port = 8888
    
    logger.info(f"Starting Sentence Transformers Service on port {port}")
    logger.info(f"ML Available: {ML_AVAILABLE}")
    
    if not ML_AVAILABLE:
        logger.error(f"❌ ML dependencies not available: {ML_ERROR}")
        logger.info("Service will start but return errors for all ML requests")
    
    try:
        server = HTTPServer(('0.0.0.0', port), SentenceTransformersHandler)
        logger.info(f"✅ Server ready at http://0.0.0.0:{port}")
        logger.info("Available endpoints:")
        logger.info("  POST /encode - Encode texts to embeddings")
        logger.info("  POST /similarity - Calculate text similarity")
        logger.info("  GET /health - Health check")
        
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()