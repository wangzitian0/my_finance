# Infra - Infrastructure

Global infrastructure management focused on environment, deployment, monitoring, and development toolchain.

## Component Structure

### Environment Management
- `env_status.py` - Environment status check
- `shutdown_all.py` - Service shutdown

### Deployment Configuration
- `ansible/` - Automated deployment configuration
- `k8s/` - Kubernetes deployment configuration
- `deployment.md` - Deployment guide

### Development Tools
- `cleanup_merged_branches.py` - Git branch cleanup
- `install_git_hooks.py` - Git hooks installation
- `commit_data_changes.py` - Data submodule commit
- `cleanup_obsolete_files.py` - File cleanup
- `git-workflow-optimization.md` - Git workflow documentation

### Monitoring Operations
- `monitoring.md` - Monitoring architecture documentation

## Usage

```bash
# Environment management
p3 env-status
p3 shutdown-all

# Git workflow
p3 cleanup-branches
pixi run install-git-hooks
p3 commit-data-changes

# Deployment
ansible-playbook infra/ansible/setup.yml
kubectl apply -f infra/k8s/
```

## Responsibilities

- **Global environment**: Docker, K8s, databases and other infrastructure services
- **Deployment automation**: CI/CD, configuration management
- **Development tools**: Git tools, code quality checks
- **Monitoring operations**: System monitoring, log management