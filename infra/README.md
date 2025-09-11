# Infra - Infrastructure and System Management

**Comprehensive infrastructure management system organized by functional domains with two-layer modularity architecture.**

## 🏗️ Modular Architecture

Following the **two-tier principle** from CLAUDE.md, this infrastructure system is organized into specialized modules with clear separation of concerns:

### Git Operations (`git-ops/`)
**Centralized Git workflow management and automation**:
- `install_git_hooks.py` - Consolidated Git hooks installation (P3 workflow enforcement + branch validation)
- `cleanup_merged_branches.py` - Automated Git branch cleanup and repository hygiene
- **Git workflow integration**: Pre-push hooks, commit message validation, branch management
- **Worktree compatibility**: Support for git worktree environments and safety protocols

### CI/CD Workflows (`workflows/`)
**Automated workflow orchestration and PR management**:
- `pr_creation.py` - Pull Request creation with mandatory testing (F2 fast-build validation)
- **Testing integration**: End-to-end testing automation with scope-based validation
- **Quality gates**: Code formatting, environment validation, build verification
- **Worktree-safe operations**: Git operations optimized for worktree environments

### Environment Management (`environment/`)
**Development environment setup and monitoring**:
- `env_status.py` - Comprehensive environment status checking and diagnostics
- `shutdown_all.py` - Service shutdown and cleanup procedures
- **Service orchestration**: Podman, Neo4j, Python environment coordination
- **Health monitoring**: Fast environment validation, dependency checking

### Deployment Configuration
**Production deployment and infrastructure as code**:
- `ansible/` - Automated deployment configuration and playbooks
- `k8s/` - Kubernetes deployment manifests and configuration
- `deployment.md` - Deployment procedures and troubleshooting guide
- **Infrastructure automation**: Service provisioning, configuration management

### Legacy Tools (Root Level)
**Transitional tools and legacy script support**:
- `commit_data_changes.py` - Data submodule commit (deprecated in P3 v2)
- `cleanup_obsolete_files.py` - Repository cleanup and file management
- `git-workflow-optimization.md` - Git workflow documentation and best practices

### Worktree Python Environment Isolation
**P3 CLI Worktree Isolation System** - Complete Python environment isolation per worktree

**Core Features:**
- **Zero Configuration**: Entering worktree automatically activates isolated environment
- **Complete Isolation**: Each worktree has completely independent Python environment  
- **Pixi-Based**: All environment management through pixi
- **Simple Workflow**: `python p3.py <command>` automatically works
- **Global Tool Reuse**: ansible/docker shared through pixi tasks
- **Repository Internal**: No external file dependencies

**Usage**: See main [README.md P3 Command System](../README.md#p3-command-system) for complete workflow reference.

**Architecture:**
```
infra/
├── system/                    # System environment and monitoring
├── data/                      # Data management and pipeline tools
├── git/                       # Git operations and release management
├── hrbp/                      # HRBP system automation and hooks
├── p3/                        # P3 command system maintenance
├── development/               # Development tools and utilities
├── deployment/                # Deployment automation and K8s
└── legacy/                    # Legacy components (transition)
```

## 📁 Module Organization

### System Environment Management (`system/`)
**Purpose**: Core environment status, validation, and monitoring
- `env_status.py` - Comprehensive environment status validation
- `environment_monitor.py` - Real-time system monitoring
- `fast_env_check.py` - Quick fail-fast environment validation
- `config_summary.py` - System configuration reporting
- `workflow_ready.py` - P3 ready command implementation (start working)
- `workflow_reset.py` - P3 reset command implementation (fix environment)
- `workflow_debug.py` - P3 debug command implementation (diagnose issues)
- `worktree_isolation.py` - Worktree Python environment isolation

**Usage**:
```bash
python infra/system/env_status.py           # Full environment status
python infra/system/fast_env_check.py       # Quick validation (5s timeout)
python infra/system/config_summary.py       # Configuration overview
python infra/system/workflow_ready.py       # P3 ready workflow
python infra/system/workflow_reset.py       # P3 reset workflow
python infra/system/workflow_debug.py       # P3 debug workflow
```

### Data Management (`data/`)
**Purpose**: Build data management, migration, and pipeline utilities
- `manage_build_data.py` - Build directory lifecycle management
- `data_migration_tools.py` - Data structure migration utilities
- `pipeline_manager.py` - ETL pipeline coordination

**Usage**:
```bash
python infra/data/manage_build_data.py create    # Create new build
python infra/data/manage_build_data.py release   # Promote to release
```

### Git Operations & Release Management (`git/`)
**Purpose**: Git workflow automation and release coordination
- `release_manager.py` - Comprehensive release management system
- `git_workflow_tools.py` - Git automation utilities
- `branch_management.py` - Branch lifecycle automation

**Usage**:
```bash
python infra/git/release_manager.py create      # Create release
python infra/git/release_manager.py validate    # Validate release
```

### HRBP System Integration (`hrbp/`)
**Purpose**: HRBP automation, hooks, and system validation
- `hrbp_automation.py` - Legacy HRBP CLI interface
- `hrbp_comprehensive_cli.py` - Full HRBP functionality
- `hrbp_system_validator.py` - Comprehensive HRBP validation
- `git_hooks/` - Git hook management
  - `install_hrbp_hooks.py` - Git hooks installation
  - `post_merge_hrbp_hook.py` - Post-merge automation

**Usage**:
```bash
python infra/hrbp/hrbp_automation.py status     # HRBP status
python infra/hrbp/git_hooks/install_hrbp_hooks.py  # Install hooks
python infra/hrbp/hrbp_system_validator.py      # Full validation
```

### P3 Command System (`p3/`)
**Purpose**: P3 CLI maintenance, development, and optimization (infra-ops-agent authority per CLAUDE.md)
- Core P3 command implementations
- Workflow optimization tools
- System integration components
- Performance monitoring utilities

**Responsibility**: As per CLAUDE.md organizational authority, **infra-ops-agent** has exclusive technical responsibility for:
- P3 CLI codebase maintenance and enhancement
- P3 command functionality development and testing
- P3 system architecture evolution and optimization
- P3 performance analysis and system reliability

### Development Tools (`development/`)
**Purpose**: Development utilities, cleanup, and maintenance tools
- `directory_cleanup_executor.py` - Directory hygiene validation
- `code_quality_tools.py` - Code quality automation
- `maintenance_utilities.py` - System maintenance automation
- `workflow_check.py` - P3 check command implementation (validate code)
- `validate_io_compliance.py` - I/O compliance validation (Python wrapper)
- `validate_io_compliance.sh` - I/O compliance validation (shell script)

**Usage**:
```bash
python infra/development/directory_cleanup_executor.py  # Post-cleanup validation
python infra/development/workflow_check.py f2           # P3 check workflow
python infra/development/validate_io_compliance.py      # I/O compliance check
bash infra/development/validate_io_compliance.sh        # Direct shell execution
```

### Deployment Automation (`deployment/`)
**Purpose**: Infrastructure deployment and orchestration
- `ansible/` - Ansible deployment configurations
- `k8s/` - Kubernetes deployment manifests
- `deployment_tools.py` - Deployment automation utilities

**Usage**:
```bash
ansible-playbook infra/deployment/ansible/setup.yml
kubectl apply -f infra/deployment/k8s/
```

## 🔄 Migration from Scripts Directory

**Scripts-to-Infra Migration Status** (Issue #129): 
- ✅ **COMPLETED**: All workflow and infrastructure scripts migrated to appropriate modules
- ✅ **P3 Integration**: P3 CLI updated to use new infra/ paths
- ✅ **Module Organization**: Scripts properly categorized by functional domain
- ✅ **Backward Compatibility**: All existing functionality preserved
- ✅ **Path Updates**: Internal references updated to new infra/ locations
- ✅ **Documentation**: Updated usage examples and module descriptions
- ✅ **Validation**: Migration validation script created for future verification
- ✅ **Final Cleanup**: Duplicate files removed, migration fully completed (2025-09-10)

**Migration Mapping**:
```yaml
scripts/ → infra/ migration:
  # System environment workflows
  scripts/workflow_ready.py → infra/system/workflow_ready.py
  scripts/workflow_reset.py → infra/system/workflow_reset.py
  scripts/workflow_debug.py → infra/system/workflow_debug.py
  scripts/worktree_isolation.py → infra/system/worktree_isolation.py
  
  # Development tools and validation
  scripts/workflow_check.py → infra/development/workflow_check.py
  scripts/validate_io_compliance.sh → infra/development/validate_io_compliance.sh
  
  # P3 CLI components
  scripts/p3/p3_version_simple.py → infra/p3/p3_version_simple.py
  scripts/p3/.p3_version.json → infra/p3/.p3_version.json
  
  # Previously migrated components
  scripts/fast_env_check.py → infra/system/fast_env_check.py
  scripts/config_summary.py → infra/system/config_summary.py
  scripts/manage_build_data.py → infra/data/manage_build_data.py
  scripts/release_manager.py → infra/git/release_manager.py
  scripts/validate_hrbp_system.py → infra/hrbp/hrbp_system_validator.py
  scripts/install_hrbp_hooks.py → infra/hrbp/git_hooks/install_hrbp_hooks.py
  scripts/post_merge_hrbp_hook.py → infra/hrbp/git_hooks/post_merge_hrbp_hook.py
  scripts/directory_cleanup_executor.py → infra/development/directory_cleanup_executor.py
  scripts/p3/ → infra/p3/
```

## 🎯 Two-Layer Modularity Benefits

Following CLAUDE.md's **two-layer modularity principle**:

1. **Clear Module Boundaries**: Each module (system/, data/, git/, etc.) has distinct responsibilities
2. **Logical Grouping**: Related functionality clustered together 
3. **Simplified Navigation**: Intuitive module names matching functional domains
4. **Scalable Architecture**: Easy to add new modules or expand existing ones
5. **Import Clarity**: Clean import paths: `from infra.system import env_status`

## 🚀 P3 Integration

**P3 CLI Maintenance Authority**: Per CLAUDE.md, **infra-ops-agent** has exclusive responsibility for P3 CLI technical maintenance, including:
- Command interface development and optimization
- Workflow integration and coordination
- System architecture evolution
- Performance monitoring and troubleshooting

**Workflow Integration**:
```bash
p3 ready            # Uses infra/system/ for environment validation
p3 debug            # Uses infra/system/env_status.py for diagnostics
p3 ship "title" 123 # Uses infra/git/ for release management
```

## 📋 Usage Examples

### Daily Development Workflow
```bash
# Environment validation
python infra/system/fast_env_check.py

# Build management  
python infra/data/manage_build_data.py create

# Git operations
python infra/git/release_manager.py create --name daily-build

# HRBP automation
python infra/hrbp/hrbp_automation.py status
```

### System Administration
```bash
# Full environment status
python infra/system/env_status.py

# HRBP system validation
python infra/hrbp/hrbp_system_validator.py --verbose

# Directory hygiene check
python infra/development/directory_cleanup_executor.py
```

## 🛡️ SSOT Compliance

**Directory Manager Integration**: All infra modules use `common.core.directory_manager` for SSOT-compliant file operations, ensuring:
- Centralized path management through DataLayer enums
- Configuration consistency via `common/config/`
- Build data organization in standardized layers

**Validation**: All modules include SSOT compliance validation before file operations.

## ✅ Migration Completion Summary

**Scripts-to-Infra Migration (Issue #129) - COMPLETED**

This migration successfully transformed the monolithic `scripts/` directory into a well-organized modular infrastructure system following CLAUDE.md's two-layer modularity principle:

### Key Achievements:
1. **Modular Organization**: All scripts categorized into logical functional modules
2. **P3 Workflow Integration**: Seamless integration with existing P3 command system  
3. **Clear Ownership**: Each module has defined responsibilities and authorities
4. **SSOT Compliance**: All modules follow centralized configuration patterns
5. **Documentation**: Comprehensive usage examples and module descriptions
6. **Future-Proof**: Scalable architecture for adding new infrastructure components

### Validation Tools:
- `python infra/development/validate_migration_complete.py` - Verify migration completeness
- `python infra/development/cleanup_old_scripts.py` - Clean up old scripts directory

---

**Governance**: Infrastructure system management follows CLAUDE.md organizational authority with **infra-ops-agent** leadership for technical components and **hrbp-agent** oversight for policy compliance.