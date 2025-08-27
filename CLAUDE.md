# CLAUDE.md - Claude Code Instructions

<!-- Test comment added for sub-agent activation testing - 2025-08-26 -->

> **Clean Repository Structure** (2025-08-26): Main repository contains only code, documentation, and configurations. Data subtree at `build_data/` with centralized configs at `common/config/`.

This file provides guidance to Claude Code when working with this SEC Filing-Enhanced Graph RAG-powered DCF valuation system.

## 🤖 MANDATORY SUB-AGENT ORCHESTRATION

**CRITICAL**: ALL non-trivial tasks MUST be routed through the agent-coordinator for optimal sub-agent utilization.

### Sub-Agent First Policy

1. **Primary Routing**: Use `agent-coordinator` as the central task distributor for ALL complex operations
2. **Intelligent Delegation**: Let agent-coordinator automatically select the most appropriate specialized agent
3. **Direct Tool Usage**: Only use direct tools for trivial single-step operations (file reads, simple edits)

### Task Routing Guidelines

```bash
# ✅ CORRECT: Route through agent-coordinator
Use Task tool with subagent_type="agent-coordinator" for:
- Any git operations (create PR, branch management, releases)
- Development workflows (testing, quality checks, deployment)
- Data processing (ETL, SEC integration, analysis)
- Infrastructure operations (environment setup, monitoring)
- Web development (frontend, backend, API design)
- Architecture decisions (RAG system, database design)

# ❌ AVOID: Direct tool usage for complex operations
Don't use Bash/Edit/Write directly for multi-step processes
```

### Agent Selection Priority

1. **agent-coordinator**: For ALL task orchestration and complex workflows
2. **Specialized agents**: Automatically selected by coordinator based on task context
3. **Direct tools**: Only for immediate single-step operations

### Decision Matrix: When to Use Sub-Agents

| Task Type | Use Agent-Coordinator | Direct Tools |
|-----------|---------------------|--------------|
| PR Creation | ✅ Always | ❌ Never |
| Git Operations | ✅ Always | ❌ Never |
| Code Quality/Testing | ✅ Always | ❌ Never |
| Data Processing | ✅ Always | ❌ Never |
| Infrastructure Setup | ✅ Always | ❌ Never |
| Web Development | ✅ Always | ❌ Never |
| Architecture Design | ✅ Always | ❌ Never |
| Single File Read | ❌ Rarely | ✅ Preferred |
| Simple File Edit | ❌ Rarely | ✅ Preferred |
| Quick Status Check | ❌ Rarely | ✅ Preferred |

### Sub-Agent Routing Examples

```typescript
// ✅ CORRECT: Multi-step workflow via agent-coordinator
"I need to create a PR for the current changes with full validation"
→ Task(agent-coordinator) → Delegates to git-ops-agent + dev-quality-agent

// ✅ CORRECT: Complex development task
"Implement new DCF calculation feature with testing"
→ Task(agent-coordinator) → Orchestrates multiple agents in sequence

// ❌ INCORRECT: Direct tool for complex operation  
Bash("p3 create-pr ...") // Should route through agent-coordinator

// ✅ CORRECT: Simple file operation
Read("path/to/file.py") // Direct tool is appropriate
```

## 🚨 CRITICAL REQUIREMENTS

1. **ALWAYS read README.md first** - Contains complete project architecture
2. **ALWAYS route through agent-coordinator** - For optimal sub-agent utilization
3. **Use `common/config/` for all configurations** - Centralized SSOT system
4. **Follow p3 command workflow** - Never use direct python scripts
5. **Test before PR creation** - `p3 e2e` is mandatory
6. **Update parent READMEs** - When modifying directory functionality

## Quick Setup

**p3 Command (Global Setup)**:
```bash
mkdir -p ~/bin && cat > ~/bin/p3 << 'EOF'
#!/bin/bash
cd /path/to/my_finance && pixi run python p3 "$@"
EOF
chmod +x ~/bin/p3 && echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
```

**Essential Commands**:
- `p3 env-status` - Check system status
- `p3 e2e` - Run end-to-end tests (M7 scope)
- `p3 create-pr "description" ISSUE_NUMBER` - Create PR with validation

## System Architecture

**See README.md and directory READMEs for complete details.**

**Key Components**:
- **ETL/**: Data processing with SEC document semantic embedding (see ETL/README.md)
- **dcf_engine/**: DCF calculations and Graph RAG Q&A (see dcf_engine/README.md)
- **common/**: Unified configuration and directory management (see common/README.md)
- **graph_rag/**: Semantic retrieval and reasoning (see graph_rag/README.md)

**Data Tiers**: F2 (dev) → M7 (testing) → N100 (validation) → V3K (production)
**SEC Integration**: 336 documents with semantic retrieval for M7 companies

## Quality Control

**Process enforcement (not technical enforcement):**
- ✅ PRs required for main branch
- ✅ M7 test validation in commit messages
- ⚠️ Status checks NOT mandatory (manual enforcement)

**MANDATORY**: `p3 create-pr` - Prevents untested code reaching main branch

**Security Rules**:
1. NEVER bypass automated scripts
2. Always verify M7 tests pass locally
3. Monitor CI status for failures

## Sub-Agent Workflow Examples

### Git Operations (via agent-coordinator → git-ops-agent)

```bash
# Instead of direct p3 create-pr, use:
Task tool with subagent_type="agent-coordinator":
"Route PR creation task: Create PR for current branch with M7 testing validation"

# Instead of direct git commands, use:
Task tool with subagent_type="agent-coordinator":
"Route git operations: Branch cleanup, merge conflict resolution, release management"
```

### Development Quality (via agent-coordinator → dev-quality-agent)

```bash
# Instead of direct p3 e2e/lint/format, use:
Task tool with subagent_type="agent-coordinator":
"Route development quality task: Run full testing suite with code quality validation"
```

### Data Processing (via agent-coordinator → data-engineer-agent)

```bash
# Instead of direct data operations, use:
Task tool with subagent_type="agent-coordinator":
"Route data processing task: SEC filing integration with M7 companies analysis"
```

### Infrastructure Management (via agent-coordinator → infra-ops-agent)

```bash
# Instead of direct environment commands, use:
Task tool with subagent_type="agent-coordinator":
"Route infrastructure task: Environment setup and service monitoring"
```

## Git Workflow

**IMPORTANT**: All git operations should be routed through agent-coordinator for optimal sub-agent utilization.

**See README.md for complete workflow.** Claude requirements:

### Protection Model

- ✅ **p3 create-pr workflow**: Fully supported
- ❌ **Direct git push**: Blocked to enforce testing
- 🎯 **Goal**: All code passes M7/F2 tests before reaching remote

### Common Issues

- **"Cannot create PR from main"**: Check worktree context with `git branch --show-current`
- **"Direct push blocked"**: Ensure `P3_CREATE_PR_PUSH` environment variable set
- **Testing failures**: Fix issues, don't skip validation - run `p3 e2e f2`

### Pre-PR Checklist

**CRITICAL**: Update parent README files when modifying directory functionality:
- ETL changes → Update root README "Core Components" → ETL description
- DCF Engine changes → Update root README "Core Components" → dcf_engine description
- Graph RAG changes → Update root README "Core Components" → graph_rag description

### PR Workflow

**MANDATORY Process**:
```bash
# 1. Run tests first
p3 e2e

# 2. Check README consistency if modified directories
# (Update parent README descriptions as needed)

# 3. Create PR via automation only
p3 create-pr "Brief description" ISSUE_NUMBER
```

**Why Manual Git FAILS**:
- Direct `git push` → Missing M7 validation → CI rejection
- Manual PR creation → No test verification → Blocked merge
- Hand-crafted commits → Fake markers detected → Validation failure

**CI Validates**: Real M7 test timestamps, actual data processing, proper test hosts

**NEVER**: Use `git push`, `gh pr create`, or manual commit messages

### Issue Management

- **ALL changes link to GitHub Issues** for traceability
- **Claude Code configs**: Link to issue #14
- **Branch naming**: `feature/description-fixes-N`
- **Current active**: #20 (Neo4j), #21 (DCF), #22 (Graph RAG), #26 (conda migration)

**See README.md for complete issue history and testing approach.**

## Development Guidelines

### Patterns
- Read README.md first for project context
- Edit existing files over creating new ones  
- Use p3 commands exclusively (never direct python)
- Reference CIK numbers from README.md for SEC work

### Core Files
- **Config**: `common/config/*.yml` (centralized SSOT)
- **ETL**: Data processing and SEC integration
- **DCF**: Valuation calculations and Graph RAG

### Command System

**Format**: `p3 <command> [scope]`
- **Scopes**: f2 (dev), m7 (testing), n100 (validation), v3k (production)
- **Key commands**: `env-status`, `e2e`, `create-pr`, `cleanup-branches`

### Testing
- **Development**: `p3 e2e` (~1-2 min) - Quick validation
- **PR Required**: `p3 e2e m7` (~5-10 min) - Full M7 validation
- **Extended**: `p3 e2e n100/v3k` - Comprehensive testing

### Daily Workflow

**CRITICAL RULES**:
1. Use `p3 <command>` (never direct python scripts)
2. Start from latest main (`git checkout main && git pull`)
3. Test before coding (`p3 e2e`)
4. Check README consistency after directory changes

**Session Sequence**:
```bash
# 1. Setup
git checkout main && git pull
p3 env-status

# 2. Branch
git checkout -b feature/description-fixes-N

# 3. Validate
p3 e2e  # Test system works

# 4. Work
# ... make changes ...
p3 format && p3 lint

# 5. PR
p3 create-pr "Description" N

# 6. Cleanup
p3 shutdown-all
```

**Conflict Resolution**:
1. Update main first: `git checkout main && git pull`
2. Rebase feature: `git checkout feature/branch && git rebase origin/main`
3. Test after resolution: `p3 e2e`

## Architecture Principles

**DRY/SSOT Implementation** - See `common/README.md` for complete details:
- **Directory paths**: Centralized in `common/directory_manager.py`
- **Configuration**: Single source at `common/config/`
- **Five-layer architecture**: Optimized data processing pipeline
- **Storage backends**: Local filesystem with cloud abstraction ready

**Key Rules**:
1. Never hard-code paths - use `directory_manager`
2. Use DataLayer enums instead of string paths
3. Update `directory_structure.yml` for new directories
4. Test path changes with migration scripts

**SSOT Configuration**: All configs at `common/config/` (migrated from `data/config/`)

---

**For detailed information, see directory-specific README files:**
- `README.md` - Complete project overview
- `common/README.md` - Configuration and directory management
- `ETL/README.md` - Data processing and SEC integration
- `dcf_engine/README.md` - DCF calculations and Graph RAG
- `graph_rag/README.md` - Semantic retrieval system
- `infra/README.md` - Infrastructure and deployment