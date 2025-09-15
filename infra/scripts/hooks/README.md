# Claude Code Hooks

This directory contains hook scripts for comprehensive logging integration with Claude Code. These hooks capture user interactions, tool usage, AI responses, and errors for improved monitoring and debugging.

## Overview

The Claude Code hooks system provides comprehensive logging of all interactions to support:
- **Debugging**: Detailed logs of user prompts, tool calls, and AI responses
- **Performance Analysis**: Execution times, success rates, and error patterns
- **Quality Assurance**: Thinking process capture and response quality analysis
- **Security**: Data sanitization to prevent sensitive information logging

## Hook Scripts

### 1. user-prompt-submit-hook.py
Captures user prompt submissions with sanitization.

**Usage:**
```bash
python user-prompt-submit-hook.py --prompt "user prompt here" [--context context.json]
```

**Features:**
- Content sanitization for sensitive data
- Context preservation
- Session correlation
- Configurable truncation

### 2. tool-use-hook.py
Logs tool invocations and responses.

**Usage:**
```bash
# Start tool invocation tracking
python tool-use-hook.py --tool-name "Bash" --parameters '{"command": "ls -la"}' --phase start

# Complete tool invocation with response
python tool-use-hook.py --tool-name "Bash" --response '{"output": "files..."}' --phase complete --success true
```

**Features:**
- Pre/post execution tracking
- Response truncation
- Success/failure logging
- Execution time measurement

### 3. response-hook.py
Captures AI responses and thinking processes.

**Usage:**
```bash
python response-hook.py --response "AI response" [--thinking "thinking process"] [--generation-time 1500]
```

**Features:**
- Thinking chain capture
- Response quality metrics
- Generation time tracking
- Content truncation

### 4. error-hook.py
Logs errors with stack traces and recovery actions.

**Usage:**
```bash
python error-hook.py --error-type "ImportError" --error-message "Module not found" [--stack-trace-file trace.txt]
```

**Features:**
- Stack trace capture
- Error categorization
- Recovery action tracking
- Context preservation

## Configuration

Hook behavior is controlled by `/common/config/monitoring/claude_hooks.json`:

```json
{
  "version": "1.0.0",
  "enabled": true,
  "hooks": {
    "user_prompt_submit": {"enabled": true, "capture_level": "full", "sanitize": true},
    "tool_invocation": {"enabled": true, "capture_requests": true, "capture_responses": true},
    "ai_response": {"enabled": true, "capture_thinking": true, "capture_final": true},
    "error_handling": {"enabled": true, "capture_stack": true, "capture_recovery": true}
  },
  "sanitization": {
    "enabled": true,
    "patterns": ["password", "token", "key", "secret", "api_key"]
  }
}
```

## Environment Variables

- `CLAUDE_SESSION_ID`: Current Claude Code session ID for correlation
- `CLAUDE_USER_AGENT`: User agent information
- `CLAUDE_SOURCE`: Source of interaction (defaults to "claude_code")

## Integration

### With ClaudeHookManager
All hooks integrate with the centralized `ClaudeHookManager` which:
- Manages session correlation
- Handles data sanitization
- Integrates with ExecutionMonitor
- Follows SSOT directory principles

### Log Storage
Logs are stored at `build_data/logs/claude_hooks/` following the established directory structure:
- Daily log files: `claude_hooks_YYYY-MM-DD.json`
- Manager logs: `claude_hook_manager.log`
- Integration with ExecutionMonitor logs

## Security

### Data Sanitization
All hooks implement comprehensive data sanitization:
- **Pattern Matching**: Removes common sensitive patterns (passwords, tokens, keys)
- **Regex Filters**: Advanced pattern matching for API keys and secrets
- **Configurable**: Patterns and replacement text can be configured
- **Recursive**: Sanitizes nested data structures

### Privacy Protection
- Sensitive environment variables are filtered
- File paths are sanitized where appropriate
- User-specific information is anonymized when possible

## Performance

### Optimization Features
- **Async Processing**: Non-blocking hook execution
- **Batch Processing**: Events batched for efficient storage
- **Compression**: Log compression for storage efficiency
- **Configurable Limits**: Response and thinking process truncation

### Resource Management
- Memory usage monitoring
- File size limits
- Automatic log rotation
- Retention policies

## Testing

### Unit Tests
```bash
# Test individual hooks
python -m pytest tests/test_claude_hooks.py

# Test hook manager
python -m pytest tests/test_hook_manager.py
```

### Integration Tests
```bash
# Test full hook pipeline
python scripts/test_hooks_integration.py
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure hook scripts are executable
2. **Import Errors**: Verify Python path includes common directory
3. **Session Not Found**: Check CLAUDE_SESSION_ID environment variable
4. **Configuration Issues**: Validate claude_hooks.json syntax

### Debug Mode
Enable verbose output with `-v` flag:
```bash
python user-prompt-submit-hook.py --prompt "test" -v
```

### Log Analysis
Check hook manager logs:
```bash
tail -f build_data/logs/claude_hooks/claude_hook_manager.log
```

## Related Files

- `/common/monitoring/claude_hook_manager.py` - Core hook management system
- `/common/config/monitoring/claude_hooks.json` - Configuration file
- `/common/execution_monitor.py` - Integrated monitoring system
- `/common/directory_manager.py` - SSOT directory management

## GitHub Issue

This implementation addresses [Issue #214: Implement Claude Code hooks for comprehensive logging integration](https://github.com/wangzitian0/my_finance/issues/214)