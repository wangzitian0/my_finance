# Configuration Management Scripts

This directory contains scripts for configuration management, validation, and migration.

## Scripts Overview

- **`migrate_config_paths.py`** - Migrates configuration paths to centralized system
- **`migrate_hardcoded_paths.py`** - Removes hardcoded paths in favor of DirectoryManager
- **`fix_pixi_run_calls.py`** - Updates pixi run calls to use proper P3 workflow
- **`validate_io_compliance.sh`** - Validates I/O compliance with SSOT DirectoryManager

## Purpose

These scripts support configuration management and compliance:
- Configuration centralization to `common/config/`
- SSOT DirectoryManager migration and validation
- P3 workflow compliance enforcement
- I/O pattern standardization and validation

## Usage

Configuration scripts support system maintenance:
- Run `validate_io_compliance.sh` before PR creation
- Use migration scripts during system upgrades
- Execute through P3 workflow system when possible

## Compliance Requirements

All configuration operations must:
- Use centralized `common/config/` for all configurations
- Follow SSOT DirectoryManager patterns exclusively
- Validate against I/O compliance standards
- Maintain English-only standard for all technical content

## Validation Command

```bash
bash scripts/config/validate_io_compliance.sh
```

This command must pass before any PR creation to ensure I/O compliance.