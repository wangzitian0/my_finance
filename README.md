# Financial Strategy Engine

**SEC Filing-Enhanced DCF valuation system with Graph RAG**

Automated investment analysis using official SEC filings to generate intrinsic valuations, buy/hold/sell recommendations, and risk assessments with regulatory backing.

## Quick Start

**Prerequisites**: [Pixi](https://pixi.sh/latest/), Docker/Podman

```bash
# Clone and setup
git clone https://github.com/wangzitian0/my_finance.git
cd my_finance

# Smart P3 setup (automatically follows worktrees)
# Add your repo root to PATH - replace with your actual repo path
export PATH="/path/to/your/my_finance:$PATH"

# Workflow-oriented development with CI-aligned testing
p3 ready            # "I want to start working" - complete environment setup
p3 check f2         # "Validate my code" - format, lint, basic tests
p3 test f2          # "Run comprehensive tests" - unit tests first, then integration + e2e (superset of CI)
p3 ship "Title" 123 # "Publish my work" - comprehensive testing + PR creation
p3 stop             # "Stop working" - release development resources
```

## P3 Command System

P3 is designed around **human intent**, not technical operations. It answers "what do I want to do?" rather than "how do I run this command?".

### Command Overview

<details>
<summary><b>Daily Workflow Commands</b> - 5 commands for everyday development</summary>

| Intent | Command | What It Does |
|--------|---------|--------------|
| **"Start working"** | `p3 ready` | Environment setup, start services, verify everything works |
| **"Stop working"** | `p3 stop [--full]` | Release resources, stop services (keeps machine for fast restart) |
| **"Check my code"** | `p3 check [scope]` | Format, lint, basic tests - quick validation |
| **"Test everything"** | `p3 test [scope]` | Unit tests + integration + e2e validation (superset of CI) |
| **"Create PR"** | `p3 ship "title" issue` | Test + PR creation with comprehensive validation |

**Daily Flow Example:**
```bash
p3 ready                    # Morning: ensure everything ready
# ... make changes ...
p3 check f2                 # Quick validation during development
p3 ci                       # Validate CI alignment (prevents CI failures)
p3 test f2                  # Comprehensive testing (unit + integration + e2e) when ready
p3 ship "Add feature" 123   # Create PR for issue #123
p3 stop                     # End of day: release resources
```
</details>

<details>
<summary><b>Troubleshooting Commands</b> - 2 commands for when things go wrong</summary>

| Intent | Command | What It Does |
|--------|---------|--------------|
| **"What's wrong?"** | `p3 reset` | Nuclear reset - clean restart of everything (destructive) |

**Troubleshooting Flow:**
```bash
p3 reset                    # Reset environment and diagnose issues
# Try fixes based on debug output...
p3 reset                    # Last resort - clean restart
p3 ready                    # Verify fix worked
```
</details>

<details>
<summary><b>Data & Version Commands</b> - 3 commands for datasets and versioning</summary>

| Intent | Command | What It Does |
|--------|---------|--------------|
| **"Build dataset"** | `p3 build [scope]` | Generate financial datasets for analysis and testing |
| **"Show version"** | `p3 version [level]` | Display version information or increment version |
| **"Check CI alignment"** | `p3 ci` | Run same tests as CI to prevent CI failures |

**Dataset Building:**
```bash
p3 build f2                 # Development data (2 companies)
p3 build m7                 # Testing data (7 companies)
p3 build n100               # Validation data (100 companies)
p3 build v3k                # Production data (3000+ companies)
```
</details>

### Scope Selection

<details>
<summary><b>Understanding Scopes</b> - f2, m7, n100, v3k</summary>

Scopes control the amount of data processed, balancing speed vs comprehensiveness:

| Scope | Companies | Duration | Use Case |
|-------|-----------|----------|----------|
| **f2** | 2 | 2-5 min | Development testing, quick validation |
| **m7** | 7 | 10-20 min | Integration testing, pre-release validation |
| **n100** | 100 | 1-3 hours | Production validation, performance testing |
| **v3k** | 3000+ | 6-12 hours | Full production datasets |

**Default Recommendations:**
- **Development**: Always use `f2` for development work
- **Testing**: Use `f2` for PR validation, `m7` for release prep  
- **Production**: Use `n100` for staging, `v3k` for production deployment
</details>

### Advanced Usage

<details>
<summary><b>Worktree Support</b> - Isolated environments per feature branch</summary>

Each worktree has completely isolated environments with automatic switching:

```bash
# Worktree A - feature X
cd /path/to/worktree-A
p3 ready                    # Uses worktree-A's Python environment

# Worktree B - feature Y  
cd /path/to/worktree-B
p3 ready                    # Uses worktree-B's Python environment
```

**Benefits**: 
- No package conflicts between branches
- Automatic environment switching
- Parallel development on multiple features
- Isolated dependency management
</details>

## Architecture

**Business-Oriented Data Flow (Issue #256)**:
```
Data Sources → ETL → Neo4j → engine → Strategies/Reports → evaluation → Backtesting Returns
```

### L1 Business Modules (Primary System Components)

The system is organized into 5 primary L1 modules, each containing specialized L2 components:

#### **`ETL/`** - Data Processing Pipeline
Complete data pipeline from raw sources to Neo4j knowledge graph.

**L2 Components**:
- `sec_filing_processor/` - SEC Edgar document processing and parsing
- `embedding_generator/` - Vector embedding creation for semantic search
- `crawlers/` - Data acquisition and web scraping automation
- `schedulers/` - Pipeline orchestration and job management
- `loaders/` - Neo4j knowledge graph population and updates

#### **`engine/`** - Graph-RAG Investment Analysis
Graph-enhanced reasoning engine for investment strategy generation.

**L2 Components**:
- `retrieval/` - Hybrid semantic + graph retrieval from Neo4j
- `reasoning/` - LLM integration and prompt template management
- `valuation/` - DCF calculations and quantitative investment logic
- `reporting/` - Professional investment report generation

#### **`evaluation/`** - Strategy Validation System
Independent validation of investment strategies through backtesting.

**L2 Components**:
- `backtesting/` - Historical strategy simulation and testing
- `metrics/` - Performance measurement and risk analysis
- `benchmarks/` - Market comparison and peer analysis

#### **`common/`** - Unified System Architecture
Cross-module shared resources and system infrastructure.

**L2 Components**:
- `core/` - Directory manager, config manager, storage backends
- `config/` - Centralized configuration management (SSOT)
- `templates/` - Analysis prompts and LLM configurations
- `tools/` - Shared utility functions and helpers
- `database/` - Database connection and query utilities
- `schemas/` - Data models and validation schemas
- `types/` - Type definitions and interfaces
- `utils/` - General-purpose utility functions

#### **`infra/`** - Infrastructure and System Management
Development tools, deployment, and system operations.

**L2 Components**:
- `system/` - Environment monitoring and validation
- `git/` - Git operations and release management
- `p3/` - P3 CLI system maintenance and optimization
- `hrbp/` - HRBP automation and policy enforcement
- `development/` - Code quality and development tools
- `deployment/` - Ansible, Kubernetes, and deployment automation

### Supporting Directories
- **`tests/`** - Integration and end-to-end testing framework
- **`build_data/`** - Local artifacts and generated outputs

## Testing Architecture

**Modular Testing Strategy**: Following L1/L2 architecture principles

### Test Distribution
- **Unit Tests**: Located within each L1/L2 module alongside source code
- **Integration Tests**: Located in root `tests/` directory for cross-module testing
- **End-to-End Tests**: Located in root `tests/e2e/` for complete workflow validation

### Testing Locations
```yaml
unit_tests:
  ETL/tests/: "Data processing, SEC parsing, pipeline validation"
  engine/tests/: "Graph-RAG, DCF calculations, reasoning logic"
  evaluation/tests/: "Backtesting, metrics, benchmark analysis"
  common/tests/: "Shared utilities, configurations, core components"
  infra/tests/: "Infrastructure tools, deployment, system validation"

integration_tests:
  tests/: "Cross-module integration, system workflows"
  tests/e2e/: "Complete user workflow validation"
```

### P3 Testing Commands
- **`p3 check f2`**: Fast validation during development
- **`p3 test f2`**: Comprehensive testing (unit + integration + e2e)
- **`p3 ci`**: CI-aligned testing to prevent pipeline failures

## Features

**SEC-Enhanced Analysis**:
- DCF valuations backed by official 10-K/10-Q filings
- Investment recommendations with SEC citation support  
- Risk analysis using regulatory disclosures
- 336 SEC documents from Magnificent 7 companies (2017-2025)

**Pipeline**:
```
SEC Edgar → Document Parser → Embeddings → Vector Search → DCF
10-K/10-Q    Text Extract    384-dim       FAISS        Analysis
```

**Workflow Automation**:
- Complete Python environment isolation per worktree
- Automatic environment switching and zero-config setup  
- Intelligent testing with smart scope selection
- Unified development workflow through P3 commands

## Environment Management

**Worktree Python Isolation**:
- Each worktree has completely isolated Python environment
- Automatic environment switching when using P3 commands  
- Global infrastructure (ansible/docker) reuse for efficiency
- Zero-configuration setup with intelligent error handling

**Global vs Local**:
- **Global**: Docker containers, ansible configs, system services
- **Local**: Python packages, pixi environments, build outputs  
- **Smart Reuse**: Shared stable components, isolated variable components

## Development Workflows

**Standard Development Process**:
1. **Environment Setup**: Automated infrastructure and dependency management
2. **Code Validation**: Continuous format/lint/test feedback during development  
3. **Integration Testing**: Comprehensive validation before publishing
4. **Pull Request Creation**: Automated PR workflow with testing and deployment

**Cross-Feature Development**:
- Independent worktree environments prevent conflicts
- Automated environment switching per directory
- Parallel development with isolated dependency management

## Maintenance & Governance

**P3 CLI Maintenance**: Managed by **infra-ops-agent** via **`infra/p3/`** module (see CLAUDE.md)
- Command interface stability and evolution
- Workflow optimization and user experience  
- Environment management and automation
- Infrastructure integration and deployment

**Agent-Managed Components**:
- Core development workflows under **infra-ops-agent**
- Data processing pipelines under **data-engineer-agent**  
- Analysis engines under **quant-research-agent**
- Quality assurance under **dev-quality-agent**

## Documentation

**Business Modules**: [ETL Pipeline](ETL/README.md), [Graph-RAG Engine](engine/README.md), [Strategy Evaluation](evaluation/README.md)
**Infrastructure**: [Common Utilities](common/README.md), [Infrastructure](infra/README.md), [Testing](tests/README.md)
**Configuration**: [Config Management](infra/config/README.md) - Centralized configuration files
**Migration**: [Scripts-to-Infra Migration](MIGRATION_SUMMARY.md) - Modular architecture implementation
**Governance**: [CLAUDE.md](CLAUDE.md) - Company policies and agent responsibilities

**Architecture Notes**: Issue #256 implements business-oriented module separation with clear data flow boundaries and independent validation systems.

**Issue #282 Implementation**: Root directory cleanup with modular testing architecture - unit tests co-located with L1/L2 modules, integration tests in root tests/ directory.
