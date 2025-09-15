#!/usr/bin/env python3
"""
Investment Reports Generation Module

Report generation and formatting for investment analysis results.
Creates structured reports, dashboards, and visualizations from strategy
calculations and Graph-RAG insights.

Business Purpose:
Package investment strategies, valuations, and recommendations into 
professional reports for investment decision making.

Key Components:
- Report template management
- Financial charts and visualizations
- Executive summary generation
- Detailed analysis formatting
- Export capabilities (PDF, HTML, JSON)
- Dashboard data preparation

Data Flow:
Strategy Results + Graph-RAG Insights → Formatted Reports → Stakeholder Consumption

This module takes the output from strategy/ calculations and formats them
into consumable reports using templates and visualization tools.

Integration Points:
- Uses strategy/ module outputs as data sources
- Leverages llm/ module for narrative generation
- Accesses graph_rag/ for supporting evidence
- Outputs to build_data/stage_04_query_results/ for consumption

Issue #256: Consolidates report generation logic to support the complete
business flow from data to actionable investment reports.
"""

__version__ = "1.0.0"

try:
    from .report_generator import ReportGenerator
    from .chart_builder import ChartBuilder
    from .template_manager import TemplateManager
    from .export_manager import ExportManager
    from .dashboard_builder import DashboardBuilder

    __all__ = [
        "ReportGenerator",
        "ChartBuilder", 
        "TemplateManager",
        "ExportManager",
        "DashboardBuilder"
    ]
except ImportError:
    __all__ = []