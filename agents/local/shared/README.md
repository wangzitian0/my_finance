# Shared Agent Documentation

This directory contains shared documentation and coordination files for inter-agent operations.

## Directory Structure

```
shared/
├── coordination/  # Inter-agent coordination logs
└── system/       # System-wide performance data
```

## Coordination Files (`coordination/`)
- **Purpose**: Track coordination between different agents
- **Format**: JSON logs with agent interaction data
- **Retention**: 14 days
- **Examples**:
  - `coordination_log_20250829.json` - Daily coordination summary
  - `agent_handoffs_20250829.json` - Task handoff tracking

## System Files (`system/`)
- **Purpose**: System-wide performance metrics across all agents
- **Format**: JSON and log files
- **Retention**: 30 days locally, permanent in build_data
- **Examples**:
  - `system_performance_20250829.json` - Overall system metrics
  - `resource_utilization_20250829.json` - Resource usage across agents

## Integration

### Cross-Agent Coordination
- Agents can write coordination logs when handing off tasks
- Central coordination tracking for HRBP system analysis
- Conflict resolution and resource contention tracking

### System Monitoring
- Aggregate performance metrics across all agents
- System-wide optimization opportunities
- Resource allocation and usage patterns

### HRBP Analysis
- Source data for agent performance comparisons
- System-wide efficiency analysis
- Coordination pattern identification