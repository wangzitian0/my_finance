# GitHub Automation & Workflows

This directory contains GitHub workflows, issue templates, and automation configuration for the SEC Filing-Enhanced Quantitative Trading Platform.

## 🏗️ CI/CD Pipeline Architecture

### Overview
Our CI/CD system uses a staged approach with different test scopes to optimize feedback speed while ensuring comprehensive validation:

- **F2 (Fast-2)**: Development testing with 2 companies (~2-5 minutes)
- **M7 (Medium-7)**: Integration testing with 7 companies (~10-20 minutes)  
- **N100 (Normal-100)**: Production validation with 100 companies (~1-3 hours)
- **V3K (Volume-3000+)**: Full production datasets (~6-12 hours)

### Current Workflow Status

| Workflow | Status | Purpose | Scope |
|----------|--------|---------|-------|
| **Fast Test Pipeline (F2)** | ✅ Active | PR validation, rapid feedback | F2 scope (2 companies) |
| **M7 Validation Check** | ✅ Active | Release validation | M7 scope (7 companies) |
| **Claude Code** | ✅ Active | AI-powered code assistance | @claude triggers |
| **Claude Code Review** | ✅ Active | Automated PR reviews | All PRs |
| **Auto-Label Issues** | ✅ Active | Intelligent issue labeling | Issue lifecycle |

## 📋 Workflows Detail

### 1. Fast Test Pipeline (F2) - `test-pipeline.yml`
**Purpose**: Primary CI validation for all pushes and PRs

**Triggers**:
- Push to `main`, `feature/**`, `hotfix/**` branches
- Pull requests to `main`

**Key Features**:
- ⚡ 3-minute timeout for rapid feedback
- 🏗️ Full F2 infrastructure setup in CI
- 🧪 Tests P3 CLI functionality (`p3 test f2`)
- 📊 Validates build completion and data generation
- 🧹 Automatic cleanup of test artifacts
- 📋 Failure artifact collection for debugging

**F2 Test Data**: Uses Microsoft (MSFT) and NVIDIA (NVDA) for consistent CI testing

### 2. M7 Test Validation Check - `check-m7-validation.yml`
**Purpose**: Ensures M7 validation requirements are met for PRs

**Triggers**: 
- PR opened/synchronized/reopened on `main`

**Validation**: Runs `ci_m7_validation.py` to check 4 core M7 conditions

### 3. Claude Code Integration - `claude.yml`
**Purpose**: Interactive AI-powered development assistance and issue management

**Triggers**:
- `@claude` mentions in issues, comments, PR reviews
- Issue creation/assignment with `@claude` in title/body

**Capabilities**:
- 🤖 Interactive code analysis and suggestions
- 🔍 CI results analysis on PRs
- 📝 Issue and PR assistance
- 🛠️ Custom model selection (Sonnet 4 default, Opus 4.1 optional)
- 💬 Sticky comments for conversation continuity

**Conflict Prevention**: Only triggers on explicit `@claude` mentions to avoid duplicating automatic reviews

### 4. Claude Code Review - `claude-code-review.yml`  
**Purpose**: Automatic PR code reviews using Claude

**Triggers**: PR opened (initial creation only, not updates)

**Review Focus**:
- ✅ Code quality and best practices
- 🐛 Potential bugs and issues
- ⚡ Performance considerations
- 🔒 Security concerns
- 🧪 Test coverage

**Smart Features**:
- 📌 Sticky comments that update on subsequent pushes
- 🚫 Skip conditions: `[skip-review]`, `[manual-review]`, `@claude` in title/body
- 🎯 Automatic exclusion when manual review is requested

### 5. Auto-Label Issues - `auto-label-issues.yml`
**Purpose**: Intelligent automatic issue labeling based on content analysis

**Triggers**: Issue opened/edited

**Labeling Categories**:
- **Priority**: P0-critical, P1-high, P2-medium, P3-low
- **Type**: bug, feature, docs, refactor, adr, ci/cd
- **Component**: infrastructure, data-storage, etl, dcf-engine, graph-rag
- **Status**: blocked, needs-triage
- **Phase**: MVP, production
- **Effort**: large (>3 days), medium (1-3 days)

**Smart Features**:
- 🎯 Prefix recognition (`[BUG]`, `[Feature]`, etc.)
- 🧠 Keyword matching with boundary detection
- 📏 Content length-based effort estimation
- 🔄 Non-destructive (adds labels, never removes)
- 📝 Automatic comment explaining labeling decisions

## 📋 Issue Templates

### 🚀 Feature Implementation (`feature-implementation.yml`)
Structured template for implementation tasks:
- **Implementation Objective**: Clear feature description
- **Acceptance Criteria**: Definition of done checklist
- **Technical Notes**: Dependencies and implementation details

### 🐛 Bug Report (`bug-report.yml`)
Standardized bug reporting with:
- **Bug Description**: Steps to reproduce, expected vs actual behavior
- **Environment**: OS, component, logs, and context information

### 🏛️ Architecture Decision Request (`architecture-decision.yml`)
Template for ADRs (Architecture Decision Records):
- **Problem Statement**: Current issues and decision drivers
- **Proposed Solution**: Recommended approach and benefits
- **Alternatives Considered**: Evaluated options and trade-offs

## 🔧 Configuration Files

### Issue Labeling Documentation (`ISSUE_LABELING.md`)
Comprehensive guide to the automated labeling system:
- 📖 Complete label taxonomy and keywords
- 🔍 Smart detection algorithms and examples
- 🛠️ Configuration and maintenance procedures
- 🐛 Troubleshooting and workflow logs

## 🚨 CI/CD Monitoring & Reliability

### Sub-Agent Reliability Optimization
Based on commit `c417b17` - **HRBP-led sub-agent reliability optimization**:

**Current Issues Addressed**:
- ❌ Sub-agent interruption and failure rates
- 🔄 Backend-architect-agent database connection failures (100% → <5% target)
- 🛡️ Enhanced error handling and defensive programming
- ⚡ Improved recovery mechanisms and fallback strategies

**Reliability Improvements**:
- **Pre-execution validation**: Connectivity, resources, permissions
- **Retry mechanisms**: Exponential backoff, circuit breakers
- **Fallback strategies**: Graceful degradation, alternative execution
- **Real-time monitoring**: Error tracking, auto-escalation

**Target Metrics**:
- Overall sub-agent reliability: **>95% success rate**
- Mean time to recovery: **<30 seconds**
- Error detection accuracy: **>90%**

### P3 CLI Integration
All workflows integrate with the P3 command system:
- **P3 Ready**: Environment setup and validation
- **P3 Test**: Scoped testing (f2/m7/n100/v3k)
- **P3 Ship**: PR creation with mandatory F2 validation
- **P3 Debug**: Failure diagnosis and recovery

## 🔍 Debugging & Troubleshooting

### Common CI Issues

**F2 Test Pipeline Failures**:
1. **Timeout Issues**: F2 should complete in <3 minutes
2. **Infrastructure Problems**: Check Pixi environment setup
3. **Data Generation**: Validate MSFT/NVDA test data creation
4. **P3 CLI Issues**: Check basic `p3 help` and `p3 version` functionality

**M7 Validation Failures**:
1. **Missing Validation Script**: Ensure `ci_m7_validation.py` exists
2. **Core Conditions**: Check the 4 M7 validation requirements
3. **Dependencies**: Verify Python 3.11 setup

**Claude Integration Issues**:
1. **Token Configuration**: Verify `CLAUDE_CODE_OAUTH_TOKEN` secret
2. **Permissions**: Check `actions: read` for CI results access
3. **Trigger Patterns**: Ensure `@claude` mentions are properly formatted
4. **Duplicate Comments**: Use conflict prevention strategies:
   - Add `[skip-review]` to PR title to disable automatic review
   - Add `[manual-review]` to request only interactive `@claude` sessions
   - Include `@claude` in PR title/body to prefer interactive mode

### Workflow Logs
Access detailed execution logs in:
- **Actions Tab**: Complete workflow execution history
- **Failure Artifacts**: Uploaded for F2 pipeline failures (3-day retention)
- **Claude Logs**: Labeling decisions and AI interaction tracking

### Recovery Procedures

**Pipeline Failures**:
1. Check GitHub Actions logs for specific error messages
2. Review failure artifacts if available
3. Test locally with same scope: `pixi run python p3.py test f2`
4. Escalate to infrastructure team for persistent issues

**Sub-Agent Interruptions**:
1. Check error handling configuration in `common/config/agent_error_handling.yml`
2. Review sub-agent reliability metrics
3. Apply defensive programming patterns from error templates
4. Use circuit breaker patterns for external service calls

## 🔄 Maintenance & Updates

### Regular Maintenance Tasks
- **Weekly**: Review workflow success rates and failure patterns
- **Monthly**: Update issue labeling keywords based on usage patterns
- **Quarterly**: Review and optimize CI/CD performance and reliability

### Configuration Updates
- **Workflow Changes**: Test in feature branches before merging to main
- **Label Updates**: Update both workflow keywords and repository labels
- **Template Changes**: Ensure consistency across all issue templates

### Performance Optimization
- **F2 Scope**: Maintain 2-5 minute execution time
- **CI Resources**: Monitor runner usage and optimize resource allocation
- **Artifact Management**: Regular cleanup of old test artifacts

---

## 📚 Related Documentation

- **Project Architecture**: `../README.md`
- **P3 CLI Usage**: `../common/README.md`
- **Agent Configuration**: `../.claude/agents/`
- **Error Handling**: `../common/config/agent_error_handling.yml`
- **Company Policies**: `../CLAUDE.md`

---

**For CI/CD support or workflow issues, please create an issue using the appropriate template above.**