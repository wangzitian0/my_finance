#!/usr/bin/env python3
"""
Issue #256 Implementation Validation Script

Validates the L1/L2 directory structure implementation and tool path mapping system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("Issue #256: L1/L2 Directory Structure Implementation Validation")
    print("=" * 65)
    
    # Test 1: Validate core L1/L2 structure exists
    print("\n1. Testing L1/L2 Directory Structure...")
    
    l1_l2_structure = {
        'core': ['etl', 'analysis', 'knowledge'],
        'common': ['tools'],  # Focus on tools for this test
    }
    
    l1_missing = []
    l2_missing = []
    
    for l1_dir, l2_dirs in l1_l2_structure.items():
        l1_path = project_root / l1_dir
        l1_init = l1_path / '__init__.py'
        
        if not l1_path.exists():
            l1_missing.append(l1_dir)
            print(f"  ❌ L1 directory missing: {l1_dir}")
        elif not l1_init.exists():
            l1_missing.append(f"{l1_dir}/__init__.py")
            print(f"  ❌ L1 __init__.py missing: {l1_dir}")
        else:
            print(f"  ✅ L1 directory valid: {l1_dir}")
            
        # Check L2 directories
        for l2_dir in l2_dirs:
            l2_path = l1_path / l2_dir
            l2_init = l2_path / '__init__.py'
            
            if not l2_path.exists():
                l2_missing.append(f"{l1_dir}/{l2_dir}")
                print(f"    ❌ L2 directory missing: {l1_dir}/{l2_dir}")
            elif not l2_init.exists():
                l2_missing.append(f"{l1_dir}/{l2_dir}/__init__.py")
                print(f"    ❌ L2 __init__.py missing: {l1_dir}/{l2_dir}")
            else:
                print(f"    ✅ L2 directory valid: {l1_dir}/{l2_dir}")
    
    # Test 2: Test DirectoryManager tool methods
    print("\n2. Testing DirectoryManager Tool Path Mapping...")
    
    try:
        # Test imports
        from common.core.directory_manager import (
            get_tool_build_path,
            list_available_tools, 
            validate_tool_structure,
            register_tool
        )
        print("  ✅ Tool path mapping functions imported successfully")
        
        # Test tool discovery
        available_tools = list_available_tools()
        print(f"  ✅ Found {len(available_tools)} tools: {available_tools}")
        
        # Test path generation
        if available_tools:
            test_tool = available_tools[0]
            test_path = get_tool_build_path(test_tool, "20250912_143000")
            print(f"  ✅ Tool path generation works: {test_path}")
            
            # Test validation
            is_valid = validate_tool_structure(test_tool)
            print(f"  ✅ Tool validation works: {test_tool} -> {is_valid}")
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Tool methods error: {e}")
        return False
    
    # Test 3: Test common module exports
    print("\n3. Testing Common Module Tool Exports...")
    
    try:
        from common import (
            get_tool_build_path,
            list_available_tools,
            validate_tool_structure,
            register_tool,
        )
        print("  ✅ Tool functions exported from common module")
        
        # Quick functionality test
        tools = list_available_tools()
        if tools:
            path = get_tool_build_path(tools[0])
            print(f"  ✅ Tool path from common module: {path}")
        
    except ImportError as e:
        print(f"  ❌ Common module import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Common module error: {e}")
        return False
    
    # Test 4: Validate existing tool structures
    print("\n4. Validating Existing Tool Structures...")
    
    expected_tools = ['sec_filing_processor', 'dcf_calculator', 'graph_rag_indexer']
    
    for tool_name in expected_tools:
        tool_path = project_root / 'common' / 'tools' / tool_name
        init_file = tool_path / '__init__.py'
        
        if tool_path.exists() and init_file.exists():
            print(f"  ✅ Tool structure exists: {tool_name}")
        else:
            print(f"  ⚠️  Tool structure incomplete: {tool_name}")
    
    # Summary
    print("\n" + "=" * 65)
    print("IMPLEMENTATION SUMMARY:")
    
    structure_complete = len(l1_missing) == 0 and len(l2_missing) == 0
    tools_working = len(available_tools) > 0
    
    if structure_complete and tools_working:
        print("✅ Issue #256 L1/L2 Directory Structure Implementation: COMPLETE")
        print("✅ Tool Path Mapping System: FUNCTIONAL")
        print("✅ Common Module Integration: SUCCESS")
        return True
    else:
        print("⚠️  Implementation Status: PARTIAL")
        if l1_missing or l2_missing:
            print(f"   - Missing directories: {len(l1_missing + l2_missing)}")
        if not tools_working:
            print("   - Tool system needs attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)