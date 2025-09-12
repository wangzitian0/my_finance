#!/usr/bin/env python3
"""
Tool Manager for Issue #256

Manages tool workspace creation and execution in the build_data/timestamp/tool_x structure.
Integrates with DirectoryManager to ensure SSOT compliance for path management.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..core.directory_manager import DataLayer, directory_manager
from .base_tool import BaseTool, ToolConfig, ToolExecutionContext, ToolStatus
from .tool_registry import get_tool_registry


class ToolManagerError(Exception):
    """Tool manager specific errors"""

    pass


class ToolManager:
    """
    Manages tool workspaces and execution in the build_data structure.

    Implements the core requirement: "define build_data/timestamp/tool_x using common/tool_x"
    by creating timestamped tool workspaces based on tool configurations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registry = get_tool_registry()

        # Active workspaces tracking
        self._active_workspaces: Dict[str, Path] = {}
        self._workspace_metadata: Dict[str, Dict] = {}

    def get_tool_build_path(self, tool_name: str, timestamp: Optional[str] = None) -> Path:
        """
        Get the build path for a tool's workspace following the pattern:
        build_data/timestamp/tool_x

        Args:
            tool_name: Name of the tool
            timestamp: Optional timestamp (YYYYMMDD_HHMMSS), generates if not provided

        Returns:
            Path to tool's build workspace
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Use directory_manager for SSOT path resolution
        build_data_root = directory_manager.get_data_root()
        tool_workspace = build_data_root / timestamp / tool_name

        return tool_workspace

    def create_tool_workspace(
        self, tool_name: str, timestamp: Optional[str] = None
    ) -> Optional[ToolExecutionContext]:
        """
        Create a tool workspace with the required directory structure.

        Args:
            tool_name: Name of the tool to create workspace for
            timestamp: Optional timestamp for workspace

        Returns:
            ToolExecutionContext for the created workspace, None if failed
        """
        # Get tool configuration
        config = self.registry.get_tool_config(tool_name)
        if not config:
            self.logger.error(f"Tool '{tool_name}' not found in registry")
            return None

        # Generate workspace path
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        workspace_path = self.get_tool_build_path(tool_name, timestamp)

        try:
            # Create base workspace directory
            workspace_path.mkdir(parents=True, exist_ok=True)

            # Create required directories
            for dir_name in config.required_directories:
                dir_path = workspace_path / dir_name
                dir_path.mkdir(exist_ok=True)
                self.logger.debug(f"Created required directory: {dir_path}")

            # Create optional directories
            for dir_name in config.optional_directories:
                dir_path = workspace_path / dir_name
                dir_path.mkdir(exist_ok=True)
                self.logger.debug(f"Created optional directory: {dir_path}")

            # Set up input/output path mappings using directory_manager
            input_paths = {}
            output_paths = {}

            for layer_name in config.input_layers:
                try:
                    layer_enum = DataLayer(layer_name)
                    layer_path = directory_manager.get_layer_path(layer_enum, timestamp)
                    input_paths[layer_name] = layer_path
                except ValueError:
                    self.logger.warning(
                        f"Invalid input layer '{layer_name}' for tool '{tool_name}'"
                    )

            for layer_name in config.output_layers:
                try:
                    layer_enum = DataLayer(layer_name)
                    layer_path = directory_manager.get_layer_path(layer_enum, timestamp)
                    output_paths[layer_name] = layer_path
                    # Ensure output layer directories exist
                    layer_path.mkdir(parents=True, exist_ok=True)
                except ValueError:
                    self.logger.warning(
                        f"Invalid output layer '{layer_name}' for tool '{tool_name}'"
                    )

            # Create execution context
            context = ToolExecutionContext(
                tool_name=tool_name,
                timestamp=timestamp,
                workspace_path=workspace_path,
                input_paths=input_paths,
                output_paths=output_paths,
            )

            # Set up logging for this tool
            log_dir = directory_manager.get_logs_path()
            log_dir.mkdir(parents=True, exist_ok=True)
            context.log_file = log_dir / f"tool_{tool_name}_{timestamp}.log"

            # Track active workspace
            workspace_key = f"{tool_name}_{timestamp}"
            self._active_workspaces[workspace_key] = workspace_path
            self._workspace_metadata[workspace_key] = {
                "tool_name": tool_name,
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "status": ToolStatus.PENDING.value,
            }

            self.logger.info(f"Created workspace for tool '{tool_name}' at: {workspace_path}")
            context.add_message(f"Workspace created at {workspace_path}")

            return context

        except Exception as e:
            self.logger.error(f"Failed to create workspace for tool '{tool_name}': {e}")
            return None

    def cleanup_tool_workspace(self, context: ToolExecutionContext, remove_workspace: bool = False):
        """
        Clean up a tool workspace after execution.

        Args:
            context: Tool execution context
            remove_workspace: Whether to remove the entire workspace directory
        """
        workspace_key = f"{context.tool_name}_{context.timestamp}"

        try:
            # Clean up temporary files
            for temp_path in context.temp_paths:
                if temp_path.exists():
                    if temp_path.is_file():
                        temp_path.unlink()
                    elif temp_path.is_dir():
                        shutil.rmtree(temp_path)
                    self.logger.debug(f"Cleaned up temp path: {temp_path}")

            # Optionally remove entire workspace
            if remove_workspace and context.workspace_path.exists():
                shutil.rmtree(context.workspace_path)
                self.logger.info(f"Removed workspace: {context.workspace_path}")
                context.add_message("Workspace removed")

            # Update metadata
            if workspace_key in self._workspace_metadata:
                self._workspace_metadata[workspace_key][
                    "cleaned_up_at"
                ] = datetime.now().isoformat()
                self._workspace_metadata[workspace_key]["removed"] = remove_workspace

            # Remove from active tracking if workspace removed
            if remove_workspace and workspace_key in self._active_workspaces:
                del self._active_workspaces[workspace_key]

        except Exception as e:
            self.logger.error(f"Failed to cleanup workspace for '{context.tool_name}': {e}")

    def execute_tool(
        self, tool_name: str, timestamp: Optional[str] = None, cleanup_on_completion: bool = False
    ) -> bool:
        """
        Execute a tool with full workspace management.

        Args:
            tool_name: Name of tool to execute
            timestamp: Optional timestamp for workspace
            cleanup_on_completion: Whether to cleanup workspace after execution

        Returns:
            True if tool executed successfully, False otherwise
        """
        # Create tool instance
        tool_instance = self.registry.create_tool_instance(tool_name)
        if not tool_instance:
            self.logger.error(f"Failed to create instance of tool '{tool_name}'")
            return False

        # Create workspace
        context = self.create_tool_workspace(tool_name, timestamp)
        if not context:
            self.logger.error(f"Failed to create workspace for tool '{tool_name}'")
            return False

        try:
            # Execute tool
            success = tool_instance.run(context)

            # Update workspace metadata
            workspace_key = f"{tool_name}_{context.timestamp}"
            if workspace_key in self._workspace_metadata:
                self._workspace_metadata[workspace_key]["status"] = context.status.value
                self._workspace_metadata[workspace_key]["completed_at"] = datetime.now().isoformat()
                self._workspace_metadata[workspace_key]["success"] = success

            return success

        finally:
            # Always cleanup if requested
            if cleanup_on_completion:
                self.cleanup_tool_workspace(context, remove_workspace=not success)

    def list_active_workspaces(self) -> Dict[str, Dict]:
        """Get information about all active tool workspaces"""
        return self._workspace_metadata.copy()

    def get_workspace_info(self, tool_name: str, timestamp: str) -> Optional[Dict]:
        """Get information about a specific workspace"""
        workspace_key = f"{tool_name}_{timestamp}"
        return self._workspace_metadata.get(workspace_key)

    def validate_tool_workspace(self, tool_name: str, workspace_path: Path) -> bool:
        """
        Validate that a tool workspace has the correct structure.

        Args:
            tool_name: Name of the tool
            workspace_path: Path to workspace to validate

        Returns:
            True if workspace structure is valid, False otherwise
        """
        config = self.registry.get_tool_config(tool_name)
        if not config:
            return False

        # Check that workspace directory exists
        if not workspace_path.exists() or not workspace_path.is_dir():
            self.logger.error(f"Workspace directory not found: {workspace_path}")
            return False

        # Check required directories
        for dir_name in config.required_directories:
            dir_path = workspace_path / dir_name
            if not dir_path.exists() or not dir_path.is_dir():
                self.logger.error(f"Required directory missing: {dir_path}")
                return False

        return True

    def get_tool_workspaces_by_timestamp(self, timestamp: str) -> List[str]:
        """
        Get all tool workspaces for a specific timestamp.

        Args:
            timestamp: Timestamp to search for

        Returns:
            List of tool names with workspaces at that timestamp
        """
        build_data_root = directory_manager.get_data_root()
        timestamp_dir = build_data_root / timestamp

        if not timestamp_dir.exists():
            return []

        tool_workspaces = []
        for item in timestamp_dir.iterdir():
            if item.is_dir():
                # Check if this is a valid tool workspace
                tool_name = item.name
                if self.validate_tool_workspace(tool_name, item):
                    tool_workspaces.append(tool_name)

        return tool_workspaces

    def cleanup_old_workspaces(self, retention_days: int = 7) -> int:
        """
        Clean up old tool workspaces based on retention policy.

        Args:
            retention_days: Number of days to retain workspaces

        Returns:
            Number of workspaces cleaned up
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        build_data_root = directory_manager.get_data_root()

        if not build_data_root.exists():
            return 0

        cleaned_count = 0

        for timestamp_dir in build_data_root.iterdir():
            if timestamp_dir.is_dir() and len(timestamp_dir.name) == 15:  # YYYYMMDD_HHMMSS
                try:
                    # Parse timestamp
                    dir_timestamp = datetime.strptime(timestamp_dir.name, "%Y%m%d_%H%M%S")

                    if dir_timestamp < cutoff_date:
                        # Clean up this timestamp directory
                        shutil.rmtree(timestamp_dir)
                        cleaned_count += 1
                        self.logger.info(f"Cleaned up old workspace directory: {timestamp_dir}")

                        # Remove from tracking
                        keys_to_remove = [
                            k
                            for k in self._active_workspaces.keys()
                            if k.endswith(f"_{timestamp_dir.name}")
                        ]
                        for key in keys_to_remove:
                            del self._active_workspaces[key]
                            if key in self._workspace_metadata:
                                del self._workspace_metadata[key]

                except ValueError:
                    # Skip directories that don't match timestamp format
                    continue
                except Exception as e:
                    self.logger.error(f"Failed to clean up {timestamp_dir}: {e}")

        return cleaned_count


# Global tool manager instance
_global_tool_manager: Optional[ToolManager] = None


def get_tool_manager() -> ToolManager:
    """Get the global tool manager instance"""
    global _global_tool_manager
    if _global_tool_manager is None:
        _global_tool_manager = ToolManager()
    return _global_tool_manager


def get_tool_build_path(tool_name: str, timestamp: Optional[str] = None) -> Path:
    """Get build path for a tool using global tool manager"""
    manager = get_tool_manager()
    return manager.get_tool_build_path(tool_name, timestamp)


def create_tool_workspace(
    tool_name: str, timestamp: Optional[str] = None
) -> Optional[ToolExecutionContext]:
    """Create tool workspace using global tool manager"""
    manager = get_tool_manager()
    return manager.create_tool_workspace(tool_name, timestamp)


def cleanup_tool_workspace(context: ToolExecutionContext, remove_workspace: bool = False):
    """Cleanup tool workspace using global tool manager"""
    manager = get_tool_manager()
    manager.cleanup_tool_workspace(context, remove_workspace)
