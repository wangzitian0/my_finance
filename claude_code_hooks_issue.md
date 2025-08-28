# Implement Claude Code Hooks for Comprehensive Logging Integration

**Labels:** `infra`, `logging`, `monitoring`, `claude-integration`, `enhancement`  
**Assignee:** infra-ops-agent  
**Priority:** High  
**Epic:** Centralized Logging and Monitoring Enhancement  

## 📋 Issue Summary

Implement comprehensive Claude Code hooks to capture and redirect all Claude Code interactions and operations to our existing centralized logging framework at `common/config/monitoring/` and integrate with our current `ExecutionMonitor` system.

## 🎯 Objective

Create a robust logging system that captures all Claude Code activities including thinking chains, tool invocations, context information, agent interactions, and error traces, then redirects this data to our established monitoring infrastructure for comprehensive analysis and troubleshooting.

## 📊 Current State Analysis

### Existing Infrastructure
- ✅ **ExecutionMonitor System**: `common/execution_monitor.py` with structured logging
- ✅ **Centralized Logging**: `common/logger.py` with DirectoryManager integration
- ✅ **Log Storage**: `build_data/logs/` directory structure via DirectoryManager
- ✅ **JSON Log Format**: Daily execution logs at `build_data/logs/execution_logs_YYYY-MM-DD.json`
- ✅ **Error Categorization**: CRITICAL, HIGH, MEDIUM, LOW classification system
- ✅ **Performance Metrics**: Execution time tracking and success/failure rates

### Gap Analysis
- ❌ **Claude Code Integration**: No hooks capturing Claude Code internal operations
- ❌ **Thinking Chain Capture**: Chain of thought reasoning not logged
- ❌ **Tool Invocation Logs**: API calls and responses not captured systematically
- ❌ **Context Tracking**: Session metadata and environment not linked to Claude activities
- ❌ **Agent Delegation Logs**: Multi-agent interactions not tracked end-to-end
- ❌ **Real-time Streaming**: Current system is batch-only

## 🛠️ Technical Requirements

### 1. Claude Code Hook Implementation

#### 1.1 Hook Types to Implement
```python
# Required Claude Code hooks
REQUIRED_HOOKS = {
    'user-prompt-submit-hook': 'Capture user requests and context',
    'tool-use-pre-hook': 'Log tool invocation start', 
    'tool-use-post-hook': 'Log tool results and performance',
    'thinking-chain-hook': 'Capture internal reasoning processes',
    'error-recovery-hook': 'Track error handling and recovery attempts',
    'agent-delegation-hook': 'Log multi-agent interactions',
    'session-start-hook': 'Initialize session tracking',
    'session-end-hook': 'Finalize session metrics'
}
```

#### 1.2 Hook Integration Points
- **Configuration Location**: `common/config/monitoring/claude_hooks_config.yml`
- **Hook Registry**: `common/monitoring/claude_hooks_registry.py`
- **Log Processors**: `common/monitoring/claude_log_processors.py`
- **Integration Layer**: `common/monitoring/claude_monitor_integration.py`

### 2. Data Capture Specifications

#### 2.1 Thinking Chain Capture
```json
{
  "hook_type": "thinking-chain",
  "timestamp": "2025-08-28T20:03:38.520600",
  "session_id": "session-uuid-12345",
  "correlation_id": "request-uuid-67890",
  "thinking_step": 1,
  "reasoning_type": "analysis|planning|decision|reflection",
  "content": "I need to analyze the user request and determine...",
  "confidence_level": 0.85,
  "duration_ms": 1245,
  "metadata": {
    "model_version": "claude-sonnet-4-20250514",
    "context_tokens": 15432,
    "reasoning_depth": 3
  }
}
```

#### 2.2 Tool Invocation Logs
```json
{
  "hook_type": "tool-invocation",
  "timestamp": "2025-08-28T20:03:39.120300",
  "session_id": "session-uuid-12345", 
  "correlation_id": "request-uuid-67890",
  "tool_name": "Read|Write|Edit|Bash|Task",
  "invocation_id": "tool-uuid-11111",
  "parameters": {
    "file_path": "/Users/SP14016/zitian/my_finance/example.py",
    "limit": 100
  },
  "execution_start": "2025-08-28T20:03:39.120300",
  "execution_end": "2025-08-28T20:03:39.145600", 
  "duration_ms": 25.3,
  "result_status": "success|failure|timeout",
  "result_size_bytes": 4567,
  "error_message": null,
  "retry_count": 0,
  "performance_metrics": {
    "cpu_usage_percent": 12.4,
    "memory_usage_mb": 45.2
  }
}
```

#### 2.3 Context Information
```json
{
  "hook_type": "context-snapshot", 
  "timestamp": "2025-08-28T20:03:38.520600",
  "session_id": "session-uuid-12345",
  "context_data": {
    "working_directory": "/Users/SP14016/zitian/my_finance",
    "git_branch": "main",
    "git_status": "?? common/config/monitoring/execution_logs_2025-08-28.json",
    "environment_variables": {
      "CLAUDECODE": "1",
      "ENV": "test",
      "CONDA_DEFAULT_ENV": "my_finance"
    },
    "pixi_environment": {
      "project_name": "my_finance",
      "project_version": "0.1.0"
    },
    "system_info": {
      "platform": "darwin",
      "os_version": "Darwin 24.3.0",
      "python_version": "3.12.11"
    }
  }
}
```

#### 2.4 Agent Interaction Tracking
```json
{
  "hook_type": "agent-delegation",
  "timestamp": "2025-08-28T20:03:40.200100", 
  "session_id": "session-uuid-12345",
  "correlation_id": "request-uuid-67890",
  "parent_agent": "agent-coordinator", 
  "target_agent": "infra-ops-agent",
  "delegation_type": "sequential|parallel|hybrid",
  "task_description": "Implement Claude Code hooks for logging",
  "delegation_start": "2025-08-28T20:03:40.200100",
  "delegation_end": "2025-08-28T20:03:45.567200",
  "delegation_status": "success|failure|timeout|in_progress",
  "response_data": {
    "files_modified": ["common/monitoring/claude_hooks.py"],
    "commands_executed": ["p3 e2e m7"],
    "artifacts_created": ["build_data/logs/agent_execution_trace.json"]
  }
}
```

### 3. Integration with Existing Infrastructure

#### 3.1 ExecutionMonitor Integration
- **Extend ExecutionLog**: Add Claude-specific fields to existing log structure
- **New Log Types**: Introduce `CLAUDE_THINKING`, `CLAUDE_TOOL_USE`, `CLAUDE_DELEGATION`
- **Correlation System**: Link Claude operations to existing agent execution tracking
- **Performance Metrics**: Merge Claude timings with existing performance monitoring

#### 3.2 DirectoryManager Integration 
- **Log Storage**: Use existing `build_data/logs/` structure via DirectoryManager
- **Configuration**: Store hook configs in `common/config/monitoring/`
- **SSOT Compliance**: Ensure all paths use centralized DirectoryManager system
- **Storage Backends**: Support local filesystem with future cloud storage compatibility

#### 3.3 Logger Integration
- **Unified Logging**: Route Claude logs through existing `common/logger.py` system
- **Job-based Organization**: Create Claude-specific job IDs for log organization
- **Log Levels**: Map Claude operations to appropriate log levels (DEBUG, INFO, WARN, ERROR)
- **Format Consistency**: Maintain existing log format with Claude-specific extensions

### 4. Configuration and Management

#### 4.1 Hook Configuration (`common/config/monitoring/claude_hooks_config.yml`)
```yaml
claude_hooks:
  enabled: true
  hooks:
    thinking_chain:
      enabled: true
      log_level: "DEBUG"
      capture_confidence: true
      max_content_length: 10000
    
    tool_invocation:
      enabled: true
      log_level: "INFO"  
      capture_parameters: true
      capture_results: true
      sanitize_sensitive: true
      
    context_tracking:
      enabled: true
      log_level: "INFO"
      capture_environment: true
      capture_git_state: true
      
    agent_delegation:
      enabled: true
      log_level: "INFO"
      track_performance: true
      capture_artifacts: true

  storage:
    location: "build_data/logs/claude_operations"
    format: "json"
    rotation: "daily"
    retention_days: 30
    
  streaming:
    enabled: true
    buffer_size: 1000
    flush_interval_seconds: 30
    
  performance:
    max_log_size_mb: 100
    compression: true
    async_processing: true

  sanitization:
    enabled: true
    patterns:
      - "password"
      - "api_key"
      - "secret"
      - "token"
    replacement: "[SANITIZED]"
```

#### 4.2 Hook Registry Implementation
```python
# common/monitoring/claude_hooks_registry.py
class ClaudeHooksRegistry:
    """Registry for Claude Code hooks with lifecycle management."""
    
    def register_hook(self, hook_type: str, handler: callable) -> None:
        """Register a hook handler."""
        
    def unregister_hook(self, hook_type: str) -> None:
        """Remove a hook handler."""
        
    def execute_hook(self, hook_type: str, data: dict) -> None:
        """Execute all handlers for a hook type."""
        
    def get_active_hooks(self) -> List[str]:
        """Get list of currently active hooks."""
```

### 5. Real-time Streaming and Batch Processing

#### 5.1 Streaming Architecture
- **Real-time Stream**: WebSocket or SSE connection for live monitoring
- **Buffer Management**: In-memory buffer with configurable size and flush intervals
- **Batch Processing**: Periodic batch writes to optimize disk I/O
- **Async Processing**: Non-blocking log processing to avoid performance impact

#### 5.2 Log Rotation and Retention
- **Daily Rotation**: New log files created daily following existing pattern
- **Size-based Limits**: Rotate files when they exceed configured size
- **Retention Policy**: Automatic cleanup of logs older than configured days
- **Compression**: Optional compression for archived logs

### 6. Data Sanitization and Security

#### 6.1 Sensitive Data Handling
- **Pattern Matching**: Configurable regex patterns for sensitive data detection
- **Automatic Sanitization**: Replace sensitive data with placeholder tokens
- **Opt-out Capability**: Allow specific tools/contexts to disable sanitization
- **Audit Trail**: Track what data was sanitized for debugging purposes

#### 6.2 Access Control
- **File Permissions**: Restrict log file access to authorized users/processes
- **Log Encryption**: Optional encryption for sensitive log data
- **Audit Logging**: Track access to log files and configuration changes

## 📋 Implementation Tasks

### Phase 1: Foundation (Week 1)
- [ ] **Task 1.1**: Create hook registry and configuration system
- [ ] **Task 1.2**: Extend ExecutionMonitor for Claude integration  
- [ ] **Task 1.3**: Implement basic thinking chain capture
- [ ] **Task 1.4**: Setup configuration at `common/config/monitoring/claude_hooks_config.yml`
- [ ] **Task 1.5**: Create unit tests for core hook functionality

### Phase 2: Tool Integration (Week 1-2)
- [ ] **Task 2.1**: Implement tool invocation pre/post hooks
- [ ] **Task 2.2**: Add parameter and result capture with sanitization
- [ ] **Task 2.3**: Integrate with existing DirectoryManager paths
- [ ] **Task 2.4**: Add performance metrics collection
- [ ] **Task 2.5**: Test integration with Read/Write/Edit/Bash tools

### Phase 3: Context and Agent Tracking (Week 2)  
- [ ] **Task 3.1**: Implement context snapshot capture
- [ ] **Task 3.2**: Add session and correlation ID tracking
- [ ] **Task 3.3**: Create agent delegation logging
- [ ] **Task 3.4**: Integrate with existing agent-coordinator workflows
- [ ] **Task 3.5**: Add git state and environment tracking

### Phase 4: Streaming and Performance (Week 2-3)
- [ ] **Task 4.1**: Implement real-time streaming capability
- [ ] **Task 4.2**: Add async processing and buffering
- [ ] **Task 4.3**: Create log rotation and retention system
- [ ] **Task 4.4**: Optimize performance impact on Claude operations
- [ ] **Task 4.5**: Add monitoring for hook system health

### Phase 5: Testing and Documentation (Week 3)
- [ ] **Task 5.1**: Comprehensive integration testing with existing systems
- [ ] **Task 5.2**: Performance impact assessment and optimization
- [ ] **Task 5.3**: Create configuration migration script for existing logs
- [ ] **Task 5.4**: End-to-end testing with multi-agent workflows
- [ ] **Task 5.5**: Update existing monitoring documentation

## 🧪 Testing Strategy

### Unit Testing
- **Hook Registry**: Test hook registration, execution, and lifecycle management
- **Log Processors**: Verify data formatting, sanitization, and storage
- **Configuration**: Test config loading, validation, and hot-reloading
- **Integration**: Test compatibility with existing ExecutionMonitor system

### Integration Testing  
- **Tool Chain**: Test hooks with all Claude Code tools (Read, Write, Edit, Bash, Task)
- **Agent Workflows**: Test multi-agent delegation tracking end-to-end
- **Performance**: Measure overhead impact on normal Claude operations
- **Storage**: Test integration with DirectoryManager and log rotation

### End-to-End Testing
- **Complete Workflows**: Test full request lifecycle from user input to completion
- **Error Scenarios**: Test hook behavior during errors and recovery
- **High Load**: Test system behavior under high logging volume
- **Multi-Session**: Test concurrent session handling and correlation

## 📊 Success Criteria

### Functional Requirements
- [ ] **Complete Coverage**: All Claude Code operations captured and logged
- [ ] **Structured Data**: All logs follow consistent JSON schema
- [ ] **Integration**: Seamless integration with existing ExecutionMonitor system
- [ ] **Performance**: <5% overhead impact on Claude operations
- [ ] **Reliability**: 99.9% hook execution success rate

### Non-Functional Requirements
- [ ] **Storage Efficiency**: Configurable log retention and compression
- [ ] **Real-time Capability**: Live streaming of log data for monitoring
- [ ] **Security**: Automatic sanitization of sensitive information
- [ ] **Maintainability**: Clear configuration and easy hook management
- [ ] **Observability**: Monitoring of the hook system itself

### Integration Requirements
- [ ] **SSOT Compliance**: All paths managed through DirectoryManager
- [ ] **P3 Workflow**: Compatible with existing p3 command system
- [ ] **Agent Ecosystem**: Supports current and future agent implementations
- [ ] **Cloud Ready**: Compatible with planned cloud storage backends

## 🔧 Configuration Examples

### Development Configuration
```yaml
# For development - verbose logging, shorter retention
claude_hooks:
  enabled: true
  hooks:
    thinking_chain:
      enabled: true
      log_level: "DEBUG"
      max_content_length: 50000
  storage:
    retention_days: 7
  performance:
    async_processing: false  # Synchronous for debugging
```

### Production Configuration
```yaml
# For production - optimized performance, longer retention
claude_hooks:
  enabled: true
  hooks:
    thinking_chain:
      enabled: false  # Disable verbose thinking logs in production
    tool_invocation:
      enabled: true
      log_level: "INFO"
      sanitize_sensitive: true
  storage:
    retention_days: 90
    compression: true
  performance:
    async_processing: true
    max_log_size_mb: 500
```

## 🔗 Dependencies

### Internal Dependencies
- **ExecutionMonitor** (`common/execution_monitor.py`): Core logging infrastructure
- **DirectoryManager** (`common/directory_manager.py`): Path management SSOT
- **Logger** (`common/logger.py`): Existing logging system
- **ConfigManager** (`common/config_manager.py`): Configuration management

### External Dependencies
- **Claude Code API**: Hook registration and event handling
- **JSON Processing**: For structured log formatting
- **Async IO**: For non-blocking log processing
- **File System**: For log storage and rotation

### Integration Points
- **P3 Command System**: Must work seamlessly with existing p3 workflows
- **Agent Ecosystem**: Compatible with all current and future agents
- **Monitoring Dashboard**: Potential future integration with monitoring UI
- **Cloud Storage**: Future compatibility with AWS S3, GCP GCS, Azure Blob

## 📈 Metrics and Monitoring

### Key Performance Indicators
- **Hook Execution Time**: Average time for hook processing
- **Log Volume**: Number of log entries per hour/day
- **Storage Usage**: Disk space consumed by Claude logs
- **Error Rate**: Percentage of failed hook executions
- **Integration Health**: Success rate of ExecutionMonitor integration

### Alerts and Thresholds
- **High Error Rate**: >1% hook execution failures
- **Storage Growth**: Log storage growth >10GB/day
- **Performance Impact**: Claude operation overhead >5%
- **System Health**: Hook system availability <99.9%

## 🚀 Future Enhancements

### Short Term (Next Quarter)
- **Dashboard Integration**: Visual monitoring of Claude operations
- **Advanced Analytics**: Pattern recognition in thinking chains
- **Custom Hook Types**: User-defined hooks for specific use cases
- **Export Capabilities**: Integration with external monitoring systems

### Medium Term (6 Months)
- **Machine Learning**: Predictive analysis of operation patterns
- **Cloud Storage**: Full integration with cloud storage backends
- **Distributed Tracing**: Cross-system request tracing
- **Performance Optimization**: Advanced caching and processing optimization

### Long Term (1 Year)
- **Multi-Instance**: Support for multiple Claude instances
- **Federation**: Cross-deployment log aggregation
- **Advanced Security**: End-to-end encryption and zero-trust architecture
- **AI-Powered Insights**: Automated analysis and recommendations

---

**Estimated Timeline**: 3 weeks  
**Effort Level**: High  
**Risk Level**: Medium  
**Business Impact**: High  

This implementation will provide comprehensive visibility into Claude Code operations, enhance debugging capabilities, improve system monitoring, and establish a foundation for advanced analytics and optimization of our AI-powered development workflow.