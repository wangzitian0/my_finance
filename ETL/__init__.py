"""ETL (Extract, Transform, Load) Data Processing Pipeline

Complete data pipeline handling extraction, transformation, and loading of
financial data from raw sources to Neo4j knowledge graph.

Business Purpose:
Transform raw data sources into a clean, structured Neo4j knowledge graph
that enables sophisticated Graph-RAG investment analysis.

Data Flow:
Raw Data Sources → Processing → Clean Neo4j Graph

This module encompasses the entire data ingestion pipeline, from initial
data collection through final knowledge graph creation.

Enhanced Structure (Issue #256):
- sec_filing_processor/: SEC Edgar document processing
- embedding_generator/: Vector embedding creation
- crawlers/: Data acquisition and transformation (professional terminology)
- schedulers/: Automated pipeline orchestration
- loaders/: Knowledge graph population (professional terminology)

Integration:
- Inputs: SEC Edgar, YFinance, manual data sources
- Outputs: Structured Neo4j knowledge graph
- Consumers: engine/ module for Graph-RAG analysis
"""

__version__ = "1.0.0"

# Import all ETL components
try:
    from . import sec_filing_processor
except ImportError:
    sec_filing_processor = None

try:
    from . import embedding_generator
except ImportError:
    embedding_generator = None

try:
    from . import crawlers
except ImportError:
    crawlers = None

try:
    from . import schedulers
except ImportError:
    schedulers = None

try:
    from . import loaders
except ImportError:
    loaders = None

__all__ = [
    "sec_filing_processor",
    "embedding_generator",
    "crawlers",
    "schedulers",
    "loaders",
]
