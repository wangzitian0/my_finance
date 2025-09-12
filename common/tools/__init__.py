#!/usr/bin/env python3
"""
Tool Definition System for Issue #256

This module implements the unified tool definition system where:
- common/tools/tool_x defines tool configuration and requirements
- build_data/timestamp/tool_x directories are dynamically created based on tool definitions
- Tools provide a standardized interface for data processing pipelines

Core Concept:
"Define build_data/timestamp/tool_x using common/tool_x"

Each tool in common/tools/ defines:
1. Tool metadata and description
2. Required build_data directory structure
3. Input/output specifications
4. Dependencies and prerequisites
5. Validation rules and quality checks
"""

from .base_tool import (
    BaseTool,
    ToolConfig,
    ToolExecutionContext,
    ToolStatus,
)
from .tool_manager import (
    ToolManager,
    cleanup_tool_workspace,
    create_tool_workspace,
    get_tool_build_path,
    get_tool_manager,
)
from .tool_registry import (
    ToolRegistry,
    get_tool_config,
    get_tool_registry,
    list_available_tools,
    register_tool,
    validate_tool_structure,
)

__all__ = [
    # Tool registry
    "ToolRegistry",
    "get_tool_registry",
    "register_tool",
    "get_tool_config",
    "list_available_tools",
    "validate_tool_structure",
    # Base tool classes
    "BaseTool",
    "ToolConfig",
    "ToolStatus",
    "ToolExecutionContext",
    # Tool management
    "ToolManager",
    "get_tool_build_path",
    "create_tool_workspace",
    "cleanup_tool_workspace",
    "get_tool_manager",
]
