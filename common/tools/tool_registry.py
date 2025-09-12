#!/usr/bin/env python3
"""
Tool Registry for Issue #256

Manages registration, discovery, and validation of tools in the unified tool system.
Provides centralized access to tool configurations and metadata.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Type

from .base_tool import BaseTool, ToolConfig


class ToolRegistryError(Exception):
    """Tool registry specific errors"""

    pass


class ToolRegistry:
    """
    Central registry for all tools in the system.

    Manages tool discovery, registration, and configuration validation.
    Provides thread-safe access to tool metadata and configurations.
    """

    def __init__(self, tools_directory: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)

        # Tools directory - default to common/tools/
        if tools_directory is None:
            # Assume this file is in common/tools/
            self.tools_directory = Path(__file__).parent
        else:
            self.tools_directory = Path(tools_directory)

        # Registry storage
        self._tool_configs: Dict[str, ToolConfig] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
        self._tool_dependencies: Dict[str, Set[str]] = {}

        # Registry state
        self._initialized = False

        # Auto-discover tools on initialization
        self._discover_tools()

    def _discover_tools(self):
        """Automatically discover and register tools from the tools directory"""
        if not self.tools_directory.exists():
            self.logger.warning(f"Tools directory not found: {self.tools_directory}")
            return

        # Look for tool directories (subdirectories with config.yaml)
        for item in self.tools_directory.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                config_file = item / "config.yaml"
                if config_file.exists():
                    try:
                        self._load_tool_from_directory(item)
                    except Exception as e:
                        self.logger.error(f"Failed to load tool from {item}: {e}")

        self._initialized = True
        self.logger.info(f"Tool registry initialized with {len(self._tool_configs)} tools")

    def _load_tool_from_directory(self, tool_dir: Path):
        """Load a tool configuration and class from its directory"""
        config_file = tool_dir / "config.yaml"
        tool_file = tool_dir / "tool_definition.py"

        # Load configuration
        try:
            config = ToolConfig.from_yaml_file(config_file)
        except Exception as e:
            raise ToolRegistryError(f"Failed to load config from {config_file}: {e}")

        # Register the configuration
        self._tool_configs[config.name] = config

        # Track dependencies
        self._tool_dependencies[config.name] = set(config.dependencies)

        # Try to load tool class if tool_definition.py exists
        if tool_file.exists():
            try:
                self._load_tool_class(tool_file, config.name)
            except Exception as e:
                self.logger.warning(f"Failed to load tool class for {config.name}: {e}")

        self.logger.debug(f"Loaded tool: {config.name} v{config.version}")

    def _load_tool_class(self, tool_file: Path, tool_name: str):
        """Dynamically load tool class from Python file"""
        import importlib.util
        import sys

        # Load module
        spec = importlib.util.spec_from_file_location(f"tool_{tool_name}", tool_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the tool class (should inherit from BaseTool)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseTool) and attr != BaseTool:
                self._tool_classes[tool_name] = attr
                break
        else:
            raise ToolRegistryError(f"No BaseTool subclass found in {tool_file}")

    def register_tool(self, config: ToolConfig, tool_class: Optional[Type[BaseTool]] = None):
        """
        Manually register a tool configuration and optional implementation class.

        Args:
            config: Tool configuration
            tool_class: Optional tool implementation class
        """
        if config.name in self._tool_configs:
            self.logger.warning(f"Tool '{config.name}' already registered, overriding")

        self._tool_configs[config.name] = config
        self._tool_dependencies[config.name] = set(config.dependencies)

        if tool_class:
            self._tool_classes[config.name] = tool_class

        self.logger.info(f"Registered tool: {config.name} v{config.version}")

    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """Get configuration for a specific tool"""
        return self._tool_configs.get(tool_name)

    def get_tool_class(self, tool_name: str) -> Optional[Type[BaseTool]]:
        """Get implementation class for a specific tool"""
        return self._tool_classes.get(tool_name)

    def list_available_tools(self) -> List[str]:
        """Get list of all available tool names"""
        return list(self._tool_configs.keys())

    def get_tool_info(self, tool_name: str) -> Dict[str, any]:
        """Get detailed information about a tool"""
        config = self.get_tool_config(tool_name)
        if not config:
            return {}

        has_implementation = tool_name in self._tool_classes
        dependencies = self._tool_dependencies.get(tool_name, set())

        return {
            "name": config.name,
            "version": config.version,
            "description": config.description,
            "has_implementation": has_implementation,
            "dependencies": list(dependencies),
            "input_layers": config.input_layers,
            "output_layers": config.output_layers,
            "required_directories": config.required_directories,
            "optional_directories": config.optional_directories,
        }

    def validate_tool_structure(self, tool_name: str) -> bool:
        """
        Validate that a tool has proper structure and configuration.

        Args:
            tool_name: Name of tool to validate

        Returns:
            True if tool structure is valid, False otherwise
        """
        config = self.get_tool_config(tool_name)
        if not config:
            self.logger.error(f"Tool '{tool_name}' not found in registry")
            return False

        # Basic configuration validation
        if not config.name or not config.version:
            self.logger.error(f"Tool '{tool_name}' missing required fields")
            return False

        # Validate dependencies exist
        for dep in config.dependencies:
            if dep not in self._tool_configs:
                self.logger.error(f"Tool '{tool_name}' has unmet dependency: {dep}")
                return False

        # Check for circular dependencies
        if self._has_circular_dependency(tool_name):
            self.logger.error(f"Tool '{tool_name}' has circular dependencies")
            return False

        return True

    def _has_circular_dependency(self, tool_name: str, visited: Optional[Set[str]] = None) -> bool:
        """Check for circular dependencies in tool chain"""
        if visited is None:
            visited = set()

        if tool_name in visited:
            return True

        visited.add(tool_name)

        dependencies = self._tool_dependencies.get(tool_name, set())
        for dep in dependencies:
            if self._has_circular_dependency(dep, visited.copy()):
                return True

        return False

    def get_dependency_order(self, tools: List[str]) -> List[str]:
        """
        Get tools sorted in dependency order (dependencies first).

        Args:
            tools: List of tool names to order

        Returns:
            Tools sorted in dependency execution order

        Raises:
            ToolRegistryError: If circular dependencies detected
        """
        ordered = []
        in_progress = set()
        completed = set()

        def visit(tool_name: str):
            if tool_name in completed:
                return
            if tool_name in in_progress:
                raise ToolRegistryError(f"Circular dependency detected involving '{tool_name}'")

            in_progress.add(tool_name)

            # Visit dependencies first
            dependencies = self._tool_dependencies.get(tool_name, set())
            for dep in dependencies:
                if dep in tools:  # Only consider dependencies that are in our tool list
                    visit(dep)

            in_progress.remove(tool_name)
            completed.add(tool_name)
            ordered.append(tool_name)

        # Visit all tools
        for tool in tools:
            visit(tool)

        return ordered

    def create_tool_instance(self, tool_name: str) -> Optional[BaseTool]:
        """
        Create an instance of a tool if implementation is available.

        Args:
            tool_name: Name of tool to instantiate

        Returns:
            Tool instance or None if not available
        """
        config = self.get_tool_config(tool_name)
        tool_class = self.get_tool_class(tool_name)

        if not config:
            self.logger.error(f"Tool configuration not found: {tool_name}")
            return None

        if not tool_class:
            self.logger.error(f"Tool implementation not found: {tool_name}")
            return None

        try:
            return tool_class(config)
        except Exception as e:
            self.logger.error(f"Failed to create tool instance '{tool_name}': {e}")
            return None

    def get_registry_stats(self) -> Dict[str, any]:
        """Get statistics about the tool registry"""
        total_tools = len(self._tool_configs)
        implemented_tools = len(self._tool_classes)

        # Count tools by category (based on output layers)
        layer_counts = {}
        for config in self._tool_configs.values():
            for layer in config.output_layers:
                layer_counts[layer] = layer_counts.get(layer, 0) + 1

        return {
            "total_tools": total_tools,
            "implemented_tools": implemented_tools,
            "config_only_tools": total_tools - implemented_tools,
            "tools_by_output_layer": layer_counts,
            "initialized": self._initialized,
        }


# Global registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_tool(config: ToolConfig, tool_class: Optional[Type[BaseTool]] = None):
    """Register a tool in the global registry"""
    registry = get_tool_registry()
    registry.register_tool(config, tool_class)


def get_tool_config(tool_name: str) -> Optional[ToolConfig]:
    """Get tool configuration from global registry"""
    registry = get_tool_registry()
    return registry.get_tool_config(tool_name)


def list_available_tools() -> List[str]:
    """Get list of all available tools from global registry"""
    registry = get_tool_registry()
    return registry.list_available_tools()


def validate_tool_structure(tool_name: str) -> bool:
    """Validate tool structure using global registry"""
    registry = get_tool_registry()
    return registry.validate_tool_structure(tool_name)
