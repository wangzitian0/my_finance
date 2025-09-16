# Post-Merge Analysis Logs

This directory contains automated tracking logs for post-merge CI analysis.

## Structure

- `post-merge-YYYY-MM.log`: Monthly aggregated analysis logs
- Each log entry includes:
  - Timestamp
  - Commit SHA
  - PR number
  - Author
  - CI status
  - Claude analysis request status

## Purpose

These logs provide:
- Historical tracking of post-merge analysis requests
- Audit trail for CI/CD pipeline health
- Metrics for code quality and review effectiveness

## Retention

Logs are maintained indefinitely for audit purposes and are automatically updated by GitHub Actions.