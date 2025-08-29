#!/usr/bin/env python3
"""
Sub-agent Glue Layer - Processes hook data and writes to SSOT logging
"""
import json
import logging
from datetime import datetime
from pathlib import Path


def process_subagent_log(hook_output: str):
    """Process sub-agent hook output and write to SSOT log."""
    try:
        log_data = json.loads(hook_output)

        # Get basic logger and write to logs
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
        logger = logging.getLogger("subagent_execution")

        # Write to SSOT log
        logger.info(
            f"SubAgent: {log_data['subagent_type']} | "
            f"Task: {log_data['description']} | "
            f"Status: {log_data['status']} | "
            f"Prompt: {log_data.get('prompt_preview', '')[:50]}..."
        )

    except (json.JSONDecodeError, KeyError) as e:
        # Fallback logging
        logger = logging.getLogger("subagent_execution")
        logger.error(f"Failed to process sub-agent log: {e}")


def log_subagent_call(subagent_type: str, description: str, prompt: str):
    """Direct function to log sub-agent calls."""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "type": "subagent_call",
        "subagent_type": subagent_type,
        "description": description,
        "prompt_preview": prompt[:200],
        "status": "started",
    }

    process_subagent_log(json.dumps(log_data))


if __name__ == "__main__":
    # Test
    test_output = '{"timestamp": "2025-08-29T18:18:21.872565", "type": "subagent_call", "subagent_type": "git-ops-agent", "description": "Test task", "prompt_preview": "This is a test prompt for logging", "status": "started"}'
    print("Testing sub-agent glue layer...")
    process_subagent_log(test_output)
    print("Test completed!")
