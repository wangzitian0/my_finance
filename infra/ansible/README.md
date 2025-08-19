# Ansible Infrastructure

This directory contains Ansible playbooks and configurations for setting up and managing the my_finance development environment.

## Purpose

Automated infrastructure management using Ansible for:
- Local development environment setup
- Podman container orchestration
- Neo4j database configuration
- Service lifecycle management

## Key Files

- `init.yml` - Initial environment setup playbook
- `start.yml` - Start all services
- `stop.yml` - Stop all services  
- `reset.yml` - Reset environment (destructive)
- `ollama.yml` - Setup Ollama and embedding models
- `roles/` - Ansible roles for modular configuration
- `templates/` - Configuration file templates

## Usage

All Ansible operations are managed through the p3 CLI:

```bash
p3 env setup                # Initial environment setup
p3 env start                # Start all services
p3 env stop                 # Stop all services
p3 env status               # Check environment status
p3 env reset                # Reset everything (destructive)
```

## Requirements

- Ansible (installed via `pixi install`)
- Podman for container management
- Python 3.12+ environment

## Architecture

The Ansible automation provides:
1. **Cross-platform compatibility** - Works on macOS, Linux, Windows
2. **Idempotent operations** - Safe to run multiple times
3. **Service orchestration** - Manages Neo4j, Ollama, and other services
4. **Environment isolation** - Containers provide clean separation

## Notes

- Ansible is installed and managed through pixi environment
- Configuration is compatible with the Pixi-based dependency management
- Playbooks are designed to be run from the project root directory