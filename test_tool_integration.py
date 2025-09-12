#!/usr/bin/env python3
"""Quick test of Issue #256 tool integration"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tool_integration():
    print("Testing Issue #256 Tool Integration...")
    
    try:
        # Test 1: Import from directory_manager
        from common.core.directory_manager import (
            get_tool_build_path,
            list_available_tools,
            validate_tool_structure,
        )
        print("✅ DirectoryManager tool methods imported")
        
        # Test 2: Import from common module
        from common import (
            get_tool_build_path as common_get_tool_path,
            list_available_tools as common_list_tools,
            validate_tool_structure as common_validate_tool,
        )
        print("✅ Common module tool methods imported")
        
        # Test 3: Check tool discovery
        tools = list_available_tools()
        print(f"✅ Found tools: {tools}")
        
        if tools:
            # Test 4: Path generation
            test_tool = tools[0]
            path1 = get_tool_build_path(test_tool, "20250912_143000")
            path2 = common_get_tool_path(test_tool, "20250912_143000")
            
            print(f"✅ DirectoryManager path: {path1}")
            print(f"✅ Common module path: {path2}")
            
            if path1 == path2:
                print("✅ Path consistency verified")
            else:
                print("❌ Path inconsistency!")
                return False
            
            # Test 5: Validation
            is_valid = validate_tool_structure(test_tool)
            print(f"✅ Tool '{test_tool}' validation: {is_valid}")
        
        print("\n🎉 Tool integration test: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ Tool integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tool_integration()
    sys.exit(0 if success else 1)