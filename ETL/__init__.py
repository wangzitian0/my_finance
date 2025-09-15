"""ETL (Extract, Transform, Load) data processing pipeline

This module handles all data extraction, transformation, and loading operations
including SEC filing processing, embedding generation, and data ingestion.

Submodules:
- embedding_generator: Vector embedding generation from processed documents
- sec_filing_processor: SEC filing document processing and parsing

Consolidation: As part of Issue #256, this module may absorb graph_rag/
functionality as both are data processing related.
"""

__version__ = "1.0.0"

# Import submodules when available
try:
    from . import embedding_generator
except ImportError:
    embedding_generator = None

try:
    from . import sec_filing_processor  
except ImportError:
    sec_filing_processor = None

__all__ = [
    "embedding_generator",
    "sec_filing_processor",
]