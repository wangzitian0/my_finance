# my-finance: A Graph RAG-powered DCF Valuation System

## Core Philosophy

This project is built on a clear separation of concerns to ensure a robust and user-friendly development experience:

- **Pixi is the Single Entry Point**: For all day-to-day development, you will only ever need to use `pixi run <task>`. It manages all application dependencies and provides a consistent command-line interface.
- **Ansible for First-Time Setup**: Ansible is used only once, via `pixi run setup-env`, to prepare the system environment (primarily setting up Docker for Neo4j). You should never need to run `ansible-playbook` directly.
- **Docker for Services**: All external services, like the Neo4j database, are managed as Docker containers to ensure perfect consistency across all machines.

## Installation: The One-Command Setup

This project is designed to go from a fresh clone to a fully running environment with a single command.

### Prerequisites

1.  **Docker**: **Docker is a mandatory requirement.** Please install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and ensure it is running.
2.  **Pixi**: Install Pixi by following the [official instructions](https://pixi.sh/latest/).

### The Setup Command

With Docker running and Pixi installed, run the following command from the project root:

```bash
pixi run setup-env
```

This command triggers an Ansible playbook that does the heavy lifting for you:
1.  Verifies that Docker is running.
2.  Creates the local `./data/neo4j` directory for persistent data storage.
3.  Pulls the official Neo4j Docker image and starts the container.
4.  Installs all Python dependencies into a managed Pixi environment.
5.  Initializes the data submodules.

After this one-time setup, you are ready to go.

## Daily Development Workflow

All common tasks are managed through Pixi. You should never need to use any other command-line tool.

### Activating the Environment

To enter the isolated development shell with all tools available:
```bash
pixi shell
```

### Key Commands

- **`pixi run status`**: Check the status of your local data and database.
- **`pixi run neo4j-start`**: Start the Neo4j Docker container.
- **`pixi run neo4j-stop`**: Stop the Neo4j Docker container.
- **`pixi run neo4j-logs`**: View real-time logs from the Neo4j container.
- **`pixi run build-m7`**: Download the initial "Magnificent 7" dataset. This command is idempotent and will not re-download existing files.
- **`pixi run run-job`**: Run the default data collection job.
- **`pixi run test`**: Run the automated test suite.
- **`pixi run format`**: Format all code according to project standards.

### Resetting Your Environment

If you ever need to completely reset your database:

```bash
# WARNING: This deletes all local Neo4j data.
pixi run neo4j-remove
```
This command will stop and remove the Neo4j container and delete the local `./data/neo4j` directory. You can then run `pixi run setup-env` to start fresh.
