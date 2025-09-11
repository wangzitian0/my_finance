# Workflow Scripts - P3 Automation and CI/CD Integration

Automated workflow scripts supporting P3 command system integration, PR creation workflows, and continuous integration processes.

## Overview

This directory contains scripts that implement the P3 workflow system's automation layer, bridging between user intent ("I want to create a PR") and the underlying technical operations (testing, validation, git operations).

## Core Components

### PR Creation and Testing Integration
- **PR workflow automation**: End-to-end PR creation with mandatory testing
- **Testing orchestration**: F2/M7/N100/V3K scope-based test execution
- **Quality gate enforcement**: Code formatting, environment validation, build verification
- **Git integration**: Worktree-safe git operations, branch management

### CI/CD Pipeline Support
- **Build automation**: Dataset generation, model validation, test execution
- **Deployment coordination**: Release preparation, artifact management
- **Environment synchronization**: Development, testing, production environment alignment
- **Monitoring integration**: Build status tracking, failure notification

### P3 Command Implementation Support
- **Command routing logic**: Supporting P3 CLI command execution
- **Scope management**: Testing scope configuration and execution
- **Workflow state management**: Session tracking, result caching
- **Error handling**: Graceful failure management, recovery procedures

## Key Features

### 1. Intent-Based Automation
**Translating user intent into technical operations**:
- `p3 ship "title" 123` → Complete PR creation workflow with testing
- Automatic scope detection (F2 if no recent tests, otherwise reuse results)
- Smart git operations (rebase, force-push with lease, PR creation)
- Comprehensive validation (environment, tests, quality gates)

### 2. Worktree-Safe Operations
**Git operations optimized for worktree environments**:
- Safe main branch synchronization (fetch+rebase vs checkout+reset)
- Worktree detection and environment variable handling
- Independent Python environment per worktree
- Data loss prevention in multi-worktree scenarios

### 3. Testing Integration
**Comprehensive validation before PR creation**:
- **F2 Fast Validation**: 2 companies, DeepSeek 1.5b, 2-5 minutes
- **M7 Complete Testing**: Magnificent 7 companies, 10-20 minutes
- **Environment validation**: Services, dependencies, configuration
- **Code quality checks**: Formatting, linting, test execution

## Script Categories

### Primary Workflow Scripts
Scripts that implement core P3 workflow functionality:
- PR creation with testing integration
- Build automation and validation
- Release workflow management
- Quality gate implementation

### CI/CD Integration Scripts
Scripts supporting continuous integration/deployment:
- Pipeline orchestration and coordination
- Build artifact management
- Environment synchronization
- Deployment automation support

### Testing Orchestration Scripts
Scripts managing test execution and validation:
- Scope-based test configuration
- Test result aggregation and reporting
- Environment validation and setup
- Failure analysis and recovery

### Workflow State Management
Scripts handling workflow state and session management:
- Test result caching and reuse
- Session state tracking
- Workflow resumption after failures
- Configuration persistence

## Usage Patterns

### Typical PR Creation Workflow
```bash
# User executes
p3 ship "Add new feature" 123

# Workflow script orchestration:
# 1. Environment validation (fast_env_check integration)
# 2. Git synchronization (worktree-safe operations)
# 3. Code formatting (black, isort automation)
# 4. Test execution (F2 scope by default)
# 5. PR creation (gh CLI integration)
# 6. Commit message updates (test markers, PR URLs)
```

### Testing Scope Management
```bash
# Scripts handle scope-specific testing:
# F2: Fast validation (2 companies, 2-5min)
# M7: Complete testing (7 companies, 10-20min)
# N100: Large-scale validation (100 companies, 1-3hr)
# V3K: Production testing (3000+ companies, 6-12hr)
```

### Error Handling and Recovery
```bash
# Scripts provide graceful error handling:
# - Environment issues → Diagnostic messages, fix suggestions
# - Test failures → Detailed failure analysis, retry options
# - Git conflicts → Safe conflict resolution, manual intervention prompts
# - Build failures → Artifact preservation, debugging information
```

## Integration Points

### With P3 CLI System
- **Command implementation**: Scripts provide the actual implementation for P3 commands
- **Scope management**: Testing scope configuration and execution logic
- **Environment integration**: Worktree isolation, Python environment switching

### With Infra Components
- **Git operations**: Integration with `infra/git-ops/` for repository management
- **Environment management**: Coordination with `infra/environment/` for service setup
- **CI/CD workflows**: Integration with `infra/workflows/` for deployment automation

### With Scripts Utilities
- **Environment validation**: Using `scripts/utilities/fast_env_check.py`
- **Development tools**: Integration with code quality and debugging utilities
- **System diagnostics**: Leveraging troubleshooting and monitoring tools

## Development Guidelines

### Adding New Workflow Scripts
1. **Identify workflow stage**: PR creation, testing, CI/CD, state management
2. **Follow P3 integration patterns**: Environment handling, error management
3. **Implement worktree safety**: Use worktree-safe git operations
4. **Add comprehensive error handling**: Clear messages, recovery suggestions

### Script Quality Standards
- **Worktree compatibility**: All git operations must be worktree-safe
- **Error resilience**: Graceful handling of environment/service failures
- **Progress reporting**: Clear status updates for long-running operations
- **State management**: Proper cleanup, session state handling

### Testing and Validation
- **Unit tests**: Individual script component testing
- **Integration tests**: Full workflow testing with P3 CLI
- **Environment testing**: Multiple environment configurations
- **Failure testing**: Error condition handling and recovery

## Maintenance and Monitoring

### Performance Monitoring
- **Workflow execution times**: Tracking command performance
- **Failure rates**: Monitoring success/failure patterns
- **Resource usage**: CPU, memory, network utilization during workflows

### Quality Assurance
- **Code review**: All workflow scripts require review
- **Documentation**: Usage examples, troubleshooting guides
- **Testing coverage**: Comprehensive test suite for critical workflows

---

**Integration References**:
- **P3 CLI**: [Main README.md](../../README.md#p3-command-system) for complete command reference
- **Infrastructure**: [infra/README.md](../../infra/README.md) for service management
- **Company Policies**: [CLAUDE.md](../../CLAUDE.md) for workflow compliance