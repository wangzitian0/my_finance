#!/usr/bin/env python3
"""
SEC Filing Processor Tool

Maps ETL functionality to the unified tool system.
Processes SEC Edgar filings and creates structured data for analysis.
"""

from .tool_definition import SECFilingProcessor

__all__ = ["SECFilingProcessor"]