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
cd /path/to/my_finance && pixi run python p3 "$@"
EOF
chmod +x ~/bin/p3 && echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc

# Complete environment setup
p3 env-setup        # Installs Neo4j, Python ML stack, SEC data
p3 env-status       # Verify all services
p3 e2e              # Run end-to-end test
p3 build m7         # Build with SEC filings (7 companies, 336 documents)
```

## Architecture

```
SEC Edgar + YFinance → ETL → Graph RAG → DCF Engine → Evaluation
```

**Core Components**:
- **`ETL/`** - SEC/YFinance data processing, document parsing, embedding generation
- **`dcf_engine/`** - SEC-enhanced DCF calculations with semantic retrieval  
- **`graph_rag/`** - Semantic search across SEC filings
- **`evaluation/`** - Backtesting and performance analysis

**Supporting**: `common/` (configs), `infra/` (services), `build_data/` (datasets), `templates/` (prompts)

## Commands

**Analysis**:
```bash
p3 build m7                 # Build M7 dataset (7 companies, 336 SEC docs)
p3 dcf-analysis             # Generate DCF reports
p3 backtest                 # Historical performance test
```

**Development**:
```bash
p3 e2e                      # End-to-end validation
p3 create-pr "Title" ISSUE  # Create PR with testing
p3 format && p3 lint        # Code quality
```

**Environment**:
```bash
p3 env-setup               # Setup everything
p3 env-status              # Health check
p3 shutdown-all            # Clean shutdown
```

**Scopes**: `f2` (2 cos, dev), `m7` (7 cos, testing), `n100` (validation), `v3k` (production)

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

## Troubleshooting

**`command not found: p3`** → Setup global p3 command (see Quick Start)  
**Python version errors** → Use p3 wrapper (ensures correct environment)  
**Pixi issues** → `pixi install` or `p3 env-reset`

## Documentation

**Components**: [ETL](ETL/README.md), [DCF Engine](dcf_engine/README.md), [Graph RAG](graph_rag/README.md), [Common](common/README.md)  
**Guides**: [Architecture](docs/README.md), [Infrastructure](infra/README.md), [Testing](tests/README.md)
