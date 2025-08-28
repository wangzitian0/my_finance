#!/usr/bin/env python3
"""
User Prompt Submit Hook for Claude Code

This script is designed to be called as a hook when users submit prompts
to Claude Code, capturing the prompt data for comprehensive logging.

Usage:
    python user-prompt-submit-hook.py --prompt "user prompt here" [--context "context.json"]

Environment Variables:
    CLAUDE_SESSION_ID: Current Claude Code session ID
    CLAUDE_USER_AGENT: User agent information
    CLAUDE_SOURCE: Source of the interaction (defaults to "claude_code")

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
    parser = argparse.ArgumentParser(description="Claude Code User Prompt Submit Hook")

    parser.add_argument("--prompt", type=str, required=True, help="User prompt content")

    parser.add_argument(
        "--context", type=str, help="Path to JSON file containing additional context"
    )

    parser.add_argument(
        "--session-id", type=str, help="Override session ID (defaults to environment variable)"
    )

    parser.add_argument("--user-agent", type=str, help="User agent information")

    parser.add_argument(
        "--source", type=str, default="claude_code", help="Source of the interaction"
    )

    parser.add_argument(
        "--max-length", type=int, default=50000, help="Maximum prompt length to capture"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    return parser.parse_args()


def load_context(context_path: str) -> dict:
    """Load context from JSON file."""
    try:
        with open(context_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load context from {context_path}: {e}", file=sys.stderr)
        return {}


def main():
    """Main hook execution."""
    args = parse_arguments()

    try:
        # Get hook manager
        hook_manager = get_hook_manager()

        # Prepare context
        context = {
            "user_agent": args.user_agent or os.getenv("CLAUDE_USER_AGENT"),
            "source": args.source or os.getenv("CLAUDE_SOURCE", "claude_code"),
            "session_id": args.session_id or os.getenv("CLAUDE_SESSION_ID"),
            "timestamp": str(os.times().elapsed) if hasattr(os, "times") else None,
            "environment": {
                "cwd": os.getcwd(),
                "user": os.getenv("USER", "unknown"),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            },
        }

        # Load additional context if provided
        if args.context:
            file_context = load_context(args.context)
            context.update(file_context)

        # Truncate prompt if too long
        prompt = args.prompt
        if len(prompt) > args.max_length:
            prompt = (
                prompt[: args.max_length] + f"... [TRUNCATED - original length: {len(args.prompt)}]"
            )
            if args.verbose:
                print(f"Warning: Prompt truncated to {args.max_length} characters", file=sys.stderr)

        # Start session if needed and capture prompt
        if not hook_manager.current_session_id:
            session_id = hook_manager.start_session(context)
            if args.verbose:
                print(f"Started new session: {session_id}", file=sys.stderr)

        # Capture the prompt
        event_id = hook_manager.capture_user_prompt(prompt, context)

        if args.verbose:
            print(f"Captured user prompt: {event_id}", file=sys.stderr)
            print(f"Session: {hook_manager.current_session_id}", file=sys.stderr)
            print(f"Prompt length: {len(args.prompt)} characters", file=sys.stderr)

        # Output event ID for chaining
        if event_id:
            print(event_id)

        return 0

    except Exception as e:
        print(f"Error in user prompt submit hook: {e}", file=sys.stderr)

        # Try to log the error
        try:
            hook_manager = get_hook_manager()
            hook_manager.capture_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={"hook": "user-prompt-submit", "args": vars(args)},
            )
        except:
            pass  # Avoid recursive errors

        return 1


if __name__ == "__main__":
    sys.exit(main())
