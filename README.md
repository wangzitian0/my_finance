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
| **"What's wrong?"** | `p3 debug` | Comprehensive diagnostics and issue identification |
| **"Fix everything"** | `p3 reset` | Nuclear reset - clean restart of everything (destructive) |

**Troubleshooting Flow:**
```bash
p3 debug                    # Diagnose what's wrong
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

**Core Business Modules**:
- **`ETL/`** - Complete data pipeline: Raw data → Clean Neo4j graph
  - `sec_filing_processor/` - SEC Edgar document processing  
  - `embedding_generator/` - Vector embedding creation
  - `crawlers/` - Data acquisition and transformation
  - `schedulers/` - Automated pipeline orchestration
  - `loaders/` - Knowledge graph population

- **`engine/`** - Graph-RAG reasoning engine: Neo4j → Investment strategies
  - `retrieval/` - Hybrid semantic + graph retrieval
  - `reasoning/` - Language model integration and prompts
  - `valuation/` - DCF calculations and investment logic
  - `reporting/` - Professional investment report generation

- **`evaluation/`** - Independent strategy validation: Strategies → Performance returns
  - `backtesting/` - Historical strategy simulation
  - `metrics/` - Performance and risk analysis
  - `benchmarks/` - Market comparison and attribution

**Supporting Infrastructure**: 
- **`common/`** - Cross-module shared resources
  - `config/` - Centralized configuration management (SSOT)
  - `templates/` - Analysis prompts and configurations
  - `tools/` - Shared utility functions
- **`infra/`** - Team infrastructure and development tools
- **`tests/`** - Testing framework across all modules
- **`build_data/`** - Local artifacts and generated outputs

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
**Migration**: [Scripts-to-Infra Migration](MIGRATION_SUMMARY.md) - Modular architecture implementation  
**Governance**: [CLAUDE.md](CLAUDE.md) - Company policies and agent responsibilities

**Architecture Notes**: Issue #256 implements business-oriented module separation with clear data flow boundaries and independent validation systems.
