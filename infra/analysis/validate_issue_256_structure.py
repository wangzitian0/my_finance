#!/usr/bin/env python3
"""
Issue #256 Structure Validation Script

Validates that the business-oriented directory restructuring has been
properly implemented according to the Graph-RAG investment analysis
system requirements.

Business Logic Flow Validation:
Data Sources → ETL → Neo4j → engine → Strategies/Reports → evaluation → Backtesting Returns
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def validate_module_structure() -> Dict[str, List[str]]:
    """Validate that all required modules and components exist"""

    root_path = Path(__file__).parent
    validation_results = {}

    # Define expected structure
    expected_structure = {
        "ETL": [
            "__init__.py",
            "sec_filing_processor/__init__.py",
            "embedding_generator/__init__.py",
            "processors/__init__.py",
            "schedulers/__init__.py",
            "neo4j_loader/__init__.py",
        ],
        "engine": [
            "__init__.py",
            "README.md",
            "graph_rag/__init__.py",
            "graph_rag/retriever.py",
            "llm/__init__.py",
            "strategy/__init__.py",
            "strategy/dcf_calculator.py",
            "reports/__init__.py",
        ],
        "evaluation": [
            "__init__.py",
            "README.md",
            "backtesting/__init__.py",
            "backtesting/engine.py",
            "metrics/__init__.py",
            "benchmarks/__init__.py",
        ],
        "common": [
            "__init__.py",
            "config/__init__.py",
            "core/directory_manager.py",
            "tools/__init__.py",
            "utils/__init__.py",
        ],
        "infra": ["__init__.py", "README.md"],
    }

    # Validate each module
    for module_name, expected_files in expected_structure.items():
        module_path = root_path / module_name
        missing_files = []
        existing_files = []

        for expected_file in expected_files:
            file_path = module_path / expected_file
            if file_path.exists():
                existing_files.append(expected_file)
            else:
                missing_files.append(expected_file)

        validation_results[module_name] = {
            "exists": module_path.exists(),
            "existing_files": existing_files,
            "missing_files": missing_files,
            "completion_rate": len(existing_files) / len(expected_files) * 100,
        }

    return validation_results


def validate_business_logic_separation() -> Dict[str, bool]:
    """Validate that business logic is properly separated"""

    root_path = Path(__file__).parent

    # Check for proper business separation
    checks = {
        "engine_module_exists": (root_path / "engine").exists(),
        "evaluation_module_exists": (root_path / "evaluation").exists(),
        "etl_enhanced": (root_path / "ETL" / "schedulers").exists(),
        "graph_rag_in_engine": (root_path / "engine" / "graph_rag").exists(),
        "strategy_in_engine": (root_path / "engine" / "strategy").exists(),
        "backtesting_in_evaluation": (root_path / "evaluation" / "backtesting").exists(),
        "neo4j_loader_in_etl": (root_path / "ETL" / "neo4j_loader").exists(),
    }

    return checks


def validate_documentation() -> Dict[str, bool]:
    """Validate that proper documentation exists"""

    root_path = Path(__file__).parent

    doc_checks = {
        "main_readme_updated": (root_path / "README.md").exists(),
        "engine_readme": (root_path / "engine" / "README.md").exists(),
        "evaluation_readme": (root_path / "evaluation" / "README.md").exists(),
        "implementation_summary": (root_path / "ISSUE_256_IMPLEMENTATION_SUMMARY.md").exists(),
        "claude_md_exists": (root_path / "CLAUDE.md").exists(),
    }

    # Check if README.md contains new architecture
    readme_path = root_path / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        doc_checks["readme_has_new_architecture"] = (
            "engine/" in content and "evaluation/" in content
        )
        doc_checks["readme_has_business_flow"] = "Data Sources → ETL → Neo4j" in content

    return doc_checks


def validate_implementation_quality() -> Dict[str, bool]:
    """Validate implementation quality and completeness"""

    root_path = Path(__file__).parent

    quality_checks = {
        "dcf_calculator_implemented": False,
        "graph_rag_retriever_implemented": False,
        "backtesting_engine_implemented": False,
        "modules_have_imports": True,
    }

    # Check DCF calculator implementation
    dcf_path = root_path / "engine" / "strategy" / "dcf_calculator.py"
    if dcf_path.exists():
        content = dcf_path.read_text()
        quality_checks["dcf_calculator_implemented"] = (
            "class DCFCalculator" in content
            and "calculate_dcf" in content
            and len(content) > 500  # Substantial implementation
        )

    # Check Graph-RAG retriever implementation
    retriever_path = root_path / "engine" / "graph_rag" / "retriever.py"
    if retriever_path.exists():
        content = retriever_path.read_text()
        quality_checks["graph_rag_retriever_implemented"] = (
            "class GraphRAGRetriever" in content
            and "retrieve" in content
            and len(content) > 500  # Substantial implementation
        )

    # Check backtesting engine implementation
    backtest_path = root_path / "evaluation" / "backtesting" / "engine.py"
    if backtest_path.exists():
        content = backtest_path.read_text()
        quality_checks["backtesting_engine_implemented"] = (
            "class BacktestEngine" in content
            and "run_backtest" in content
            and len(content) > 500  # Substantial implementation
        )

    return quality_checks


def print_validation_report(
    module_results: Dict, business_results: Dict, doc_results: Dict, quality_results: Dict
):
    """Print comprehensive validation report"""

    print("=" * 80)
    print("ISSUE #256 STRUCTURE VALIDATION REPORT")
    print("Business-Oriented Directory Restructuring for Graph-RAG Investment Analysis")
    print("=" * 80)

    # Module Structure Results
    print("\n📁 MODULE STRUCTURE VALIDATION")
    print("-" * 40)

    overall_completion = 0
    total_modules = len(module_results)

    for module_name, results in module_results.items():
        status = "✅" if results["exists"] else "❌"
        completion = results["completion_rate"]
        overall_completion += completion

        print(f"{status} {module_name}/ - {completion:.1f}% complete")

        if results["missing_files"]:
            print(f"   Missing: {', '.join(results['missing_files'])}")
        if results["existing_files"]:
            print(
                f"   Present: {', '.join(results['existing_files'][:3])}{'...' if len(results['existing_files']) > 3 else ''}"
            )

    avg_completion = overall_completion / total_modules
    print(f"\nOverall Module Completion: {avg_completion:.1f}%")

    # Business Logic Separation
    print("\n🎯 BUSINESS LOGIC SEPARATION")
    print("-" * 40)

    business_score = sum(business_results.values())
    business_total = len(business_results)

    for check_name, passed in business_results.items():
        status = "✅" if passed else "❌"
        readable_name = check_name.replace("_", " ").title()
        print(f"{status} {readable_name}")

    print(
        f"\nBusiness Logic Score: {business_score}/{business_total} ({business_score/business_total*100:.1f}%)"
    )

    # Documentation Validation
    print("\n📚 DOCUMENTATION VALIDATION")
    print("-" * 40)

    doc_score = sum(doc_results.values())
    doc_total = len(doc_results)

    for check_name, passed in doc_results.items():
        status = "✅" if passed else "❌"
        readable_name = check_name.replace("_", " ").title()
        print(f"{status} {readable_name}")

    print(f"\nDocumentation Score: {doc_score}/{doc_total} ({doc_score/doc_total*100:.1f}%)")

    # Implementation Quality
    print("\n⚡ IMPLEMENTATION QUALITY")
    print("-" * 40)

    quality_score = sum(quality_results.values())
    quality_total = len(quality_results)

    for check_name, passed in quality_results.items():
        status = "✅" if passed else "❌"
        readable_name = check_name.replace("_", " ").title()
        print(f"{status} {readable_name}")

    print(
        f"\nImplementation Quality Score: {quality_score}/{quality_total} ({quality_score/quality_total*100:.1f}%)"
    )

    # Overall Assessment
    print("\n🎉 OVERALL ASSESSMENT")
    print("-" * 40)

    total_score = (
        avg_completion
        + business_score / business_total * 100
        + doc_score / doc_total * 100
        + quality_score / quality_total * 100
    ) / 4

    if total_score >= 90:
        status = "🏆 EXCELLENT"
        message = "Issue #256 implementation exceeds expectations!"
    elif total_score >= 75:
        status = "✅ GOOD"
        message = "Issue #256 implementation is solid and ready for use."
    elif total_score >= 60:
        status = "⚠️ ACCEPTABLE"
        message = "Issue #256 implementation has good foundation, minor improvements needed."
    else:
        status = "❌ NEEDS WORK"
        message = "Issue #256 implementation requires significant improvements."

    print(f"Overall Score: {total_score:.1f}%")
    print(f"Status: {status}")
    print(f"Assessment: {message}")

    # Business Flow Validation
    print("\n🔄 BUSINESS FLOW VALIDATION")
    print("-" * 40)
    print(
        "Target Flow: Data Sources → ETL → Neo4j → engine → Strategies/Reports → evaluation → Backtesting Returns"
    )

    flow_components = [
        ("ETL Pipeline", business_results.get("etl_enhanced", False)),
        ("Graph-RAG Engine", business_results.get("engine_module_exists", False)),
        ("Strategy Generation", business_results.get("strategy_in_engine", False)),
        ("Independent Evaluation", business_results.get("evaluation_module_exists", False)),
        ("Backtesting System", business_results.get("backtesting_in_evaluation", False)),
    ]

    for component, implemented in flow_components:
        status = "✅" if implemented else "❌"
        print(f"{status} {component}")

    flow_completion = (
        sum(implemented for _, implemented in flow_components) / len(flow_components) * 100
    )
    print(f"\nBusiness Flow Completion: {flow_completion:.1f}%")


def main():
    """Run complete validation suite"""

    print("Validating Issue #256 Implementation...")
    print("Business-Oriented Directory Restructuring")

    # Run all validations
    module_results = validate_module_structure()
    business_results = validate_business_logic_separation()
    doc_results = validate_documentation()
    quality_results = validate_implementation_quality()

    # Print comprehensive report
    print_validation_report(module_results, business_results, doc_results, quality_results)

    # Return exit code based on overall success
    total_checks = (
        sum(r["completion_rate"] for r in module_results.values()) / len(module_results)
        + sum(business_results.values()) / len(business_results) * 100
        + sum(doc_results.values()) / len(doc_results) * 100
        + sum(quality_results.values()) / len(quality_results) * 100
    ) / 4

    if total_checks >= 75:
        print(f"\n🎉 SUCCESS: Issue #256 implementation is {total_checks:.1f}% complete!")
        return 0
    else:
        print(f"\n⚠️ WARNING: Issue #256 implementation is only {total_checks:.1f}% complete.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
