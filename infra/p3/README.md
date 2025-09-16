# P3 Command System Module

**P3 CLI maintenance, development, and optimization under infra-ops-agent authority**

## Authority and Governance

Per **CLAUDE.md organizational authority**, **infra-ops-agent** has exclusive technical responsibility for:

- **P3 CLI codebase maintenance and enhancement**
- **P3 command functionality development and testing**  
- **P3 system architecture evolution and optimization**
- **P3 performance analysis and system reliability**
- **P3 troubleshooting and technical support**

## Module Structure

```
infra/p3/
├── commands/              # Individual P3 command implementations
├── core/                  # Core P3 system functionality
├── optimization/          # Performance and workflow optimization
├── testing/               # P3 system testing and validation
└── integration/           # System integration components
```

## P3 Command Architecture

**Streamlined 8-Workflow System**: The P3 CLI has evolved from a complex 49-command system to a streamlined 8-workflow system with advanced worktree Python isolation capabilities.

### Core Commands
1. **`p3 ready`** - Complete environment setup and service initialization
2. **`p3 check [scope]`** - Code validation (format, lint, basic tests)
3. **`p3 test [scope]`** - Comprehensive end-to-end testing
4. **`p3 ship "title" issue`** - PR creation with testing validation
5. **`p3 reset`** - System reset and recovery
6. **`p3 build [scope]`** - Dataset generation and processing
7. **`p3 version [level]`** - Version management and information

### Scope System
- **f2**: 2 companies, 2-5min (development, PR validation)
- **m7**: 7 companies, 10-20min (integration testing, release prep)
- **n100**: 100 companies, 1-3hr (production validation)
- **v3k**: 3000+ companies, 6-12hr (full production datasets)

## Technical Responsibilities

### Core P3 System Maintenance
- Command interface stability and evolution
- Workflow optimization and user experience
- Environment management and automation
- Infrastructure integration and deployment

### Performance Optimization
- Command execution performance monitoring
- System resource utilization analysis
- Workflow efficiency improvements
- Bottleneck identification and resolution

### System Integration
- P3 integration with git workflows and CI/CD pipelines
- Multi-agent coordination through P3 commands
- Environment isolation and worktree management
- Cross-platform compatibility

### Development and Testing
- P3 command development and testing
- System architecture evolution
- Feature implementation and validation
- Regression testing and quality assurance

## Usage and Integration

### Daily Development Integration
```bash
# Environment setup
p3 ready                    # infra/system/ environment validation

# Development cycle
p3 check f2                 # Quick validation during development
p3 test f2                  # Comprehensive testing before PR

# Release workflow  
p3 ship "Title" 123         # infra/git/ release management
```

### System Administration
```bash
# Diagnostics and troubleshooting
p3 reset                    # infra/system/env_status.py integration

# System maintenance
p3 reset                    # Complete system reset and recovery
p3 version                  # Version information and management
```

## Governance and Escalation

### Technical Issues
- **Primary Contact**: infra-ops-agent
- **Escalation Path**: Technical issues route directly to infra-ops-agent
- **Support**: P3 troubleshooting and technical support

### Policy Compliance
- **Primary Contact**: hrbp-agent  
- **Governance**: P3 workflow policy compliance monitoring
- **Violations**: Policy violation tracking and remediation

### Integration Coordination
- **Primary Contact**: agent-coordinator
- **Workflow**: P3 workflow integration and orchestration
- **Optimization**: Multi-agent P3 workflow optimization analysis

## Migration Notes

**Scripts-to-Infra Migration**: This module consolidates P3 system components previously scattered across scripts/ directory into a unified, maintainable structure under infra-ops-agent governance.

---

**Governance**: P3 Command System management follows CLAUDE.md organizational authority with **infra-ops-agent** technical leadership and **hrbp-agent** policy oversight.