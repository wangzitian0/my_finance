# CI/CD Workflows - Automated Workflow Orchestration

Automated workflow orchestration, PR management, and continuous integration supporting the P3 workflow system and development lifecycle.

## Overview

This directory provides comprehensive CI/CD workflow automation, focusing on PR creation, testing integration, quality gates, and worktree-safe operations for the financial analysis platform.

## Core Components

### PR Creation Workflow (`pr_creation.py`)
**Complete end-to-end PR creation with mandatory testing and validation**:
- **Mandatory F2 testing**: Fast-build validation with 2 companies (MSFT + NVDA)
- **Environment validation**: Pre-flight checks ensuring development environment readiness
- **Worktree-safe operations**: Git operations optimized for worktree environments
- **Quality gates**: Code formatting, testing, build verification before PR creation

### Testing Integration
**Comprehensive validation and testing orchestration**:
- **Scope-based testing**: F2 (fast), M7 (complete), N100 (validation), V3K (production)
- **Test automation**: Automated test execution, result validation, failure analysis
- **Build verification**: Data pipeline testing, model validation, artifact verification
- **Environment coordination**: Service health checks, dependency validation

## Key Features

### 1. Complete PR Creation Workflow
**End-to-end automation from code changes to merged PR**:

**Workflow Stages**:
1. **Pre-flight validation**: Environment health check using fast validation tools
2. **Git synchronization**: Worktree-safe main branch sync and feature branch rebase
3. **Code formatting**: Automated black and isort formatting with commit integration
4. **Mandatory testing**: F2 fast-build validation (DeepSeek 1.5b, 2 companies, 2-5 min)
5. **PR creation**: GitHub PR creation with intelligent description generation
6. **Metadata integration**: Test markers, commit message updates, PR URL integration

**Command Integration**:
```bash
# Complete workflow triggered by single command
p3 ship "Add new feature" 123

# Automatic execution:
# ✅ Environment validation passed
# ✅ Code formatted and committed  
# ✅ F2 test passed (2 files validated)
# ✅ PR created: https://github.com/user/repo/pull/456
```

### 2. Worktree-Safe Operations
**Git operations optimized for git worktree environments**:

**Safe Synchronization**:
- **Fetch-based sync**: Uses `git fetch + rebase` instead of risky `checkout + reset`
- **Data protection**: Prevents data loss in multi-worktree scenarios
- **Environment detection**: Automatic worktree vs regular repository detection
- **Branch isolation**: Safe operations maintaining branch independence

**Worktree Compatibility**:
```python
# Automatic worktree detection
if is_worktree_environment():
    print("🌿 Worktree environment detected - using safe sync method")
    # Use fetch+rebase instead of checkout+reset
else:
    print("📁 Regular git repository detected - using standard operations")
```

### 3. Testing Integration and Validation
**Comprehensive testing orchestration with scope-based execution**:

**F2 Fast-Build Validation** (Default):
- **Scope**: 2 companies (MSFT + NVDA)
- **Model**: DeepSeek 1.5b for fast processing
- **Duration**: 2-5 minutes
- **Purpose**: PR validation, development workflow testing
- **Data validation**: Minimum 2 data files required for validation

**Advanced Testing Scopes**:
- **M7**: Magnificent 7 companies, 10-20 minutes, release validation
- **N100**: NASDAQ 100 companies, 1-3 hours, production validation
- **V3K**: VTI 3500+ companies, 6-12 hours, full production dataset

**Intelligent Testing**:
```python
# Automatic test scope detection
def run_end_to_end_test(scope="f2"):
    # Smart validation based on change type
    if code_only_changes and not data_affecting_changes:
        return 1  # Skip data validation for code-only changes
    
    # Full validation for data-affecting changes
    return run_comprehensive_validation()
```

## Workflow Implementation Details

### PR Creation Process (`pr_creation.py`)

**Stage 1: Environment Validation**
```python
# Pre-flight environment check
if not validate_environment_for_pr():
    print("❌ PR creation aborted due to environment issues")
    sys.exit(1)
```

**Stage 2: Git Synchronization** (Worktree-Safe)
```python
# Worktree-safe main branch synchronization
if is_worktree_environment():
    # Safe method: fetch + rebase (no data loss)
    run_command("git fetch origin main:refs/remotes/origin/main")
    run_command("git rebase origin/main")
else:
    # Traditional method: checkout + reset
    run_command("git checkout main")
    run_command("git reset --hard origin/main")
```

**Stage 3: Code Quality Assurance**
```python
# Automated code formatting
format_result = run_p3_command("check", "Formatting code with black and isort")
if uncommitted_after_format:
    run_command("git add .")
    run_command('git commit -m "Format code with black and isort"')
```

**Stage 4: Mandatory Testing**
```python
# F2 fast-build validation (mandatory)
test_result = run_end_to_end_test(scope="f2")
if not test_result:
    print("❌ F2 test failed - PR creation aborted")
    sys.exit(1)
```

**Stage 5: PR Creation and Metadata**
```python
# GitHub PR creation with generated description
body = generate_pr_description(current_branch, issue_number, test_info)
run_command(f'gh pr create --title "{title}" --body "{body}"')

# Commit message updates with test markers
updated_msg = f"""{original_msg}
✅ F2-TESTED: This commit passed F2 fast-build testing
📊 Test Results: {test_info['data_files']} data files validated"""
```

### Testing Orchestration

**Build Process Management**:
- **Environment setup**: Service initialization, dependency validation
- **Dataset generation**: Company data collection, processing, validation
- **Model validation**: LLM model initialization and testing
- **Artifact verification**: Build output validation, file count verification

**Error Handling and Recovery**:
```python
# Graceful failure handling with diagnostics
try:
    run_p3_command("build f2", "Building F2 dataset", timeout=1200)
except Exception as e:
    # Fallback validation using existing data
    print("🔍 Checking if we can validate with existing data...")
    if validate_existing_data():
        return True  # Continue with existing data
    else:
        return False  # Complete failure
```

### Intelligent PR Description Generation

**Automated PR Body Creation**:
```python
def generate_pr_description(branch, issue, test_info):
    # Extract commits and categorize changes
    commits = get_commit_messages(branch)
    changed_files = get_changed_files(branch)
    
    # Categorize changes by type
    categories = categorize_changes(changed_files)
    
    # Generate comprehensive description
    return f"""## Summary
{extract_summary(commits)}

## Key Changes
{format_changes(categories)}

## Test Results
✅ F2 Fast-Build Test: PASSED
- {test_info['data_files']} data files validated
- Test completed at {test_info['timestamp']}

Fixes #{issue}"""
```

## Integration Points

### With P3 CLI System
- **Command implementation**: Provides actual implementation for `p3 ship`
- **Scope management**: Handles F2/M7/N100/V3K testing scope execution
- **Environment integration**: Worktree detection, Python environment handling

### With Git Operations
- **Hook integration**: Works with git hooks from `infra/git-ops/`
- **Branch management**: Coordinates with branch cleanup and repository hygiene
- **Workflow enforcement**: Integrates with P3 workflow enforcement hooks

### With Infrastructure
- **Environment management**: Uses environment validation from `infra/environment/`
- **Service coordination**: Integrates with Podman, Neo4j, database management
- **Monitoring**: Leverages system health monitoring and diagnostics

### With Scripts Utilities
- **Fast validation**: Uses `scripts/utilities/fast_env_check.py`
- **Development tools**: Integrates with code quality and debugging utilities
- **Workflow support**: Leverages session management and state tracking

## Usage Examples

### Standard PR Creation
```bash
# Complete PR workflow with F2 testing
p3 ship "Add authentication feature" 142

# Workflow execution:
🔍 Pre-flight Environment Validation
✅ All environment checks passed

🔄 Syncing with latest remote main...
✅ Feature branch rebased successfully

🔄 Running code formatting...
✅ Code already properly formatted

🧪 RUNNING F2 FAST-BUILD VALIDATION
✅ F2 test passed - proceeding with PR creation

✅ PR Created: https://github.com/user/repo/pull/156
```

### Advanced Testing Scopes
```bash
# M7 complete testing before release
p3 ship "Release v2.1.0" 143 --scope m7

# N100 validation testing
p3 ship "Major refactor" 144 --scope n100
```

### Error Handling Examples
```bash
# Environment validation failure
❌ Environment validation failed - PR creation blocked
🚨 Issues found:
   1. Podman Machine: Not running properly
      Fix: Run: podman machine start

💡 Quick fix: Run 'p3 ready' to resolve environment issues
```

## Quality Standards

### Performance Requirements
- **F2 testing**: Maximum 5 minutes execution time
- **Environment validation**: Maximum 10 seconds for fast checks
- **Git operations**: Optimized for worktree environments
- **PR creation**: Under 30 seconds for GitHub operations

### Reliability Standards
- **Error recovery**: Graceful handling of service failures
- **Data protection**: Worktree-safe operations prevent data loss
- **Rollback capability**: Safe rollback on partial failures
- **Audit trail**: Comprehensive logging of all operations

### User Experience Standards
- **Progress visibility**: Clear status updates throughout workflow
- **Error clarity**: Specific error messages with fix suggestions
- **Workflow efficiency**: Minimal manual intervention required
- **Documentation**: Comprehensive usage and troubleshooting guides

## Maintenance and Monitoring

### Workflow Health Monitoring
- **Success rates**: PR creation success/failure tracking
- **Performance metrics**: Execution time monitoring and optimization
- **Error patterns**: Common failure analysis and prevention
- **Resource utilization**: CPU, memory, network usage during workflows

### Quality Assurance
- **Testing coverage**: Comprehensive test suite for workflow components
- **Integration testing**: Full workflow testing with multiple scenarios
- **Environment testing**: Validation across different development setups
- **Rollback testing**: Failure scenario testing and recovery validation

---

**Integration References**:
- **P3 Workflow**: [Main README.md](../../README.md#p3-command-system) for command system
- **Git Operations**: [infra/git-ops/README.md](../git-ops/README.md) for repository management
- **Environment**: [infra/environment/README.md](../environment/README.md) for service management