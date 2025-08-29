#!/usr/bin/env python3
"""
Sub-agent Hook - Captures Task() calls and sub-agent executions
"""
import json
import sys
from datetime import datetime

def main():
    """Hook that captures sub-agent calls."""
    if len(sys.argv) < 2:
        return
    
    # Parse hook data
    hook_data = json.loads(sys.argv[1])
    
    # Extract sub-agent info
    subagent_type = hook_data.get('subagent_type', 'unknown')
    description = hook_data.get('description', '')
    prompt = hook_data.get('prompt', '')[:200]  # Truncate
    
    # Create log entry
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': 'subagent_call',
        'subagent_type': subagent_type,
        'description': description,
        'prompt_preview': prompt,
        'status': 'started'
    }
    
    # Send to glue layer
    print(json.dumps(log_entry))

if __name__ == '__main__':
    main()