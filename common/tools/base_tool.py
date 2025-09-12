#!/usr/bin/env python3
"""
Base Tool Definition for Issue #256

Provides the foundational classes and interfaces for the unified tool system.
Each tool inherits from BaseTool and defines its specific requirements.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

try:
    import yaml
except ImportError:
    yaml = None


class ToolStatus(Enum):
    """Tool execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ToolConfig:
    """Tool configuration structure"""

    name: str
    version: str
    description: str

    # Build data structure requirements
    required_directories: List[str] = field(default_factory=list)
    optional_directories: List[str] = field(default_factory=list)

    # Input/output specifications
    input_layers: List[str] = field(default_factory=list)  # DataLayer names
    output_layers: List[str] = field(default_factory=list)  # DataLayer names

    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # Other tools
    prerequisites: List[str] = field(default_factory=list)  # System requirements

    # Configuration overrides
    config_overrides: Dict[str, Any] = field(default_factory=dict)

    # Validation and quality rules
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    quality_checks: List[str] = field(default_factory=list)

    @classmethod
    def from_yaml_file(cls, config_path: Path) -> "ToolConfig":
        """Load configuration from YAML file"""
        if yaml is None:
            raise ImportError("PyYAML is required for YAML configuration files")

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolConfig":
        """Create configuration from dictionary"""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "required_directories": self.required_directories,
            "optional_directories": self.optional_directories,
            "input_layers": self.input_layers,
            "output_layers": self.output_layers,
            "dependencies": self.dependencies,
            "prerequisites": self.prerequisites,
            "config_overrides": self.config_overrides,
            "validation_rules": self.validation_rules,
            "quality_checks": self.quality_checks,
        }


@dataclass
class ToolExecutionContext:
    """Context information for tool execution"""

    tool_name: str
    timestamp: str
    workspace_path: Path

    # Execution metadata
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: ToolStatus = ToolStatus.PENDING

    # Resource tracking
    input_paths: Dict[str, Path] = field(default_factory=dict)
    output_paths: Dict[str, Path] = field(default_factory=dict)
    temp_paths: Set[Path] = field(default_factory=set)

    # Logging and monitoring
    log_file: Optional[Path] = None
    progress: float = 0.0
    messages: List[str] = field(default_factory=list)

    def add_message(self, message: str, level: str = "INFO"):
        """Add execution message with timestamp"""
        timestamp = datetime.now().isoformat()
        self.messages.append(f"[{timestamp}] {level}: {message}")

        # Also log to standard logger if available
        logger = logging.getLogger(f"tool.{self.tool_name}")
        getattr(logger, level.lower(), logger.info)(message)

    def mark_started(self):
        """Mark tool execution as started"""
        self.start_time = datetime.now()
        self.status = ToolStatus.RUNNING
        self.add_message(f"Tool '{self.tool_name}' execution started")

    def mark_completed(self):
        """Mark tool execution as completed"""
        self.end_time = datetime.now()
        self.status = ToolStatus.COMPLETED
        self.progress = 1.0

        duration = self.end_time - self.start_time if self.start_time else None
        duration_str = f" in {duration}" if duration else ""
        self.add_message(f"Tool '{self.tool_name}' execution completed{duration_str}")

    def mark_failed(self, error_message: str):
        """Mark tool execution as failed"""
        self.end_time = datetime.now()
        self.status = ToolStatus.FAILED
        self.add_message(f"Tool '{self.tool_name}' execution failed: {error_message}", "ERROR")

    def update_progress(self, progress: float, message: Optional[str] = None):
        """Update execution progress"""
        self.progress = max(0.0, min(1.0, progress))
        if message:
            self.add_message(f"Progress: {progress:.1%} - {message}")


class BaseTool(ABC):
    """
    Abstract base class for all tools in the unified tool system.

    Each tool defines how its build_data/timestamp/tool_x structure should be created
    and managed based on its common/tools/tool_x configuration.
    """

    def __init__(self, config: ToolConfig):
        self.config = config
        self.logger = logging.getLogger(f"tool.{config.name}")

    @property
    def name(self) -> str:
        """Tool name"""
        return self.config.name

    @property
    def version(self) -> str:
        """Tool version"""
        return self.config.version

    @abstractmethod
    def validate_prerequisites(self, context: ToolExecutionContext) -> bool:
        """
        Validate that all prerequisites for tool execution are met.

        Args:
            context: Tool execution context

        Returns:
            True if prerequisites are satisfied, False otherwise
        """
        pass

    @abstractmethod
    def create_workspace_structure(self, context: ToolExecutionContext) -> bool:
        """
        Create the required directory structure for this tool in build_data/timestamp/tool_x.

        Args:
            context: Tool execution context with workspace path

        Returns:
            True if structure created successfully, False otherwise
        """
        pass

    @abstractmethod
    def execute(self, context: ToolExecutionContext) -> bool:
        """
        Execute the main tool functionality.

        Args:
            context: Tool execution context

        Returns:
            True if execution successful, False otherwise
        """
        pass

    @abstractmethod
    def validate_outputs(self, context: ToolExecutionContext) -> bool:
        """
        Validate that tool outputs meet quality requirements.

        Args:
            context: Tool execution context

        Returns:
            True if outputs are valid, False otherwise
        """
        pass

    def cleanup(self, context: ToolExecutionContext):
        """
        Clean up temporary resources after tool execution.

        Args:
            context: Tool execution context
        """
        # Default cleanup implementation
        for temp_path in context.temp_paths:
            try:
                if temp_path.exists():
                    if temp_path.is_file():
                        temp_path.unlink()
                    elif temp_path.is_dir():
                        import shutil

                        shutil.rmtree(temp_path)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {temp_path}: {e}")

        context.temp_paths.clear()

    def run(self, context: ToolExecutionContext) -> bool:
        """
        Complete tool execution workflow with error handling and monitoring.

        Args:
            context: Tool execution context

        Returns:
            True if tool execution successful, False otherwise
        """
        try:
            context.mark_started()

            # Phase 1: Validate prerequisites
            context.update_progress(0.1, "Validating prerequisites")
            if not self.validate_prerequisites(context):
                context.mark_failed("Prerequisites validation failed")
                return False

            # Phase 2: Create workspace structure
            context.update_progress(0.2, "Creating workspace structure")
            if not self.create_workspace_structure(context):
                context.mark_failed("Workspace structure creation failed")
                return False

            # Phase 3: Execute main functionality
            context.update_progress(0.3, "Executing tool functionality")
            if not self.execute(context):
                context.mark_failed("Tool execution failed")
                return False

            # Phase 4: Validate outputs
            context.update_progress(0.9, "Validating outputs")
            if not self.validate_outputs(context):
                context.mark_failed("Output validation failed")
                return False

            # Phase 5: Complete
            context.mark_completed()
            return True

        except Exception as e:
            context.mark_failed(f"Unexpected error: {e}")
            self.logger.exception(f"Tool '{self.name}' execution failed with exception")
            return False

        finally:
            # Always cleanup, regardless of success/failure
            try:
                context.update_progress(1.0, "Cleaning up resources")
                self.cleanup(context)
            except Exception as e:
                self.logger.warning(f"Cleanup failed for tool '{self.name}': {e}")

    def get_required_paths(self, workspace_path: Path) -> Dict[str, Path]:
        """
        Get the required directory paths for this tool.

        Args:
            workspace_path: Base workspace path (build_data/timestamp/tool_x)

        Returns:
            Dictionary mapping directory names to paths
        """
        paths = {}

        for dir_name in self.config.required_directories:
            paths[dir_name] = workspace_path / dir_name

        for dir_name in self.config.optional_directories:
            paths[dir_name] = workspace_path / dir_name

        return paths

    def __str__(self) -> str:
        return f"Tool(name='{self.name}', version='{self.version}')"

    def __repr__(self) -> str:
        return self.__str__()
