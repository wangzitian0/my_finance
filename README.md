# my-finance: A Graph RAG-powered DCF Valuation System

## Core Philosophy

This project follows a **two-tier command architecture** for clear separation of responsibilities:

- **Ansible manages Environment**: System setup, infrastructure services (Minikube, Neo4j), and environment lifecycle
- **Pixi manages Development**: Application dependencies, data processing, code quality, and development workflows  
- **Python handles Complexity**: Complex operations that can't be handled by the above tools

All commands are accessed through `pixi run <task>`, but internally delegate to the appropriate management layer.

## Installation: The One-Command Setup

This project is designed to go from a fresh clone to a fully running environment with a single command.

### Prerequisites

1.  **Docker**: Install Docker Desktop for your platform (required for Minikube):
    - **macOS**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [OrbStack](https://orbstack.dev/) (faster)
    - **Linux**: Docker via system package manager (`sudo apt install docker.io` or `sudo dnf install docker`)
    - **Windows**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

2.  **Pixi**: Install Pixi by following the [official instructions](https://pixi.sh/latest/).

### The Setup Command

From the project root, run:

```bash
pixi run setup-env
```

This Ansible-powered setup:
1. **Installs Minikube** (cross-platform Kubernetes)
2. **Installs kubectl** (if needed)
3. **Starts Minikube cluster** with Neo4j
4. **Deploys Neo4j** via Kubernetes manifests
5. **Initializes data submodules**
6. **Sets up Pixi environment**

Data is stored in `./data/neo4j/` (not tracked in git).

## Daily Development Workflow

All common tasks are managed through Pixi. You should never need to use any other command-line tool.

### Activating the Environment

To enter the isolated development shell with all tools available:
```bash
pixi shell
```

### Environment Commands (Ansible-managed)

- **`pixi run env-status`**: Check overall environment health (Minikube, Neo4j, Pixi)
- **`pixi run env-start`**: Start all services (Minikube cluster + Neo4j)  
- **`pixi run env-stop`**: Stop all services
- **`pixi run env-reset`**: Reset everything (destructive - removes all data)

### Development Commands (Pixi-managed)

- **`pixi run status`**: Check data collection status
- **`pixi run build-m7`**: Build the "Magnificent 7" test dataset
- **`pixi run run-job`**: Run data collection jobs
- **`pixi run format`**: Format code (black + isort)
- **`pixi run lint`**: Lint code with pylint  
- **`pixi run test`**: Run test suite with pytest

### Quick Status Check

To see if everything is working:

```bash
pixi shell                # Enter development environment
pixi run env-status       # Check environment health
```

### Troubleshooting

- **Environment issues**: Use `pixi run env-reset` to start fresh (destructive)
- **Minikube problems**: Check with `minikube status` and restart with `pixi run env-start`
- **Neo4j connection**: Get connection details with `pixi run env-status`
