# CLAUDE.md - Claude Code Instructions

<!-- Test comment added for sub-agent activation testing - 2025-08-26 -->

> **Clean Repository Structure** (2025-08-26): Main repository contains only code, documentation, and configurations. Data subtree at `build_data/` with centralized configs at `common/config/`.

This file provides guidance to Claude Code when working with this SEC Filing-Enhanced Graph RAG-powered DCF valuation system.

## 🤖 MANDATORY SUB-AGENT ORCHESTRATION

**CRITICAL**: ALL tasks (except trivial file operations) MUST start with agent-coordinator for analysis and delegation.

### Universal Entry Point Policy

1. **ALWAYS START WITH AGENT-COORDINATOR**: Every user request must begin with Task(agent-coordinator)
2. **Analysis First**: Agent-coordinator analyzes the task and determines optimal sub-agent delegation
3. **Learning Integration**: Each task contributes to the continuous learning and optimization system
4. **Issue-Based Tracking**: All tasks link to GitHub issues for experience accumulation and pattern analysis

### Mandatory Workflow Pattern

```typescript
// ✅ MANDATORY PATTERN: Start every task with agent-coordinator
User Request: "Any development, git, data, or infrastructure task"
↓
Step 1: Task(agent-coordinator, "Analyze and delegate: [user request]")
↓  
Step 2: Agent-coordinator analyzes task complexity, issue labels, and delegates to appropriate agents
↓
Step 3: Specialized agents execute with full context and learning feedback
```

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

## 🏷️ ISSUE LABEL-AGENT MAPPING SYSTEM

### Label-Based Agent Selection

| Issue Label | Primary Agent | Secondary Agents | Priority Level |
|-------------|---------------|------------------|----------------|
| `git-ops` | git-ops-agent | dev-quality-agent | P0-Critical |
| `infrastructure` | infra-ops-agent | monitoring-agent | P0-Critical |
| `data-processing` | data-engineer-agent | monitoring-agent, database-admin-agent | P1-High |
| `web-frontend` | web-frontend-agent | api-designer-agent, performance-engineer-agent | P1-High |
| `web-backend` | web-backend-agent | database-admin-agent, security-engineer-agent | P1-High |
| `security` | security-engineer-agent | compliance-risk-agent | P0-Critical |
| `performance` | performance-engineer-agent | monitoring-agent, database-admin-agent | P1-High |
| `dcf-engine` | quant-research-agent | data-engineer-agent, compliance-risk-agent | P1-High |
| `graph-rag` | backend-architect-agent | data-engineer-agent, database-admin-agent | P1-High |
| `testing` | dev-quality-agent | git-ops-agent | P1-High |
| `compliance` | compliance-risk-agent | quant-research-agent | P0-Critical |
| `api-design` | api-designer-agent | web-backend-agent, security-engineer-agent | P2-Medium |
| `database` | database-admin-agent | performance-engineer-agent, security-engineer-agent | P1-High |
| `monitoring` | monitoring-agent | infra-ops-agent, performance-engineer-agent | P2-Medium |
| `architecture` | backend-architect-agent | performance-engineer-agent, security-engineer-agent | P1-High |

## 🧠 CONTINUOUS LEARNING SYSTEM

### Learning Workflow (Every Task)

1. **Pre-Task Analysis**: Agent-coordinator analyzes issue labels and task complexity
2. **Execution Tracking**: Primary and secondary agents document decisions and blockers
3. **Post-Task Reflection**: Generate lessons learned and optimization suggestions
4. **Issue Comments**: Post learning insights to the linked GitHub issue as comments

### PR Learning Integration

**MANDATORY**: Every PR must include learning feedback in the associated issue:

```markdown
## 🧠 Task Learning Report

### Agent Performance Analysis
- **Primary Agent Used**: [agent-name]
- **Secondary Agents**: [list]  
- **Task Complexity**: [Simple/Medium/Complex/Critical]
- **Execution Time**: [duration]
- **Success Metrics**: [specific measurements]

### Lessons Learned
- **What Worked Well**: [specific successes]
- **Optimization Opportunities**: [areas for improvement]
- **Agent Delegation Accuracy**: [was the right agent chosen?]
- **Workflow Efficiency**: [bottlenecks, delays, or quick wins]

### Proposed Optimizations
- **Sub-Agent Improvements**: [specific agent enhancements needed]
- **CLAUDE.md Updates**: [configuration or process changes]
- **Label-Agent Mapping**: [mapping accuracy and suggested adjustments]

### Next Task Predictions
- **Similar Tasks**: [expected related work]
- **Resource Requirements**: [computational, time, or expertise needs]
- **Risk Factors**: [potential issues to watch for]
```

### Automatic System Optimization (Every 10 PRs)

**CRITICAL**: The system now automatically triggers optimization when PR numbers are divisible by 10.

**Automatic Trigger Logic**:
```typescript
// Automatic optimization detection
if (PR_NUMBER % 10 === 0) {
  // Automatically trigger system optimization
  Task(agent-coordinator, "AUTO_OPTIMIZATION_TRIGGER: PR #${PR_NUMBER} reached. Analyze last 10 PRs and optimize entire sub-agent ecosystem based on accumulated learning data from issue comments.")
}
```

**Trigger Examples**:
- PR #10 → First system optimization
- PR #20 → Second optimization cycle  
- PR #30 → Third optimization cycle
- And so on...

**Optimization Execution Pattern**:
1. **Detection Phase**: Detect when PR number % 10 === 0
2. **Analysis Phase**: Collect learning data from last 10 GitHub issue comments
3. **Optimization Phase**: Generate system-wide improvements
4. **Implementation Phase**: Update sub-agents and CLAUDE.md automatically
5. **Documentation Phase**: Document optimization results in the milestone PR

**Optimization Scope** (Executed Automatically):
1. **Label-Agent Mapping Refinement**: Adjust based on success patterns from last 10 PRs
2. **Agent Role Evolution**: Modify agent capabilities based on usage patterns
3. **Workflow Pattern Updates**: Optimize common multi-agent sequences
4. **Performance Metrics**: Update KPIs and success criteria  
5. **CLAUDE.md Configuration**: System-wide process improvements
6. **New Agent Specializations**: Create new agents if patterns show need

## 🚨 CRITICAL REQUIREMENTS

1. **ALWAYS read README.md first** - Contains complete project architecture
2. **ALWAYS route through agent-coordinator** - For optimal sub-agent utilization
3. **Use `common/config/` for all configurations** - Centralized SSOT system
4. **Follow p3 command workflow** - Never use direct python scripts
5. **Test before PR creation** - `p3 e2e` is mandatory
6. **Update parent READMEs** - When modifying directory functionality
7. **ENGLISH-ONLY POLICY** - All technical content must use English

## 🌐 ENGLISH-ONLY CODING STANDARDS

**CRITICAL**: All technical content in this quantitative trading platform must use English for international standards compliance and professional development practices.

### Mandatory English Usage

#### ✅ MUST BE IN ENGLISH:
- **Code**: All variable names, function names, class names, module names
- **Comments**: All code comments, docstrings, and inline documentation
- **Configuration Files**: All config keys, values, and documentation
- **Log Messages**: All logging output, error messages, and debug information
- **Documentation**: README files, technical specifications, API docs
- **Git Commits**: All commit messages, PR titles, and descriptions
- **Issue Tracking**: Issue titles, descriptions, and comments
- **Database Schema**: Table names, column names, constraints, indexes

#### ✅ ACCEPTABLE NON-ENGLISH:
- **Templates**: User-facing templates for multi-language support (e.g., `templates/` directory)
- **Test Data**: Sample data strings for testing internationalization features
- **Build Artifacts**: Generated content that may contain localized data
- **User Interface Strings**: UI text meant for localization (must be in separate i18n files)

### Implementation Guidelines

#### Code Examples

```python
# ✅ CORRECT: English code
def calculate_dcf_valuation(company_ticker, growth_rate, discount_rate):
    """Calculate DCF valuation for a given company.
    
    Args:
        company_ticker: Stock ticker symbol (e.g., 'AAPL')
        growth_rate: Annual growth rate as decimal (e.g., 0.05 for 5%)
        discount_rate: Discount rate as decimal (e.g., 0.10 for 10%)
    
    Returns:
        Calculated DCF value as float
    """
    logger.info(f"Starting DCF calculation for {company_ticker}")
    # Implementation here
    logger.info("DCF calculation completed successfully")
    return dcf_value

# ❌ INCORRECT: Non-English code
def 计算DCF估值(公司代码, 增长率, 折现率):  # Don't do this
    """计算给定公司的DCF估值"""  # Don't do this
    logger.info(f"开始计算 {公司代码} 的DCF")  # Don't do this
```

#### Configuration Examples

```yaml
# ✅ CORRECT: English configuration
database_config:
  host: "localhost"
  port: 5432
  database_name: "quantitative_trading"
  connection_timeout: 30
  retry_attempts: 3
  
# ❌ INCORRECT: Non-English configuration  
数据库配置:  # Don't do this
  主机: "localhost"  # Don't do this
```

#### Git Commit Examples

```bash
# ✅ CORRECT: English commit messages
git commit -m "Implement SEC filing data integration for M7 companies

Added semantic embedding generation and vector search capabilities
for enhanced Graph RAG query processing with regulatory backing.

Fixes #123"

# ❌ INCORRECT: Non-English commit messages
git commit -m "实现SEC文件数据集成"  # Don't do this
```

### Enforcement Mechanisms

1. **Pre-commit Hooks**: Automated language validation for code and comments
2. **CI/CD Validation**: GitHub Actions check for English-only policy compliance
3. **Agent Enforcement**: Sub-agents will validate and suggest English alternatives
4. **Code Review Requirements**: All PRs must pass English-only validation

### Exception Handling

**For Legacy Code**: When working with existing non-English content:
1. **Refactor Gradually**: Update to English during normal maintenance
2. **Document Exceptions**: Clearly mark temporary non-English content with TODO comments
3. **Migration Plan**: Create issues to track English conversion progress

**For International Features**: When building localization features:
1. **Separate Concerns**: Keep internationalized content in dedicated i18n directories
2. **English Default**: Always provide English as the primary/fallback language
3. **Template Isolation**: Non-English content only in `templates/` or `i18n/` directories

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

**Command Quality**: The p3 CLI automatically validates and sanitizes commands before execution to prevent syntax errors (Issue #153 protection).

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

## Enhanced Git Workflow with Auto-Optimization

**CRITICAL**: All git operations now include automatic optimization detection and execution every 10 PRs.

#### Mandatory PR Creation Pattern

```typescript
// Every PR creation must follow this pattern
User: "Create PR for [task]"
↓
Step 1: Task(agent-coordinator, "Analyze and delegate PR creation with auto-optimization check")
↓
Step 2: Agent-coordinator checks: if (PR_NUMBER % 10 === 0) → Trigger AUTO_OPTIMIZATION_TRIGGER
↓  
Step 3: If optimization triggered → Execute full system optimization before completing PR
↓
Step 4: Complete PR creation with learning report posted to issue comments
```

#### Auto-Optimization Integration Workflow

**For Regular PRs** (PR# % 10 ≠ 0):
1. Standard task execution via agent-coordinator
2. Generate and post learning report to issue comments  
3. Complete PR creation normally

**For Milestone PRs** (PR# % 10 === 0, e.g., #10, #20, #30):
1. **Pre-Optimization**: Complete the original task first
2. **Auto-Trigger Detection**: Detect milestone PR number  
3. **System Optimization**: Execute comprehensive analysis of last 10 PRs
4. **Implementation**: Update agents and CLAUDE.md automatically
5. **Documentation**: Post optimization results to milestone PR
6. **Completion**: Finalize milestone PR with both task results + optimization report

**See README.md for complete workflow.** Claude requirements:

### Protection Model

- ✅ **p3 create-pr workflow**: Fully supported
- ❌ **Direct git push**: Blocked to enforce testing
- 🎯 **Goal**: All code passes M7/F2 tests before reaching remote

### Common Issues

- **"Cannot create PR from main"**: Check worktree context with `git branch --show-current`
- **"Direct push blocked"**: Ensure `P3_CREATE_PR_PUSH` environment variable set
- **Testing failures**: Fix issues, don't skip validation - run `p3 e2e f2`
- **Malformed pixi commands**: Automatic sanitization fixes unquoted parameters (Issue #153 resolved)

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

**Quality Assurance**: p3.py includes automatic command sanitization for malformed pixi commands (fixed Issue #153). String parameters like 'f2', ['sec_edgar'], 'development' are automatically quoted when syntax errors are detected.

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

**AI-Generated Command Guidelines**:
- The p3 CLI automatically sanitizes malformed commands with unquoted parameters
- String parameters will be auto-quoted: `f2` → `'f2'`, `[sec_edgar]` → `['sec_edgar']`
- Watch for sanitization messages: "⚠️ Fixed malformed pixi command (Issue #153)"
- Trust the automatic fixes - they prevent common syntax errors in pixi commands

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