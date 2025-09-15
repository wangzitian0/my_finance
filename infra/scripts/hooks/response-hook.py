#!/usr/bin/env python3
"""
Response Hook for Claude Code

This script captures AI response data including thinking processes and final responses
for comprehensive logging and analysis.

Usage:
    python response-hook.py --response "AI response here" [--thinking "thinking process"] [--generation-time 1500]

Environment Variables:
    CLAUDE_SESSION_ID: Current Claude Code session ID

GitHub Issue #214: Implement Claude Code hooks for comprehensive logging integration
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add common directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))

from monitoring.claude_hook_manager import get_hook_manager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Claude Code AI Response Hook")

    parser.add_argument("--response", type=str, help="Final AI response content")

    parser.add_argument("--thinking", type=str, help="AI thinking process content")

    parser.add_argument(
        "--generation-time", type=int, help="Response generation time in milliseconds"
    )

    parser.add_argument(
        "--response-file",
        type=str,
        help="Path to file containing the response (alternative to --response)",
    )

    parser.add_argument(
        "--thinking-file",
        type=str,
        help="Path to file containing thinking process (alternative to --thinking)",
    )

    parser.add_argument("--session-id", type=str, help="Override session ID")

    parser.add_argument(
        "--max-response-length", type=int, default=50000, help="Maximum response length to capture"
    )

    parser.add_argument(
        "--max-thinking-length",
        type=int,
        default=25000,
        help="Maximum thinking process length to capture",
    )

    parser.add_argument("--context", type=str, help="Additional context as JSON string")

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    return parser.parse_args()


def load_file_content(file_path: str, max_length: int = None) -> str:
    """Load content from file with optional truncation."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if max_length and len(content) > max_length:
            content = content[:max_length] + f"... [TRUNCATED - original length: {len(content)}]"

        return content
    except Exception as e:
        print(f"Warning: Failed to load content from {file_path}: {e}", file=sys.stderr)
        return ""


def truncate_content(content: str, max_length: int, content_type: str = "content") -> str:
    """Truncate content if it exceeds maximum length."""
    if len(content) > max_length:
        truncated = (
            content[:max_length]
            + f"... [TRUNCATED - original {content_type} length: {len(content)}]"
        )
        return truncated
    return content


def parse_json_safely(json_string: str) -> dict:
    """Safely parse JSON string."""
    if not json_string:
        return {}

    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse context JSON: {e}", file=sys.stderr)
        return {"_parse_error": str(e)}


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

        # Get response content
        if args.response_file:
            response_content = load_file_content(args.response_file, args.max_response_length)
        else:
            response_content = args.response or ""

        # Truncate response if needed
        response_content = truncate_content(response_content, args.max_response_length, "response")

        # Get thinking content
        thinking_content = None
        if args.thinking_file:
            thinking_content = load_file_content(args.thinking_file, args.max_thinking_length)
        elif args.thinking:
            thinking_content = truncate_content(args.thinking, args.max_thinking_length, "thinking")

        # Validate we have content or file
        if not response_content and not args.response_file:
            print("Error: Either --response or --response-file must be provided", file=sys.stderr)
            return 1

        if not response_content:
            print("Error: No response content could be loaded", file=sys.stderr)
            return 1

        # Parse additional context
        context = parse_json_safely(args.context)

        # Add metadata to context
        context.update(
            {
                "capture_method": "hook_script",
                "response_source": "response_file" if args.response_file else "command_line",
                "thinking_source": (
                    "thinking_file"
                    if args.thinking_file
                    else ("command_line" if args.thinking else None)
                ),
                "truncation_applied": {
                    "response": len(args.response or response_content) > args.max_response_length,
                    "thinking": thinking_content
                    and len(thinking_content) > args.max_thinking_length,
                },
            }
        )

        # Capture the response
        event_id = hook_manager.capture_ai_response(
            final_response=response_content,
            thinking_process=thinking_content,
            generation_time_ms=args.generation_time,
        )

        if args.verbose:
            print(f"Captured AI response: {event_id}", file=sys.stderr)
            print(f"Session: {hook_manager.current_session_id}", file=sys.stderr)
            print(f"Response length: {len(response_content)} characters", file=sys.stderr)
            if thinking_content:
                print(f"Thinking length: {len(thinking_content)} characters", file=sys.stderr)
            if args.generation_time:
                print(f"Generation time: {args.generation_time}ms", file=sys.stderr)

        # Output event ID
        if event_id:
            print(event_id)

        return 0

    except Exception as e:
        print(f"Error in response hook: {e}", file=sys.stderr)

        # Try to log the error
        try:
            hook_manager = get_hook_manager()
            hook_manager.capture_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={"hook": "response", "args": vars(args)},
            )
        except:
            pass  # Avoid recursive errors

        return 1


if __name__ == "__main__":
    sys.exit(main())
