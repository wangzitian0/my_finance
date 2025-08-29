# Agent Local Documentation

This directory contains agent-specific local documentation files that are gitignored for short-term operational data.

## Directory Structure

```
agents/local/
├── {agent-name}/           # Agent-specific directories
│   ├── performance/        # Performance logs and metrics
│   ├── analysis/          # Temporary analysis files
│   ├── reports/           # Local report drafts
│   └── temp/              # Temporary working files
└── shared/                # Cross-agent shared local files
    ├── coordination/      # Inter-agent coordination logs
    └── system/           # System-wide performance data
```

## Documentation Lifecycle

### Short-term (Local Files - This Directory)
- **Purpose**: Operational logs, performance data, temporary analysis
- **Retention**: Session-based or short-term (hours to days)
- **Location**: `agents/local/{agent-name}/`
- **Git Status**: Ignored (not tracked)

### Medium-term (GitHub Issues)
- **Purpose**: Consolidated reports, milestone tracking, decision records
- **Retention**: Project lifecycle (weeks to months)
- **Location**: GitHub Issues with proper labels
- **Git Status**: Tracked via issue references

### Long-term (Agent Description Files)
- **Purpose**: Core capabilities, permanent policies, architecture decisions
- **Retention**: Permanent
- **Location**: `agents/{agent-name}.md` or similar
- **Git Status**: Tracked in repository

## Usage Guidelines

### For HRBP System
- **Performance Logs**: Store in `agents/local/hrbp-agent/performance/`
- **Analysis Reports**: Store in `agents/local/hrbp-agent/analysis/`
- **Temp Files**: Store in `agents/local/hrbp-agent/temp/`

### Integration Points
- **Configuration**: Use centralized `common/config/` system
- **Permanent Data**: Link to build_data structure when needed
- **Shared Resources**: Use `agents/local/shared/` for cross-agent data

## File Naming Conventions

```
performance_log_YYYYMMDD_HHMMSS.json
analysis_report_YYYYMMDD_HHMMSS.md
temp_task_{task_id}_YYYYMMDD.txt
coordination_log_YYYYMMDD.json
```

## Integration with P3 Workflow

This local documentation system integrates with:
- **p3 env-status**: Can include agent performance in status reports
- **p3 e2e**: May generate local performance logs during testing
- **Common Configuration**: Uses SSOT principles from `common/config/`