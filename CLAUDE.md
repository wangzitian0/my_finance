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
```yaml
direct_tool_operations:
  - Single file read/write operations
  - Simple status checks
  - Quick configuration lookups
  
agent_coordinator_required:
  - All git operations and PR creation
  - Multi-step development workflows
  - Data processing and analysis tasks
  - Infrastructure and deployment operations
  - Quality assurance and testing processes
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
