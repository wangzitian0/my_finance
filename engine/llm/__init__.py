#!/usr/bin/env python3
"""
LLM Integration and Prompt Management

Language model integration for the Graph-RAG investment analysis engine.
Handles prompt templates, model inference, and structured output generation
for investment analysis tasks.

Business Purpose:
Transform retrieved graph and vector data into structured investment insights,
valuations, and recommendations using language models.

Key Components:
- Prompt template management for financial analysis
- Model inference and response handling  
- Structured output parsing (JSON, financial metrics)
- Context window management for large document analysis
- Model routing (GPT-4, DeepSeek, local models)

Integration Points:
- Uses templates from common/templates/
- Retrieves context from graph_rag/ module
- Generates inputs for strategy/ calculations
- Produces content for reports/ generation

Issue #256: Centralized LLM operations in engine/ to support both strategy
generation and report creation from a single, consistent interface.
"""

__version__ = "1.0.0"

try:
    from .prompt_manager import PromptManager
    from .model_interface import ModelInterface
    from .output_parser import OutputParser
    from .context_manager import ContextManager

    __all__ = [
        "PromptManager",
        "ModelInterface",
        "OutputParser", 
        "ContextManager"
    ]
except ImportError:
    __all__ = []