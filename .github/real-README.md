# GitHub CI/CD Workflows

CI/CD automation configuration for the SEC Filing-Enhanced Quantitative Trading Platform.

## 🎯 F2-Only Testing Architecture

**Core Principle: The entire testing system only needs to run F2**

- **F2 Definition**: Fast-2 testing using 2 companies data (MSFT + NVDA)
- **Execution Time**: 2-5 minute complete test cycle
- **Data Scope**: Real SEC filings with statistical significance
- **CI Standard**: All automated testing uses F2 scope exclusively

## 🧪 Complete Testing System

### 1. Unit Tests (Must Pass)
**Execution**: Integrated within F2 test pipeline  
**Requirement**: 100% pass rate - any failure blocks PR merge  
**Coverage**:
- Python syntax and import validation
- Type checking and code standards
- Core functionality module unit tests
- Dependency validation

### 2. Integration Tests (Generate Reports)
**Execution**: F2 end-to-end test pipeline  
**Requirement**: Generate complete test reports (LLM bot quality review will be introduced later)  
**Coverage**:
- SEC data retrieval → DCF model calculation → output generation
- Database interaction testing (PostgreSQL, Neo4j, Redis, Vector DB)
- P3 CLI functionality verification
- Real data quality validation

### 3. Test Coverage
**Execution**: Overall coverage statistics and reporting  
**Requirement**: Track comprehensive coverage across all tests  
**Includes**: Unit test coverage + Integration test path coverage + F2 data validation coverage

## 🤖 AI-Powered Code Review

### Claude Review Triggers
1. **Automatic Review**: Every push to PR triggers general code review
2. **Interactive Q&A**: Use `@claude` mentions to trigger questions and specific tasks

### Review Content
- CLAUDE.md policy compliance checks
- Code quality and best practices
- Security vulnerabilities and performance issues
- F2 testing compliance validation
- Technical debt identification

## 🔄 Post-Merge Automation

### Automatic Issue Generation
**Trigger**: After code merges to main branch  
**Functionality**:
- Analyze merged code changes
- Identify technical debt and improvement opportunities
- Automatically create GitHub issues with proper linking
- Intelligent labeling and priority assignment

### F2 Performance Monitoring
- Continuously track F2 execution time
- Auto-create performance alert issues when >5 minutes
- CSV data storage for trend analysis

## 📋 Active Workflow Inventory

| Workflow | Status | Trigger | Primary Function |
|----------|--------|---------|------------------|
| **test-pipeline.yml** | ✅ Active | Push/PR | F2 execution: unit tests + integration tests + coverage |
| **claude-code-review.yml** | ✅ Active | PR create/update | Automatic code review and compliance checks |
| **claude.yml** | ✅ Active | @claude mentions | Interactive AI assistant and Q&A |
| **post-merge-analysis.yml** | ✅ Active | Push to main | Auto issue generation and F2 performance monitoring |
| **check-m7-validation.yml** | ✅ Active | PR validation | M7 environment readiness check (lightweight) |
| **auto-label-issues.yml** | ✅ Active | Issue management | Intelligent label assignment |

## 🎯 F2 Testing Details

### Test Data
- **Companies**: Microsoft (MSFT) and NVIDIA (NVDA)
- **Data Type**: Real SEC 10-K/10-Q filings
- **Update Frequency**: Synchronized with actual filing releases

### Performance Targets
- **Target Execution Time**: <3 minutes
- **Alert Threshold**: >5 minutes
- **Success Rate Target**: >95%
- **Timeout Setting**: 3-minute hard timeout to prevent CI blocking

### Validation Scope
```yaml
F2 Testing Includes:
  Unit Tests: Python modules, type checking, syntax validation
  Integration Tests: Complete data pipeline validation
  Data Quality: MSFT+NVDA data processing verification
  System Integration: P3 CLI functionality and database interactions
  Output Validation: DCF model calculation result verification
```

## 🔧 Usage Guide

### Developer Workflow
1. **Write Code** → Local validation
2. **Create PR** → F2 auto-testing + Claude auto-review
3. **Address Feedback** → Fix issues and review suggestions
4. **Merge Code** → Post-merge auto-analysis generates follow-up issues

### Manual Operations
- **@claude [question]**: Get AI assistance and Q&A
- **[skip-review]**: Add to PR title to skip auto-review
- **[manual-review]**: Add to PR title for manual review mode

### Performance Monitoring
- F2 execution time trend auto-tracking
- Performance degradation auto-alerts and issue creation
- Test coverage reporting and trend analysis

---

## 📚 Related Documentation

- **Project Architecture**: `../README.md`
- **P3 CLI Usage**: `../common/README.md`
- **Company Policies**: `../CLAUDE.md`

**Support**: Create an issue or use `@claude` for help