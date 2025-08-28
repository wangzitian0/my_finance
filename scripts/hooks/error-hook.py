#!/usr/bin/env python3
"""
Error Hook for Claude Code

This script captures error events with stack traces and recovery actions
for comprehensive error tracking and debugging.

Usage:
    python error-hook.py --error-type "ImportError" --error-message "Module not found" [--stack-trace-file trace.txt] [--recovery-action "retry with fallback"]

Environment Variables:
    CLAUDE_SESSION_ID: Current Claude Code session ID

GitHub Issue #214: Implement Claude Code hooks for comprehensive logging integration
"""

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

# Add common directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))

from monitoring.claude_hook_manager import get_hook_manager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Claude Code Error Hook")
    
    parser.add_argument(
        "--error-type",
        type=str,
        required=True,
        help="Type/class of the error"
    )
    
    parser.add_argument(
        "--error-message",
        type=str,
        required=True,
        help="Error message description"
    )
    
    parser.add_argument(
        "--stack-trace",
        type=str,
        help="Stack trace as string"
    )
    
    parser.add_argument(
        "--stack-trace-file",
        type=str,
        help="Path to file containing stack trace"
    )
    
    parser.add_argument(
        "--context",
        type=str,
        help="Additional context as JSON string"
    )
    
    parser.add_argument(
        "--context-file",
        type=str,
        help="Path to JSON file containing context"
    )
    
    parser.add_argument(
        "--recovery-action",
        type=str,
        help="Description of recovery action taken"
    )
    
    parser.add_argument(
        "--recovery-successful",
        type=str,
        choices=["true", "false"],
        help="Whether recovery was successful"
    )
    
    parser.add_argument(
        "--session-id",
        type=str,
        help="Override session ID"
    )
    
    parser.add_argument(
        "--max-stack-trace-length",
        type=int,
        default=20000,
        help="Maximum stack trace length to capture"
    )
    
    parser.add_argument(
        "--capture-current-stack",
        action="store_true",
        help="Capture current stack trace if no stack trace provided"
    )
    
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Manual error severity override"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def load_file_content(file_path: str, max_length: int = None) -> str:
    """Load content from file with optional truncation."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if max_length and len(content) > max_length:
            content = content[:max_length] + f"... [TRUNCATED - original length: {len(content)}]"
        
        return content
    except Exception as e:
        print(f"Warning: Failed to load content from {file_path}: {e}", file=sys.stderr)
        return ""


def load_json_file(file_path: str) -> dict:
    """Load JSON from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load JSON from {file_path}: {e}", file=sys.stderr)
        return {"_load_error": str(e)}


def parse_json_safely(json_string: str) -> dict:
    """Safely parse JSON string."""
    if not json_string:
        return {}
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse context JSON: {e}", file=sys.stderr)
        return {"_parse_error": str(e)}


def get_current_stack_trace() -> str:
    """Get current stack trace."""
    try:
        # Create a dummy exception to get the stack
        raise Exception("Stack trace capture")
    except Exception:
        # Remove the last frame (this function) and the dummy exception
        return ''.join(traceback.format_stack()[:-2])


def main():
    """Main hook execution."""
    args = parse_arguments()
    
    try:
        # Get hook manager
        hook_manager = get_hook_manager()
        
        # Start session if needed
        if not hook_manager.current_session_id:
            session_id = hook_manager.start_session()
            if args.verbose:
                print(f"Started new session: {session_id}", file=sys.stderr)
        
        # Get stack trace
        stack_trace = None
        if args.stack_trace_file:
            stack_trace = load_file_content(args.stack_trace_file, args.max_stack_trace_length)
        elif args.stack_trace:
            if len(args.stack_trace) > args.max_stack_trace_length:
                stack_trace = args.stack_trace[:args.max_stack_trace_length] + \
                             f"... [TRUNCATED - original length: {len(args.stack_trace)}]"
            else:
                stack_trace = args.stack_trace
        elif args.capture_current_stack:
            stack_trace = get_current_stack_trace()
            if len(stack_trace) > args.max_stack_trace_length:
                stack_trace = stack_trace[:args.max_stack_trace_length] + \
                             f"... [TRUNCATED - original length: {len(stack_trace)}]"
        
        # Get context
        context = {}
        if args.context_file:
            context.update(load_json_file(args.context_file))
        if args.context:
            context.update(parse_json_safely(args.context))
        
        # Add environment context
        context.update({
            "capture_method": "hook_script",
            "working_directory": os.getcwd(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "environment_variables": {
                "USER": os.getenv("USER"),
                "PATH": os.getenv("PATH", "").split(":") if os.getenv("PATH") else [],
                "PYTHON_PATH": os.getenv("PYTHONPATH", "").split(":") if os.getenv("PYTHONPATH") else []
            },
            "hook_args": vars(args)
        })
        
        # If severity provided, add to context
        if args.severity:
            context["manual_severity"] = args.severity
        
        # Parse recovery successful
        recovery_successful = None
        if args.recovery_successful:
            recovery_successful = args.recovery_successful.lower() == "true"
        
        # Capture the error
        event_id = hook_manager.capture_error(
            error_type=args.error_type,
            error_message=args.error_message,
            stack_trace=stack_trace,
            context=context,
            recovery_action=args.recovery_action,
            recovery_successful=recovery_successful
        )
        
        if args.verbose:
            print(f"Captured error event: {event_id}", file=sys.stderr)
            print(f"Session: {hook_manager.current_session_id}", file=sys.stderr)
            print(f"Error type: {args.error_type}", file=sys.stderr)
            print(f"Error message: {args.error_message}", file=sys.stderr)
            if stack_trace:
                print(f"Stack trace length: {len(stack_trace)} characters", file=sys.stderr)
            if args.recovery_action:
                print(f"Recovery action: {args.recovery_action}", file=sys.stderr)
                print(f"Recovery successful: {recovery_successful}", file=sys.stderr)
        
        # Output event ID
        if event_id:
            print(event_id)
        
        return 0
        
    except Exception as e:
        print(f"Error in error hook: {e}", file=sys.stderr)
        
        # Try to log the error (avoiding infinite recursion)
        try:
            hook_manager = get_hook_manager()
            hook_manager.capture_error(
                error_type="HookError",
                error_message=f"Error in error-hook.py: {str(e)}",
                context={"hook": "error", "original_error_type": args.error_type if 'args' in locals() else "unknown"}
            )
        except:
            pass  # Avoid infinite recursion
        
        return 1


if __name__ == "__main__":
    sys.exit(main())