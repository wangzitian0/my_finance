# Environment Management - Development Environment Setup and Monitoring

Comprehensive development environment management, service orchestration, and system health monitoring supporting the financial analysis platform.

## Overview

This directory provides essential environment management tools for setting up, monitoring, and maintaining the development environment. These tools ensure consistent, reliable development experiences across different systems and configurations.

## Core Components

### Environment Status Monitoring (`env_status.py`)
**Unified environment health checking and service status validation**:
- **Service status verification**: Minikube, Neo4j, Pixi environment monitoring
- **Comprehensive diagnostics**: IP addresses, connection details, service health
- **Quick command reference**: Common development operations and troubleshooting
- **Integration ready**: Used by P3 commands for environment validation

### Service Management (`shutdown_all.py`)
**Graceful service shutdown and environment cleanup**:
- **Service coordination**: Orderly shutdown of all development services
- **Resource cleanup**: Container cleanup, process termination, resource release
- **Safe shutdown**: Prevents data loss, ensures clean environment state
- **Reset integration**: Used by P3 reset command for complete environment reset

## Key Features

### 1. Comprehensive Environment Validation
**Complete development environment health monitoring**:

**Service Status Checking**:
```python
# Minikube cluster validation
def check_minikube():
    if success and "Running" in output:
        print("✅ Minikube is running")
        print(f"📍 Minikube IP: {ip}")
        return ip
    else:
        print("❌ Minikube is not running")
        print("💡 Start with: p3 ready")
```

**Neo4j Database Monitoring**:
```python
# Neo4j service and connectivity validation
def check_neo4j(minikube_ip):
    if success and "Running" in output:
        print("✅ Neo4j is running")
        print(f"🌐 Web Interface: http://{minikube_ip}:30474")
        print(f"🔌 Bolt Connection: bolt://{minikube_ip}:30687")
        print("🔑 Credentials: neo4j / finance123")
```

**Development Environment Verification**:
```python
# Pixi environment and project configuration
def check_pixi():
    if "PIXI_ENV_DIR" in os.environ and Path("pixi.toml").exists():
        print("✅ Pixi environment is active")
        print("✅ Project configuration found")
        return True
```

### 2. Service Orchestration
**Coordinated management of all development services**:

**Service Dependencies**:
- **Minikube**: Container runtime and Kubernetes cluster
- **Neo4j**: Graph database for financial data relationships
- **Pixi**: Python environment and dependency management
- **Supporting services**: Additional tools and monitoring systems

**Health Monitoring**:
- **Connectivity testing**: Service accessibility and response validation
- **Resource monitoring**: CPU, memory, disk usage tracking
- **Performance validation**: Response time monitoring, throughput testing
- **Dependency verification**: Service interdependency health checking

### 3. Development Workflow Integration
**Seamless integration with P3 workflow system**:

**Command Integration**:
- **p3 ready**: Uses environment setup and validation tools
- **p3 debug**: Leverages comprehensive diagnostics and status checking
- **p3 reset**: Integrates with service shutdown and cleanup procedures
- **Workflow validation**: Pre-flight checks for PR creation and testing

**Troubleshooting Support**:
```python
def show_quick_commands():
    print("🚀 Quick Commands:")
    print("  Environment:")
    print("    p3 ready    - Start all services")
    print("    p3 debug    - This status check")
    print("    p3 reset    - Reset everything")
```

## Environment Management Tools

### Status Checker (`env_status.py`)
**Comprehensive development environment status monitoring**:

**Features**:
- **Multi-service validation**: Minikube, Neo4j, Pixi environment checking
- **Detailed diagnostics**: IP addresses, ports, credentials, connection strings
- **Quick command guide**: Context-aware command suggestions
- **Integration support**: Exit codes and structured output for automation

**Usage**:
```bash
# Complete environment status check
python infra/environment/env_status.py

# Expected output:
🩺 Development Environment Status
==================================================
🔍 Checking Minikube...
  ✅ Minikube is running
  📍 Minikube IP: 192.168.49.2

🔍 Checking Neo4j...
  ✅ Neo4j is running
  🌐 Web Interface: http://192.168.49.2:30474
  🔌 Bolt Connection: bolt://192.168.49.2:30687
  🔑 Credentials: neo4j / finance123

🔍 Checking Pixi...
  ✅ Pixi environment is active
  ✅ Project configuration found

✅ Environment is ready for development!
```

### Service Shutdown (`shutdown_all.py`)
**Graceful service shutdown and environment cleanup**:

**Shutdown Process**:
1. **Application services**: Graceful shutdown of running applications
2. **Database services**: Safe Neo4j shutdown with data persistence
3. **Container runtime**: Minikube cluster shutdown and cleanup
4. **Environment cleanup**: Temporary file cleanup, resource release

**Safety Features**:
- **Confirmation prompts**: User confirmation for destructive operations
- **Data protection**: Ensures data persistence before shutdown
- **Resource cleanup**: Complete cleanup of temporary resources
- **Recovery preparation**: Environment prepared for clean restart

## Service Configuration Details

### Minikube Configuration
**Kubernetes cluster setup for local development**:
- **Cluster management**: Start, stop, status monitoring
- **Resource allocation**: CPU, memory, disk space management
- **Network configuration**: Port forwarding, service exposure
- **Integration**: Container registry, persistent volumes

### Neo4j Database Setup
**Graph database configuration and management**:
- **Database initialization**: Schema setup, initial data loading
- **Security configuration**: Authentication, access control
- **Performance tuning**: Memory allocation, query optimization
- **Backup and recovery**: Data backup procedures, disaster recovery

### Pixi Environment Management
**Python environment and dependency management**:
- **Environment isolation**: Project-specific Python environments
- **Dependency management**: Package installation, version control
- **Environment activation**: Automatic environment switching
- **Integration**: IDE integration, command-line tools

## Integration Points

### With P3 CLI System
- **Environment validation**: Used by `p3 ready` for environment setup
- **Health checking**: Integrated with `p3 debug` for diagnostics
- **Service management**: Used by `p3 reset` for environment reset
- **Workflow validation**: Pre-flight checks for PR creation workflows

### With Infrastructure Components
- **Service coordination**: Integration with deployment automation
- **Monitoring integration**: Health status reporting to monitoring systems
- **Configuration management**: Centralized configuration handling
- **Logging integration**: Structured logging for troubleshooting

### With Development Workflows
- **CI/CD integration**: Environment validation in automated pipelines
- **Testing support**: Environment setup for test execution
- **Development tools**: IDE integration, debugging support
- **Quality assurance**: Environment consistency validation

## Usage Examples

### Daily Development Startup
```bash
# Check environment status before starting work
python infra/environment/env_status.py

# If services not running:
❌ Environment needs attention.
🔧 Setup steps:
  1. Install Pixi: https://pixi.sh/
  2. Run: pixi shell
  3. Run: p3 ready

# After running p3 ready:
✅ Environment is ready for development!
```

### Troubleshooting Common Issues
```bash
# Minikube not running
❌ Minikube is not running
💡 Start with: p3 ready

# Neo4j connection issues  
❌ Neo4j pod is not running
💡 Check logs with: kubectl logs -l app=neo4j

# Pixi environment issues
❌ Not in Pixi shell
💡 Run: pixi shell
```

### Complete Environment Reset
```bash
# Full environment shutdown and reset
python infra/environment/shutdown_all.py
p3 reset
p3 ready

# Verify environment after reset
python infra/environment/env_status.py
```

## Quality Standards

### Reliability Requirements
- **Service health monitoring**: Continuous monitoring of critical services
- **Graceful degradation**: Handling of partial service failures
- **Recovery procedures**: Automated recovery from common failure scenarios
- **Data protection**: Ensuring data safety during service operations

### Performance Standards
- **Fast health checks**: Status checks complete within 10 seconds
- **Efficient resource usage**: Minimal overhead for monitoring operations
- **Responsive service management**: Quick service start/stop operations
- **Optimized configurations**: Performance-tuned service configurations

### User Experience Standards
- **Clear status reporting**: Human-readable status messages and diagnostics
- **Actionable error messages**: Specific fix suggestions for detected issues
- **Consistent interface**: Standard command patterns across tools
- **Comprehensive documentation**: Usage guides and troubleshooting procedures

## Troubleshooting Guide

### Common Environment Issues

**Minikube Problems**:
```bash
# Issue: Minikube won't start
# Solution: Check virtualization support, restart Docker
minikube delete
minikube start --driver=docker

# Issue: Insufficient resources
# Solution: Increase resource allocation
minikube config set memory 8192
minikube config set cpus 4
```

**Neo4j Database Issues**:
```bash
# Issue: Neo4j not accessible
# Solution: Check pod status and logs
kubectl get pods -l app=neo4j
kubectl logs -l app=neo4j

# Issue: Connection refused
# Solution: Verify service port forwarding
kubectl port-forward svc/neo4j 7474:7474 7687:7687
```

**Pixi Environment Problems**:
```bash
# Issue: Environment not activating
# Solution: Reinstall environment
pixi install

# Issue: Package conflicts
# Solution: Clear cache and reinstall
pixi clean
pixi install
```

## Maintenance Guidelines

### Regular Maintenance Tasks
- **Service health monitoring**: Daily health checks and performance monitoring
- **Resource cleanup**: Weekly cleanup of temporary files and unused resources
- **Configuration updates**: Regular updates to service configurations
- **Dependency updates**: Scheduled updates to packages and dependencies

### Performance Optimization
- **Resource allocation**: Optimize CPU, memory allocation based on usage patterns
- **Configuration tuning**: Adjust service configurations for optimal performance
- **Monitoring enhancement**: Improve monitoring tools for better insights
- **Automation improvement**: Enhance automation for reduced manual intervention

---

**Integration References**:
- **P3 Commands**: [Main README.md](../../README.md#p3-command-system) for workflow integration
- **Service Management**: [infra/README.md](../README.md) for infrastructure overview
- **Workflow Integration**: [infra/workflows/README.md](../workflows/README.md) for CI/CD coordination