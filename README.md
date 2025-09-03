# Financial Strategy Engine

**SEC Filing-Enhanced DCF valuation system with Graph RAG**

Automated investment analysis using official SEC filings to generate intrinsic valuations, buy/hold/sell recommendations, and risk assessments with regulatory backing.

## Quick Start

**Prerequisites**: [Pixi](https://pixi.sh/latest/), Docker/Podman

```bash
# Clone and setup
git clone https://github.com/wangzitian0/my_finance.git
cd my_finance

# Global p3 command setup (recommended)
mkdir -p ~/bin && cat > ~/bin/p3 << 'EOF'
#!/bin/bash
cd /path/to/my_finance && python p3.py "$@"
EOF
chmod +x ~/bin/p3 && echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc

# Workflow-oriented development
p3 ready            # "I want to start working" - complete environment setup
p3 check f2         # "Validate my code" - format, lint, test, build  
p3 test f2          # "Run comprehensive tests" - e2e validation
p3 ship "Title" 123 # "Publish my work" - create PR with testing
```

## Workflow-Oriented P3 Commands

The P3 CLI is designed around **developer workflows**, not technical operations:

### 🚀 Development Workflow
```bash
# Daily workflow - only 4 commands needed
p3 ready                    # Start working (env + services + format)
p3 check [scope]           # Validate code (format + lint + test + build) 
p3 test [scope]            # Comprehensive testing (e2e + validation)
p3 ship "title" issue      # Publish work (test + PR + cleanup)

# Emergency troubleshooting  
p3 debug                   # Diagnose issues (unified status check)
p3 reset                   # Fix environment (clean restart everything)
```

### 🎯 Design Philosophy
- **User Intent**: Commands match what developers think ("I want to start working")
- **Smart Automation**: Intelligent combinations reduce decision fatigue  
- **Error Tolerance**: Graceful handling of common issues
- **Zero Configuration**: Auto-detection and setup

**Scopes**: `f2` (2 cos, dev), `m7` (7 cos, testing), `n100` (validation), `v3k` (production)

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
- **`infra/`** - Infrastructure services and deployment  
- **`build_data/`** - Generated datasets and outputs
- **`templates/`** - Analysis prompts and configurations
- **`scripts/`** - Workflow automation and tooling

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
- **Worktree Isolation**: Complete Python environment isolation per worktree
- **Auto-switching**: P3 automatically uses correct Python environment
- **Zero-config**: No manual environment setup required
- **Intelligent Testing**: Smart test suite selection based on scope

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

**Typical Daily Flow**:
```bash
cd /path/to/worktree
p3 ready                # Ensure everything ready
# ... make code changes ...
p3 check f2             # Quick validation  
p3 test f2              # Comprehensive testing
p3 ship "Add feature" 123  # Create PR
```

**Emergency Fix Flow**:
```bash
p3 debug                # Diagnose what's wrong
p3 reset                # Clean restart everything
p3 ready                # Verify fix worked
```

**Multiple Worktree Support**:
```bash
# Each worktree completely isolated
cd /path/to/worktree-A
p3 ready                # Uses worktree-A's Python environment

cd /path/to/worktree-B  
p3 ready                # Uses worktree-B's Python environment
```

## Version Management

**P3 Version System**:
- Automatic version tracking with git integration
- Semantic versioning (major.minor.patch)
- Automatic patch increment on git changes
- Branch and hash tracking for full traceability

```bash
p3 version              # Show current version
p3 version major        # Manual version bumps
```

## Troubleshooting

**Common Issues**:
```bash
# Environment problems
p3 debug                # Diagnose issues  
p3 reset                # Clean restart

# Package/dependency issues  
p3 ready                # Auto-fix most problems

# Python environment confusion
# P3 automatically switches to correct environment
```

**Worktree-Specific Issues**:
- P3 auto-detects worktree vs main repository
- Automatic Python environment isolation 
- No manual configuration required

## Maintenance & Governance

**P3 CLI Maintenance**: Managed by **infra-ops-agent** (see CLAUDE.md)
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
**Governance**: [CLAUDE.md](CLAUDE.md) - Company policies and agent responsibilities