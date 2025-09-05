# HRBP Agent Local Documentation

This directory contains local documentation for the HRBP (Human Resources Business Partner) agent system.

## Directory Structure

```
hrbp-agent/
├── performance/    # Performance logs and metrics
├── analysis/      # Temporary analysis files
├── reports/       # Local report drafts
└── temp/          # Temporary working files
```

## File Types and Usage

### Performance Logs (`performance/`)
- **Purpose**: Track agent performance metrics, task completion times, quality scores
- **Format**: JSON files with structured performance data
- **Retention**: 7 days locally, backed up to build_data/logs for long-term analysis
- **Example**: `performance_log_20250829_143000.json`

### Analysis Files (`analysis/`)
- **Purpose**: Temporary analysis reports, capability assessments, optimization findings
- **Format**: Markdown and JSON files
- **Retention**: 30 days locally
- **Example**: `hrbp_analysis_agent-coordinator_20250829.json`

### Reports (`reports/`)
- **Purpose**: Draft reports before they're consolidated into GitHub issues
- **Format**: Markdown files
- **Retention**: Until promoted to GitHub issues
- **Example**: `agent_report_monthly_20250829.md`

### Temporary Files (`temp/`)
- **Purpose**: Session-specific working files, intermediate calculations
- **Format**: Various (txt, json, md)
- **Retention**: 24 hours
- **Example**: `temp_task_123_20250829.txt`

## Integration Points

### With Build Data System
- Important performance logs are backed up to `build_data/logs/agents/hrbp/`
- Uses centralized `DirectoryManager` for path resolution
- Follows SSOT principles from `common/config/`

### With P3 Workflow
- `p3 debug` may include agent performance metrics
- `p3 test` generates performance logs here
- Integration with quality reporting system

### With GitHub Issues
- Local analysis files feed into consolidated GitHub issue reports
- Medium-term documentation lifecycle managed through GitHub
- Labels and milestones track agent performance trends

## Example Files

The files in this directory are examples of the types of local documentation the HRBP system will generate. They are gitignored but the directory structure is preserved.