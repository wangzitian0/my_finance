#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML Module - Machine Learning and AI Utilities
Unified interface for ML operations, templates, and prompt management.

Issue #284: Consolidation of ML operations into single module
- fallback.py: ML fallback implementations (from utils/ml_fallback.py)
- templates.py: Template management (from templates/)
- prompts.py: Prompt management and LLM integration (new)
"""

# ML fallback implementations
from .fallback import (
    NUMPY_AVAILABLE,
    FallbackEmbeddings,
    FallbackLLM,
    FallbackRetrieval,
)

# Prompt management
from .prompts import (
    PromptManager,
    PromptType,
    get_dcf_valuation_prompt,
    get_financial_analysis_prompt,
    get_investment_recommendation_prompt,
    get_sec_filing_prompt,
    prompt_manager,
)

# Template management
from .templates import (
    TemplateManager,
    get_template,
    list_templates,
    render_template,
    template_manager,
)

__all__ = [
    # ML fallback
    "FallbackEmbeddings",
    "FallbackLLM",
    "FallbackRetrieval",
    "NUMPY_AVAILABLE",
    # Prompt management
    "PromptManager",
    "PromptType",
    "prompt_manager",
    "get_financial_analysis_prompt",
    "get_dcf_valuation_prompt",
    "get_sec_filing_prompt",
    "get_investment_recommendation_prompt",
    # Template management
    "TemplateManager",
    "template_manager",
    "get_template",
    "render_template",
    "list_templates",
]
