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

**Basic Workflow:**
```bash
# 1. Enter worktree directory
cd /path/to/worktree

# 2. Direct usage - automatic environment isolation
python p3.py version-info          # Auto-switches to worktree Python
python p3.py build f2              # Uses isolated environment
python p3.py e2e                   # Uses isolated environment
```

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

```bash
# Environment management
p3 debug          # Check environment status
p3 reset          # Shutdown and reset environment

# Git workflow (simplified in P3 v2)
p3 ship "title" ISSUE  # Create PR with validation
# Note: Most git operations now automated in workflow commands

# Deployment
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