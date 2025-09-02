# CLAUDE.md - Global Company Policies

## 🚨 MANDATORY TASK INITIATION PROTOCOL (READ FIRST)

**BEFORE ANY TASK EXECUTION - COMPLETE THIS CHECKLIST:**

### Phase 1: Foundation Knowledge ✅
- [ ] **Read CLAUDE.md completely** (this file) - understand all company policies  
- [ ] **Read README.md** - understand project architecture and setup
- [ ] **Identify task complexity** - single-step vs multi-step vs multi-domain

### Phase 2: Tool & Agent Selection ✅  
- [ ] **Determine tool requirements**:
  - Simple read/analysis → Direct tools (Read, Grep, Glob)
  - Git operations → Use `p3` commands (NEVER direct git for PR creation)
  - Complex workflows → Route through `agent-coordinator`
- [ ] **Select appropriate specialist agents** from 17 available:
  - Orchestration: agent-coordinator
  - Core Ops: git-ops, dev-quality, data-engineer, infra-ops, monitoring  
  - Specialized: quant-research, compliance-risk, backend-architect, web-frontend, web-backend, api-designer, security-engineer, performance-engineer, database-admin
  - Strategic: hrbp, revops

### Phase 3: Workflow Validation ✅
- [ ] **Confirm routing decision**:
  - Direct execution: Only for single-step read operations
  - Agent-coordinator: All complex, multi-step, or multi-domain tasks
  - P3 commands: All PR creation (`p3 create-pr "title" ISSUE_NUM`)
- [ ] **Validate execution keywords** for agent tasks:
  - Use "EXECUTE", "IMPLEMENT", "WRITE CODE" for action
  - End with "COMPLETE THE FULL IMPLEMENTATION"

### Phase 4: Quality Assurance ✅
- [ ] **Pre-execution checks**:
  - Issue linked and properly scoped (≤5 days)
  - GitHub issue exists for context preservation
  - Agent issue tracking confirmed (each agent → specific GitHub issue)
- [ ] **Compliance verification**:
  - English-only standard maintained
  - Configuration centralization (`common/config/`)  
  - Documentation currency planned

### Phase 5: Completion & PR Creation ✅
- [ ] **Task completion verification**:
  - All implementation work finished
  - Code tested and validated
  - Documentation updated appropriately
- [ ] **Self-validation of design goals** (MANDATORY before PR):
  - Execute validation commands to verify changes work as intended
  - Check compliance with original requirements
  - Validate no regressions introduced
  - Confirm architectural integrity maintained
- [ ] **Automatic PR creation** (MANDATORY for significant changes):
  - Route through `agent-coordinator` with EXECUTE keywords
  - Use `p3 create-pr "title" ISSUE_NUM` workflow
  - Include comprehensive change description
  - Add proper labels and milestone assignment

---

**❌ TASK EXECUTION WITHOUT COMPLETING THIS CHECKLIST VIOLATES COMPANY POLICY**

**🎯 QUICK REFERENCE - MOST COMMON VIOLATIONS:**
- Creating PRs with `gh pr create` instead of `p3 create-pr`
- Using direct tools for complex multi-step tasks instead of agent-coordinator
- Skipping README.md reading before architecture tasks
- Creating .md planning files instead of using GitHub Issues

---

## 👥 ORGANIZATIONAL AUTHORITY STRUCTURE

### 🚨 OFFICIAL ANNOUNCEMENT: P3 CLI MAINTENANCE TRANSFER (Effective Immediately)

**P3 CLI GOVERNANCE TRANSITION**: As of 2025-09-02, the P3 Command Line Interface maintenance and development responsibility is officially transferred from general infrastructure management to **infra-ops-agent** as the designated specialist.

**RATIONALE**: The P3 CLI has evolved from a complex 49-command system to a streamlined 8-workflow system with advanced worktree Python isolation capabilities. This simplified yet sophisticated system requires specialized infrastructure expertise for ongoing maintenance, optimization, and enhancement.

**INFRA-OPS-AGENT P3 RESPONSIBILITIES** (Effective Immediately):
- **P3 Command Development**: All new P3 command creation and modification
- **Workflow Optimization**: P3 workflow efficiency analysis and improvement
- **System Integration**: P3 integration with git workflows and CI/CD pipelines
- **Performance Monitoring**: P3 execution performance tracking and optimization
- **Documentation Maintenance**: P3 usage documentation and troubleshooting guides
- **Version Management**: P3 CLI versioning, release coordination, and deployment
- **User Support**: P3 workflow guidance and issue resolution

### HRBP Agent - CLAUDE.md Owner and Policy Manager
**DESIGNATED AUTHORITY**: HRBP agent has exclusive responsibility for:
- CLAUDE.md content design, updates, and version control
- Agent definition file standardization and template enforcement  
- Company policy compliance monitoring and violation tracking
- Cross-agent communication protocol specifications
- Policy exemption evaluation and approval processes
- **ORGANIZATIONAL GOVERNANCE**: P3 workflow policy compliance monitoring (not technical maintenance)

**CHANGE MANAGEMENT**: All CLAUDE.md modifications must be:
1. Proposed through HRBP agent via GitHub issue
2. Reviewed for organizational impact and consistency
3. Approved by HRBP agent before implementation
4. Documented with rationale and effective date

### Infra-Ops Agent - P3 CLI Technical Authority
**DESIGNATED AUTHORITY**: Infra-ops-agent has exclusive technical responsibility for:
- P3 CLI codebase maintenance and enhancement
- P3 command functionality development and testing
- P3 system architecture evolution and optimization
- P3 integration with development workflows and tools
- P3 performance analysis and system reliability
- P3 troubleshooting and technical support

---

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
  - P3 CLI maintenance and development
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
  - infra-ops-agent: Infrastructure management, P3 CLI maintenance, environment setup
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

## 📋 AGENT DOCUMENTATION STANDARDS

### Mandatory Agent File Structure (HRBP-Enforced)
ALL agent definition files MUST include:

```yaml
required_sections:
  - Precise role definition and scope boundaries
  - GitHub issue tracking link for context preservation  
  - CLAUDE.md policy compliance acknowledgment
  - P3 workflow integration requirements (infra-ops-agent leads P3 CLI maintenance)
  - Inter-agent communication protocols
  - Performance metrics and success criteria

documentation_consistency:
  - Standardized description format and length
  - Consistent terminology across all agents
  - Regular review cycles (quarterly by HRBP)
  - Version control for significant changes
```

**AGENT FILE TEMPLATE REQUIREMENTS**:
- **Header Section**: Name, description, tools specification
- **Core Expertise**: Detailed specialization areas and capabilities
- **Primary Responsibilities**: Specific duties and scope boundaries
- **Workflow Integration**: P3 command usage and agent-coordinator routing
- **Quality Standards**: Compliance requirements and success metrics
- **Issue Tracking**: Direct link to corresponding GitHub issue
- **Policy Compliance**: Reference to CLAUDE.md adherence

**STANDARDIZATION ENFORCEMENT**: HRBP agent conducts quarterly reviews of all agent definition files to ensure consistency, accuracy, and policy compliance.

### Sub-Agent Maintenance Guidelines

**P3 CLI GOVERNANCE STRUCTURE** (Updated 2025-09-02):
```yaml
p3_maintenance_hierarchy:
  technical_authority:
    - Primary: infra-ops-agent (P3 CLI codebase, commands, functionality)
    - Secondary: agent-coordinator (workflow integration, routing logic)
    
  policy_authority:
    - Primary: hrbp-agent (P3 workflow compliance, organizational governance)
    - Secondary: git-ops-agent (PR creation workflows, release coordination)
    
  operational_support:
    - dev-quality-agent: P3 command testing and validation
    - monitoring-agent: P3 performance tracking and system health
```

**MAINTENANCE RESPONSIBILITIES BY AGENT**:
```yaml
infra_ops_responsibilities:
  # P3 CLI Technical Ownership (NEW)
  - P3 command development and modification
  - P3 system architecture and optimization  
  - P3 version management and releases
  - P3 integration with development tools
  - P3 troubleshooting and technical support
  - P3 documentation maintenance
  
hrbp_responsibilities:
  # P3 Workflow Policy Governance (UNCHANGED)
  - P3 workflow compliance monitoring
  - P3 usage policy enforcement
  - P3 violation tracking and remediation
  - Agent training on P3 workflows
  
agent_coordinator_responsibilities:
  # P3 Workflow Integration (UNCHANGED)
  - P3 command routing in complex workflows
  - Multi-agent P3 workflow orchestration
  - P3 workflow optimization analysis
  
git_ops_responsibilities:
  # P3 Git Integration (UNCHANGED)
  - P3 PR creation workflow implementation
  - P3 git command integration
  - P3 release coordination support
```

**ESCALATION PROTOCOLS FOR P3 ISSUES**:
1. **Technical Issues**: Report directly to infra-ops-agent
2. **Policy Violations**: Report to hrbp-agent for compliance tracking
3. **Workflow Integration**: Route through agent-coordinator for analysis
4. **Performance Issues**: Monitor via monitoring-agent, escalate to infra-ops-agent

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
3. **SSOT I/O ENFORCEMENT** - Only use `common.core.directory_manager` for ALL file operations (see `common/README.md`)
4. **CONFIGURATION CENTRALIZATION** - Use `common/config/` for all configurations
5. **P3 WORKFLOW COMPLIANCE** - Never bypass p3 command system
6. **QUALITY ASSURANCE** - Test before PR creation (`p3 e2e` mandatory)
7. **AUTOMATIC PR CREATION** - Always create PR after completing significant changes via `agent-coordinator`
8. **DOCUMENTATION CURRENCY** - Update parent READMEs when modifying functionality  
9. **ENGLISH-ONLY STANDARD** - All technical content must use English
10. **OPERATIONAL EXCELLENCE** - Monitor and handle system errors appropriately
11. **PROJECT MANAGEMENT** - Break down oversized issues (>5 days) before execution

## 📋 PROJECT MANAGEMENT STANDARDS

### Issue Scope Policy
**REQUIREMENT**: All issues must be properly scoped (≤5 days) before execution
**ENFORCEMENT**: Agent-coordinator evaluates and decomposes oversized issues
**STANDARDS**: Single domain focus, clear dependencies, measurable outcomes

### GitHub Integration Requirements
**POLICY**: All development work must link to GitHub issues for traceability
**LABELING**: Use standardized labels that map to agent specializations
**TRACKING**: Maintain issue dependency relationships and progress visibility

### Agent Persistence Principle
**CRITICAL**: Each agent must maintain context and continuity through a structured persistence hierarchy.

#### Agent Context Management
```yaml
PERSISTENCE_HIERARCHY:
  # Long-term Objectives (Agent Description Files)
  - Agent capabilities and specializations
  - Core responsibilities and scope
  - Interface specifications and protocols
  - Permanent configuration and settings
  
  # Medium-term Goals (GitHub Issues)  
  - Current development objectives
  - Performance improvement targets
  - Integration milestones and dependencies
  - Context preservation across sessions
  
  # Short-term Work (Local, Gitignored)
  - Session-specific execution state
  - Temporary debugging information
  - Runtime logs and diagnostics
  - Transient workflow data
```

**IMPLEMENTATION REQUIREMENTS**:
- Every agent description file MUST link to its corresponding GitHub issue for context preservation
- Agent issues serve as persistent memory for medium-term objectives and session continuity
- Local work stays ephemeral and is automatically gitignored

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

## 🚨 POLICY COMPLIANCE MONITORING

### HRBP-Managed Violation Tracking System
**IMPLEMENTATION**: GitHub issues labeled "policy-violation" managed by HRBP agent
**ESCALATION**: Repeated violations trigger HRBP intervention and remediation protocols
**REMEDIATION**: Mandatory agent retraining, documentation updates, and process improvements

### Common Violations to Monitor
**CRITICAL POLICY VIOLATIONS**:
- **PR Creation Bypass**: Using `gh pr create` instead of mandatory `p3 create-pr`
- **Agent-Coordinator Bypass**: Using direct tools for complex multi-step tasks
- **Policy Reading Failure**: Skipping mandatory task initiation protocol checklist
- **GitHub Issue Avoidance**: Creating .md planning files instead of using GitHub issues
- **P3 Workflow Non-Compliance**: Bypassing required testing and validation steps
- **P3 CLI Unauthorized Modification**: Modifying P3 CLI without infra-ops-agent approval

### Violation Response Protocol
```yaml
violation_severity:
  level_1_warning:
    - First-time policy bypass
    - Immediate correction with documentation reference
    - HRBP notification for tracking
    
  level_2_intervention:
    - Repeated violations (2+ instances)
    - HRBP-mandated policy review session
    - GitHub issue creation for violation tracking
    
  level_3_remediation:
    - Persistent non-compliance (3+ instances)
    - Formal HRBP assessment and retraining
    - Agent definition file review and updates
    - Management escalation consideration
```

### Performance Metrics and Tracking
**HRBP MONITORING RESPONSIBILITIES**:
- Weekly policy compliance rate analysis
- Violation pattern identification and root cause analysis
- Agent-specific compliance tracking and improvement planning
- Quarterly compliance reporting and policy optimization recommendations

## 🛡️ OPERATIONAL RESILIENCE POLICY

### Error Management Standards
**REQUIREMENT**: All system errors must be handled gracefully with appropriate fallback mechanisms
**IMPLEMENTATION**: Agent-coordinator manages error detection, recovery protocols, and system resilience
**MONITORING**: Continuous error pattern analysis and system optimization

### Agent Availability Management  
**CURRENT STATUS**: Limited agent implementation requires robust fallback strategies
**POLICY**: All delegations must include fallback routing when primary agents unavailable
**EVOLUTION**: Agent ecosystem will expand based on usage patterns and business needs

## 🛠️ UNIFIED I/O CONSTRAINTS

**CRITICAL**: All file I/O operations must use the SSOT DirectoryManager system exclusively. No exceptions.

**ENFORCEMENT**: All PR creation must pass I/O compliance checks. Any non-SSOT I/O patterns will block PR approval.

**📖 DETAILED RULES**: See `common/README.md` for complete I/O standards, violation levels, migration guide, and compliance validation procedures.

### Quick Reference

#### ✅ REQUIRED Pattern
```python
from common.core.directory_manager import directory_manager, DataLayer
data_path = directory_manager.get_layer_path(DataLayer.RAW_DATA, partition="20250901")
```

#### ❌ PROHIBITED Patterns
```python
data_path = Path("build_data/stage_00_raw/20250901")  # FORBIDDEN
from common.io_utils import load_json                 # REMOVED
```

#### Validation Command
```bash
bash scripts/validate_io_compliance.sh  # Run before PR creation
```

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
**P3 CLI MAINTENANCE**: All P3 CLI modifications must route through infra-ops-agent

### Quality Assurance Requirements
**PRE-PR TESTING**: `p3 e2e m7` validation mandatory before PR creation
**README CONSISTENCY**: Update parent READMEs when modifying directory functionality
**ISSUE LINKING**: All changes must link to GitHub issues for traceability

---

**For detailed implementation procedures, see:**
- **Agent-Coordinator**: Workflow orchestration and delegation logic
- **README.md**: Complete project architecture and technical details  
- **Directory READMEs**: Component-specific implementation guidance
