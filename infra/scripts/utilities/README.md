# Development Utilities - Tools and Diagnostics

Essential development tools, environment validation utilities, and system diagnostics supporting daily development workflows.

## Overview

This directory provides the foundational utilities that support development activities, environment management, and system troubleshooting. These tools are designed for direct developer use and integration with automated workflows.

## Core Utilities

### Environment Validation
- **`fast_env_check.py`** - 5-second environment health check with parallel validation
- **Service status checking**: Podman machine, Neo4j web interface, Python environment
- **Dependency validation**: Package availability, import testing
- **Quick diagnostics**: Fast fail detection with clear error messages

### Development Helpers
- **Code quality tools**: Integration helpers for formatting, linting, testing
- **Debugging utilities**: Environment introspection, configuration validation
- **Development workflow support**: Session management, state tracking

### System Diagnostics
- **Performance monitoring**: Resource usage tracking, bottleneck identification
- **Troubleshooting tools**: Comprehensive system analysis, issue resolution
- **Configuration validation**: Settings verification, environment consistency

## Key Features

### 1. Fast Environment Validation (`fast_env_check.py`)
**5-second comprehensive environment health check**:
```python
# Parallel service validation with 2-second individual timeouts
✅ Podman Machine: Currently running  
✅ Neo4j Web: Interface responding on localhost:7474
✅ Environment ready for development
```

**Features**:
- **Parallel execution**: All checks run simultaneously for speed
- **Timeout protection**: Individual 2s timeouts, 5s total maximum
- **Clear diagnostics**: Specific error messages with fix suggestions
- **Integration ready**: Used by PR workflows for pre-flight validation

### 2. Service Health Monitoring
**Critical service status checking**:
- **Podman Machine**: Container runtime availability and status
- **Neo4j Database**: Web interface and bolt connection health
- **Python Environment**: Package availability and import testing
- **Development Services**: Additional tool availability checking

### 3. Development Workflow Integration
**Tools supporting daily development**:
- **Pre-commit validation**: Environment readiness before code changes
- **PR preparation**: Environment validation before PR creation
- **Troubleshooting**: Quick problem identification and resolution
- **Session management**: Development session state tracking

## Utility Categories

### Environment Validation Tools
Tools for checking development environment health:
- Service availability checking (Podman, Neo4j, databases)
- Dependency validation (Python packages, system tools)
- Configuration verification (settings, paths, credentials)
- Performance monitoring (resource usage, response times)

### Development Support Tools
Tools supporting daily development activities:
- Code quality helpers (formatting, linting integration)
- Debugging utilities (environment introspection, logging)
- Session management (state tracking, workflow context)
- Configuration management (settings validation, environment setup)

### System Diagnostic Tools
Tools for troubleshooting and system analysis:
- Comprehensive system health checks
- Performance analysis and bottleneck identification
- Error pattern analysis and resolution suggestions
- Service dependency mapping and validation

### Integration Utilities
Tools supporting integration with other system components:
- P3 workflow integration helpers
- CI/CD pipeline utilities
- Infrastructure automation support
- Testing framework integration

## Usage Examples

### Daily Development Validation
```bash
# Quick environment check before starting work
python scripts/utilities/fast_env_check.py

# Expected output:
🚀 Fast Environment Check (5s timeout)
✅ Podman Machine: Currently running
✅ Neo4j Web: Interface responding
✅ All checks passed! Environment ready.
```

### Troubleshooting Environment Issues
```bash
# When environment issues are detected:
❌ Neo4j Web: Not responding on localhost:7474
🔧 Quick fixes:
   • Run: ansible-playbook infra/ansible/start.yml
   
# After fixing:
✅ Neo4j Web: Interface responding
✅ All checks passed! Environment ready.
```

### Integration with P3 Workflows
```python
# Used internally by PR creation workflow
if not validate_environment_for_pr():
    print("❌ PR creation aborted due to environment issues")
    sys.exit(1)
```

## Development Utilities Reference

### Environment Health Check (`fast_env_check.py`)
**Purpose**: Fast environment validation for development workflows
**Timeout**: 5 seconds total, 2 seconds per check
**Checks**: Podman machine, Neo4j web interface, Python environment
**Integration**: Used by PR workflows, manual troubleshooting

```bash
# Usage
python scripts/utilities/fast_env_check.py

# Parallel execution ensures fast results
# Clear error messages with specific fix suggestions
# Exit codes: 0 = success, 1 = validation failed
```

### Service Status Validation
**Purpose**: Individual service health checking
**Scope**: All critical development services
**Output**: Detailed status with diagnostic information
**Integration**: Standalone use, workflow integration

### Dependency Validation
**Purpose**: Development dependency verification
**Scope**: Python packages, system tools, configuration files
**Output**: Missing dependencies, version conflicts, configuration issues
**Integration**: Pre-development validation, CI/CD pipeline checks

## Integration Points

### With P3 Workflow System
- **Pre-flight validation**: Environment checks before PR creation
- **Command integration**: Used by `p3 debug` and `p3 ready` commands
- **Error diagnostics**: Detailed troubleshooting for workflow failures

### With Infrastructure Components
- **Service coordination**: Integration with `infra/environment/` management
- **Monitoring integration**: Health status reporting to monitoring systems
- **Automation support**: Used by deployment and setup scripts

### With Development Workflows
- **IDE integration**: Environment status for development tools
- **Automated workflows**: Pre-commit hooks, CI/CD pipeline validation
- **Manual troubleshooting**: Developer-friendly diagnostic tools

## Quality Standards

### Performance Requirements
- **Speed**: All utilities must complete within reasonable timeframes
- **Efficiency**: Minimal resource usage, parallel execution where beneficial
- **Reliability**: Consistent results across different environments
- **Responsiveness**: Clear progress indication for longer operations

### User Experience Standards
- **Clear output**: Human-readable status messages and error descriptions
- **Actionable errors**: Specific fix suggestions for detected issues
- **Consistent interface**: Standard command-line patterns across utilities
- **Documentation**: Usage examples and troubleshooting guides

### Integration Standards
- **Exit codes**: Standard success/failure indication for automation
- **Output format**: Structured output for programmatic consumption
- **Configuration**: Environment-aware configuration handling
- **Error handling**: Graceful failure with meaningful error messages

## Maintenance Guidelines

### Adding New Utilities
1. **Identify use case**: Developer productivity, system diagnostics, workflow support
2. **Define scope**: Clear purpose, input/output specifications
3. **Implement standards**: Performance, user experience, integration requirements
4. **Add documentation**: Usage examples, integration patterns

### Quality Assurance
- **Testing**: Unit tests, integration tests, environment variation testing
- **Performance**: Execution time monitoring, resource usage optimization
- **User feedback**: Developer experience validation, usability testing
- **Maintenance**: Regular updates, deprecation management

---

**Integration References**:
- **P3 Commands**: [Main README.md](../../README.md#p3-command-system) for workflow integration
- **Infrastructure**: [infra/README.md](../../infra/README.md) for service management
- **Workflow Scripts**: [scripts/workflow/README.md](../workflow/README.md) for automation integration