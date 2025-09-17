# CLAUDE.md - Streamlined Company Policies (HRBP Issue #174 Implementation)

## 🚨 MANDATORY TASK INITIATION PROTOCOL 

**🔒 PROTECTED GOVERNANCE DOCUMENT**: This checklist is under HRBP exclusive protection - cannot be arbitrarily deleted

**CRITICAL**: Complete these 5 phases before any task execution:

### Phase 1: Foundation ✅
**Objective**: Understand project environment and task requirements
**Completion Standard**: Complete understanding of task, architecture, policies, and tool selection
**Self-Modification**: If not fully understood, continue studying until clear

- [ ] Read CLAUDE.md (this file) - company policies
- [ ] Read README.md files - project architecture (layered directory approach)
- [ ] Identify task complexity: simple/multi-step/multi-domain
- [ ] Select appropriate tools: Direct tools vs agent-coordinator vs p3 commands
- [ ] **Engineering mindset**: Reuse existing patterns, avoid bypassing core processes
- [ ] **NEVER BYPASS P3 SHIP FAILURES**: Always fix root causes, never create workarounds

### Phase 2: Task Breakdown ✅
**Objective**: Create clear and executable implementation plan
**Completion Standard**: Specific TodoWrite task list with clear execution steps
**Self-Modification**: If plan is unclear or not executable, re-analyze and break down

- [ ] Analyze task scope and dependencies
- [ ] Create TodoWrite task list with specific, actionable items
- [ ] Plan execution sequence and milestone checkpoints
- [ ] Identify potential risks and mitigation strategies
- [ ] Route complex workflows through `agent-coordinator`
- [ ] Validate task scope ≤5 days, create GitHub issue if needed

### Phase 3: Implementation & Unit Testing ✅
**Objective**: Implement functionality and ensure code correctness
**Completion Standard**: All functionality implemented, unit tests pass, code runs correctly
**Self-Modification**: If errors or test failures occur, fix code until all tests pass

- [ ] **Migrate TodoWrite tasks to GitHub issue todo list** for persistent tracking
- [ ] Execute implementation tasks using GitHub issue as progress tracker
- [ ] Write and run unit tests for new functionality
- [ ] Fix bugs and errors as they arise, document solutions in GitHub issue
- [ ] Mark GitHub issue tasks as completed upon successful implementation
- [ ] Self-validate functionality meets requirements
- [ ] **Update GitHub issue with test results and validation status**
- [ ] **No progression until all unit tests pass and GitHub issue reflects completion**

### Phase 4: Quality Assurance ✅
**Objective**: Ensure code quality and architectural compliance
**Completion Standard**: Pass all quality checks and policy validation
**Self-Modification**: If standards not met, modify code/architecture until fully compliant

- [ ] **File placement validation**: Correct L1/L2 directories, avoid root placement
- [ ] **CLAUDE.md Policy Compliance**: P3 workflow, SSOT enforcement, configuration centralization
- [ ] **Technical Standards**: Code quality, modular architecture, TypeScript usage, error handling
- [ ] **System Architecture**: RAG/DCF integration, database patterns, API consistency, performance
- [ ] **Security & Testing**: Financial platform security, test coverage requirements
- [ ] **English-only standard**: All technical content in English
- [ ] **Temporary Script Cleanup**: Remove one-time scripts (e.g., migration, setup scripts) - only commit if essential for future use

### Phase 5: Completion & PR ✅
**Objective**: Complete code commit and successfully create PR
**Completion Standard**: PR created successfully, CI passes, all process validation passes
**Self-Modification**: If any step fails, fix issues until PR is successfully created

- [ ] **CODE COMMIT**: Commit all changes with clear commit messages
- [ ] **SYNC MAIN**: Rebase against main branch (`git fetch origin main && git rebase origin/main`)
- [ ] **README REVIEW**: **MANDATORY** - Review and update ALL README.md files in directories containing modified files + perform hierarchical review from modified directories up to root directory (may require updating multiple README.md files in the path hierarchy). Every code change must be reflected in corresponding directory documentation.
- [ ] **FINAL COMMIT**: Commit documentation updates if any README changes were made
- [ ] **MANDATORY PR creation**: Route DIRECTLY to `git-ops-agent` with `p3 ship` workflow
- [ ] **Self-validation**: Verify `p3 ship` completed successfully with all tests passing
- [ ] **Policy compliance**: Verify no checklist protection violations occurred
- [ ] **CI SUCCESS**: Ensure PR passes all automated checks

---

## 📋 PR REVIEW CHECKLIST

**Critical PR Review Standards (Applied in Phase 4):**

### 🔒 CLAUDE.md Policy Compliance
- [ ] P3 workflow compliance (proper use of p3 commands)
- [ ] SSOT I/O enforcement (use of common.core.directory_manager)
- [ ] Configuration centralization (common/config/ usage)
- [ ] English-only standard adherence
- [ ] GitHub issue traceability

### ⚙️ Technical Standards
- [ ] Code quality and best practices
- [ ] **Modular architecture**: L1/L2 structure, no cross-module deps, use common/core
- [ ] TypeScript usage for new features
- [ ] Proper error handling and validation
- [ ] Existing code pattern consistency
- [ ] **Module interface compliance**:
  - [ ] Use common.core.directory_manager for file operations
  - [ ] Follow established import/export patterns
  - [ ] Respect module boundaries and abstraction layers

### 🏗️ System Architecture
- [ ] Integration with existing RAG and DCF systems
- [ ] Database interaction patterns (PostgreSQL, Neo4j, Redis, Vector DB)
- [ ] API design consistency
- [ ] Performance considerations for financial data processing

### 🛡️ Quality Assurance
- [ ] Test coverage (fast testing scope: f2)
- [ ] Security concerns for financial platform
- [ ] Documentation updates
- [ ] Potential bug identification

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
- **🔒 Checklist Guardian**: hrbp-agent (EXCLUSIVE protection of Task Initiation Protocol)
- **Governance Protection**: Level 3 violations for unauthorized checklist modifications

---

## 🚨 NON-NEGOTIABLE STANDARDS

1. **ORCHESTRATION MANDATORY**: Route complex tasks through agent-coordinator
2. **P3 WORKFLOW COMPLIANCE**: Never bypass p3 command system (`p3 ready`, `p3 test`, `p3 ship`)
3. **SSOT I/O ENFORCEMENT**: Use `common.core.directory_manager` for ALL file operations
4. **CONFIGURATION CENTRALIZATION**: All configs at `common/config/`
5. **AUTOMATIC PR CREATION**: Always create PR via `git-ops-agent` after significant changes
6. **ENGLISH-ONLY STANDARD**: All technical content in English
7. **GITHUB ISSUES ONLY**: Never create .md planning files - use GitHub Issues
8. **MODULAR FILE PLACEMENT**: All files must be in appropriate L1/L2 directories - avoid root directory unless essential (project config, entry points, documentation)
9. **TESTING ARCHITECTURE**:
   - Unit tests: Located within each module (e.g., `infra/tests/`, `common/tests/`)
   - Integration tests: Located in root `tests/` directory only
   - No mixing of unit and integration tests

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
- **🔒 Checklist Protection**: EXCLUSIVE authority over Task Initiation Protocol (Phase 1-5)
- **Governance Enforcement**: Immediate escalation for checklist tampering or unauthorized modifications
- **🔍 Claude Code Hooks Audit**: EXCLUSIVE audit authority over `~/.claude/settings.json` for agent execution monitoring and success rate analysis

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
- **Module Architecture Violations**:
  - Placing files in root directory instead of appropriate L1/L2 modules
  - Creating cross-module dependencies that break abstraction layers
  - Bypassing common.core.directory_manager for file operations
  - Inconsistent import/export patterns across modules

**🚨 CRITICAL Checklist Protection Violations (Level 3 - Immediate Escalation)**:
- **Checklist Deletion**: Removing any Phase 1-5 items from Task Initiation Protocol
- **Checklist Tampering**: Unauthorized modification of checklist structure or content
- **Checklist Bypass**: Skipping mandatory checklist completion before task execution
- **Protection Rule Modification**: Altering checklist protection governance without HRBP approval

**Agent Reference in Checklist (PERMITTED)**:
- Checklist items MAY reference specific agents (e.g., "Route through agent-coordinator", "Create PR via git-ops-agent")
- Agent delegation must occur WITHIN checklist framework, not bypass it
- Framework integrity maintained while enabling proper coordination

---

**For detailed procedures**: See specialized agent documentation and README.md

**Current Reduction**: ~600 lines → ~150 lines (75% reduction) with governance delegation

<!-- STREAMLINED DEPLOYMENT: 2025-09-12T12:00:40.897048 -->
<!-- FULL VERSION BACKUP: CLAUDE_FULL_BACKUP.md -->
<!-- DEPLOYMENT SCRIPT: deploy_streamlined_policies.py -->