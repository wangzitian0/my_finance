#!/usr/bin/env python3
"""
Demonstration of Claude Code hooks in action

This script shows how the Claude hooks would be used in a real scenario
to capture user interactions, tool usage, and AI responses.

Usage:
    python demo_claude_hooks.py

GitHub Issue #214: Implement Claude Code hooks for comprehensive logging integration
"""

import sys
import time
from pathlib import Path

# Add common directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from monitoring.claude_hook_manager import get_hook_manager


def simulate_claude_interaction():
    """Simulate a typical Claude Code interaction."""
    
    print("🎬 Claude Code Interaction Demo")
    print("=" * 40)
    
    # Get hook manager
    hook_manager = get_hook_manager()
    
    # 1. Start a new session (would typically be done at Claude startup)
    print("\n1. Starting Claude session...")
    session_id = hook_manager.start_session({
        "user": "demo_user",
        "interface": "claude_code",
        "version": "1.0.0"
    })
    print(f"   Session ID: {session_id}")
    
    # 2. User submits a prompt
    print("\n2. User submits prompt...")
    user_prompt = """
    Analyze the financial data for AAPL and create a DCF valuation model.
    Use the SEC filings from the last 3 years and include sensitivity analysis.
    My API key is sk-secret123 for the data source.
    """
    
    prompt_event = hook_manager.capture_user_prompt(
        user_prompt.strip(),
        {
            "timestamp": time.time(),
            "interface": "web",
            "user_id": "demo_user"
        }
    )
    print(f"   Prompt captured: {prompt_event}")
    print(f"   Original length: {len(user_prompt.strip())} chars")
    
    # 3. Claude thinks and calls tools
    print("\n3. AI thinking and tool invocation...")
    
    # Simulate thinking process
    thinking = """
    I need to analyze AAPL's financial data for DCF valuation. Let me:
    1. First read the SEC filings to get historical financials
    2. Extract key metrics like revenue, FCF, growth rates
    3. Build the DCF model with multiple scenarios
    4. Run sensitivity analysis on key assumptions
    """
    
    # Simulate tool call to read SEC data
    tool_start_time = time.time()
    
    tool_event = hook_manager.capture_tool_invocation(
        tool_name="Read",
        parameters={
            "file_path": "/Users/SP14016/zitian/my_finance/build_data/stage_00_raw/sec-edgar/AAPL/10-K-2023.json",
            "limit": 1000
        }
    )
    
    # Simulate tool execution time
    time.sleep(0.1)  # Simulate processing time
    execution_time = int((time.time() - tool_start_time) * 1000)
    
    # Update tool event with response
    tool_response = {
        "content_length": 45678,
        "sections_found": ["business", "risk_factors", "financial_statements"],
        "revenue_2023": 383285000000,
        "status": "success"
    }
    
    hook_manager.capture_tool_invocation(
        tool_name="Read",
        parameters={
            "file_path": "/Users/SP14016/zitian/my_finance/build_data/stage_00_raw/sec-edgar/AAPL/10-K-2023.json"
        },
        response=tool_response,
        execution_time_ms=execution_time,
        success=True
    )
    
    print(f"   Tool invocation captured: {tool_event}")
    print(f"   Execution time: {execution_time}ms")
    
    # 4. AI provides response
    print("\n4. AI generates response...")
    
    final_response = """
    # DCF Valuation Analysis for Apple Inc. (AAPL)
    
    Based on the SEC filings analysis, here's the comprehensive DCF model:
    
    ## Historical Performance (2021-2023)
    - Revenue CAGR: 8.2%
    - Free Cash Flow: $99.6B (2023)
    - ROIC: 29.3%
    
    ## DCF Model Results
    - Base Case Fair Value: $195.50 per share
    - Bull Case: $245.30 per share  
    - Bear Case: $145.20 per share
    
    ## Sensitivity Analysis
    The valuation is most sensitive to:
    1. Revenue growth assumptions (±15% impact)
    2. Terminal growth rate (±12% impact)
    3. WACC assumptions (±10% impact)
    
    **Investment Recommendation**: BUY
    Current price offers attractive risk-adjusted returns.
    """
    
    generation_time = 1500  # Simulate 1.5 second generation
    
    response_event = hook_manager.capture_ai_response(
        final_response.strip(),
        thinking.strip(),
        generation_time
    )
    
    print(f"   Response captured: {response_event}")
    print(f"   Response length: {len(final_response.strip())} chars")
    print(f"   Generation time: {generation_time}ms")
    
    # 5. Simulate an error during processing
    print("\n5. Simulating error handling...")
    
    try:
        # Simulate an error
        raise ValueError("Failed to connect to SEC EDGAR database")
    except Exception as e:
        import traceback
        
        error_event = hook_manager.capture_error(
            error_type=type(e).__name__,
            error_message=str(e),
            stack_trace=traceback.format_exc(),
            context={
                "operation": "sec_edgar_fetch",
                "symbol": "AAPL",
                "retry_count": 0
            },
            recovery_action="Fallback to cached data",
            recovery_successful=True
        )
        
        print(f"   Error captured: {error_event}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Recovery: Successful")
    
    # 6. Session statistics
    print("\n6. Session statistics...")
    stats = hook_manager.get_session_stats()
    print(f"   Events captured: {stats['total_stats']['events_captured']}")
    print(f"   Events sanitized: {stats['total_stats']['events_sanitized']}")
    print(f"   Errors logged: {stats['total_stats']['errors_logged']}")
    
    # 7. End session
    print("\n7. Ending session...")
    hook_manager.end_session()
    print(f"   Session {session_id} ended")
    
    # 8. Show hook status
    print("\n8. System status...")
    status = hook_manager.get_hook_status()
    print(f"   Hooks enabled: {status['enabled']}")
    print(f"   Config version: {status['config_version']}")
    print(f"   Storage backend: {status['storage_backend']}")
    print(f"   Logs directory: {status['logs_directory']}")
    
    print("\n" + "=" * 40)
    print("✅ Demo completed successfully!")
    print(f"📁 Check logs at: {status['logs_directory']}/claude_hooks_*.json")


if __name__ == "__main__":
    simulate_claude_interaction()