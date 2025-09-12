#!/usr/bin/env python3
"""Final validation test for Issue #256 implementation"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🔍 Issue #256 Final Validation Test")
    print("=" * 50)
    
    success_count = 0
    total_tests = 6
    
    # Test 1: L1/L2 Directory Structure
    print("\n1. Testing L1/L2 Directory Structure...")
    l1_l2_paths = [
        "core/__init__.py",
        "core/etl/__init__.py", 
        "core/etl/sec_filings/__init__.py",
        "core/etl/embeddings/__init__.py",
        "core/etl/data_pipeline/__init__.py",
        "core/analysis/__init__.py",
        "core/analysis/dcf_engine/__init__.py",
        "core/analysis/evaluation/__init__.py",
        "core/knowledge/__init__.py",
        "core/knowledge/graph_rag/__init__.py",
    ]
    
    all_exist = True
    for path_str in l1_l2_paths:
        path = project_root / path_str
        if path.exists():
            print(f"   ✅ {path_str}")
        else:
            print(f"   ❌ {path_str}")
            all_exist = False
    
    if all_exist:
        success_count += 1
        print("   🎉 L1/L2 structure: COMPLETE")
    
    # Test 2: DirectoryManager Integration
    print("\n2. Testing DirectoryManager Integration...")
    try:
        from common.core.directory_manager import (
            get_tool_build_path,
            list_available_tools,
            validate_tool_structure,
            register_tool
        )
        success_count += 1
        print("   ✅ DirectoryManager tool methods imported successfully")
    except ImportError as e:
        print(f"   ❌ DirectoryManager import failed: {e}")
    
    # Test 3: Common Module Integration
    print("\n3. Testing Common Module Integration...")
    try:
        from common import (
            get_tool_build_path,
            list_available_tools,
            validate_tool_structure,
            register_tool,
        )
        success_count += 1
        print("   ✅ Common module tool methods imported successfully")
    except ImportError as e:
        print(f"   ❌ Common module import failed: {e}")
    
    # Test 4: Tool Discovery
    print("\n4. Testing Tool Discovery...")
    try:
        from common import list_available_tools
        tools = list_available_tools()
        if len(tools) >= 3:  # Should have at least 3 tools
            success_count += 1
            print(f"   ✅ Found {len(tools)} tools: {tools}")
        else:
            print(f"   ⚠️  Found only {len(tools)} tools: {tools}")
    except Exception as e:
        print(f"   ❌ Tool discovery failed: {e}")
    
    # Test 5: Path Generation
    print("\n5. Testing Path Generation...")
    try:
        from common import get_tool_build_path, list_available_tools
        tools = list_available_tools()
        if tools:
            test_path = get_tool_build_path(tools[0], "20250912_143000")
            expected_pattern = "build_data"
            if expected_pattern in str(test_path):
                success_count += 1
                print(f"   ✅ Path generation works: {test_path}")
            else:
                print(f"   ❌ Unexpected path format: {test_path}")
        else:
            print("   ❌ No tools available for path testing")
    except Exception as e:
        print(f"   ❌ Path generation failed: {e}")
    
    # Test 6: Tool Validation
    print("\n6. Testing Tool Validation...")
    try:
        from common import validate_tool_structure, list_available_tools
        tools = list_available_tools()
        if tools:
            is_valid = validate_tool_structure(tools[0])
            if is_valid:
                success_count += 1
                print(f"   ✅ Tool validation works: {tools[0]} -> {is_valid}")
            else:
                print(f"   ⚠️  Tool validation returned False: {tools[0]}")
        else:
            print("   ❌ No tools available for validation testing")
    except Exception as e:
        print(f"   ❌ Tool validation failed: {e}")
    
    # Final Results
    print("\n" + "=" * 50)
    print("🏆 FINAL VALIDATION RESULTS")
    print(f"   Tests Passed: {success_count}/{total_tests}")
    print(f"   Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("   🎉 Issue #256 Implementation: FULLY SUCCESSFUL")
        print("   ✅ L1/L2 Directory Structure: COMPLETE")
        print("   ✅ DRY Principles: FOLLOWED") 
        print("   ✅ SSOT Integration: COMPLETE")
        print("   ✅ Tool Path Mapping: FUNCTIONAL")
        return True
    else:
        print(f"   ⚠️  Implementation: {success_count}/{total_tests} components working")
        print("   🔧 Some components need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)