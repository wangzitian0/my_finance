# CLAUDE.md - Claude Code Instructions

<!-- Test comment added for sub-agent activation testing - 2025-08-26 -->

> **Clean Repository Structure** (2025-08-26): Main repository contains only code, documentation, and configurations. Data subtree at `build_data/` with centralized configs at `common/config/`.

This file provides guidance to Claude Code when working with this SEC Filing-Enhanced Graph RAG-powered DCF valuation system.

## 🤖 MANDATORY SUB-AGENT ORCHESTRATION

**CRITICAL**: ALL tasks (except trivial file operations) MUST start with agent-coordinator for analysis and delegation.

### Universal Entry Point Policy

1. **ALWAYS START WITH AGENT-COORDINATOR**: Every user request must begin with Task(agent-coordinator)
2. **Analysis First**: Agent-coordinator analyzes the task and determines optimal sub-agent delegation
3. **Learning Integration**: Each task contributes to the continuous learning and optimization system
4. **Issue-Based Tracking**: All tasks link to GitHub issues for experience accumulation and pattern analysis

### Mandatory Workflow Pattern

```typescript
// ✅ MANDATORY PATTERN: Start every task with agent-coordinator
User Request: "Any development, git, data, or infrastructure task"
↓
Step 1: Task(agent-coordinator, "Analyze and delegate: [user request]")
↓  
Step 2: Agent-coordinator analyzes task complexity, issue labels, and delegates to appropriate agents
↓
Step 3: Specialized agents execute with full context and learning feedback
```

### Task Routing Guidelines

```bash
# ✅ CORRECT: Route through agent-coordinator
Use Task tool with subagent_type="agent-coordinator" for:
- Any git operations (create PR, branch management, releases)
- Development workflows (testing, quality checks, deployment)
- Data processing (ETL, SEC integration, analysis)
- Infrastructure operations (environment setup, monitoring)
- Web development (frontend, backend, API design)
- Architecture decisions (RAG system, database design)

# ❌ AVOID: Direct tool usage for complex operations
Don't use Bash/Edit/Write directly for multi-step processes
```

### Agent Selection Priority

1. **agent-coordinator**: For ALL task orchestration and complex workflows
2. **Specialized agents**: Automatically selected by coordinator based on task context
3. **Direct tools**: Only for immediate single-step operations

### Decision Matrix: When to Use Sub-Agents

| Task Type | Use Agent-Coordinator | Direct Tools |
|-----------|---------------------|--------------|
| PR Creation | ✅ Always | ❌ Never |
| Git Operations | ✅ Always | ❌ Never |
| Code Quality/Testing | ✅ Always | ❌ Never |
| Data Processing | ✅ Always | ❌ Never |
| Infrastructure Setup | ✅ Always | ❌ Never |
| Web Development | ✅ Always | ❌ Never |
| Architecture Design | ✅ Always | ❌ Never |
| Single File Read | ❌ Rarely | ✅ Preferred |
| Simple File Edit | ❌ Rarely | ✅ Preferred |
| Quick Status Check | ❌ Rarely | ✅ Preferred |

### Sub-Agent Routing Examples

```typescript
// ✅ CORRECT: Multi-step workflow via agent-coordinator
"I need to create a PR for the current changes with full validation"
→ Task(agent-coordinator) → Delegates to git-ops-agent + dev-quality-agent

// ✅ CORRECT: Complex development task
"Implement new DCF calculation feature with testing"
→ Task(agent-coordinator) → Orchestrates multiple agents in sequence

// ❌ INCORRECT: Direct tool for complex operation  
Bash("p3 create-pr ...") // Should route through agent-coordinator

// ✅ CORRECT: Simple file operation
Read("path/to/file.py") // Direct tool is appropriate
```

## 🏷️ ISSUE LABEL-AGENT MAPPING SYSTEM

### Label-Based Agent Selection

| Issue Label | Primary Agent | Secondary Agents | Priority Level |
|-------------|---------------|------------------|----------------|
| `git-ops` | git-ops-agent | dev-quality-agent | P0-Critical |
| `infrastructure` | infra-ops-agent | monitoring-agent | P0-Critical |
| `data-processing` | data-engineer-agent | monitoring-agent, database-admin-agent | P1-High |
| `web-frontend` | web-frontend-agent | api-designer-agent, performance-engineer-agent | P1-High |
| `web-backend` | web-backend-agent | database-admin-agent, security-engineer-agent | P1-High |
| `security` | security-engineer-agent | compliance-risk-agent | P0-Critical |
| `performance` | performance-engineer-agent | monitoring-agent, database-admin-agent | P1-High |
| `dcf-engine` | quant-research-agent | data-engineer-agent, compliance-risk-agent | P1-High |
| `graph-rag` | backend-architect-agent | data-engineer-agent, database-admin-agent | P1-High |
| `testing` | dev-quality-agent | git-ops-agent | P1-High |
| `compliance` | compliance-risk-agent | quant-research-agent | P0-Critical |
| `api-design` | api-designer-agent | web-backend-agent, security-engineer-agent | P2-Medium |
| `database` | database-admin-agent | performance-engineer-agent, security-engineer-agent | P1-High |
| `monitoring` | monitoring-agent | infra-ops-agent, performance-engineer-agent | P2-Medium |
| `architecture` | backend-architect-agent | performance-engineer-agent, security-engineer-agent | P1-High |
| `cost-optimization` | revops-agent | monitoring-agent, infra-ops-agent | P1-High |
| `agent-management` | hrbp-agent | agent-coordinator | P0-Critical |

## 🧠 CONTINUOUS LEARNING SYSTEM

### Learning Workflow (Every Task)

1. **Pre-Task Analysis**: Agent-coordinator analyzes issue labels and task complexity
2. **Execution Tracking**: Primary and secondary agents document decisions and blockers
3. **Post-Task Reflection**: Generate lessons learned and optimization suggestions
4. **Issue Comments**: Post learning insights to the linked GitHub issue as comments

## 🎯 COMPLEX ISSUE MANAGEMENT

### Issue Complexity Assessment

**CRITICAL**: Before starting any multi-day task, agent-coordinator MUST assess if issue breakdown is needed.

#### Automatic Issue Analysis Triggers

```typescript
// Issue breakdown required if ANY of these conditions met:
if (estimated_duration > 5_days || 
    distinct_phases >= 3 || 
    required_agents > 3 ||
    cross_system_integration ||
    multiple_testing_phases) {
  
  // Trigger breakdown workflow
  Task(agent-coordinator, "ISSUE_BREAKDOWN_REQUIRED: Analyze and decompose complex issue")
}
```

#### Issue Breakdown Workflow

**Step 1: Complexity Analysis**
- Estimate duration and identify distinct work streams
- Map agent specializations required
- Assess dependency complexity and integration points
- Evaluate testing and validation requirements

**Step 2: Decomposition Strategy**  
- **Vertical Split**: Separate by functional area (error recovery, monitoring, analytics)
- **Horizontal Split**: Separate by implementation layer (core, API, UI, tests)
- **Dependency Mapping**: Identify critical path and parallel work opportunities
- **Timeline Optimization**: Create realistic 3-4 day child issues

**Step 3: Issue Structure Creation**
- **Root Issue**: Meta-coordination hub with overall strategy and child issue links
- **Child Issues**: Focused 3-4 day implementations with single clear objectives
- **Labels**: Proper agent mapping labels for optimal delegation
- **Dependencies**: Clear cross-issue coordination requirements

#### Root Issue Template

```markdown
# [Root Issue Title] - Implementation Strategy

## Overview
Brief description of overall objective and breakdown rationale.

## Child Issues Strategy  
- **#XXXa**: [Focused area 1] (Agent: primary-agent) - Est: 3-4 days
- **#XXXb**: [Focused area 2] (Agent: primary-agent) - Est: 3-4 days  
- **#XXXc**: [Focused area 3] (Agent: primary-agent) - Est: 3-4 days

## Dependencies & Coordination
- Cross-issue coordination points and critical path
- Integration testing requirements
- Shared component architecture needs

## Success Criteria
- [ ] All child issues completed successfully
- [ ] Integration testing validates full system
- [ ] Documentation updated with new capabilities
- [ ] Performance metrics meet requirements
```

#### Child Issue Template

```markdown
# [Specific Implementation] - Part of #XXX

## Scope
Single, focused objective with clear deliverables and boundaries.

## Agent Assignment
- **Primary**: [agent-name] (specialization match)
- **Secondary**: [agent-name] (support capabilities)
- **Labels**: [agent-mapping-labels]

## Implementation Plan
1. **Day 1**: [Specific milestone]
2. **Day 2**: [Specific milestone]
3. **Day 3**: [Specific milestone]
4. **Day 4**: Testing, validation, documentation

## Acceptance Criteria
- [ ] Core implementation complete and tested
- [ ] Integration points validated
- [ ] Documentation updated
- [ ] Performance requirements met

## Parent Issue: #XXX
Links back to root coordination issue.
```

### Issue Management Integration

**GitHub Integration**:
- Use consistent labels that map to agent specializations
- Cross-reference issues with #XXX notation for dependency tracking
- Post learning reports as issue comments per CLAUDE.md requirements

**Agent-Coordinator Integration**:
- Automatically assess all tasks for breakdown needs before delegation
- Route child issues to appropriate specialized agents
- Coordinate cross-issue dependencies and integration points
- Track progress and optimize future breakdown strategies

### PR Learning Integration

**MANDATORY**: Every PR must include learning feedback in the associated issue:

```markdown
## 🧠 Task Learning Report

### Agent Performance Analysis
- **Primary Agent Used**: [agent-name]
- **Secondary Agents**: [list]  
- **Task Complexity**: [Simple/Medium/Complex/Critical]
- **Execution Time**: [duration]
- **Success Metrics**: [specific measurements]

### Lessons Learned
- **What Worked Well**: [specific successes]
- **Optimization Opportunities**: [areas for improvement]
- **Agent Delegation Accuracy**: [was the right agent chosen?]
- **Workflow Efficiency**: [bottlenecks, delays, or quick wins]

### Proposed Optimizations
- **Sub-Agent Improvements**: [specific agent enhancements needed]
- **CLAUDE.md Updates**: [configuration or process changes]
- **Label-Agent Mapping**: [mapping accuracy and suggested adjustments]

### Next Task Predictions
- **Similar Tasks**: [expected related work]
- **Resource Requirements**: [computational, time, or expertise needs]
- **Risk Factors**: [potential issues to watch for]
```

### Automatic System Optimization (Every 10 PRs)

**CRITICAL**: The system now automatically triggers optimization when PR numbers are divisible by 10.

**Automatic Trigger Logic**:
```typescript
// Automatic optimization detection
if (PR_NUMBER % 10 === 0) {
  // Automatically trigger system optimization
  Task(agent-coordinator, "AUTO_OPTIMIZATION_TRIGGER: PR #${PR_NUMBER} reached. Analyze last 10 PRs and optimize entire sub-agent ecosystem based on accumulated learning data from issue comments.")
}
```

**Trigger Examples**:
- PR #10 → First system optimization
- PR #20 → Second optimization cycle  
- PR #30 → Third optimization cycle
- And so on...

**Optimization Execution Pattern**:
1. **Detection Phase**: Detect when PR number % 10 === 0
2. **Analysis Phase**: Collect learning data from last 10 GitHub issue comments
3. **Optimization Phase**: Generate system-wide improvements
4. **Implementation Phase**: Update sub-agents and CLAUDE.md automatically
5. **Documentation Phase**: Document optimization results in the milestone PR

**Optimization Scope** (Executed Automatically):
1. **Label-Agent Mapping Refinement**: Adjust based on success patterns from last 10 PRs
2. **Agent Role Evolution**: Modify agent capabilities based on usage patterns
3. **Workflow Pattern Updates**: Optimize common multi-agent sequences
4. **Performance Metrics**: Update KPIs and success criteria  
5. **CLAUDE.md Configuration**: System-wide process improvements
6. **New Agent Specializations**: Create new agents if patterns show need

## 🚨 CRITICAL REQUIREMENTS

1. **ALWAYS read README.md first** - Contains complete project architecture
2. **ALWAYS route through agent-coordinator** - For optimal sub-agent utilization
3. **Use `common/config/` for all configurations** - Centralized SSOT system
4. **Follow p3 command workflow** - Never use direct python scripts
5. **Test before PR creation** - `p3 e2e` is mandatory
6. **Update parent READMEs** - When modifying directory functionality
7. **ENGLISH-ONLY POLICY** - All technical content must use English
8. **SUB-AGENT ERROR MONITORING** - Monitor and interrupt failed sub-agent executions
9. **ISSUE SIZE EVALUATION** - Break down large issues into manageable pieces

## 📋 ISSUE MANAGEMENT STRATEGY

**CRITICAL**: Evaluate issue complexity and break down oversized issues before creation.

### Issue Size Evaluation Criteria

#### ✅ Properly Sized Issues (Create Directly)
- **Duration**: 3-5 days maximum
- **Scope**: Single functional area or system component
- **Dependencies**: Clear, minimal blockers
- **Success Metrics**: 3-5 measurable outcomes
- **Complexity**: Single domain expertise required

#### ❌ Oversized Issues (Require Breakdown)
- **Duration**: >5 days or multiple phases
- **Scope**: Multiple systems, domains, or major architectural changes
- **Dependencies**: Complex dependency chains or circular dependencies
- **Success Metrics**: >5 outcomes or vague/unmeasurable metrics
- **Complexity**: Multi-domain expertise or sequential phase requirements

### Issue Breakdown Process

#### Step 1: Complexity Assessment
```yaml
evaluation_checklist:
  duration_check: "Is this >5 days or multiple phases?"
  scope_check: "Does this span multiple systems/domains?"
  dependency_check: "Are there complex dependency chains?"
  success_metric_check: "Are there >5 success metrics?"
  
# If ANY check is "yes" → Break down the issue
```

#### Step 2: Issue Breakdown Strategy
```typescript
function breakdownLargeIssue(originalIssue) {
  // 1. Identify natural phase boundaries
  const phases = identifyPhases(originalIssue);
  
  // 2. Create focused sub-issues
  const subIssues = phases.map(phase => createFocusedIssue(phase));
  
  // 3. Establish clear dependencies
  const dependencies = establishDependencies(subIssues);
  
  // 4. Link to parent issue
  linkToParent(subIssues, originalIssue);
  
  return subIssues;
}
```

#### Step 3: Parent-Child Issue Structure
```yaml
issue_hierarchy:
  parent_issue: "Analysis or planning issue (like #139)"
  child_issues: "Focused implementation issues"
  linking_strategy: "Reference parent in child, update parent with child links"
  
example_structure:
  parent: "#139 - Sub-Agent Architecture Analysis"
  children:
    - "#167 - Error Recovery & Resilience (5 days, Phase 1)"
    - "#168 - Load Balancing & Performance (4 days, Phase 2, depends on #167)"
    - "#169 - Analytics & Learning (4 days, Phase 3, depends on #167 & #168)"
```

### Implementation Examples

#### ✅ Good Issue Creation
```markdown
Title: "Sub-Agent Error Recovery & Resilience System"
Duration: 3-5 days
Scope: Error handling mechanisms only
Dependencies: Existing agent-coordinator system
Success Metrics: 4 clear, measurable outcomes
```

#### ❌ Bad Issue Creation (Should be Broken Down)
```markdown
Title: "Implement Complete Sub-Agent Optimization System"
Duration: 21 days, 3 phases
Scope: Error recovery + Load balancing + Analytics + Learning
Dependencies: Multiple complex systems
Success Metrics: 12+ outcomes across different domains
```

### Integration with Agent-Coordinator

The agent-coordinator has been optimized to focus on delegation rather than detailed analysis:

#### Agent-Coordinator Changes (Implemented)
- **Reduced from 643 to ~270 lines** (58% reduction)
- **Focused on workflow orchestration and task delegation**
- **Removed detailed technical specifications** (delegate to specialists)
- **Added strategic delegation to HRBP and RevOps agents**

#### Strategic Delegation Handoffs
```yaml
agent_coordinator_delegates:
  agent_management: "hrbp-agent (every 10 PRs, performance reviews)"
  cost_analysis: "revops-agent (ROI, optimization, efficiency)"
  detailed_technical_analysis: "specialized domain agents"
  issue_breakdown: "Follow issue management strategy first"
```

## 🛠️ SUB-AGENT ERROR MONITORING & INTERRUPTION PROTOCOL

**CRITICAL**: Monitor sub-agent execution for errors and implement immediate interruption and recovery protocols.

### Error Detection Patterns

#### Common Sub-Agent Execution Errors

1. **Missing Agent References**
   ```bash
   Error: "Agent [agent-name] not found"
   Cause: Task delegated to non-existent sub-agent
   Action: Interrupt immediately, use fallback delegation
   ```

2. **Workflow Pattern Failures**
   ```bash
   Error: "Cannot complete workflow - missing dependency agent"
   Cause: Complex workflow references unavailable agents
   Action: Interrupt, revise workflow to use available agents
   ```

3. **Task Parameter Validation Errors**
   ```bash
   Error: "Invalid task parameters for agent"
   Cause: Agent receives incompatible task specifications
   Action: Interrupt, reformulate task parameters
   ```

4. **Agent Communication Timeouts**
   ```bash
   Error: "Sub-agent execution timeout"
   Cause: Agent takes too long or becomes unresponsive
   Action: Interrupt after 2 minutes, delegate to backup agent
   ```

### Mandatory Interruption Protocol

#### Step 1: Immediate Error Detection
```typescript
// Monitor sub-agent execution for these error signals
const ERROR_PATTERNS = [
  "Agent [*] not found",
  "Cannot complete workflow",
  "Invalid task parameters", 
  "Sub-agent execution timeout",
  "Missing dependency agent",
  "Workflow pattern failure"
];

// Interrupt execution immediately when detected
if (sub_agent_error_detected) {
  INTERRUPT_EXECUTION();
  LOG_ERROR_DETAILS();
  INITIATE_RECOVERY_PROTOCOL();
}
```

#### Step 2: Error Analysis and Recovery
```markdown
1. **Identify Error Type**: Categorize as missing agent, workflow failure, or parameter error
2. **Document Error Context**: Log task details, agent called, error message
3. **Implement Fallback**: Route to available agent or direct tools
4. **Update Agent Descriptions**: Revise agent capabilities to prevent recurrence
5. **Continue Execution**: Resume with corrected approach
```

#### Step 3: Agent Description Updates
**MANDATORY**: When sub-agent errors occur, immediately update agent descriptions and CLAUDE.md mappings.

```markdown
## Error-Driven Agent Description Updates

### Missing Agent Errors
When Task(agent-name) fails due to missing agent:
1. Update CLAUDE.md label-agent mapping with available fallback
2. Modify agent-coordinator delegation logic  
3. Document planned implementation timeline for missing agent

### Workflow Pattern Errors  
When complex workflows fail due to missing dependencies:
1. Revise workflow patterns in agent-coordinator.md
2. Create simplified workflows using available agents
3. Add workflow validation before execution

### Parameter Validation Errors
When agents receive incompatible task specifications:
1. Update agent prompt templates with parameter validation
2. Add input sanitization and type checking
3. Implement parameter transformation logic
```

### Error Recovery Examples

#### Example 1: Missing Quant-Research-Agent
```typescript
// ❌ ORIGINAL: Fails due to missing agent
Task(quant-research-agent, "Perform DCF analysis for AAPL")

// ✅ RECOVERY: Use available agents with direct tools
Task(data-engineer-agent, "Extract AAPL financial data for DCF analysis") 
→ Use direct tools for DCF calculations
→ Task(git-ops-agent, "Create PR with DCF analysis results")
```

#### Example 2: Broken Multi-Agent Workflow  
```typescript
// ❌ ORIGINAL: Complex workflow with missing agents
"Implement full RAG pipeline with security validation"
→ backend-architect-agent (❌ missing)
→ security-engineer-agent (❌ missing)  
→ database-admin-agent (❌ missing)

// ✅ RECOVERY: Simplified workflow with available agents
"Implement RAG pipeline components with available agents"
→ Task(agent-coordinator, "Route RAG implementation using available agents")
→ data-engineer-agent (ETL components)
→ infra-ops-agent (infrastructure setup)
→ dev-quality-agent (testing and validation)
```

### Proactive Error Prevention

#### Agent Availability Validation
```python
def validate_agent_before_delegation(agent_name):
    """Validate agent exists before Task() call"""
    agent_path = f".claude/agents/{agent_name}.md"
    if not os.path.exists(agent_path):
        return False, f"Agent {agent_name} not implemented - use fallback"
    return True, f"Agent {agent_name} available"
```

#### Fallback Agent Mapping
```yaml
# Automatic fallback when primary agents unavailable
agent_fallbacks:
  quant-research-agent: data-engineer-agent
  backend-architect-agent: infra-ops-agent  
  web-backend-agent: dev-quality-agent
  security-engineer-agent: git-ops-agent
  database-admin-agent: infra-ops-agent
```

### Error Logging and Improvement Tracking

#### Mandatory Error Documentation
Every sub-agent error must be logged with:
```markdown
## Sub-Agent Error Report

**Timestamp**: [ISO timestamp]
**Error Type**: [Missing Agent | Workflow Failure | Parameter Error | Timeout]
**Agent Requested**: [agent-name]
**Task Description**: [original task]
**Error Message**: [exact error text]
**Recovery Action**: [fallback approach used]
**Resolution Time**: [duration to recover]
**Prevention Update**: [changes made to prevent recurrence]
```

#### Integration with Learning System
Sub-agent errors feed into the continuous learning system:
```markdown
## Error-Driven Learning Integration

1. **Error Pattern Recognition**: Track frequent error types and causes
2. **Agent Prioritization**: Prioritize implementation of frequently-needed missing agents  
3. **Workflow Optimization**: Revise common workflow patterns to avoid error-prone sequences
4. **Documentation Updates**: Automatically update CLAUDE.md based on error patterns
5. **Predictive Prevention**: Anticipate potential errors in similar future tasks
```

### Implementation Status Alert

**CURRENT STATE WARNING**: As of the analysis in Issue #139, only 4/15 promised agents exist:

✅ **Available Agents**: agent-coordinator, git-ops-agent, data-engineer-agent, infra-ops-agent, dev-quality-agent, monitoring-agent

❌ **Missing Agents (High Error Risk)**: quant-research-agent, compliance-risk-agent, backend-architect-agent, web-frontend-agent, web-backend-agent, api-designer-agent, security-engineer-agent, performance-engineer-agent, database-admin-agent

**Immediate Action Required**: All sub-agent delegations must include error monitoring and immediate fallback to available agents until missing agents are implemented.

## 🔄 ADVANCED SUB-AGENT ERROR RECOVERY & INTERRUPTION SYSTEM

**CRITICAL**: Implement comprehensive error recovery, interruption protocols, and intelligent retry mechanisms for robust sub-agent execution.

### Error Classification and Recovery Framework

#### Sub-Agent Error Categories

```yaml
error_categories:
  timeout:
    description: "Agent execution exceeds time limit"
    retry_count: 3
    backoff_strategy: "exponential"
    base_delay: 2  # seconds
    max_delay: 30  # seconds
    escalation_after: 3
    
  resource_unavailable:
    description: "Required resources not accessible"
    retry_count: 2
    backoff_strategy: "linear"
    base_delay: 5  # seconds
    escalation_after: 2
    
  validation_failure:
    description: "Task parameters or output validation failed"
    retry_count: 1
    backoff_strategy: "immediate"
    escalation_after: 1
    fallback: "direct_tools"
    
  agent_not_found:
    description: "Requested sub-agent does not exist"
    retry_count: 0
    immediate_action: "fallback_delegation"
    log_priority: "high"
    
  workflow_dependency_failure:
    description: "Multi-agent workflow chain broken"
    retry_count: 2
    recovery_mode: "partial_workflow"
    checkpoint_restore: true
```

### Intelligent Interruption Protocol

#### Circuit Breaker Implementation

```python
class SubAgentCircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = {}
        self.last_failure_time = {}
        self.circuit_state = {}  # 'closed', 'open', 'half_open'
    
    def can_execute(self, agent_name):
        """Check if agent can execute based on circuit state"""
        state = self.circuit_state.get(agent_name, 'closed')
        
        if state == 'closed':
            return True
        elif state == 'open':
            if self._should_attempt_reset(agent_name):
                self.circuit_state[agent_name] = 'half_open'
                return True
            return False
        elif state == 'half_open':
            return True
    
    def record_success(self, agent_name):
        """Reset circuit on successful execution"""
        self.failure_count[agent_name] = 0
        self.circuit_state[agent_name] = 'closed'
    
    def record_failure(self, agent_name):
        """Track failures and open circuit if threshold exceeded"""
        self.failure_count[agent_name] = self.failure_count.get(agent_name, 0) + 1
        self.last_failure_time[agent_name] = time.time()
        
        if self.failure_count[agent_name] >= self.failure_threshold:
            self.circuit_state[agent_name] = 'open'
            return True  # Circuit opened
        return False
```

#### Real-Time Task Interruption System

```python
class TaskInterruptionManager:
    def __init__(self):
        self.active_tasks = {}
        self.interruption_signals = set()
        self.task_checkpoints = {}
    
    def start_task_monitoring(self, task_id, agent_name, timeout=120):
        """Begin monitoring task execution with timeout"""
        self.active_tasks[task_id] = {
            'agent': agent_name,
            'start_time': time.time(),
            'timeout': timeout,
            'status': 'running'
        }
        
        # Start timeout monitoring thread
        threading.Timer(timeout, self._timeout_handler, [task_id]).start()
    
    def interrupt_task(self, task_id, reason="manual_interruption"):
        """Immediately interrupt running task"""
        if task_id in self.active_tasks:
            self.interruption_signals.add(task_id)
            self.active_tasks[task_id]['status'] = 'interrupted'
            self.active_tasks[task_id]['interruption_reason'] = reason
            
            # Save checkpoint for recovery
            self._create_checkpoint(task_id)
            return True
        return False
    
    def _create_checkpoint(self, task_id):
        """Save task state for potential recovery"""
        task_info = self.active_tasks.get(task_id)
        if task_info:
            checkpoint = {
                'task_id': task_id,
                'agent': task_info['agent'],
                'timestamp': time.time(),
                'partial_results': self._gather_partial_results(task_id),
                'execution_context': self._capture_context(task_id)
            }
            self.task_checkpoints[task_id] = checkpoint
```

### Adaptive Retry Mechanisms

#### Exponential Backoff with Jitter

```python
class AdaptiveRetryManager:
    def __init__(self):
        self.retry_statistics = {}
        self.success_patterns = {}
    
    def calculate_retry_delay(self, agent_name, attempt_number, error_type):
        """Calculate optimal retry delay based on historical data"""
        base_delay = self._get_base_delay(error_type)
        
        # Exponential backoff with jitter
        exponential_delay = base_delay * (2 ** (attempt_number - 1))
        jitter = random.uniform(0.1, 0.3) * exponential_delay
        
        # Adaptive adjustment based on historical success rates
        historical_modifier = self._get_historical_modifier(agent_name, error_type)
        
        final_delay = min((exponential_delay + jitter) * historical_modifier, 300)  # Max 5 minutes
        return final_delay
    
    def should_retry(self, agent_name, error_type, attempt_number):
        """Intelligent retry decision based on patterns"""
        max_retries = self._get_max_retries(error_type)
        
        if attempt_number >= max_retries:
            return False
        
        # Check historical success patterns
        success_probability = self._calculate_success_probability(
            agent_name, error_type, attempt_number
        )
        
        return success_probability > 0.3  # 30% threshold for retry
```

### Workflow State Management

#### Multi-Agent Workflow Checkpointing

```python
class WorkflowStateManager:
    def __init__(self):
        self.workflow_states = {}
        self.agent_dependencies = {}
    
    def save_workflow_checkpoint(self, workflow_id, completed_agents, pending_agents):
        """Save current workflow state"""
        checkpoint = {
            'workflow_id': workflow_id,
            'completed_agents': completed_agents,
            'pending_agents': pending_agents,
            'intermediate_results': {},
            'timestamp': time.time()
        }
        
        # Capture intermediate results from completed agents
        for agent in completed_agents:
            checkpoint['intermediate_results'][agent] = self._capture_agent_output(agent)
        
        self.workflow_states[workflow_id] = checkpoint
    
    def restore_workflow(self, workflow_id):
        """Restore workflow from checkpoint after failure"""
        if workflow_id not in self.workflow_states:
            return None
        
        checkpoint = self.workflow_states[workflow_id]
        
        # Resume from last successful agent
        return {
            'resume_from': checkpoint['completed_agents'][-1] if checkpoint['completed_agents'] else None,
            'pending_tasks': checkpoint['pending_agents'],
            'context': checkpoint['intermediate_results']
        }
```

### Error Recovery Patterns

#### Graceful Degradation Strategies

```yaml
degradation_patterns:
  missing_specialized_agent:
    fallback_sequence:
      1: "Use available general-purpose agent with specialized prompts"
      2: "Break task into smaller components for direct tool execution"
      3: "Escalate to human with detailed context"
    
  resource_contention:
    fallback_sequence:
      1: "Queue task for retry during low-load period"
      2: "Use alternative resource allocation strategy"
      3: "Execute with reduced resource requirements"
    
  network_connectivity:
    fallback_sequence:
      1: "Switch to local resource alternatives"
      2: "Cache-based execution with stale data warning"
      3: "Defer to next maintenance window"
    
  validation_failure:
    fallback_sequence:
      1: "Re-validate with relaxed criteria"
      2: "Manual validation escalation"
      3: "Accept with risk documentation"
```

#### Human Escalation Protocols

```python
class HumanEscalationManager:
    def __init__(self):
        self.escalation_rules = {
            'security_critical': {'response_time': 15, 'notification': ['security_team', 'oncall']},
            'data_integrity': {'response_time': 30, 'notification': ['data_team', 'engineering']},
            'system_failure': {'response_time': 60, 'notification': ['sre_team', 'infrastructure']},
            'default': {'response_time': 120, 'notification': ['general_support']}
        }
    
    def escalate_task(self, task_id, agent_name, error_type, context):
        """Escalate failed task to human intervention"""
        escalation_type = self._classify_escalation(error_type, context)
        rules = self.escalation_rules.get(escalation_type, self.escalation_rules['default'])
        
        escalation_record = {
            'escalation_id': f"ESC_{task_id}_{int(time.time())}",
            'original_task': task_id,
            'failed_agent': agent_name,
            'error_details': error_type,
            'context': context,
            'escalation_time': time.time(),
            'expected_response': rules['response_time'],
            'notified_teams': rules['notification']
        }
        
        # Send notifications
        self._notify_teams(escalation_record)
        return escalation_record
```

### Performance Monitoring and Analytics

#### Real-Time Agent Performance Tracking

```python
class AgentPerformanceMonitor:
    def __init__(self):
        self.performance_metrics = {}
        self.trend_analysis = TrendAnalyzer()
    
    def track_execution_metrics(self, agent_name, task_type, execution_time, success, error_type=None):
        """Track detailed performance metrics"""
        if agent_name not in self.performance_metrics:
            self.performance_metrics[agent_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'average_execution_time': 0,
                'error_patterns': defaultdict(int),
                'success_rate_trend': [],
                'performance_trend': []
            }
        
        metrics = self.performance_metrics[agent_name]
        metrics['total_executions'] += 1
        
        if success:
            metrics['successful_executions'] += 1
        else:
            metrics['error_patterns'][error_type] += 1
        
        # Update running averages
        metrics['average_execution_time'] = (
            (metrics['average_execution_time'] * (metrics['total_executions'] - 1) + execution_time)
            / metrics['total_executions']
        )
        
        # Track trends
        current_success_rate = metrics['successful_executions'] / metrics['total_executions']
        metrics['success_rate_trend'].append((time.time(), current_success_rate))
        metrics['performance_trend'].append((time.time(), execution_time))
        
        # Maintain trend history (last 100 data points)
        if len(metrics['success_rate_trend']) > 100:
            metrics['success_rate_trend'] = metrics['success_rate_trend'][-100:]
            metrics['performance_trend'] = metrics['performance_trend'][-100:]
```

### Integration with Learning System

#### Error Pattern Recognition and Learning

```python
class ErrorPatternLearningSystem:
    def __init__(self):
        self.error_patterns = {}
        self.prediction_models = {}
        self.optimization_recommendations = []
    
    def analyze_error_patterns(self, time_window_hours=24):
        """Analyze recent error patterns and generate insights"""
        recent_errors = self._get_recent_errors(time_window_hours)
        
        patterns = {
            'most_common_errors': self._identify_common_errors(recent_errors),
            'error_correlation': self._analyze_error_correlation(recent_errors),
            'temporal_patterns': self._analyze_temporal_patterns(recent_errors),
            'agent_specific_patterns': self._analyze_agent_patterns(recent_errors)
        }
        
        # Generate optimization recommendations
        recommendations = self._generate_recommendations(patterns)
        self.optimization_recommendations.extend(recommendations)
        
        return patterns, recommendations
    
    def predict_task_success_probability(self, agent_name, task_type, current_context):
        """Predict likelihood of task success based on historical patterns"""
        if agent_name not in self.prediction_models:
            return 0.8  # Default optimistic probability
        
        model = self.prediction_models[agent_name]
        features = self._extract_features(task_type, current_context)
        
        success_probability = model.predict_probability(features)
        return success_probability
```

### Implementation Status and Rollout Plan

#### Phase 1: Core Error Recovery (Week 1)
- ✅ Implement basic circuit breaker pattern
- ✅ Add exponential backoff retry mechanism
- ✅ Create task interruption system
- ✅ Implement workflow checkpointing

#### Phase 2: Advanced Analytics (Week 2)
- 🔄 Deploy real-time performance monitoring
- 🔄 Add error pattern recognition system
- 🔄 Implement predictive success probability
- 🔄 Create human escalation protocols

#### Phase 3: Optimization Integration (Week 3)
- 📋 Integrate with existing 10-PR learning cycle
- 📋 Add adaptive retry strategy optimization
- 📋 Deploy intelligent agent selection based on performance data
- 📋 Create comprehensive monitoring dashboard

This advanced error recovery system ensures robust sub-agent execution with intelligent failure handling, comprehensive monitoring, and continuous optimization based on real-world performance patterns.

## 🌐 ENGLISH-ONLY CODING STANDARDS

**CRITICAL**: All technical content in this quantitative trading platform must use English for international standards compliance and professional development practices.

### Mandatory English Usage

#### ✅ MUST BE IN ENGLISH:
- **Code**: All variable names, function names, class names, module names
- **Comments**: All code comments, docstrings, and inline documentation
- **Configuration Files**: All config keys, values, and documentation
- **Log Messages**: All logging output, error messages, and debug information
- **Documentation**: README files, technical specifications, API docs
- **Git Commits**: All commit messages, PR titles, and descriptions
- **Issue Tracking**: Issue titles, descriptions, and comments
- **Database Schema**: Table names, column names, constraints, indexes

#### ✅ ACCEPTABLE NON-ENGLISH:
- **Templates**: User-facing templates for multi-language support (e.g., `templates/` directory)
- **Test Data**: Sample data strings for testing internationalization features
- **Build Artifacts**: Generated content that may contain localized data
- **User Interface Strings**: UI text meant for localization (must be in separate i18n files)

### Implementation Guidelines

#### Code Examples

```python
# ✅ CORRECT: English code
def calculate_dcf_valuation(company_ticker, growth_rate, discount_rate):
    """Calculate DCF valuation for a given company.
    
    Args:
        company_ticker: Stock ticker symbol (e.g., 'AAPL')
        growth_rate: Annual growth rate as decimal (e.g., 0.05 for 5%)
        discount_rate: Discount rate as decimal (e.g., 0.10 for 10%)
    
    Returns:
        Calculated DCF value as float
    """
    logger.info(f"Starting DCF calculation for {company_ticker}")
    # Implementation here
    logger.info("DCF calculation completed successfully")
    return dcf_value

# ❌ INCORRECT: Non-English code
def 计算DCF估值(公司代码, 增长率, 折现率):  # Don't do this
    """计算给定公司的DCF估值"""  # Don't do this
    logger.info(f"开始计算 {公司代码} 的DCF")  # Don't do this
```

#### Configuration Examples

```yaml
# ✅ CORRECT: English configuration
database_config:
  host: "localhost"
  port: 5432
  database_name: "quantitative_trading"
  connection_timeout: 30
  retry_attempts: 3
  
# ❌ INCORRECT: Non-English configuration  
数据库配置:  # Don't do this
  主机: "localhost"  # Don't do this
```

#### Git Commit Examples

```bash
# ✅ CORRECT: English commit messages
git commit -m "Implement SEC filing data integration for M7 companies

Added semantic embedding generation and vector search capabilities
for enhanced Graph RAG query processing with regulatory backing.

Fixes #123"

# ❌ INCORRECT: Non-English commit messages
git commit -m "实现SEC文件数据集成"  # Don't do this
```

### Enforcement Mechanisms

1. **Pre-commit Hooks**: Automated language validation for code and comments
2. **CI/CD Validation**: GitHub Actions check for English-only policy compliance
3. **Agent Enforcement**: Sub-agents will validate and suggest English alternatives
4. **Code Review Requirements**: All PRs must pass English-only validation

### Exception Handling

**For Legacy Code**: When working with existing non-English content:
1. **Refactor Gradually**: Update to English during normal maintenance
2. **Document Exceptions**: Clearly mark temporary non-English content with TODO comments
3. **Migration Plan**: Create issues to track English conversion progress

**For International Features**: When building localization features:
1. **Separate Concerns**: Keep internationalized content in dedicated i18n directories
2. **English Default**: Always provide English as the primary/fallback language
3. **Template Isolation**: Non-English content only in `templates/` or `i18n/` directories

## Quick Setup

**p3 Command (Global Setup)**:
```bash
mkdir -p ~/bin && cat > ~/bin/p3 << 'EOF'
#!/bin/bash
cd /path/to/my_finance && pixi run python p3 "$@"
EOF
chmod +x ~/bin/p3 && echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
```

**Essential Commands**:
- `p3 env-status` - Check system status
- `p3 e2e` - Run end-to-end tests (M7 scope)
- `p3 create-pr "description" ISSUE_NUMBER` - Create PR with validation

## System Architecture

**See README.md and directory READMEs for complete details.**

**Key Components**:
- **ETL/**: Data processing with SEC document semantic embedding (see ETL/README.md)
- **dcf_engine/**: DCF calculations and Graph RAG Q&A (see dcf_engine/README.md)
- **common/**: Unified configuration and directory management (see common/README.md)
- **graph_rag/**: Semantic retrieval and reasoning (see graph_rag/README.md)

**Data Tiers**: F2 (dev) → M7 (testing) → N100 (validation) → V3K (production)
**SEC Integration**: 336 documents with semantic retrieval for M7 companies

## Quality Control

**Process enforcement (not technical enforcement):**
- ✅ PRs required for main branch
- ✅ M7 test validation in commit messages
- ⚠️ Status checks NOT mandatory (manual enforcement)

**MANDATORY**: `p3 create-pr` - Prevents untested code reaching main branch

**Security Rules**:
1. NEVER bypass automated scripts
2. Always verify M7 tests pass locally
3. Monitor CI status for failures

**Command Quality**: The p3 CLI automatically validates and sanitizes commands before execution to prevent syntax errors (Issue #153 protection).

## Sub-Agent Workflow Examples

### Git Operations (via agent-coordinator → git-ops-agent)

```bash
# Instead of direct p3 create-pr, use:
Task tool with subagent_type="agent-coordinator":
"Route PR creation task: Create PR for current branch with M7 testing validation"

# Instead of direct git commands, use:
Task tool with subagent_type="agent-coordinator":
"Route git operations: Branch cleanup, merge conflict resolution, release management"
```

### Development Quality (via agent-coordinator → dev-quality-agent)

```bash
# Instead of direct p3 e2e/lint/format, use:
Task tool with subagent_type="agent-coordinator":
"Route development quality task: Run full testing suite with code quality validation"
```

### Data Processing (via agent-coordinator → data-engineer-agent)

```bash
# Instead of direct data operations, use:
Task tool with subagent_type="agent-coordinator":
"Route data processing task: SEC filing integration with M7 companies analysis"
```

### Infrastructure Management (via agent-coordinator → infra-ops-agent)

```bash
# Instead of direct environment commands, use:
Task tool with subagent_type="agent-coordinator":
"Route infrastructure task: Environment setup and service monitoring"
```

## Enhanced Git Workflow with Auto-Optimization

**CRITICAL**: All git operations now include automatic optimization detection and execution every 10 PRs.

#### Mandatory PR Creation Pattern

```typescript
// Every PR creation must follow this pattern
User: "Create PR for [task]"
↓
Step 1: Task(agent-coordinator, "Analyze and delegate PR creation with auto-optimization check")
↓
Step 2: Agent-coordinator checks: if (PR_NUMBER % 10 === 0) → Trigger AUTO_OPTIMIZATION_TRIGGER
↓  
Step 3: If optimization triggered → Execute full system optimization before completing PR
↓
Step 4: Complete PR creation with learning report posted to issue comments
```

#### Auto-Optimization Integration Workflow

**For Regular PRs** (PR# % 10 ≠ 0):
1. Standard task execution via agent-coordinator
2. Generate and post learning report to issue comments  
3. Complete PR creation normally

**For Milestone PRs** (PR# % 10 === 0, e.g., #10, #20, #30):
1. **Pre-Optimization**: Complete the original task first
2. **Auto-Trigger Detection**: Detect milestone PR number  
3. **System Optimization**: Execute comprehensive analysis of last 10 PRs
4. **Implementation**: Update agents and CLAUDE.md automatically
5. **Documentation**: Post optimization results to milestone PR
6. **Completion**: Finalize milestone PR with both task results + optimization report

**See README.md for complete workflow.** Claude requirements:

### Protection Model

- ✅ **p3 create-pr workflow**: Fully supported
- ❌ **Direct git push**: Blocked to enforce testing
- 🎯 **Goal**: All code passes M7/F2 tests before reaching remote

### Common Issues

- **"Cannot create PR from main"**: Check worktree context with `git branch --show-current`
- **"Direct push blocked"**: Ensure `P3_CREATE_PR_PUSH` environment variable set
- **Testing failures**: Fix issues, don't skip validation - run `p3 e2e f2`
- **Malformed pixi commands**: Automatic sanitization fixes unquoted parameters (Issue #153 resolved)

### Pre-PR Checklist

**CRITICAL**: Update parent README files when modifying directory functionality:
- ETL changes → Update root README "Core Components" → ETL description
- DCF Engine changes → Update root README "Core Components" → dcf_engine description
- Graph RAG changes → Update root README "Core Components" → graph_rag description

### PR Workflow

**MANDATORY Process**:
```bash
# 1. Run tests first
p3 e2e

# 2. Check README consistency if modified directories
# (Update parent README descriptions as needed)

# 3. Create PR via automation only
p3 create-pr "Brief description" ISSUE_NUMBER
```

**Why Manual Git FAILS**:
- Direct `git push` → Missing M7 validation → CI rejection
- Manual PR creation → No test verification → Blocked merge
- Hand-crafted commits → Fake markers detected → Validation failure

**CI Validates**: Real M7 test timestamps, actual data processing, proper test hosts

**NEVER**: Use `git push`, `gh pr create`, or manual commit messages

### Issue Management

- **ALL changes link to GitHub Issues** for traceability
- **Claude Code configs**: Link to issue #14
- **Branch naming**: `feature/description-fixes-N`
- **Current active**: #20 (Neo4j), #21 (DCF), #22 (Graph RAG), #26 (conda migration)

**See README.md for complete issue history and testing approach.**

## Development Guidelines

### Patterns
- Read README.md first for project context
- Edit existing files over creating new ones  
- Use p3 commands exclusively (never direct python)
- Reference CIK numbers from README.md for SEC work

### Core Files
- **Config**: `common/config/*.yml` (centralized SSOT)
- **ETL**: Data processing and SEC integration
- **DCF**: Valuation calculations and Graph RAG

### Command System

**Format**: `p3 <command> [scope]`
- **Scopes**: f2 (dev), m7 (testing), n100 (validation), v3k (production)
- **Key commands**: `env-status`, `e2e`, `create-pr`, `cleanup-branches`

**Quality Assurance**: p3.py includes automatic command sanitization for malformed pixi commands (fixed Issue #153). String parameters like 'f2', ['sec_edgar'], 'development' are automatically quoted when syntax errors are detected.

### Testing
- **Development**: `p3 e2e` (~1-2 min) - Quick validation
- **PR Required**: `p3 e2e m7` (~5-10 min) - Full M7 validation
- **Extended**: `p3 e2e n100/v3k` - Comprehensive testing

### Daily Workflow

**CRITICAL RULES**:
1. Use `p3 <command>` (never direct python scripts)
2. Start from latest main (`git checkout main && git pull`)
3. Test before coding (`p3 e2e`)
4. Check README consistency after directory changes

**AI-Generated Command Guidelines**:
- The p3 CLI automatically sanitizes malformed commands with unquoted parameters
- String parameters will be auto-quoted: `f2` → `'f2'`, `[sec_edgar]` → `['sec_edgar']`
- Watch for sanitization messages: "⚠️ Fixed malformed pixi command (Issue #153)"
- Trust the automatic fixes - they prevent common syntax errors in pixi commands

**Session Sequence**:
```bash
# 1. Setup
git checkout main && git pull
p3 env-status

# 2. Branch
git checkout -b feature/description-fixes-N

# 3. Validate
p3 e2e  # Test system works

# 4. Work
# ... make changes ...
p3 format && p3 lint

# 5. PR
p3 create-pr "Description" N

# 6. Cleanup
p3 shutdown-all
```

**Conflict Resolution**:
1. Update main first: `git checkout main && git pull`
2. Rebase feature: `git checkout feature/branch && git rebase origin/main`
3. Test after resolution: `p3 e2e`

## Architecture Principles

**DRY/SSOT Implementation** - See `common/README.md` for complete details:
- **Directory paths**: Centralized in `common/directory_manager.py`
- **Configuration**: Single source at `common/config/`
- **Five-layer architecture**: Optimized data processing pipeline
- **Storage backends**: Local filesystem with cloud abstraction ready

**Key Rules**:
1. Never hard-code paths - use `directory_manager`
2. Use DataLayer enums instead of string paths
3. Update `directory_structure.yml` for new directories
4. Test path changes with migration scripts

**SSOT Configuration**: All configs at `common/config/` (migrated from `data/config/`)

---

**For detailed information, see directory-specific README files:**
- `README.md` - Complete project overview
- `common/README.md` - Configuration and directory management
- `ETL/README.md` - Data processing and SEC integration
- `dcf_engine/README.md` - DCF calculations and Graph RAG
- `graph_rag/README.md` - Semantic retrieval system
- `infra/README.md` - Infrastructure and deployment