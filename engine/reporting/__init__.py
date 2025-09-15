#!/usr/bin/env python3
"""
Professional Investment Reporting

Investment report generation and formatting for professional-grade investment
analysis presentations with regulatory compliance and audit trails.

Business Purpose:
Generate comprehensive investment reports with SEC citation support,
risk analysis, and regulatory disclosure integration for institutional use.

Key Components:
- Professional report templates and formatting
- SEC filing citation and reference management
- Investment thesis presentation frameworks
- Risk disclosure and compliance integration
- Multi-format output (PDF, HTML, Markdown)
- Audit trail and version control

Reporting Pipeline:
Investment Analysis + Valuation → Report Generation → Professional Presentation

This module ensures all investment analysis is presented in professional,
compliant, and actionable formats suitable for institutional decision-making.

Integration Points:
- Inputs: Investment recommendations from valuation/
- Processing: Professional report generation
- Outputs: Client-ready investment reports and presentations
"""

__version__ = "1.0.0"

try:
    from .audit_logger import AuditLogger
    from .citation_manager import CitationManager
    from .format_converter import FormatConverter
    from .report_generator import ReportGenerator
    from .template_manager import TemplateManager

    __all__ = [
        "ReportGenerator",
        "TemplateManager",
        "CitationManager",
        "FormatConverter",
        "AuditLogger",
    ]
except ImportError:
    __all__ = []
