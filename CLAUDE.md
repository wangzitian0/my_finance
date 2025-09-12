# CLAUDE.md - Streamlined Company Policies (HRBP Issue #174 Implementation)

## 🚨 MANDATORY TASK INITIATION PROTOCOL

**CRITICAL**: Complete these 5 phases before any task execution:

### Phase 1: Foundation ✅
- [ ] Read CLAUDE.md (this file) - company policies
- [ ] Read README.md - project architecture  
- [ ] Identify task complexity: simple/multi-step/multi-domain
- [ ] Think like an engineer: reuse existing patterns, avoid bypassing core processes
- [ ] **NEVER BYPASS P3 SHIP FAILURES**: Always fix root causes, never create workarounds

### Phase 2: Tool Selection ✅  
- [ ] Simple read/analysis → Direct tools (Read, Grep, Glob)
- [ ] Git operations → `p3` commands (NEVER direct git for PR creation)
- [ ] Complex workflows → Route through `agent-coordinator`

### Phase 3: Workflow Validation ✅
- [ ] Direct execution: Only single-step read operations
- [ ] Agent-coordinator: All complex, multi-step, or multi-domain tasks
- [ ] P3 commands: All PR creation (`p3 ship "title" ISSUE_NUM`)

### Phase 4: Quality Assurance ✅
- [ ] Issue linked and scoped (≤5 days)
- [ ] GitHub issue exists for context preservation
- [ ] English-only standard maintained

### Phase 5: Completion & PR ✅
- [ ] Task completion verified
- [ ] Self-validation executed  
- [ ] **MANDATORY PR creation**: Route to `git-ops-agent` with `p3 ship` workflow

---

## 👥 CORE DELEGATION POLICIES

### **Universal Entry Point**: Agent-Coordinator
- **ALL complex tasks** route through agent-coordinator
- **Direct tools**: Only for simple, single-step read operations
- **PR Creation Exception**: Routes DIRECTLY to git-ops-agent

### **Available Agents** (17 total)
```yaml
orchestration: agent-coordinator
core_ops: git-ops, dev-quality, data-engineer, infra-ops, monitoring  
specialized: quant-research, compliance-risk, backend-architect, web-frontend, web-backend, api-designer, security-engineer, performance-engineer, database-admin
strategic: hrbp, revops
```

### **Critical Execution Requirements**
- Use **"EXECUTE"**, **"IMPLEMENT"**, **"WRITE CODE"** for action tasks
- End with **"COMPLETE THE FULL IMPLEMENTATION"**
- Never accept planning-only responses from agents

---

## 🏢 AUTHORITY STRUCTURE 

### P3 CLI Governance (Effective 2025-09-02)
- **Technical Authority**: infra-ops-agent (P3 CLI maintenance, development)
- **Policy Authority**: hrbp-agent (P3 workflow compliance, governance)

### Policy Management
- **CLAUDE.md Owner**: hrbp-agent (exclusive authority for policy updates)
- **Agent Standards**: hrbp-agent (quarterly reviews, consistency enforcement)

---

## 🚨 NON-NEGOTIABLE STANDARDS

1. **ORCHESTRATION MANDATORY**: Route complex tasks through agent-coordinator
2. **P3 WORKFLOW COMPLIANCE**: Never bypass p3 command system (`p3 ready`, `p3 test`, `p3 ship`)
3. **SSOT I/O ENFORCEMENT**: Use `common.core.directory_manager` for ALL file operations
4. **CONFIGURATION CENTRALIZATION**: All configs at `common/config/`
5. **AUTOMATIC PR CREATION**: Always create PR via `git-ops-agent` after significant changes
6. **ENGLISH-ONLY STANDARD**: All technical content in English
7. **GITHUB ISSUES ONLY**: Never create .md planning files - use GitHub Issues

---

## ⚙️ SIMPLIFIED WORKFLOW MATRIX

| Task Type | Route To | Example |
|-----------|----------|---------|
| **Git Operations** | agent-coordinator | `git status` → Task(agent-coordinator) |
| **PR Creation** | git-ops-agent (direct) | Create PR → Task(git-ops-agent) |
| **Code Writing** | agent-coordinator | Write functions → Task(agent-coordinator) |
| **File Reading** | Direct tools | Read("file.py") |
| **Complex Analysis** | agent-coordinator | Multi-file analysis → Task(agent-coordinator) |

---

## 📋 DELEGATED GOVERNANCE AREAS

### Agent-Coordinator Responsibilities
- **Workflow Matrix**: Task-to-agent mapping (see agent-coordinator.md)
- **Multi-Agent Coordination**: Inter-agent collaboration patterns
- **Execution Enforcement**: Ensure agents execute vs. plan

### HRBP Agent Responsibilities  
- **Agent Performance**: Capability assessment, organizational development
- **Policy Compliance**: Violation tracking, remediation protocols
- **Documentation Standards**: Agent file consistency, quarterly reviews

### Infra-Ops Agent Responsibilities
- **P3 CLI Technical**: Command development, system integration, performance
- **Environment Management**: Worktree isolation, dependency management

### RevOps Agent Responsibilities
- **Cost Optimization**: ROI analysis, efficiency metrics
- **Resource Planning**: Capacity analysis, budget optimization

---

## 🎯 QUICK VIOLATION REFERENCE

**Most Common Policy Violations**:
- Creating PRs with `gh pr create` instead of `p3 ship`
- Routing PR creation through agent-coordinator instead of git-ops-agent directly
- Using direct tools for complex tasks instead of agent-coordinator
- Creating .md planning files instead of GitHub Issues
- Bypassing P3 workflow system

---

**For detailed procedures**: See specialized agent documentation and README.md

**Current Reduction**: ~600 lines → ~150 lines (75% reduction) with governance delegation

<!-- STREAMLINED DEPLOYMENT: 2025-09-12T12:00:40.897048 -->
<!-- FULL VERSION BACKUP: CLAUDE_FULL_BACKUP.md -->
<!-- DEPLOYMENT SCRIPT: deploy_streamlined_policies.py -->