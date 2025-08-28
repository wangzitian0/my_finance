#!/usr/bin/env python3
"""
Tool Use Hook for Claude Code

This script captures tool invocation and response data for comprehensive logging.

Usage:
    # For tool invocation start
    python tool-use-hook.py --tool-name "Bash" --parameters '{"command": "ls -la"}' --phase start

    # For tool invocation completion  
    python tool-use-hook.py --tool-name "Bash" --event-id "uuid-from-start" --response '{"output": "files..."}' --phase complete --success true

Environment Variables:
    CLAUDE_SESSION_ID: Current Claude Code session ID

GitHub Issue #214: Implement Claude Code hooks for comprehensive logging integration
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add common directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))

from monitoring.claude_hook_manager import get_hook_manager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Claude Code Tool Use Hook")
    
    parser.add_argument(
        "--tool-name",
        type=str,
        required=True,
        help="Name of the tool being invoked"
    )
    
    parser.add_argument(
        "--parameters",
        type=str,
        help="Tool parameters as JSON string"
    )
    
    parser.add_argument(
        "--response",
        type=str,
        help="Tool response as JSON string"
    )
    
    parser.add_argument(
        "--phase",
        choices=["start", "complete"],
        default="complete",
        help="Hook phase: start (before tool execution) or complete (after)"
    )
    
    parser.add_argument(
        "--event-id",
        type=str,
        help="Event ID from start phase (for completion tracking)"
    )
    
    parser.add_argument(
        "--execution-time",
        type=int,
        help="Execution time in milliseconds"
    )
    
    parser.add_argument(
        "--success",
        type=str,
        choices=["true", "false"],
        help="Whether the tool execution was successful"
    )
    
    parser.add_argument(
        "--error-message",
        type=str,
        help="Error message if tool execution failed"
    )
    
    parser.add_argument(
        "--session-id",
        type=str,
        help="Override session ID"
    )
    
    parser.add_argument(
        "--max-response-length",
        type=int,
        default=10000,
        help="Maximum response length to capture"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def parse_json_safely(json_string: str, field_name: str) -> dict:
    """Safely parse JSON string."""
    if not json_string:
        return {}
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse {field_name} JSON: {e}", file=sys.stderr)
        return {"_parse_error": str(e), "_raw_content": json_string}


def truncate_response(response: any, max_length: int) -> any:
    """Truncate response if it's too long."""
    if isinstance(response, str) and len(response) > max_length:
        return response[:max_length] + f"... [TRUNCATED - original length: {len(response)}]"
    elif isinstance(response, dict):
        # Check if any string values are too long
        truncated = {}
        for key, value in response.items():
            if isinstance(value, str) and len(value) > max_length:
                truncated[key] = value[:max_length] + f"... [TRUNCATED - original length: {len(value)}]"
            else:
                truncated[key] = value
        return truncated
    return response


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
        
        # Parse parameters and response
        parameters = parse_json_safely(args.parameters, "parameters")
        response = parse_json_safely(args.response, "response")
        
        # Truncate response if needed
        if args.response:
            response = truncate_response(response, args.max_response_length)
        
        # Parse success flag
        success = None
        if args.success:
            success = args.success.lower() == "true"
        
        # For start phase, we just capture the tool invocation start
        if args.phase == "start":
            start_time = time.time()
            event_id = hook_manager.capture_tool_invocation(
                tool_name=args.tool_name,
                parameters=parameters,
                success=None,  # Unknown at start
                error_message=None
            )
            
            if args.verbose:
                print(f"Started tool invocation tracking: {event_id}", file=sys.stderr)
                print(f"Tool: {args.tool_name}", file=sys.stderr)
                print(f"Parameters: {len(str(parameters))} characters", file=sys.stderr)
            
            # Output event ID for completion tracking
            if event_id:
                print(event_id)
        
        # For complete phase, capture the full execution
        else:
            event_id = hook_manager.capture_tool_invocation(
                tool_name=args.tool_name,
                parameters=parameters,
                response=response,
                execution_time_ms=args.execution_time,
                success=success,
                error_message=args.error_message
            )
            
            if args.verbose:
                print(f"Captured tool invocation completion: {event_id}", file=sys.stderr)
                print(f"Tool: {args.tool_name}", file=sys.stderr)
                print(f"Success: {success}", file=sys.stderr)
                if args.execution_time:
                    print(f"Execution time: {args.execution_time}ms", file=sys.stderr)
                if response:
                    print(f"Response length: {len(str(response))} characters", file=sys.stderr)
            
            # Output event ID
            if event_id:
                print(event_id)
        
        return 0
        
    except Exception as e:
        print(f"Error in tool use hook: {e}", file=sys.stderr)
        
        # Try to log the error
        try:
            hook_manager = get_hook_manager()
            hook_manager.capture_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={"hook": "tool-use", "args": vars(args)}
            )
        except:
            pass  # Avoid recursive errors
        
        return 1


if __name__ == "__main__":
    sys.exit(main())