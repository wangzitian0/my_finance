# CLAUDE.md - Global Company Policies

<!-- Company Policy Document for SEC Filing-Enhanced Quantitative Trading Platform -->

> **Clean Repository Structure** (2025-08-26): Main repository contains only code, documentation, and configurations. Data subtree at `build_data/` with centralized configs at `common/config/`.

This file establishes the global company policies and standards for all Claude Code operations on this SEC Filing-Enhanced Graph RAG-powered DCF valuation system.

## 🏢 COMPANY GOVERNANCE POLICIES

### Universal Entry Point Policy

**CRITICAL**: ALL complex tasks MUST route through agent-coordinator for optimal resource allocation and quality assurance.

#### Core Delegation Principle
- **Agent-Coordinator**: Primary orchestration agent for all multi-step workflows
- **Direct Tools**: Only for simple, single-step operations (file reads, status checks)
- **Specialized Agents**: Selected by agent-coordinator based on task requirements

#### Task Classification Standards

**MANDATORY AGENT-COORDINATOR ROUTING**:
```yaml
ALWAYS_use_agent_coordinator:
  # Git Operations (NEVER use direct tools)
  - ALL git commands (status, diff, log, add, commit, push, rebase)
  - PR creation and management  
  - Branch operations and merging
  - Release coordination and tagging
  
  # Development Workflows (NEVER do directly)
  - Code implementation (writing, editing code files)
  - Multi-file refactoring and restructuring
  - Testing and validation workflows
  - Build and deployment processes
  
  # Complex Analysis Tasks
  - Multi-file code analysis and search
  - Architecture planning and system design
  - Data processing and ETL operations
  - Performance analysis and optimization
  
  # Infrastructure Operations  
  - Environment setup and configuration
  - System monitoring and diagnostics
  - Quality assurance processes
  - Documentation generation
```

**DIRECT TOOL USAGE ONLY**:
```yaml
simple_single_step_only:
  # File Operations (READ-ONLY information gathering)
  - Reading single files for information
  - Directory listing for exploration
  - File pattern searching (Glob, Grep) for analysis
  - Simple configuration lookups
  
  # Status and Information Commands
  - Quick system status checks (non-git)
  - Environment variable checks
  - Simple path validation
  
  # NOTE: If any task involves WRITING, MODIFYING, or EXECUTING 
  # multiple steps, it MUST go through agent-coordinator
```

**KEY PRINCIPLE**: When in doubt, route through agent-coordinator. Direct tools are ONLY for read-only information gathering and simple status checks.

#### Claude Code Operation Matrix

| Operation Type | Tool Usage | Example |
|---|---|---|
| **Git Commands** | 🚫 NEVER Direct → ✅ agent-coordinator | `git status` → Task(agent-coordinator) |
| **Code Writing** | 🚫 NEVER Direct → ✅ agent-coordinator | Writing functions → Task(backend-architect-agent) |
| **Multi-file Edit** | 🚫 NEVER Direct → ✅ agent-coordinator | Refactoring → Task(dev-quality-agent) |
| **PR Creation** | 🚫 NEVER Direct → ✅ agent-coordinator | `p3 create-pr` → Task(git-ops-agent) |
| **File Reading** | ✅ Direct Tools OK | Read("path/file.py") |
| **Directory Listing** | ✅ Direct Tools OK | LS("/path/to/dir") |
| **Pattern Search** | ✅ Direct Tools OK | Grep("pattern", glob="*.py") |
| **Status Check** | ✅ Direct Tools OK | Non-git status commands |

#### Violation Examples to Avoid
```bash
# ❌ WRONG: Direct git commands
Bash("git status")
Bash("git add .")
Bash("git commit -m 'message'")

# ✅ CORRECT: Route through agent-coordinator with EXECUTION instructions
Task(subagent_type="agent-coordinator", prompt="EXECUTE git commit workflow: analyze current changes with git status and git diff, add all modified files, create commit with descriptive message, and push to remote. WRITE CODE and COMPLETE THE FULL IMPLEMENTATION.")
```

```python
# ❌ WRONG: Direct code implementation  
Write("/path/file.py", "def new_function()...")
Edit("/path/file.py", old="...", new="...")

# ✅ CORRECT: Route through agent-coordinator with EXECUTION instructions
Task(subagent_type="agent-coordinator", prompt="IMPLEMENT new function in file.py: WRITE CODE to create the function, add proper error handling, update tests, and validate functionality. COMPLETE THE FULL IMPLEMENTATION, do not just provide a plan.")
```

#### Critical Execution Instructions for Sub-Agents

**🚨 MANDATORY EXECUTION KEYWORDS**: Always include these in Task prompts to ensure execution rather than planning:

```yaml
EXECUTION_REQUIRED_KEYWORDS:
  # Primary Action Directives (MUST include one)
  - "EXECUTE": For operational tasks (git, builds, deployments)
  - "IMPLEMENT": For code writing and development tasks  
  - "WRITE CODE": For programming tasks requiring file creation/modification
  - "COMPLETE THE FULL IMPLEMENTATION": End all prompts with this phrase

  # Clarity Modifiers (include when applicable)
  - "do not just provide a plan": Explicitly prevent planning-only responses
  - "write actual code": Distinguish from analysis tasks
  - "complete all steps": Ensure full workflow execution
  - "validate and test": Include verification steps

RESEARCH_ONLY_KEYWORDS:
  # Use these ONLY when you want analysis without execution
  - "ANALYZE": For code review and investigation
  - "RESEARCH": For information gathering
  - "STUDY": For understanding existing systems
```

**✅ CORRECT Task Prompt Structure**:
```python
# Full execution pattern
Task(subagent_type="[agent-type]", prompt="[ACTION_VERB] [specific_task]: [detailed_requirements]. COMPLETE THE FULL IMPLEMENTATION, do not just provide a plan.")

# Examples that WORK:
Task(subagent_type="git-ops-agent", prompt="EXECUTE PR creation workflow: analyze current branch changes, create comprehensive PR description, submit PR with proper labels and reviewers. COMPLETE THE FULL IMPLEMENTATION.")

Task(subagent_type="backend-architect-agent", prompt="IMPLEMENT user authentication system: WRITE CODE for login endpoints, add JWT token handling, create middleware, update database models. COMPLETE THE FULL IMPLEMENTATION, do not just provide a plan.")

Task(subagent_type="data-engineer-agent", prompt="EXECUTE ETL pipeline setup: configure data ingestion from SEC filings, implement processing logic, setup output validation. WRITE CODE and COMPLETE THE FULL IMPLEMENTATION.")
```

**❌ WRONG Task Prompts That Cause Planning-Only Responses**:
```python
# These cause agents to stop at planning phase:
Task(subagent_type="agent-coordinator", prompt="Handle git commit for changes")
Task(subagent_type="backend-architect-agent", prompt="Implement new function in file.py") 
Task(subagent_type="data-engineer-agent", prompt="Setup ETL pipeline")
```

## 🏷️ AGENT SPECIALIZATION DIRECTORY

**NOTE**: Detailed agent selection and routing logic is managed by agent-coordinator. This is a reference directory only.

### Available Specialist Agents
```yaml
core_operations:
  - git-ops-agent: Git workflows, PR management, release coordination
  - dev-quality-agent: Code quality, testing, validation processes
  - data-engineer-agent: ETL pipelines, SEC data processing
  - infra-ops-agent: Infrastructure management, environment setup
  - monitoring-agent: System monitoring, performance tracking
  
specialized_domains:
  - quant-research-agent: DCF calculations, financial analysis  
  - compliance-risk-agent: Regulatory compliance, audit processes
  - backend-architect-agent: System architecture, RAG design
  - web-frontend-agent: UI/UX, dashboard development
  - web-backend-agent: API design, microservices
  - api-designer-agent: API specification, integration design
  - security-engineer-agent: Security protocols, vulnerability assessment
  - performance-engineer-agent: Performance optimization, scaling
  - database-admin-agent: Database management, optimization
  
strategic_management:
  - hrbp-agent: Agent performance management, capability assessment
  - revops-agent: ROI analysis, cost optimization, efficiency metrics
```

## 🧠 CONTINUOUS IMPROVEMENT MANDATE

### Company Learning Policy
**REQUIREMENT**: All task execution must contribute to organizational learning and system optimization.

**Implementation**: Agent-coordinator manages all learning workflows, issue breakdown analysis, and optimization cycles. Detailed procedures are defined in agent-coordinator specifications.

### Performance Optimization Schedule
**POLICY**: System-wide optimization occurs every 10 PRs automatically
**SCOPE**: Agent performance analysis, workflow efficiency, and capability enhancement
**EXECUTION**: Agent-coordinator triggers and manages optimization cycles

## 🚨 NON-NEGOTIABLE COMPANY STANDARDS

1. **ARCHITECTURE FIRST** - Always read README.md before starting any task
2. **ORCHESTRATION MANDATORY** - Route complex tasks through agent-coordinator 
3. **CONFIGURATION CENTRALIZATION** - Use `common/config/` for all configurations
4. **P3 WORKFLOW COMPLIANCE** - Never bypass p3 command system
5. **QUALITY ASSURANCE** - Test before PR creation (`p3 e2e` mandatory)
6. **DOCUMENTATION CURRENCY** - Update parent READMEs when modifying functionality  
7. **ENGLISH-ONLY STANDARD** - All technical content must use English
8. **OPERATIONAL EXCELLENCE** - Monitor and handle system errors appropriately
9. **PROJECT MANAGEMENT** - Break down oversized issues (>5 days) before execution

## 📋 PROJECT MANAGEMENT STANDARDS

### Issue Scope Policy
**REQUIREMENT**: All issues must be properly scoped (≤5 days) before execution
**ENFORCEMENT**: Agent-coordinator evaluates and decomposes oversized issues
**STANDARDS**: Single domain focus, clear dependencies, measurable outcomes

### GitHub Integration Requirements
**POLICY**: All development work must link to GitHub issues for traceability
**LABELING**: Use standardized labels that map to agent specializations
**TRACKING**: Maintain issue dependency relationships and progress visibility

### Documentation and Planning Policy
**CRITICAL**: Use GitHub Issues for ALL planning and documentation, NOT additional .md files

#### Planning Management Rules
```yaml
ALWAYS_use_github_issues:
  # Project Planning (NEVER create .md files)
  - Architecture planning and design documents
  - Implementation roadmaps and phase planning  
  - Task breakdown and dependency tracking
  - Progress reports and status updates
  - Review findings and recommendations
  - Optimization plans and strategies

PROHIBITED_documentation_files:
  - ARCHITECTURE_REVIEW.md
  - IMPLEMENTATION_PLAN.md  
  - OPTIMIZATION_ROADMAP.md
  - PROJECT_STATUS.md
  - Any planning or tracking .md files

ALLOWED_documentation_only:
  - README.md (project overview and setup)
  - CLAUDE.md (global company policies)
  - Module-specific README.md (technical documentation)
  - API documentation (when required)
```

**ENFORCEMENT**: All planning, tracking, and architectural documentation MUST be managed through GitHub Issues with proper labels, milestones, and cross-references. Never create additional .md files for project management.

## 🛡️ OPERATIONAL RESILIENCE POLICY

### Error Management Standards
**REQUIREMENT**: All system errors must be handled gracefully with appropriate fallback mechanisms
**IMPLEMENTATION**: Agent-coordinator manages error detection, recovery protocols, and system resilience
**MONITORING**: Continuous error pattern analysis and system optimization

### Agent Availability Management  
**CURRENT STATUS**: Limited agent implementation requires robust fallback strategies
**POLICY**: All delegations must include fallback routing when primary agents unavailable
**EVOLUTION**: Agent ecosystem will expand based on usage patterns and business needs

## 🌐 ENGLISH-ONLY STANDARD

**CRITICAL**: All technical content must use English for international standards compliance.

### Mandatory English Usage
- **Code**: Variables, functions, classes, modules
- **Documentation**: Comments, docstrings, README files  
- **Configuration**: Config keys, values, documentation
- **Operations**: Log messages, error messages, commit messages
- **Communication**: Issue tracking, PR descriptions, technical discussions

### Exception Policy
**Acceptable Non-English**: User-facing templates for localization (in dedicated i18n directories only)

## ⚙️ SYSTEM ARCHITECTURE STANDARDS

### Configuration Management
**CENTRALIZATION**: All configurations at `common/config/` for SSOT compliance
**DIRECTORY PATHS**: Use centralized `directory_manager` - never hard-code paths
**DATA LAYERS**: Use DataLayer enums instead of string paths

### Command System Compliance  
**P3 WORKFLOW**: Always use `p3 <command> [scope]` - never direct python scripts
**TESTING SCOPES**: f2 (dev), m7 (testing), n100 (validation), v3k (production)
**MANDATORY COMMANDS**: `p3 env-status`, `p3 e2e`, `p3 create-pr`

### Quality Assurance Requirements
**PRE-PR TESTING**: `p3 e2e m7` validation mandatory before PR creation
**README CONSISTENCY**: Update parent READMEs when modifying directory functionality
**ISSUE LINKING**: All changes must link to GitHub issues for traceability

---

**For detailed implementation procedures, see:**
- **Agent-Coordinator**: Workflow orchestration and delegation logic
- **README.md**: Complete project architecture and technical details  
- **Directory READMEs**: Component-specific implementation guidance
