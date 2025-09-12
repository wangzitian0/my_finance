# P3 Workflow Standards and Command System

**Authority**: Delegated from CLAUDE.md 
**Technical Maintainer**: infra-ops-agent (P3 CLI development)
**Policy Compliance**: hrbp-agent (workflow governance)
**Implementation Integration**: agent-coordinator (workflow orchestration)

## ⚙️ SYSTEM ARCHITECTURE STANDARDS

### Configuration Management
**CENTRALIZATION**: All configurations at `common/config/` for SSOT compliance
**DIRECTORY PATHS**: Use centralized `directory_manager` - never hard-code paths
**DATA LAYERS**: Use DataLayer enums instead of string paths

### Command System Compliance  
**P3 WORKFLOW**: Always use `p3 <command> [scope]` - never direct python scripts
**TESTING SCOPES**: f2 (dev), m7 (testing), n100 (validation), v3k (production)
**MANDATORY COMMANDS**: `p3 ready`, `p3 test`, `p3 ship`
**P3 CLI MAINTENANCE**: All P3 CLI modifications must route through infra-ops-agent

## P3 Workflow Decision Matrix

**🎯 "What do I want to do?" → Command Selection Guide**

| What You Want | Command | When to Use |
|---------------|---------|-------------|
| **"Start working"** | `p3 ready` | Beginning of work session, after restart, uncertain environment |
| **"Check my code"** | `p3 check [scope]` | After changes, before commit, during development (use `f2` for speed) |
| **"Test everything"** | `p3 test [scope]` | Before PR (F2 mandatory), after architectural changes, final validation |
| **"Create PR"** | `p3 ship "title" issue` | Work complete, tested, ready for review (F2 tests must pass) |
| **"What's wrong?"** | `p3 debug` | Tests failing, environment issues, services not responding |
| **"Fix everything"** | `p3 reset` | Multiple failures, corruption, last resort (⚠️ destructive) |
| **"Build datasets"** | `p3 build [scope]` | Data pipeline testing, analysis prep, production data generation |
| **"Show version"** | `p3 version` | Debugging version issues, documentation, system verification |

**Scope Guidelines**:
- **f2** (2 companies, 2-5min): Development default, PR validation
- **m7** (7 companies, 10-20min): Release prep, integration testing
- **n100** (100 companies, 1-3hr): Production validation, performance testing
- **v3k** (3000+ companies, 6-12hr): Full production datasets only

## 🚨 MANDATORY P3 USAGE PATTERNS

```yaml
REQUIRED_WORKFLOWS:
  daily_start:
    sequence: ["p3 ready"]
    frequency: "Every work session start"
    
  development_cycle:
    sequence: ["p3 check f2", "make changes", "p3 check f2", "repeat"]
    frequency: "During active development"
    
  pr_creation:
    sequence: ["p3 test f2", "p3 ship 'Title' ISSUE_NUM"]
    frequency: "When work is complete"
    requirements: "F2 tests MUST pass"
    
  emergency_recovery:
    sequence: ["p3 debug", "attempt fixes", "p3 reset if needed", "p3 ready"]
    frequency: "When systems fail"

PROHIBITED_PATTERNS:
  # NEVER bypass P3 system
  - Direct git commands for PR creation
  - Direct python script execution  
  - Manual environment setup
  - Skip testing before PR (F2 minimum mandatory)
  - Use old testing options (--skip-m7-test removed)
```

## 🎯 SCOPE SELECTION GUIDELINES

```yaml
SCOPE_DECISION_MATRIX:
  f2_fast_scope:
    companies: 2
    duration: "2-5 minutes"
    use_cases:
      - Development testing (mandatory before PR)
      - Quick code validation
      - Rapid feedback cycles
      - CI/CD validation
    when: "Default choice for most development work"
    
  m7_medium_scope:
    companies: 7
    duration: "10-20 minutes"  
    use_cases:
      - Pre-release validation
      - Integration testing
      - Performance baseline
      - Regression testing
    when: "Before major releases or architectural changes"
    
  n100_large_scope:
    companies: 100
    duration: "1-3 hours"
    use_cases:
      - Production validation
      - Performance testing
      - Data quality validation
      - Release candidate testing
    when: "Release preparation and production readiness"
    
  v3k_production_scope:
    companies: "3000+"
    duration: "6-12 hours"
    use_cases:
      - Full production datasets
      - Complete system validation
      - Production deployment
      - Final release validation
    when: "Production deployment only"

DEFAULT_RECOMMENDATIONS:
  development: "Always use f2 for development work"
  testing: "Use f2 for PR validation, m7 for release prep"
  production: "Use n100 for staging, v3k for production"
```

## Quality Assurance Requirements
**PRE-PR TESTING**: `p3 test m7` validation mandatory before PR creation
**README CONSISTENCY**: Update parent READMEs when modifying directory functionality
**ISSUE LINKING**: All changes must link to GitHub issues for traceability

## P3 CLI Governance Structure

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
  # P3 CLI Technical Ownership
  - P3 command development and modification
  - P3 system architecture and optimization  
  - P3 version management and releases
  - P3 integration with development tools
  - P3 troubleshooting and technical support
  - P3 documentation maintenance
  
hrbp_responsibilities:
  # P3 Workflow Policy Governance
  - P3 workflow compliance monitoring
  - P3 usage policy enforcement
  - P3 violation tracking and remediation
  - Agent training on P3 workflows
  
agent_coordinator_responsibilities:
  # P3 Workflow Integration
  - P3 command routing in complex workflows
  - Multi-agent P3 workflow orchestration
  - P3 workflow optimization analysis
  
git_ops_responsibilities:
  # P3 Git Integration
  - P3 PR creation workflow implementation
  - P3 git command integration
  - P3 release coordination support
```

**ESCALATION PROTOCOLS FOR P3 ISSUES**:
1. **Technical Issues**: Report directly to infra-ops-agent
2. **Policy Violations**: Report to hrbp-agent for compliance tracking
3. **Workflow Integration**: Route through agent-coordinator for analysis
4. **Performance Issues**: Monitor via monitoring-agent, escalate to infra-ops-agent

---

**DELEGATION AUTHORITY**: This document is maintained by infra-ops-agent under HRBP governance oversight. All technical modifications must follow P3 CLI governance protocols.