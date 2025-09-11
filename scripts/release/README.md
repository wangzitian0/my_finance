# Release Management Scripts

This directory contains scripts for release management, testing, and coordination.

## Scripts Overview

- **`release_manager.py`** - Main release management and coordination system
- **`run_release_tests.py`** - Executes comprehensive release validation tests
- **`demo_release_system.py`** - Demonstrates and tests release system functionality

## Purpose

These scripts support release engineering operations including:
- Release coordination and management workflows
- Release testing across all scopes (f2, m7, n100, v3k)
- Release system demonstrations and validation
- Integration with P3 ship workflow

## Usage

Release scripts should be integrated with P3 workflow system:
- Use `p3 test [scope]` for release validation testing
- Use `p3 ship "title" ISSUE_NUM` for actual release coordination
- Scope selection: f2 (dev), m7 (testing), n100 (validation), v3k (production)

## Release Process Compliance

All release operations must:
- Pass F2 testing before any release creation
- Follow proper GitHub issue linking
- Integrate with git-ops-agent for PR management
- Maintain release documentation and change logs