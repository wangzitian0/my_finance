# GitHub Automation & CI/CD Workflows

This directory contains GitHub workflows, issue templates, and automation configuration for the SEC Filing-Enhanced Quantitative Trading Platform.

## 🎯 F2-Centered CI/CD Architecture

### Core Philosophy: F2-First Development

Our entire CI/CD system is architected around **F2 (Fast-2) testing** as the primary validation mechanism:

- **F2 as CI Standard**: All automated tests use F2 scope (2 companies, 2-5 minutes)
- **Rapid Feedback**: Sub-5-minute validation cycles for immediate developer feedback
- **Production Validation**: F2 provides statistically significant validation with MSFT & NVDA
- **Cost Efficiency**: Minimize CI resource usage while maintaining quality assurance

### Test Scope Hierarchy

| Scope | Companies | Duration | Primary Use Case | CI Integration |
|-------|-----------|----------|------------------|----------------|
| **F2** | 2 (MSFT, NVDA) | 2-5 min | **Primary CI validation** | ✅ All workflows |
| **M7** | 7 companies | 10-20 min | Release validation | Manual trigger only |
| **N100** | 100 companies | 1-3 hours | Production readiness | Manual only |
| **V3K** | 3000+ companies | 6-12 hours | Full production | Manual only |

## 🏗️ CI/CD Workflow Architecture

### 1. Independent Testing Modules

#### A. Repository Unit Tests
**Workflow**: Integrated into `test-pipeline.yml`
**Purpose**: Code-level validation without data dependencies
- ✅ Python syntax and imports
- ✅ Type checking and linting
- ✅ Unit test suite execution
- ✅ Dependency validation

#### B. Local F2 End-to-End Testing  
**Workflow**: `test-pipeline.yml` (Primary CI)
**Purpose**: Complete system validation with real data
- ✅ Full F2 infrastructure setup (Pixi + Python 3.11)
- ✅ End-to-end data pipeline: SEC filings → DCF models → outputs
- ✅ P3 CLI functionality testing (`p3 test f2`)
- ✅ Data quality validation (MSFT & NVDA)
- ⚡ **3-minute timeout** for rapid feedback
- 📊 Artifact collection for debugging failures

#### C. Claude Code Review
**Workflow**: `claude-code-review.yml` (Fixed)
**Purpose**: AI-powered automatic code review
- ✅ **FIXED**: Direct prompt configuration for automatic reviews
- ✅ Code quality and best practices analysis
- 🐛 Bug detection and security concerns
- ⚡ Performance and F2 compliance validation
- 📌 Sticky comments for PR conversation continuity
- 🚫 Smart skip conditions: `[skip-review]`, `[manual-review]`

#### D. Post-Merge Review & Issue Generation
**Workflow**: `post-merge-analysis.yml` (To be implemented)
**Purpose**: Production-ready code analysis and task generation
- 📋 **Automated issue creation** for identified technical debt
- 🔍 Performance optimization opportunities
- 📝 Documentation update requirements
- 🧪 Test coverage gap analysis
- 🚀 Feature enhancement suggestions

### 2. Interactive @claude Auto-Reply System

#### @claude Mention Triggers
**Workflow**: `claude.yml` (Verified working)
**Triggers**: Explicit `@claude` mentions in:
- 💬 Issue comments and PR comments  
- 📝 PR review comments
- 🎯 Issue creation with `@claude` in title/body
- 🔍 Issue assignment with Claude integration

#### Smart Conflict Prevention
- 🚫 **Automatic review disabled** when `@claude` detected in PR title/body
- 📝 Manual review mode: Add `[manual-review]` to PR title
- ⚡ Skip automatic review: Add `[skip-review]` to PR title
- 🤖 Dual-mode operation: Automatic + interactive without conflicts

## 📋 Complete Workflow Inventory

### Current Active Workflows

| Workflow | Status | Trigger | Purpose | F2 Integration |
|----------|--------|---------|---------|----------------|
| **test-pipeline.yml** | ✅ Active | Push/PR to main | Primary F2 CI validation | Core F2 testing |
| **claude-code-review.yml** | ✅ Fixed | PR opened | Automatic code review | F2 compliance check |
| **claude.yml** | ✅ Active | @claude mentions | Interactive AI assistance | F2 context aware |
| **check-m7-validation.yml** | ✅ Active | PR validation | M7 requirements check | F2 baseline required |
| **auto-label-issues.yml** | ✅ Active | Issue lifecycle | Intelligent labeling | N/A |

### Planned Workflows

| Workflow | Status | Implementation Priority | Purpose |
|----------|--------|------------------------|---------|
| **post-merge-analysis.yml** | 🚧 To implement | High | Issue generation from analysis |
| **f2-performance-monitor.yml** | 📋 Planned | Medium | F2 execution time tracking |
| **dependency-update.yml** | 📋 Planned | Low | Automated dependency management |

## 🎯 Individual Workflow Design Goals

### 1. Fast Test Pipeline (test-pipeline.yml)
**Design Goal**: Sub-5-minute comprehensive validation
- **Performance Target**: <3 minutes for F2 complete cycle
- **Coverage Goal**: 100% critical path validation with 2-company dataset
- **Reliability Target**: >95% success rate with proper error reporting
- **Resource Efficiency**: Minimal CI runner usage with maximum validation

**Key Features**:
- ⚡ 3-minute hard timeout prevents CI queue blocking
- 🏗️ Complete F2 infrastructure bootstrap in CI environment
- 🧪 Real data validation with MSFT/NVDA SEC filings
- 📊 Comprehensive artifact collection for failure analysis
- 🧹 Automatic cleanup prevents storage bloat

### 2. Claude Code Review (claude-code-review.yml)
**Design Goal**: Intelligent, non-intrusive automatic code review
- **Quality Target**: Catch 80%+ of common code quality issues
- **Efficiency Goal**: No developer workflow interruption
- **Intelligence Level**: F2-testing aware, project-context understanding
- **Conflict Avoidance**: Smart detection of manual review requests

**Key Features**:
- 🤖 **FIXED**: Direct prompt triggers automatic review without @claude mention
- 📌 Sticky comments maintain conversation continuity
- 🧠 F2 testing compliance validation
- 🚫 Intelligent skip conditions for manual review scenarios

### 3. Interactive Claude (claude.yml)  
**Design Goal**: Seamless AI-powered development assistance
- **Responsiveness**: Sub-30-second response to @claude mentions
- **Context Awareness**: Full CI results, codebase, and F2 testing context
- **Conversation Quality**: Persistent conversation threads with memory
- **Integration Depth**: Read CI logs, suggest fixes, understand project architecture

**Key Features**:
- 💬 Multi-trigger support: issues, comments, PR reviews
- 🔍 CI results analysis for intelligent debugging assistance
- 📚 Project-aware responses with F2 testing context
- 🚫 Conflict prevention with automatic review workflows

### 4. M7 Validation Check (check-m7-validation.yml)
**Design Goal**: Release readiness validation gateway  
- **Validation Scope**: 4 core M7 readiness conditions
- **Integration Point**: Pre-release validation only (not blocking F2 CI)
- **Performance**: Lightweight check without full M7 execution
- **Purpose**: Ensure M7 infrastructure readiness before manual testing

### 5. Auto-Label Issues (auto-label-issues.yml)
**Design Goal**: Intelligent project management automation
- **Accuracy Target**: 90%+ correct label assignment
- **Scope Coverage**: Priority, type, component, effort estimation
- **Learning Capability**: Keyword-based with pattern recognition
- **Integration**: Seamless with project management workflows

### 6. Post-Merge Analysis (Planned)
**Design Goal**: Proactive technical debt and improvement identification
- **Issue Generation**: Automatic GitHub issue creation for identified items
- **Analysis Depth**: Code quality, performance, documentation, testing gaps
- **Prioritization**: Intelligent priority assignment based on impact analysis
- **Integration**: F2 performance baseline tracking for optimization opportunities

## 🚨 Claude Code Review Fix Summary

### ❌ Previous Issue
The Claude code review workflow was not triggering because:
- `direct_prompt` was incorrectly placed in `env` section instead of `with` section
- Action was looking for `@claude` triggers instead of using direct prompt
- `use_sticky_comment` configuration mismatch between env and inputs

### ✅ Resolution Applied
```yaml
# FIXED: Moved direct_prompt to 'with' section for proper action input
- name: Run Claude Code Review
  uses: anthropics/claude-code-action@beta
  with:
    claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    direct_prompt: |
      Please review this pull request and provide feedback on:
      - Code quality and best practices
      - Potential bugs or issues  
      - Performance considerations
      - Security concerns
      - Test coverage
      - CI/CD workflow compliance (note: only F2 testing is used in CI)
    use_sticky_comment: true
```

### 🔧 Verification Steps
1. **Test Direct Prompt**: Next PR will trigger automatic review without @claude mention
2. **Sticky Comments**: Reviews will update existing comments instead of creating new ones
3. **Conflict Prevention**: Workflow properly skips when manual review requested

## 🔍 F2 Testing Integration Details

### F2 CI Implementation
```yaml
# Primary CI workflow using F2 scope exclusively
test-pipeline.yml:
  scope: f2  # 2 companies (MSFT, NVDA)
  timeout: 3 minutes
  validation: Full end-to-end pipeline
  artifact_collection: Failure debugging
  success_criteria: Pipeline completion + data validation
```

### F2 Performance Monitoring
- **Baseline**: 2-5 minute execution time for complete F2 cycle
- **Monitoring**: Execution time tracking in workflow logs  
- **Optimization**: Continuous pipeline efficiency improvements
- **Scaling**: F2 scope proven sufficient for CI validation

### F2 Data Validation
- **Dataset**: Microsoft (MSFT) and NVIDIA (NVDA) SEC filings
- **Coverage**: Representative sample of different company profiles
- **Quality**: Real production data ensuring realistic validation
- **Consistency**: Fixed dataset for reproducible CI results

## 🛠️ Maintenance & Monitoring

### 🤖 Agent-Automated Responsibilities

#### monitoring-agent - CI/CD System Health
**Automated Tasks** (Real-time):
- **F2 Performance Tracking**: Continuous execution time monitoring (<3min threshold)
- **CI Success Rate Monitoring**: Track pipeline success rates (>95% target)
- **Resource Usage Analysis**: Monitor GitHub Actions runner utilization
- **Alert Generation**: Auto-create issues when thresholds exceeded

**Escalation Triggers**:
- F2 execution time >5 minutes (3 consecutive failures)
- CI success rate <90% (24-hour period)
- GitHub Actions quota >80% monthly usage

#### dev-quality-agent - Code Quality Assurance
**Automated Tasks** (Per PR/Commit):
- **Test Coverage Analysis**: Track F2 test coverage completeness
- **Code Quality Metrics**: Monitor complexity, maintainability scores
- **Dependency Vulnerability Scanning**: Security issue detection
- **Technical Debt Identification**: Automated code smell detection

**Quality Gates**:
- F2 test coverage: >90% critical path coverage
- Code complexity: Cyclomatic complexity <15 per function
- Security: Zero high/critical vulnerabilities in dependencies

#### hrbp-agent - Process & Workflow Optimization
**Automated Tasks** (Weekly):
- **Claude Review Effectiveness**: Analyze review comment quality and response rates
- **Workflow Compliance**: Monitor adherence to F2-first development process
- **Agent Performance**: Track sub-agent reliability and response times
- **Process Improvement**: Identify workflow bottlenecks and optimization opportunities

**Performance Metrics**:
- Claude review adoption rate: >80% developer engagement
- Workflow compliance: >95% F2-first process adherence
- Sub-agent reliability: >95% successful task completion

#### infra-ops-agent - Infrastructure Management
**Automated Tasks** (Daily):
- **P3 CLI Health**: Monitor P3 command functionality and performance
- **Environment Consistency**: Validate Pixi environment setup across runners
- **Infrastructure Optimization**: Resource allocation and performance tuning
- **System Recovery**: Automated failure recovery and environment reset

**Infrastructure SLAs**:
- P3 CLI availability: >99.5% uptime
- Environment setup time: <2 minutes for CI runners
- System recovery time: <5 minutes for automated fixes

### 👥 Human Intervention Points

#### Development Team Responsibilities
**Daily** (Individual Developers):
- Monitor F2 test results for their PRs
- Respond to Claude code review feedback
- Address automated quality gate failures
- Use `@claude` for complex debugging assistance

**Weekly** (Team Leads):
- Review team F2 performance trends
- Address recurring CI/CD issues identified by agents
- Validate agent-generated technical debt issues
- Approve/prioritize optimization recommendations

#### DevOps/Platform Team Responsibilities
**Weekly**:
- Review agent-generated infrastructure alerts
- Validate system performance trends and optimization needs
- Update CI/CD configurations based on agent recommendations
- Monitor GitHub Actions usage and cost optimization

**Monthly**:
- **F2 Scope Validation**: Ensure 2-company dataset remains representative
- **Workflow Architecture Review**: Evaluate new CI modules based on usage patterns
- **Agent Configuration Tuning**: Optimize agent thresholds and performance targets
- **Cost Optimization**: Review CI resource usage and implement efficiency improvements

#### Product/Project Management
**Monthly**:
- Review Claude integration effectiveness metrics
- Prioritize agent-identified feature enhancement opportunities
- Validate process compliance and quality metrics
- Plan quarterly architecture improvements

**Quarterly**:
- **F2 Strategy Validation**: Confirm F2-first approach meets business goals
- **ROI Analysis**: Evaluate CI/CD system cost vs. productivity benefits
- **Technology Roadmap**: Plan integration of new CI/CD technologies
- **Compliance Review**: Ensure system meets regulatory and security requirements

### 🚨 Alert & Escalation Matrix

#### Automated Alert Levels

**🟢 Level 1 - Info (Agent Handled)**
- F2 performance within normal variance (2-4 minutes)
- Minor dependency updates available
- Code quality suggestions generated
- **Action**: Logged for trend analysis, no human intervention

**🟡 Level 2 - Warning (Team Notification)**
- F2 execution time 4-5 minutes consistently
- CI success rate 90-95% (24-hour period)
- Claude review engagement <70%
- **Action**: Slack notification to development team, investigate within 48 hours

**🟠 Level 3 - Alert (Immediate Action Required)**
- F2 execution time >5 minutes (3 consecutive runs)
- CI success rate <90% (24-hour period)
- Critical security vulnerabilities detected
- P3 CLI functionality failures
- **Action**: GitHub issue auto-created, team lead notified, resolution within 24 hours

**🔴 Level 4 - Critical (Emergency Response)**
- Complete F2 pipeline failure (>6 hours)
- GitHub Actions quota exceeded
- Security incident detected
- System-wide CI/CD outage
- **Action**: Immediate escalation to DevOps team, incident response activated

#### Escalation Workflow
```yaml
Level_2_Warning:
  notification: Slack #ci-cd-alerts channel
  timeline: 48 hours for investigation
  owner: Development team lead
  
Level_3_Alert:
  notification: GitHub issue + Slack + Email
  timeline: 24 hours for resolution
  owner: Assigned team member + DevOps backup
  
Level_4_Critical:
  notification: Immediate call + All channels
  timeline: 4 hours for emergency response
  owner: DevOps incident commander + Management
```

### 📊 Success Metrics & KPIs

#### System Performance Metrics
- **F2 Execution Time**: Target <3min, Alert >5min
- **CI Success Rate**: Target >95%, Alert <90%
- **Claude Review Quality**: Target >80% helpful feedback rate
- **System Uptime**: Target >99.5%, Alert <99%

#### Developer Experience Metrics
- **PR Cycle Time**: F2 validation to merge (Target <2 hours)
- **Claude Interaction Rate**: @claude usage frequency (Target >5 per week)
- **Quality Gate Pass Rate**: First-time F2 test success (Target >85%)
- **Developer Satisfaction**: Monthly survey score (Target >4.0/5.0)

#### Business Impact Metrics
- **Cost Per PR**: GitHub Actions cost per merged PR (Target optimization)
- **Defect Detection Rate**: Issues caught in F2 vs production (Target >90%)
- **Time to Production**: Feature development to production deployment
- **Technical Debt Reduction**: Agent-identified issues resolved monthly

## 🚀 Getting Started

### For Developers
1. **Development Cycle**: Code → F2 validation (automatic) → PR creation
2. **CI Feedback**: Monitor F2 test results for immediate validation
3. **Claude Review**: Automatic code review comments on every PR
4. **Interactive Help**: Use `@claude` mentions for assistance

### For Reviewers  
1. **F2 Validation**: Ensure green F2 tests before code review
2. **Claude Insights**: Review automatic Claude feedback for additional context
3. **Manual Review**: Add `[manual-review]` to PR title for Claude-assisted review
4. **Release Readiness**: Use M7 validation check for release verification

### For CI/CD Maintenance
1. **F2 Performance**: Monitor execution times and optimize bottlenecks
2. **Claude Quality**: Track review effectiveness and improve prompts
3. **Workflow Reliability**: Maintain >95% success rate for all workflows
4. **Issue Generation**: Monitor post-merge analysis quality and automation

---

## 📚 Related Documentation

- **Project Architecture**: `../README.md`
- **P3 CLI Usage**: `../common/README.md` 
- **Company Policies**: `../CLAUDE.md`
- **Agent Configuration**: `../.claude/agents/`

---


**For CI/CD support, workflow issues, or F2 testing questions, create an issue using the appropriate template.**

