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
Repository Root/
├── .pixi/                          # Main repository pixi environment
├── infra/                          # Global infrastructure (ansible/docker)
├── scripts/                        # Global scripts
│   └── worktree_isolation.py       # Core isolation manager
└── worktrees/
    └── feature-branch/
        ├── .pixi/                  # Isolated Python environment
        ├── .worktree_config.json   # Global tool configuration
        ├── p3.py                   # Auto-environment switching integration
        └── scripts/ -> ../scripts  # Reused scripts
```

**Environment Verification:**
```bash
# Complete verification
pixi run worktree-verify

# Manual verification
python scripts/worktree_isolation.py status
python scripts/worktree_isolation.py verify
```

### Monitoring Operations
- `monitoring.md` - Monitoring architecture documentation

## Usage

**P3 Commands**: See [README.md](../README.md) for complete P3 usage guide and [CLAUDE.md](../CLAUDE.md) for workflow decision tree.

```bash
# Deployment and infrastructure commands
ansible-playbook infra/ansible/setup.yml
kubectl apply -f infra/k8s/
```

## Responsibilities

- **Global environment**: Docker, K8s, databases and other infrastructure services
- **Deployment automation**: CI/CD, configuration management
- **Development tools**: Git tools, code quality checks
- **Monitoring operations**: System monitoring, log management
- **P3 CLI Maintenance**: Command development, workflow optimization, system integration (per CLAUDE.md)
- **Worktree Isolation**: Python environment isolation, pixi integration, environment switching