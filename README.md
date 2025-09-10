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

# Workflow-oriented development
p3 ready            # "I want to start working" - complete environment setup
p3 check f2         # "Validate my code" - format, lint, test, build  
p3 test f2          # "Run comprehensive tests" - e2e validation
p3 ship "Title" 123 # "Publish my work" - create PR with testing
```

## P3 Command System

P3 is designed around **human intent**, not technical operations. It answers "what do I want to do?" rather than "how do I run this command?".

### Command Overview

<details>
<summary><b>Daily Workflow Commands</b> - 4 commands for everyday development</summary>

| Intent | Command | What It Does |
|--------|---------|--------------|
| **"Start working"** | `p3 ready` | Environment setup, start services, verify everything works |
| **"Check my code"** | `p3 check [scope]` | Format, lint, basic tests - quick validation |
| **"Test everything"** | `p3 test [scope]` | Complete end-to-end validation including builds |
| **"Create PR"** | `p3 ship "title" issue` | Test + PR creation with comprehensive validation |

**Daily Flow Example:**
```bash
p3 ready                    # Morning: ensure everything ready
# ... make changes ...
p3 check f2                 # Quick validation during development
p3 test f2                  # Comprehensive testing when ready
p3 ship "Add feature" 123   # Create PR for issue #123
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
<summary><b>Data & Version Commands</b> - 2 commands for datasets and versioning</summary>

| Intent | Command | What It Does |
|--------|---------|--------------|
| **"Build dataset"** | `p3 build [scope]` | Generate financial datasets for analysis and testing |
| **"Show version"** | `p3 version [level]` | Display version information or increment version |

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

```
SEC Edgar + YFinance → ETL → Graph RAG → DCF Engine → Evaluation
```

**Core Components**:
- **`ETL/`** - SEC/YFinance data processing, document parsing, embedding generation
- **`dcf_engine/`** - SEC-enhanced DCF calculations with semantic retrieval  
- **`graph_rag/`** - Semantic search across SEC filings
- **`evaluation/`** - Backtesting and performance analysis

**Supporting**: 
- **`common/`** - Shared configurations and utilities
- **`infra/`** - Modular infrastructure system (system/, data/, git/, hrbp/, p3/, development/)
- **`build_data/`** - Generated datasets and outputs
- **`templates/`** - Analysis prompts and configurations

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

**Component Docs**: [ETL](ETL/README.md), [DCF Engine](dcf_engine/README.md), [Graph RAG](graph_rag/README.md), [Common](common/README.md)  
**Infrastructure**: [Infrastructure](infra/README.md), [Testing](tests/README.md)
**Migration**: [Scripts-to-Infra Migration](MIGRATION_SUMMARY.md) - Modular architecture implementation  
**Governance**: [CLAUDE.md](CLAUDE.md) - Company policies and agent responsibilities
