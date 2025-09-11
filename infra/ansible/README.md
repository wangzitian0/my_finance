# Ansible Infrastructure Management

## 🎯 Overview

Simplified Ansible infrastructure for development environment management with **3 core operations**:
- **SETUP**: Initialize/reset complete environment 
- **START**: Launch dependencies and services
- **STOP**: Shutdown services (save laptop battery)

## 📁 File Structure

### 🎮 Core Playbooks (3 Essential Operations)
```
infra/ansible/
├── setup.yml         # Environment initialization/reset
├── start.yml         # Start all services and dependencies  
└── stop.yml          # Stop services (battery optimization)
```

### 🧩 Supporting Playbooks (4 Legacy/Specialized)
```
├── init.yml           # Legacy full environment setup (comprehensive)
├── reset.yml          # Environment reset (destructive cleanup)  
├── p3_ready_setup.yml # P3 ready command integration
└── p3_stop_cleanup.yml # P3 stop command integration
```

### 🛠️ Role Modules (16 Components)
```
roles/
├── system_requirements_check.yml  # System validation
├── podman_setup.yml               # Container platform setup
├── podman_neo4j_setup.yml         # Podman + Neo4j integration
├── neo4j_install.yml              # Neo4j database setup
├── neo4j_check_restart.yml        # Neo4j health management
├── pixi_setup.yml                 # Python environment setup
├── python_environment_check.yml   # Python validation
├── data_directory_setup.yml       # Data structure initialization
├── dependency_cache.yml           # Dependency management
├── docker_setup.yml               # Docker compatibility layer
├── ollama_setup.yml               # AI model setup
├── repo_code.yml                  # Code repository management
├── repo_data.yml                  # Data repository management  
├── final_validation.yml           # Environment validation
└── templates/                     # Configuration templates
```

## 🚀 Usage Patterns

### P3 Command Integration (Recommended)
```bash
# Smart environment management
p3 ready          # Auto-detects: setup vs start
p3 stop           # Stop services, save battery
p3 stop --full    # Complete shutdown including Podman machine
```

### Direct Ansible Usage
```bash
# Manual control
ansible-playbook infra/ansible/setup.yml  # Full environment setup
ansible-playbook infra/ansible/start.yml  # Start services only
ansible-playbook infra/ansible/stop.yml   # Stop services only
```

## 🧠 P3 Ready Logic

`p3 ready` intelligently chooses between setup and start:

### **SETUP** Triggers (Heavy Operation)
- First-time environment setup
- Missing Podman machine
- Missing Neo4j container
- Corrupted environment state
- After `p3 reset`

### **START** Triggers (Light Operation)  
- Environment exists but services stopped
- Daily development workflow
- After `p3 stop`
- Services are healthy but not running

## 🔄 Operation Details

### 🏗️ SETUP (`setup.yml`)
**Purpose**: Complete environment initialization
**Duration**: 5-15 minutes (first time)
**Triggered by**: Missing environment components

**Operations**:
- System requirements validation
- Podman machine creation and configuration
- Neo4j container deployment with persistent data
- Python environment setup via Pixi
- Data directory structure creation
- Service health validation

### ▶️ START (`start.yml`) 
**Purpose**: Launch existing services
**Duration**: 2-5 minutes
**Triggered by**: Services exist but stopped

**Operations**:
- Podman machine startup (if stopped)
- Neo4j container startup
- Service connectivity validation
- Health check confirmation

### ⏹️ STOP (`stop.yml`)
**Purpose**: Shutdown services to save battery
**Duration**: 30-60 seconds
**Triggered by**: End of work session

**Operations**:
- Graceful Neo4j database shutdown
- Container service stopping
- Port release validation
- Optional Podman machine management

## 🔋 Battery Optimization Strategy

### Default Stop Behavior (Smart)
- Stop all development containers
- Keep Podman machine running (fast restart)
- Minimal resource usage
- 2-5 minute restart time

### Full Stop Behavior (`--full`)
- Stop all containers  
- Stop Podman machine completely
- Maximum battery savings
- 5-15 minute restart time

## 📊 Service Dependencies

### Core Services Started by SETUP/START
```
Podman Machine (VM)
├── Neo4j Container (neo4j-finance)
│   ├── Port 7474 (HTTP Web Interface)
│   ├── Port 7687 (Bolt Protocol)
│   └── Persistent Volume (neo4j-data)
└── Additional Dev Containers (optional)
    ├── redis-dev
    ├── postgres-dev  
    ├── mongodb-dev
    └── elasticsearch-dev
```

### Services Stopped by STOP
```
✅ All development containers
✅ Neo4j graceful shutdown
✅ Port cleanup (7474, 7687)  
⚠️  Podman Machine (default: keep running)
🔋 Podman Machine (--full: stop for max battery savings)
```

## 🎛️ Configuration Management

### Environment Variables
- `NEO4J_AUTH=neo4j/password` - Database credentials
- `NEO4J_PLUGINS=["apoc"]` - Neo4j extensions
- Memory allocation: 512MB-1GB heap size
- Container restart policy: `unless-stopped`

### Data Persistence
- **Neo4j Data**: Persistent volume `neo4j-data`
- **Python Environment**: Pixi managed isolation
- **Configuration**: Centralized in `common/config/`

## 🛠️ File Consolidation Analysis

### Current Structure Issues
- **22 YAML files** (excessive complexity)
- **Overlapping responsibilities** across playbooks
- **Inconsistent naming patterns**
- **Legacy files** not actively used

### Recommended Consolidation
1. **Keep 3 core files**: `setup.yml`, `start.yml`, `stop.yml`
2. **Merge specialized playbooks**: Consolidate p3_* files into core operations
3. **Preserve role modules**: Keep modular components for maintainability
4. **Archive legacy files**: Move unused files to `archive/` directory

## 🧪 Testing and Validation

### Validation Commands
```bash
# Environment health check
ansible-playbook --syntax-check infra/ansible/setup.yml
ansible-playbook --syntax-check infra/ansible/start.yml  
ansible-playbook --syntax-check infra/ansible/stop.yml

# Service connectivity
curl -s http://localhost:7474  # Neo4j web interface
podman ps                      # Container status
p3 debug                       # Comprehensive diagnostics
```

## 🚨 Troubleshooting

### Common Issues
1. **Podman machine startup failures**
   - Solution: `podman machine rm && podman machine init`
   
2. **Neo4j container won't start**
   - Solution: Check port conflicts, verify data volume

3. **Port already in use (7474, 7687)**
   - Solution: Stop conflicting services, use `p3 stop --full`

4. **Memory issues**
   - Solution: Adjust Neo4j heap size in container env vars

### Debug Commands
```bash
p3 debug                           # Comprehensive environment status
podman machine list               # Check VM status  
podman ps -a                      # Check all containers
podman logs neo4j-finance         # Neo4j service logs
ansible-playbook infra/ansible/start.yml -v  # Verbose execution
```

## 🔄 Lifecycle Management

### Daily Development Workflow
```bash
# Morning: Start work
p3 ready          # Smart start (2-5 min)

# During development
p3 check f2       # Validate code
p3 test f2        # Run tests

# Evening: End work  
p3 stop           # Save battery (30 sec)
```

### Weekly/Weekend Workflow
```bash
# Friday evening: Maximum battery savings
p3 stop --full    # Complete shutdown

# Monday morning: Full restart
p3 ready          # Longer startup (5-10 min) but fully fresh
```

This structure provides **simple semantic operations** (setup/start/stop) while maintaining the flexibility of the underlying role-based architecture for complex environment management.