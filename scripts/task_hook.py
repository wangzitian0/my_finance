#!/usr/bin/env python3
"""
Simple Task Hook for Sub-Agent Failure Capture

GitHub Issue #181: Replace AgentNeo with simple dump-and-process approach

Usage:
    from scripts.task_hook import hook_task_start, hook_task_end, process_dumps

    # Hook task execution
    exec_id = hook_task_start("git-ops-agent", "Check git status")
    try:
        # ... execute task ...
        hook_task_end(exec_id, success=True, result="Clean repository")
    except Exception as e:
        hook_task_end(exec_id, success=False, error=str(e))

    # Process dumps into SSOT logs
    process_dumps()
"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path


# Simple hook system
class TaskHook:
    def __init__(self):
        self.dump_dir = Path("task_dumps")
        self.dump_dir.mkdir(exist_ok=True)
        self.active_tasks = {}

    def start(self, agent_type: str, prompt: str, description: str = None) -> str:
        exec_id = str(uuid.uuid4())
        self.active_tasks[exec_id] = {
            "execution_id": exec_id,
            "agent_type": agent_type,
            "prompt": prompt,
            "description": description or f"Task: {agent_type}",
            "start_time": time.time(),
            "timestamp": datetime.now().isoformat(),
        }
        return exec_id

    def end(
        self, exec_id: str, success: bool, result: str = None, error: str = None, output: str = None
    ):
        if exec_id not in self.active_tasks:
            return

        task = self.active_tasks[exec_id]
        task.update(
            {
                "success": success,
                "result": result,
                "error": error,
                "output": output,
                "end_time": time.time(),
                "duration_ms": int((time.time() - task["start_time"]) * 1000),
            }
        )

        # Dump to file
        dump_file = self.dump_dir / f"task_{exec_id}.json"
        with open(dump_file, "w") as f:
            json.dump(task, f, indent=2)

        del self.active_tasks[exec_id]


# Global hook instance
_hook = TaskHook()


def hook_task_start(agent_type: str, prompt: str, description: str = None) -> str:
    """Start task hook."""
    return _hook.start(agent_type, prompt, description)


def hook_task_end(
    exec_id: str, success: bool, result: str = None, error: str = None, output: str = None
):
    """End task hook."""
    _hook.end(exec_id, success, result, error, output)


# Process dumps into SSOT logs
def process_dumps():
    """Process task dumps into SSOT logs."""
    dump_dir = Path("task_dumps")
    if not dump_dir.exists():
        return 0

    # SSOT directories
    logs_dir = Path("build_data/logs")
    hrbp_dir = logs_dir / "hrbp_reviews"
    logs_dir.mkdir(parents=True, exist_ok=True)
    hrbp_dir.mkdir(parents=True, exist_ok=True)

    # Process all dumps
    dumps = list(dump_dir.glob("task_*.json"))
    if not dumps:
        return 0

    # Load existing execution log
    today = datetime.now().strftime("%Y-%m-%d")
    exec_log = logs_dir / f"execution_logs_{today}.json"
    logs = []
    if exec_log.exists():
        try:
            with open(exec_log, "r") as f:
                logs = json.load(f)
        except:
            logs = []

    processed = 0
    for dump_file in dumps:
        try:
            with open(dump_file, "r") as f:
                task = json.load(f)

            # Add to execution log
            logs.append(
                {
                    "timestamp": task["timestamp"],
                    "agent_type": f"task-{task['agent_type']}",
                    "task_description": task["description"],
                    "execution_time_ms": task.get("duration_ms", 0),
                    "result": "success" if task.get("success") else "failure",
                    "error_message": task.get("error"),
                    "additional_context": {
                        "execution_id": task["execution_id"],
                        "prompt": task["prompt"][:200],
                        "output": (task.get("output", "") or "")[:500],
                    },
                }
            )

            # Create HRBP review for failures
            if not task.get("success") and task.get("error"):
                review_file = hrbp_dir / f"failure_{task['execution_id']}.json"
                with open(review_file, "w") as f:
                    json.dump(
                        {
                            "review_id": task["execution_id"],
                            "timestamp": task["timestamp"],
                            "subagent_type": task["agent_type"],
                            "task_description": task["description"],
                            "prompt": task["prompt"],
                            "error_message": task["error"],
                            "execution_time_ms": task.get("duration_ms", 0),
                            "raw_output": (task.get("output", "") or "")[:1000],
                        },
                        f,
                        indent=2,
                    )

            dump_file.unlink()  # Remove processed dump
            processed += 1

        except Exception as e:
            print(f"Failed to process {dump_file}: {e}")

    # Save updated logs
    with open(exec_log, "w") as f:
        json.dump(logs, f, indent=2)

    return processed


# Test function
def test_hook():
    """Simple test of the hook system."""
    print("Testing simple hook system...")

    # Test success
    exec_id = hook_task_start("git-ops-agent", "git status", "Git health check")
    time.sleep(0.1)
    hook_task_end(exec_id, success=True, result="Repository clean")

    # Test failure
    exec_id = hook_task_start("backend-architect-agent", "connect db", "Database connection")
    time.sleep(0.1)
    hook_task_end(exec_id, success=False, error="Connection refused")

    # Process dumps
    processed = process_dumps()
    print(f"Processed {processed} task dumps")

    return processed


if __name__ == "__main__":
    test_hook()