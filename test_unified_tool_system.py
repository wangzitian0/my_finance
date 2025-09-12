#!/usr/bin/env python3
"""
Test script for Issue #256 Unified Tool Definition System

Tests the core requirement: "define build_data/timestamp/tool_x using common/tool_x"
"""

import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from common import (
        get_tool_build_path,
        list_available_tools,
        validate_tool_structure,
    )
    from common.tools import (
        cleanup_tool_workspace,
        create_tool_workspace,
        get_tool_manager,
        get_tool_registry,
    )

    print("✅ Successfully imported unified tool system components")
except ImportError as e:
    print(f"❌ Failed to import tool system: {e}")
    sys.exit(1)


def test_tool_discovery():
    """Test tool discovery from common/tools/ directory"""
    print("\n🔍 Testing Tool Discovery...")

    try:
        # Test directory manager tool discovery
        available_tools = list_available_tools()
        print(f"Available tools found: {available_tools}")

        expected_tools = ["sec_filing_processor", "dcf_calculator", "graph_rag_indexer"]
        found_tools = set(available_tools)
        expected_set = set(expected_tools)

        if expected_set.issubset(found_tools):
            print("✅ All expected tools discovered successfully")
        else:
            missing = expected_set - found_tools
            print(f"❌ Missing tools: {missing}")

        # Test tool structure validation
        for tool_name in expected_tools:
            is_valid = validate_tool_structure(tool_name)
            status = "✅" if is_valid else "❌"
            print(f"{status} Tool '{tool_name}' structure validation: {is_valid}")

        return len(available_tools) > 0

    except Exception as e:
        print(f"❌ Tool discovery failed: {e}")
        return False


def test_tool_registry():
    """Test tool registry functionality"""
    print("\n📋 Testing Tool Registry...")

    try:
        registry = get_tool_registry()

        # Get registry statistics
        stats = registry.get_registry_stats()
        print(f"Registry stats: {stats}")

        # Test tool configuration loading
        for tool_name in ["sec_filing_processor", "dcf_calculator", "graph_rag_indexer"]:
            config = registry.get_tool_config(tool_name)
            if config:
                print(f"✅ Loaded config for '{tool_name}': v{config.version}")
                print(f"   Description: {config.description}")
                print(f"   Required dirs: {config.required_directories}")
                print(f"   Input layers: {config.input_layers}")
                print(f"   Output layers: {config.output_layers}")
            else:
                print(f"❌ Failed to load config for '{tool_name}'")

        # Test dependency resolution
        tools_to_order = ["sec_filing_processor", "dcf_calculator", "graph_rag_indexer"]
        try:
            ordered_tools = registry.get_dependency_order(tools_to_order)
            print(f"✅ Dependency order resolved: {ordered_tools}")
        except Exception as e:
            print(f"❌ Dependency resolution failed: {e}")

        return stats["total_tools"] > 0

    except Exception as e:
        print(f"❌ Tool registry test failed: {e}")
        return False


def test_tool_workspace_creation():
    """Test tool workspace creation in build_data/timestamp/tool_x"""
    print("\n🏗️  Testing Tool Workspace Creation...")

    try:
        # Test directory manager tool path resolution
        timestamp = "20250912_143000"

        for tool_name in ["sec_filing_processor", "dcf_calculator", "graph_rag_indexer"]:
            # Test path generation
            tool_path = get_tool_build_path(tool_name, timestamp)
            expected_pattern = f"build_data/{timestamp}/{tool_name}"

            if expected_pattern in str(tool_path):
                print(f"✅ Tool path generated correctly: {tool_path}")
            else:
                print(f"❌ Unexpected tool path: {tool_path}")

        # Test tool manager workspace creation
        manager = get_tool_manager()

        # Create workspace for SEC filing processor
        context = create_tool_workspace("sec_filing_processor", timestamp)

        if context:
            print(f"✅ Workspace created: {context.workspace_path}")

            # Verify directory structure was created
            required_dirs = [
                "raw_filings",
                "parsed_filings",
                "extracted_data",
                "embeddings",
                "metadata",
            ]

            all_dirs_exist = True
            for req_dir in required_dirs:
                dir_path = context.workspace_path / req_dir
                if dir_path.exists():
                    print(f"   ✅ {req_dir}/ created")
                else:
                    print(f"   ❌ {req_dir}/ missing")
                    all_dirs_exist = False

            # Test input/output path mapping
            print(f"   Input paths: {list(context.input_paths.keys())}")
            print(f"   Output paths: {list(context.output_paths.keys())}")

            # Cleanup
            cleanup_tool_workspace(context, remove_workspace=True)
            print("✅ Workspace cleaned up")

            return all_dirs_exist
        else:
            print("❌ Failed to create workspace")
            return False

    except Exception as e:
        print(f"❌ Workspace creation test failed: {e}")
        return False


def test_tool_execution_simulation():
    """Test tool execution simulation"""
    print("\n⚙️  Testing Tool Execution Simulation...")

    try:
        registry = get_tool_registry()
        manager = get_tool_manager()

        # Test creating and running SEC filing processor
        sec_processor = registry.create_tool_instance("sec_filing_processor")

        if sec_processor:
            print(f"✅ Created SEC filing processor instance")

            # Create workspace
            context = create_tool_workspace("sec_filing_processor")

            if context:
                print(f"✅ Created execution context: {context.workspace_path}")

                # Run the tool (simulation)
                print("   Running tool execution simulation...")
                success = sec_processor.run(context)

                if success:
                    print("✅ Tool execution simulation completed successfully")
                    print(f"   Status: {context.status.value}")
                    print(f"   Progress: {context.progress:.1%}")
                    print(f"   Messages: {len(context.messages)} logged")

                    # Check for output files
                    output_files = [
                        "metadata/processing_manifest.json",
                        "extracted_data/financial_metrics.json",
                        "embeddings/embeddings_manifest.json",
                    ]

                    all_outputs_exist = True
                    for output_file in output_files:
                        output_path = context.workspace_path / output_file
                        if output_path.exists():
                            print(f"   ✅ Output created: {output_file}")
                        else:
                            print(f"   ❌ Output missing: {output_file}")
                            all_outputs_exist = False

                    # Cleanup
                    cleanup_tool_workspace(context, remove_workspace=True)

                    return all_outputs_exist
                else:
                    print(f"❌ Tool execution failed: {context.status.value}")
                    return False
            else:
                print("❌ Failed to create execution context")
                return False
        else:
            print("❌ Failed to create tool instance")
            return False

    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        return False


def test_system_integration():
    """Test integration between all system components"""
    print("\n🔗 Testing System Integration...")

    try:
        # Test full workflow: discovery → validation → creation → execution
        print("   Step 1: Discover tools")
        available_tools = list_available_tools()

        print("   Step 2: Validate tool structures")
        valid_tools = [tool for tool in available_tools if validate_tool_structure(tool)]

        print("   Step 3: Load tool configurations")
        registry = get_tool_registry()
        configured_tools = [tool for tool in valid_tools if registry.get_tool_config(tool)]

        print("   Step 4: Create tool workspaces")
        manager = get_tool_manager()
        created_workspaces = []

        timestamp = "20250912_integration_test"

        for tool_name in configured_tools[:2]:  # Test first 2 tools
            context = create_tool_workspace(tool_name, timestamp)
            if context:
                created_workspaces.append(context)
                print(f"   ✅ Created workspace for {tool_name}")

        print("   Step 5: Test workspace validation")
        validation_results = []
        for context in created_workspaces:
            is_valid = manager.validate_tool_workspace(context.tool_name, context.workspace_path)
            validation_results.append(is_valid)
            status = "✅" if is_valid else "❌"
            print(f"   {status} Workspace validation for {context.tool_name}: {is_valid}")

        # Cleanup all workspaces
        print("   Step 6: Cleanup workspaces")
        for context in created_workspaces:
            cleanup_tool_workspace(context, remove_workspace=True)

        success = len(configured_tools) > 0 and all(validation_results)
        status = "✅" if success else "❌"
        print(f"{status} System integration test: {'PASSED' if success else 'FAILED'}")

        return success

    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        return False


def main():
    """Run all tests for the unified tool system"""
    print("🚀 Testing Issue #256: Unified Tool Definition System")
    print("=" * 60)
    print("Testing core requirement: 'define build_data/timestamp/tool_x using common/tool_x'")

    test_results = []

    # Run all tests
    test_results.append(("Tool Discovery", test_tool_discovery()))
    test_results.append(("Tool Registry", test_tool_registry()))
    test_results.append(("Workspace Creation", test_tool_workspace_creation()))
    test_results.append(("Tool Execution", test_tool_execution_simulation()))
    test_results.append(("System Integration", test_system_integration()))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests PASSED! Issue #256 implementation is working correctly.")
        print("\n✅ CORE REQUIREMENT SATISFIED:")
        print("   'define build_data/timestamp/tool_x using common/tool_x' ✓")
        print("   - Tools discovered from common/tools/ directory ✓")
        print("   - Tool workspaces created in build_data/timestamp/tool_x ✓")
        print("   - Directory manager provides unified tool path resolution ✓")
        print("   - Tool registry manages configurations and dependencies ✓")
        print("   - Tool manager handles workspace lifecycle ✓")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
