#!/usr/bin/env python3
"""
ETL Scheduling and Orchestration

Automated scheduling system for ETL pipelines, managing data collection,
processing, and Neo4j loading operations.

Business Purpose:
Ensure continuous, reliable data flow from sources (SEC Edgar, YFinance)
through processing pipelines to Neo4j knowledge graph for analysis.

Key Components:
- Daily data collection schedules
- Incremental processing workflows  
- Error handling and retry logic
- Data quality monitoring
- Pipeline dependency management
- Resource usage optimization

Scheduling Features:
- CRON-based scheduling for regular updates
- Event-driven triggers for new SEC filings
- Market hours awareness for YFinance data
- Backfill capabilities for missed data
- Parallel processing for efficiency
- Health checks and monitoring

Data Pipeline Flow:
Sources → Schedulers → Processors → Neo4j Loader → Knowledge Graph

This module ensures that the engine/ always has fresh, complete data
available in the Neo4j knowledge graph for analysis.
"""

__version__ = "1.0.0"

try:
    from .scheduler_manager import SchedulerManager
    from .pipeline_orchestrator import PipelineOrchestrator
    from .task_queue import TaskQueue
    from .monitoring import PipelineMonitor
    from .retry_handler import RetryHandler

    __all__ = [
        "SchedulerManager",
        "PipelineOrchestrator", 
        "TaskQueue",
        "PipelineMonitor",
        "RetryHandler"
    ]
except ImportError:
    __all__ = []