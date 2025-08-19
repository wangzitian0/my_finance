# Scripts Directory

This directory contains utility scripts for various maintenance and setup tasks.

## Scripts

### Data Management
- **`manage_build_data.py`** - Manages build data artifacts and cleanup
- **`add_cik_numbers_to_n100.py`** - Adds CIK numbers to NASDAQ 100 dataset configuration
- **`update_dataset_schemas.py`** - Updates and validates dataset schemas

### Development Tools
- **`p3-completion.zsh`** - ZSH completion script for the p3 command-line tool
- **`fix_pixi_run_calls.py`** - Fixes pixi run calls in codebase for consistency

## Usage

These scripts are typically run manually for maintenance tasks or as part of development workflows. Check individual script documentation for specific usage instructions.

## Dependencies

Scripts in this directory may have dependencies on:
- Core project modules (`common/`, `ETL/`)
- External tools configured in `pixi.toml`
- Configuration files in `data/config/`