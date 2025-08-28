# Agent Execution Monitoring

This directory contains execution logs and monitoring data for the Agent Execution Monitoring System (Issue #180).

## Structure

```
monitoring/
├── execution_logs_YYYY-MM-DD.json  # Daily execution logs
├── performance_metrics.json        # Aggregated performance data
└── error_patterns.json            # Error pattern analysis
```

## Log Schema

Each execution log entry contains:

```json
{
  "timestamp": "2025-08-28T12:00:00.000Z",
  "agent_type": "p3-command|agent-coordinator|git-ops|data-engineer|...",
  "task_description": "Human readable task description",
  "execution_result": "success|failure|timeout|retry",
  "error_category": "critical|high|medium|low",
  "execution_time_ms": 1500,
  "retry_count": 0,
  "environment_state": {
    "working_directory": "/path/to/project",
    "python_version": "3.11.0",
    "timestamp": "2025-08-28T12:00:00.000Z",
    "process_id": 12345
  },
  "error_message": "Error description if failed",
  "stack_trace": "Full stack trace if available",
  "command": "p3 build m7",
  "working_directory": "/path/to/project"
}
```

## Usage

The monitoring system automatically:
- Tracks all p3 command executions
- Logs agent-coordinator delegations
- Categorizes errors automatically
- Maintains performance metrics
- Provides <5% overhead impact

## Analysis

Use `ExecutionMonitor.get_execution_stats()` for trend analysis:
- Success/failure rates by agent
- Average execution times
- Error category distributions
- Retry patterns