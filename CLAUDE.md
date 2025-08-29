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

# ✅ CORRECT: Route through agent-coordinator
Task(subagent_type="agent-coordinator", prompt="Handle git commit for changes")
```

```python
# ❌ WRONG: Direct code implementation  
Write("/path/file.py", "def new_function()...")
Edit("/path/file.py", old="...", new="...")

# ✅ CORRECT: Route through agent-coordinator
Task(subagent_type="agent-coordinator", prompt="Implement new function in file.py")
```

## 🏷️ AGENT SPECIALIZATION DIRECTORY

**NOTE**: Detailed agent selection and routing logic is managed by agent-coordinator. This is a reference directory only. Each agent has a dedicated GitHub management issue for context tracking (see Agent Context Management Policy).

### Available Specialist Agents
```yaml
core_operations:
  - git-ops-agent: Git workflows, PR management, release coordination
    # Management Issue: [Agent] Context and Responsibility Tracking - git-ops-agent
  - dev-quality-agent: Code quality, testing, validation processes
    # Management Issue: [Agent] Context and Responsibility Tracking - dev-quality-agent
  - data-engineer-agent: ETL pipelines, SEC data processing
    # Management Issue: [Agent] Context and Responsibility Tracking - data-engineer-agent
  - infra-ops-agent: Infrastructure management, environment setup
    # Management Issue: [Agent] Context and Responsibility Tracking - infra-ops-agent
  - monitoring-agent: System monitoring, performance tracking
    # Management Issue: [Agent] Context and Responsibility Tracking - monitoring-agent
  
specialized_domains:
  - quant-research-agent: DCF calculations, financial analysis
    # Management Issue: [Agent] Context and Responsibility Tracking - quant-research-agent
  - compliance-risk-agent: Regulatory compliance, audit processes
    # Management Issue: [Agent] Context and Responsibility Tracking - compliance-risk-agent
  - backend-architect-agent: System architecture, RAG design
    # Management Issue: [Agent] Context and Responsibility Tracking - backend-architect-agent
  - web-frontend-agent: UI/UX, dashboard development
    # Management Issue: [Agent] Context and Responsibility Tracking - web-frontend-agent
  - web-backend-agent: API design, microservices
    # Management Issue: [Agent] Context and Responsibility Tracking - web-backend-agent
  - api-designer-agent: API specification, integration design
    # Management Issue: [Agent] Context and Responsibility Tracking - api-designer-agent
  - security-engineer-agent: Security protocols, vulnerability assessment
    # Management Issue: [Agent] Context and Responsibility Tracking - security-engineer-agent
  - performance-engineer-agent: Performance optimization, scaling
    # Management Issue: [Agent] Context and Responsibility Tracking - performance-engineer-agent
  - database-admin-agent: Database management, optimization
    # Management Issue: [Agent] Context and Responsibility Tracking - database-admin-agent
  
strategic_management:
  - hrbp-agent: Agent performance management, capability assessment
    # Management Issue: [Agent] Context and Responsibility Tracking - hrbp-agent
  - revops-agent: ROI analysis, cost optimization, efficiency metrics
    # Management Issue: [Agent] Context and Responsibility Tracking - revops-agent
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

### Agent Context Management Policy
**REQUIREMENT**: Each agent must have a dedicated GitHub issue for context tracking and organizational management

#### Agent Management Issue Standards
```yaml
agent_context_tracking:
  # Issue Creation Requirements
  - Each agent has dedicated management issue
  - Issues labeled "management" for organizational tracking
  - Issues created and immediately closed for documentation
  - Issue title format: "[Agent] Context and Responsibility Tracking - [agent-name]"
  
  # Content Requirements  
  - Agent specialization and core responsibilities
  - Capability usage design and effective utilization
  - Current organizational role and integration points
  - Performance tracking and assessment framework
  - Context persistence for organizational learning
  
  # Management Integration
  - All agents reference their management issue
  - Issues serve as persistent context repository
  - Regular updates for capability evolution
  - Cross-agent coordination and dependency tracking
```

**PURPOSE**: Establish persistent context tracking, improve organizational management, and maintain consistent documentation standards across the entire agent ecosystem.

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
