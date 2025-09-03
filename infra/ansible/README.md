# Ansible Infrastructure Management

This directory contains Ansible playbooks for infrastructure setup and management.

## Purpose

Automated infrastructure management for:
- Cross-platform environment setup
- Container orchestration (Podman)
- Database setup (Neo4j)
- Service lifecycle management

## Playbooks

### Core Infrastructure
- `init.yml` - Initial environment setup
- `start.yml` - Start all services
- `stop.yml` - Stop all services  
- `status.yml` - Check service status

### Service Management
- `podman-setup.yml` - Container platform setup
- `neo4j-setup.yml` - Graph database setup
- `cleanup.yml` - Environment cleanup

## Usage

### Environment Commands (via p3)
```bash
# Initial setup (run once)
p3 ready         # Setup and start all services

# Daily operations
p3 ready         # Ensure environment ready (starts services)
p3 debug         # Check service status
p3 reset         # Reset everything (destructive)
```

### Direct Ansible Usage
```bash
# Manual playbook execution
ansible-playbook infra/ansible/init.yml
ansible-playbook infra/ansible/start.yml
ansible-playbook infra/ansible/stop.yml
```

## Platform Support

### Linux/WSL
- Native Podman support
- Systemd integration
- Package manager automation

### macOS
- Podman Machine setup
- Homebrew integration  
- Lima VM configuration

### Windows
- WSL2 integration
- Windows Subsystem setup
- Cross-platform compatibility

## Service Architecture

### Container Platform (Podman)
- Rootless container execution
- Docker-compatible API
- Systemd integration
- Resource management

### Database (Neo4j)  
- Graph database for financial data
- Containerized deployment
- Persistent data storage
- Performance optimization

## Configuration

### Inventory Management
- `hosts.yml` - Target host configuration
- `group_vars/` - Group-specific variables
- `host_vars/` - Host-specific variables

### Variable Management
- Environment-specific configurations
- Service discovery settings
- Resource allocation parameters
- Security configurations

## Monitoring

### Health Checks
- Service availability monitoring
- Resource usage tracking
- Performance metrics collection
- Error detection and alerting

### Status Reporting
- Comprehensive status dashboard
- Service dependency mapping
- Resource utilization reports
- Error log aggregation

## Best Practices

1. **Run env setup once** per development environment
2. **Use p3 commands** instead of direct ansible calls
3. **Check env status regularly** during development
4. **Clean shutdown with env stop** before system shutdown
5. **Reset only when necessary** (destructive operation)

## Troubleshooting

### Common Issues
- Port conflicts: Check for running services
- Permission issues: Verify rootless setup
- Network problems: Check firewall settings
- Resource constraints: Monitor system resources

### Debug Commands
```bash
# Detailed status with debugging
python infra/comprehensive_env_status.py

# Service-specific checks
p3 podman status
p3 neo4j logs

# Manual service restart
p3 neo4j restart
```