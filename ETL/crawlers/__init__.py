#!/usr/bin/env python3
"""
ETL Data Crawlers - Financial Data Acquisition

Professional data acquisition components for collecting financial information
from multiple sources including SEC Edgar, YFinance, and manual data sources.

Business Purpose:
Systematic data collection with validation, normalization, and quality assurance
to ensure consistent input for downstream processing pipelines.

Key Components:
- Document text extraction and parsing
- Financial metrics calculation and normalization
- Entity recognition and relationship extraction
- Data validation and quality assurance
- Format standardization across data sources
- Incremental processing for efficiency

Processing Pipeline:
Raw Data → Text Extraction → Entity Recognition → Validation → Structured Output

This module bridges the gap between raw data collection and knowledge graph
creation, ensuring high-quality data flows to Neo4j for analysis.

Integration Points:
- Receives input from sec_filing_processor/ and embedding_generator/
- Outputs structured data to loaders/ for graph creation
- Coordinates with schedulers/ for automated processing
"""

__version__ = "1.0.0"

try:
    from .data_validator import DataValidator
    from .entity_extractor import EntityExtractor
    from .financial_normalizer import FinancialNormalizer
    from .format_converter import FormatConverter
    from .text_processor import TextProcessor

    __all__ = [
        "TextProcessor",
        "EntityExtractor",
        "FinancialNormalizer",
        "DataValidator",
        "FormatConverter",
    ]
except ImportError:
    __all__ = []