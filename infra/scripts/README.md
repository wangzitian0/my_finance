# Scripts - Development Tools and Utilities

Central directory for development scripts, workflow automation, and utility tools supporting the financial analysis platform.

## Directory Structure

### HRBP System Management (`hrbp/`)
- **Agent performance monitoring** - Validation, tracking, and compliance systems
- **Git hook automation** - Post-merge hooks for PR tracking and cycle management
- **System validation tools** - Comprehensive HRBP system health checks
- **Task execution tracking** - Agent failure capture and analysis

### Data Processing (`data/`)
- **SEC data management** - CIK number integration and formatting
- **Dataset configuration** - N100 and VTI configuration normalization
- **Build data management** - Dataset lifecycle and directory management
- **Schema management** - Dataset schema updates and validation

### Release Management (`release/`)
- **Release orchestration** - Version control and release preparation
- **Release testing** - Comprehensive validation across all scopes
- **Release demonstrations** - System functionality validation and testing

### Configuration Management (`config/`)
- **ETL configuration validation** - Unified ETL configuration checking tool (`check_etl_config.py`)
- **Path migration tools** - Hardcoded path elimination and centralization
- **I/O compliance validation** - SSOT DirectoryManager enforcement
- **Configuration migration** - Legacy configuration system updates
- **Pixi workflow fixes** - P3 workflow compliance improvements

### Demo and Testing (`demos/`)
- **Claude Code integration** - Hooks system demonstrations and testing
- **System validation** - Development environment verification
- **Integration testing** - Workflow and system functionality validation

### Workflow Automation (`workflow/`)
- **P3 workflow integration scripts** - Supporting automated PR creation and testing workflows
- **CI/CD pipeline scripts** - Build automation, testing orchestration
- **Core P3 commands** - Check, debug, ready, reset implementations

### Development Utilities (`utilities/`)
- **Environment validation tools** - Fast environment checks, dependency validation
- **Development helpers** - Code quality tools, debugging utilities
- **System diagnostics** - Performance monitoring, troubleshooting scripts
- **Git workflow tools** - Hook checking and repository management

### P3 Command System (`p3/`)
- **P3 CLI core components** - Version management and completion scripts
- **Shell integration** - ZSH completion and shell environment support

### Git Integration (`hooks/`)
- **Claude Code hooks** - Error handling, response processing, tool usage tracking
- **User interaction hooks** - Prompt submission and workflow integration

## Key Features

### 1. P3 Workflow System
**Complete development lifecycle automation**:
- **Intent-based commands**: "Start working" (`p3 ready`), "Test code" (`p3 test`), "Create PR" (`p3 ship`)
- **Scope-based testing**: F2 (fast), M7 (complete), N100 (validation), V3K (production)
- **Worktree isolation**: Independent Python environments per feature branch
- **Automated PR creation**: End-to-end testing → PR creation → validation

### 2. Environment Management
**Robust development environment support**:
- **Fast validation**: 5-second environment health checks
- **Service orchestration**: Podman, Neo4j, Python environment coordination
- **Dependency management**: Pixi-based package management
- **Troubleshooting tools**: Comprehensive diagnostic capabilities

### 3. Code Quality Automation
**Integrated quality assurance**:
- **Code formatting**: Black, isort automation
- **Lint checking**: Comprehensive code analysis
- **Test automation**: Unit tests, integration tests, end-to-end validation
- **Build validation**: Data pipeline testing, model validation

## Usage Examples

### Daily Development Workflow
```bash
# Start work session
p3 ready                    # "I want to start working"

# Development cycle
p3 check f2                 # "Validate my code quickly"
# ... make changes ...
p3 test f2                  # "Run comprehensive tests"

# Create PR
p3 ship "Feature title" 123 # "Publish my work" (issue #123)
```

### Environment Troubleshooting
```bash
# Quick health check
python scripts/utilities/fast_env_check.py

# Comprehensive diagnostics
p3 debug

# Reset environment
p3 reset
```

### ETL Configuration Management (Issue #278)
```bash
# Check all ETL configurations
python infra/scripts/config/check_etl_config.py --all

# Check specific configurations
python infra/scripts/config/check_etl_config.py --stock-list f2 --details
python infra/scripts/config/check_etl_config.py --data-source yfinance
python infra/scripts/config/check_etl_config.py --scenario development

# Test runtime configuration combinations
python infra/scripts/config/check_etl_config.py --runtime f2 yfinance development

# Run ETL configuration examples
python infra/scripts/examples/etl_config_example.py

# Configuration migration (if needed)
python infra/scripts/migrate_etl_config.py --migrate
python infra/scripts/migrate_etl_config.py --validate
```

### System Management and Validation
```bash
# HRBP system validation
python scripts/hrbp/validate_hrbp_system.py

# I/O compliance validation
bash scripts/config/validate_io_compliance.sh

# Data processing
python scripts/data/add_cik_numbers_to_n100.py
python scripts/data/normalize_n100_config.py

# Release management
python scripts/release/release_manager.py list
python scripts/release/demo_release_system.py
```

### Development Utilities
```bash
# Code quality
p3 check                    # Format, lint, quick validation
p3 test m7                  # Comprehensive testing (M7 scope)

# Environment validation
python scripts/utilities/fast_env_check.py

# Git hooks validation
python scripts/utilities/check_git_hooks.py
```

## Integration with Parent Systems

### With Infra Directory
- **Git operations**: Infra git-ops/ provides PR creation, branch management
- **Environment setup**: Infra environment/ provides service management
- **CI/CD workflows**: Infra workflows/ provides deployment automation

### With P3 CLI System
- **Command routing**: Scripts implement P3 command logic
- **Scope management**: Testing scope implementations (F2, M7, N100, V3K)
- **Environment integration**: Worktree isolation, Python environment switching

### With Main Repository
- **Workflow enforcement**: Git hooks ensure P3 workflow compliance
- **Quality gates**: Pre-PR testing, code formatting, validation
- **Issue integration**: GitHub issue linking, automated tracking

## Development Guidelines

### Adding New Scripts
1. **Determine category**: hrbp/, data/, release/, config/, demos/, workflow/, utilities/, p3/, or hooks/
2. **Follow naming conventions**: snake_case, descriptive names
3. **Include documentation**: Docstrings, usage examples, update subdirectory README
4. **Test thoroughly**: Unit tests, integration with P3 workflow
5. **Update references**: Check and update any cross-references to moved scripts

### Script Organization Principles
- **Single responsibility**: Each script has one clear purpose within its category
- **Categorical organization**: Scripts grouped by functional domain (HRBP, data, release, etc.)
- **Reusability**: Common functionality in shared utilities subdirectory
- **P3 integration**: Scripts should work within P3 workflow system
- **Error handling**: Robust error handling with clear messages
- **Cross-references**: Maintain accurate paths in documentation and scripts

### Quality Standards
- **Python 3.8+ compatibility**: Modern Python features and type hints
- **Command-line interface**: Argparse-based CLI for user-facing scripts
- **Logging and debugging**: Comprehensive logging for troubleshooting
- **Documentation**: README files for complex subdirectories

## Responsibilities

- **HRBP System Management**: Agent monitoring, compliance tracking, system validation
- **Data Processing**: SEC data integration, dataset management, schema maintenance
- **Release Management**: Version control, release testing, deployment coordination
- **Configuration Management**: Path migration, I/O compliance, system configuration
- **Demo and Testing**: System validation, integration testing, functionality verification
- **Workflow Automation**: P3 command implementations, CI/CD scripts
- **Environment Management**: Setup, validation, troubleshooting tools
- **Development Support**: Utilities, diagnostics, debugging tools
- **Git Integration**: Hooks, workflow enforcement, repository management
- **Documentation**: Script usage guides, troubleshooting procedures, README maintenance

---

**For detailed implementation procedures, see:**
- **P3 Command System**: [Main README.md](../README.md#p3-command-system) for complete workflow reference
- **Company Policies**: [CLAUDE.md](../CLAUDE.md) for governance and compliance
- **Infrastructure**: [infra/README.md](../infra/README.md) for service management