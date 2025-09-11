#!/usr/bin/env python3
"""
Claude Code Hook Manager for Comprehensive Logging Integration

This module implements comprehensive logging hooks for Claude Code interactions
to capture thinking chains, tool logs, context, and agent interactions for
improved monitoring and debugging capabilities.

Integrates with ExecutionMonitor for unified logging architecture.
GitHub Issue #214: Implement Claude Code hooks for comprehensive logging integration
"""

import json
import logging
import re
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add common directory to path for imports
_common_dir = Path(__file__).parent.parent
if str(_common_dir) not in sys.path:
    sys.path.insert(0, str(_common_dir))

from common.core.config_manager import config_manager
from common.core.directory_manager import directory_manager
from common.monitoring.execution_monitor import ExecutionMonitor, ExecutionResult


@dataclass
class HookEvent:
    """Base structure for all hook events."""

    event_id: str
    session_id: str
    timestamp: str
    event_type: str
    metadata: Dict[str, Any]


@dataclass
class UserPromptEvent(HookEvent):
    """User prompt submission event."""

    prompt_content: str
    sanitized_content: str
    content_length: int
    user_context: Optional[Dict[str, Any]] = None


@dataclass
class ToolInvocationEvent(HookEvent):
    """Tool invocation event."""

    tool_name: str
    tool_parameters: Dict[str, Any]
    sanitized_parameters: Dict[str, Any]
    execution_start: str
    execution_end: Optional[str] = None
    execution_time_ms: Optional[int] = None
    tool_response: Optional[Any] = None
    sanitized_response: Optional[Any] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None


@dataclass
class AIResponseEvent(HookEvent):
    """AI response event."""

    thinking_process: Optional[str]
    sanitized_thinking: Optional[str]
    final_response: str
    sanitized_response: str
    response_length: int
    thinking_length: Optional[int] = None
    generation_time_ms: Optional[int] = None


@dataclass
class ErrorEvent(HookEvent):
    """Error handling event."""

    error_type: str
    error_message: str
    stack_trace: Optional[str]
    context: Dict[str, Any]
    recovery_action: Optional[str] = None
    recovery_successful: Optional[bool] = None


class ClaudeHookManager:
    """
    Claude Code Hook Manager for comprehensive logging integration.

    Provides centralized management of all Claude Code interaction logging
    with integration to ExecutionMonitor and following SSOT principles.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize Claude Hook Manager."""
        self.config_path = config_path or (
            directory_manager.get_config_path() / "monitoring" / "claude_hooks.json"
        )
        try:
            self.config = config_manager.get_config("claude_hooks")
        except Exception:
            self.config = self._get_default_config()

        # Setup logging directory following SSOT principles
        self.logs_directory = directory_manager.get_logs_path() / "claude_hooks"
        self.logs_directory.mkdir(parents=True, exist_ok=True)

        # Initialize execution monitor for integration
        self.execution_monitor = ExecutionMonitor(self.logs_directory.parent)

        # Setup logging
        self._setup_logging()

        # Session management
        self.current_session_id = None
        self.session_start_time = None
        self.event_buffer = []

        # Performance tracking
        self.stats = {
            "events_captured": 0,
            "events_sanitized": 0,
            "sessions_tracked": 0,
            "errors_logged": 0,
        }

        self.logger.info("Claude Hook Manager initialized successfully")

    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration when config file is missing."""
        return {
            "version": "1.0.0",
            "enabled": True,
            "hooks": {
                "user_prompt_submit": {"enabled": True, "capture_level": "full", "sanitize": True},
                "tool_invocation": {
                    "enabled": True,
                    "capture_requests": True,
                    "capture_responses": True,
                },
                "ai_response": {"enabled": True, "capture_thinking": True, "capture_final": True},
                "error_handling": {
                    "enabled": True,
                    "capture_stack": True,
                    "capture_recovery": True,
                },
            },
            "storage": {"backend": "execution_monitor", "streaming": True, "batch_size": 100},
            "sanitization": {
                "enabled": True,
                "patterns": ["password", "token", "key", "secret", "api_key"],
                "replacement_text": "[SANITIZED]",
            },
        }

    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.logs_directory / "claude_hook_manager.log"

        # Create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def start_session(self, session_context: Optional[Dict[str, Any]] = None) -> str:
        """Start a new logging session."""
        if not self.config.get("enabled", True):
            return None

        self.current_session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        self.stats["sessions_tracked"] += 1

        self.logger.info(f"Started new session: {self.current_session_id}")

        # Log session start to ExecutionMonitor
        self.execution_monitor.start_execution(
            "claude-hook-manager", f"Claude Code session {self.current_session_id}"
        )

        return self.current_session_id

    def end_session(self):
        """End the current logging session."""
        if not self.current_session_id:
            return

        # Flush any remaining events
        self._flush_events()

        # Log session end to ExecutionMonitor
        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        self.execution_monitor.log_execution(
            ExecutionResult.SUCCESS,
            additional_context={
                "session_id": self.current_session_id,
                "session_duration_seconds": session_duration,
                "events_captured": len(self.event_buffer),
            },
        )

        self.logger.info(f"Ended session: {self.current_session_id}")
        self.current_session_id = None
        self.session_start_time = None

    def _sanitize_content(
        self, content: Union[str, Dict, List, Any]
    ) -> Union[str, Dict, List, Any]:
        """Sanitize content to remove sensitive information."""
        if not self.config.get("sanitization", {}).get("enabled", True):
            return content

        patterns = self.config["sanitization"]["patterns"]
        replacement = self.config["sanitization"].get("replacement_text", "[SANITIZED]")
        case_insensitive = self.config["sanitization"].get("case_insensitive", True)
        regex_patterns = self.config["sanitization"].get("regex_patterns", [])

        def _sanitize_string(text: str) -> str:
            if not isinstance(text, str):
                return text

            flags = re.IGNORECASE if case_insensitive else 0

            # Basic pattern matching
            for pattern in patterns:
                text = re.sub(rf"\b{re.escape(pattern)}\b", replacement, text, flags=flags)

            # Advanced regex patterns
            for regex_pattern in regex_patterns:
                text = re.sub(regex_pattern, replacement, text, flags=flags)

            return text

        def _sanitize_recursive(obj):
            if isinstance(obj, str):
                return _sanitize_string(obj)
            elif isinstance(obj, dict):
                return {k: _sanitize_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_sanitize_recursive(item) for item in obj]
            else:
                return obj

        sanitized = _sanitize_recursive(content)

        if sanitized != content:
            self.stats["events_sanitized"] += 1

        return sanitized

    def capture_user_prompt(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Capture user prompt submission."""
        if not self._is_hook_enabled("user_prompt_submit"):
            return None

        if not self.current_session_id:
            self.start_session()

        event_id = str(uuid.uuid4())
        sanitized_content = self._sanitize_content(prompt)

        event = UserPromptEvent(
            event_id=event_id,
            session_id=self.current_session_id,
            timestamp=datetime.now().isoformat(),
            event_type="user_prompt_submit",
            metadata={
                "content_type": "text",
                "user_agent": context.get("user_agent") if context else None,
                "source": context.get("source", "claude_code") if context else "claude_code",
            },
            prompt_content=prompt,
            sanitized_content=sanitized_content,
            content_length=len(prompt),
            user_context=context,
        )

        self._add_event(event)
        self.logger.debug(f"Captured user prompt: {event_id}")
        return event_id

    def capture_tool_invocation(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        response: Optional[Any] = None,
        execution_time_ms: Optional[int] = None,
        success: Optional[bool] = None,
        error_message: Optional[str] = None,
    ) -> Optional[str]:
        """Capture tool invocation event."""
        if not self._is_hook_enabled("tool_invocation"):
            return None

        if not self.current_session_id:
            self.start_session()

        event_id = str(uuid.uuid4())
        sanitized_parameters = self._sanitize_content(parameters)
        sanitized_response = self._sanitize_content(response) if response else None

        event = ToolInvocationEvent(
            event_id=event_id,
            session_id=self.current_session_id,
            timestamp=datetime.now().isoformat(),
            event_type="tool_invocation",
            metadata={
                "capture_requests": self.config["hooks"]["tool_invocation"].get(
                    "capture_requests", True
                ),
                "capture_responses": self.config["hooks"]["tool_invocation"].get(
                    "capture_responses", True
                ),
            },
            tool_name=tool_name,
            tool_parameters=parameters,
            sanitized_parameters=sanitized_parameters,
            execution_start=datetime.now().isoformat(),
            execution_time_ms=execution_time_ms,
            tool_response=response,
            sanitized_response=sanitized_response,
            success=success,
            error_message=error_message,
        )

        self._add_event(event)
        self.logger.debug(f"Captured tool invocation: {tool_name} - {event_id}")
        return event_id

    def capture_ai_response(
        self,
        final_response: str,
        thinking_process: Optional[str] = None,
        generation_time_ms: Optional[int] = None,
    ) -> Optional[str]:
        """Capture AI response event."""
        if not self._is_hook_enabled("ai_response"):
            return None

        if not self.current_session_id:
            self.start_session()

        event_id = str(uuid.uuid4())
        sanitized_response = self._sanitize_content(final_response)
        sanitized_thinking = self._sanitize_content(thinking_process) if thinking_process else None

        event = AIResponseEvent(
            event_id=event_id,
            session_id=self.current_session_id,
            timestamp=datetime.now().isoformat(),
            event_type="ai_response",
            metadata={
                "capture_thinking": self.config["hooks"]["ai_response"].get(
                    "capture_thinking", True
                ),
                "capture_final": self.config["hooks"]["ai_response"].get("capture_final", True),
            },
            thinking_process=thinking_process,
            sanitized_thinking=sanitized_thinking,
            final_response=final_response,
            sanitized_response=sanitized_response,
            response_length=len(final_response),
            thinking_length=len(thinking_process) if thinking_process else None,
            generation_time_ms=generation_time_ms,
        )

        self._add_event(event)
        self.logger.debug(f"Captured AI response: {event_id}")
        return event_id

    def capture_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        recovery_action: Optional[str] = None,
        recovery_successful: Optional[bool] = None,
    ) -> Optional[str]:
        """Capture error event."""
        if not self._is_hook_enabled("error_handling"):
            return None

        if not self.current_session_id:
            self.start_session()

        event_id = str(uuid.uuid4())
        self.stats["errors_logged"] += 1

        event = ErrorEvent(
            event_id=event_id,
            session_id=self.current_session_id,
            timestamp=datetime.now().isoformat(),
            event_type="error_handling",
            metadata={
                "capture_stack": self.config["hooks"]["error_handling"].get("capture_stack", True),
                "capture_recovery": self.config["hooks"]["error_handling"].get(
                    "capture_recovery", True
                ),
                "error_severity": self._categorize_error_severity(error_type, error_message),
            },
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context or {},
            recovery_action=recovery_action,
            recovery_successful=recovery_successful,
        )

        self._add_event(event)
        self.logger.error(f"Captured error: {error_type} - {event_id}")

        # Also log to ExecutionMonitor for integration
        self.execution_monitor.log_execution(
            ExecutionResult.FAILURE,
            error_message=error_message,
            stack_trace=stack_trace,
            additional_context={"hook_event_id": event_id},
        )

        return event_id

    def _categorize_error_severity(self, error_type: str, error_message: str) -> str:
        """Categorize error severity for prioritization."""
        critical_patterns = ["system", "memory", "disk", "permission", "authentication"]
        high_patterns = ["network", "timeout", "connection", "import", "module"]
        medium_patterns = ["warning", "deprecated", "invalid", "parsing"]

        error_lower = f"{error_type} {error_message}".lower()

        if any(pattern in error_lower for pattern in critical_patterns):
            return "critical"
        elif any(pattern in error_lower for pattern in high_patterns):
            return "high"
        elif any(pattern in error_lower for pattern in medium_patterns):
            return "medium"
        else:
            return "low"

    def _is_hook_enabled(self, hook_type: str) -> bool:
        """Check if a specific hook type is enabled."""
        return self.config.get("enabled", True) and self.config.get("hooks", {}).get(
            hook_type, {}
        ).get("enabled", True)

    def _add_event(self, event: HookEvent):
        """Add event to buffer and handle batching."""
        self.event_buffer.append(event)
        self.stats["events_captured"] += 1

        # Check if we should flush based on batch size
        batch_size = self.config.get("storage", {}).get("batch_size", 100)
        if len(self.event_buffer) >= batch_size:
            self._flush_events()

    def _flush_events(self):
        """Flush events to storage."""
        if not self.event_buffer:
            return

        # Create daily log files following ExecutionMonitor pattern
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_directory / f"claude_hooks_{log_date}.json"

        # Load existing logs or create new list
        logs = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                self.logger.warning(f"Could not parse existing log file: {log_file}")
                logs = []

        # Add new events
        for event in self.event_buffer:
            logs.append(asdict(event))

        # Save updated logs
        try:
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
            self.logger.info(f"Flushed {len(self.event_buffer)} events to {log_file}")
        except Exception as e:
            self.logger.error(f"Failed to save events: {e}")

        # Clear buffer
        self.event_buffer.clear()

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        return {
            "current_session_id": self.current_session_id,
            "session_start_time": (
                self.session_start_time.isoformat() if self.session_start_time else None
            ),
            "events_in_buffer": len(self.event_buffer),
            "total_stats": self.stats.copy(),
        }

    def get_hook_status(self) -> Dict[str, Any]:
        """Get comprehensive hook system status."""
        return {
            "enabled": self.config.get("enabled", True),
            "config_version": self.config.get("version", "unknown"),
            "hooks_status": {
                hook_type: self._is_hook_enabled(hook_type)
                for hook_type in [
                    "user_prompt_submit",
                    "tool_invocation",
                    "ai_response",
                    "error_handling",
                ]
            },
            "storage_backend": self.config.get("storage", {}).get("backend", "execution_monitor"),
            "logs_directory": str(self.logs_directory),
            "sanitization_enabled": self.config.get("sanitization", {}).get("enabled", True),
            "session_stats": self.get_session_stats(),
            "performance_stats": self.stats,
        }


# Global hook manager instance
_global_hook_manager = None


def get_hook_manager() -> ClaudeHookManager:
    """Get global hook manager instance."""
    global _global_hook_manager
    if _global_hook_manager is None:
        _global_hook_manager = ClaudeHookManager()
    return _global_hook_manager


# Convenience functions for external use
def start_session(context: Optional[Dict[str, Any]] = None) -> str:
    """Start a new Claude Code session."""
    return get_hook_manager().start_session(context)


def end_session():
    """End the current Claude Code session."""
    get_hook_manager().end_session()


def log_user_prompt(prompt: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Log user prompt submission."""
    return get_hook_manager().capture_user_prompt(prompt, context)


def log_tool_usage(
    tool_name: str,
    parameters: Dict[str, Any],
    response: Optional[Any] = None,
    execution_time_ms: Optional[int] = None,
    success: Optional[bool] = None,
    error_message: Optional[str] = None,
) -> Optional[str]:
    """Log tool invocation."""
    return get_hook_manager().capture_tool_invocation(
        tool_name, parameters, response, execution_time_ms, success, error_message
    )


def log_ai_response(
    response: str, thinking: Optional[str] = None, generation_time_ms: Optional[int] = None
) -> Optional[str]:
    """Log AI response."""
    return get_hook_manager().capture_ai_response(response, thinking, generation_time_ms)


def log_error(
    error_type: str,
    error_message: str,
    stack_trace: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    recovery_action: Optional[str] = None,
    recovery_successful: Optional[bool] = None,
) -> Optional[str]:
    """Log error event."""
    return get_hook_manager().capture_error(
        error_type, error_message, stack_trace, context, recovery_action, recovery_successful
    )
