#!/usr/bin/env python3
"""
HRBP Comprehensive CLI Interface

Enhanced command-line interface for complete HRBP automation system.
Provides comprehensive access to agent performance management, coordination
optimization, and workflow orchestration capabilities.

Commands:
- status: Complete HRBP system status
- performance: Agent performance analysis
- coordination: Cross-agent coordination analysis
- optimize: Performance optimization recommendations
- workflow: Manual workflow execution
- integration: Integration health checks
"""
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


def main():
    """Main CLI interface for comprehensive HRBP system."""
    parser = argparse.ArgumentParser(
        description="HRBP Comprehensive Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Commands:

SYSTEM STATUS:
  status                    Complete system status and health
  integration-health        Integration health checks
  
PERFORMANCE ANALYSIS:
  performance               Run agent performance analysis
  coordination              Analyze cross-agent coordination
  optimize                  Generate optimization recommendations
  
WORKFLOW MANAGEMENT:
  workflow manual           Manually trigger HRBP workflows
  workflow history          Show workflow execution history
  
DATA MANAGEMENT:  
  data agents               Show agent registry and capabilities
  data metrics              Show performance metrics summary
  data export               Export HRBP data for analysis

Examples:
  python infra/hrbp_comprehensive_cli.py status
  python infra/hrbp_comprehensive_cli.py performance --days 30
  python infra/hrbp_comprehensive_cli.py optimize --priority high
  python infra/hrbp_comprehensive_cli.py workflow manual
  python infra/hrbp_comprehensive_cli.py data agents --format json
        """,
    )

    parser.add_argument(
        "command",
        choices=[
            "status",
            "integration-health",
            "performance",
            "coordination",
            "optimize",
            "workflow",
            "data",
        ],
        help="HRBP command to execute",
    )

    parser.add_argument("subcommand", nargs="?", help="Subcommand for the main command")

    parser.add_argument(
        "--days", type=int, default=30, help="Number of days for historical analysis (default: 30)"
    )

    parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low", "all"],
        default="all",
        help="Filter by priority level (default: all)",
    )

    parser.add_argument(
        "--format",
        choices=["table", "json", "summary"],
        default="table",
        help="Output format (default: table)",
    )

    parser.add_argument("--output", type=str, help="Output file path (optional)")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    try:
        # Add project root to Python path for imports
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        # Initialize HRBP system
        from common.agent_coordination_optimizer import get_coordination_optimizer
        from common.hrbp_integration_framework import get_hrbp_integration_framework
        from common.hrbp_performance_manager import get_hrbp_performance_manager
        from common.hrbp_pr_tracker import get_hrbp_tracker

        # Execute commands
        if args.command == "status":
            execute_status_command(args)
        elif args.command == "integration-health":
            execute_integration_health_command(args)
        elif args.command == "performance":
            execute_performance_command(args)
        elif args.command == "coordination":
            execute_coordination_command(args)
        elif args.command == "optimize":
            execute_optimize_command(args)
        elif args.command == "workflow":
            execute_workflow_command(args)
        elif args.command == "data":
            execute_data_command(args)

    except ImportError as e:
        print(f"❌ Failed to import HRBP components: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ HRBP CLI error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def execute_status_command(args):
    """Execute system status command."""
    print("\n" + "=" * 70)
    print("🤖 HRBP COMPREHENSIVE SYSTEM STATUS")
    print("=" * 70)

    from common.hrbp_integration_framework import get_hrbp_integration_framework

    framework = get_hrbp_integration_framework()
    system_status = framework.get_system_status()

    # Print basic status
    print(f"📅 Status Time: {system_status.get('timestamp', 'unknown')}")
    print(f"🔧 System Version: {system_status.get('system_version', 'unknown')}")
    print(f"⚡ Framework Status: {system_status.get('integration_framework_status', 'unknown')}")
    print(f"🔄 Active Workflows: {system_status.get('active_workflows', 0)}")
    print(f"📜 Workflow History: {system_status.get('workflow_history_count', 0)}")

    # Integration health
    health = system_status.get("integration_health", {})
    health_status = health.get("overall_status", "unknown")
    health_icon = {"healthy": "🟢", "degraded": "🟡", "critical": "🔴"}.get(health_status, "❓")

    print(f"\n🏥 Integration Health: {health_icon} {health_status.upper()}")

    integration_status = health.get("integration_status", {})
    for integration, status in integration_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {integration.replace('_', ' ').title()}")

    # Issues
    issues = health.get("issues_detected", [])
    if issues:
        print(f"\n⚠️  Issues Detected ({len(issues)}):")
        for issue in issues:
            print(f"   - {issue}")

    # PR cycle status
    pr_status = system_status.get("pr_cycle_status", {})
    if pr_status:
        print(f"\n📊 20-PR Cycle Status:")
        print(f"   🎯 Threshold: {pr_status.get('pr_threshold', 'unknown')} PRs")
        print(f"   📈 Current Cycle: {pr_status.get('current_cycle_prs', 0)}")
        print(f"   ⏳ Until Next: {pr_status.get('prs_until_next_trigger', 'unknown')}")
        print(f"   🚀 Total Triggers: {pr_status.get('total_triggers', 0)}")

    # Last workflow
    last_workflow = system_status.get("last_workflow")
    if last_workflow:
        print(f"\n🔄 Last Workflow Execution:")
        print(f"   ID: {last_workflow.get('trigger_id', 'unknown')}")
        print(f"   Status: {last_workflow.get('status', 'unknown')}")
        print(f"   Time: {last_workflow.get('timestamp', 'unknown')}")
        print(f"   Workflows: {last_workflow.get('workflows_executed', 0)}")


def execute_integration_health_command(args):
    """Execute integration health check command."""
    print("\n" + "=" * 60)
    print("🏥 HRBP INTEGRATION HEALTH CHECK")
    print("=" * 60)

    from common.hrbp_integration_framework import get_hrbp_integration_framework

    framework = get_hrbp_integration_framework()
    health_report = framework.validate_integration_health()

    # Overall status
    status = health_report.get("overall_status", "unknown")
    status_icon = {"healthy": "🟢", "degraded": "🟡", "critical": "🔴"}.get(status, "❓")

    print(f"📊 Overall Status: {status_icon} {status.upper()}")
    print(f"📅 Check Time: {health_report.get('timestamp', 'unknown')}")

    # Integration components
    print(f"\n🔧 Integration Components:")
    integration_status = health_report.get("integration_status", {})
    for component, status in integration_status.items():
        status_icon = "✅" if status else "❌"
        component_name = component.replace("_", " ").title()
        print(f"   {status_icon} {component_name}")

    # Component health
    print(f"\n⚙️  Core Components:")
    component_health = health_report.get("component_health", {})
    for component, health in component_health.items():
        health_icon = "✅" if health == "healthy" else "❌"
        component_name = component.replace("_", " ").title()
        print(f"   {health_icon} {component_name}: {health}")

    # Issues
    issues = health_report.get("issues_detected", [])
    if issues:
        print(f"\n⚠️  Issues Detected ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print(f"\n✅ No issues detected")

    # Recommendations
    if status == "critical":
        print(f"\n🚨 CRITICAL: Immediate attention required")
        print(f"   - Review and resolve all detected issues")
        print(f"   - Restart HRBP system after fixes")
    elif status == "degraded":
        print(f"\n⚠️  WARNING: System functionality limited")
        print(f"   - Address issues to restore full functionality")


def execute_performance_command(args):
    """Execute performance analysis command."""
    print("\n" + "=" * 60)
    print("📊 AGENT PERFORMANCE ANALYSIS")
    print("=" * 60)

    from common.hrbp_performance_manager import get_hrbp_performance_manager

    performance_manager = get_hrbp_performance_manager()

    print(f"📅 Analyzing last {args.days} days of performance data...")
    start_time = time.time()

    # Run comprehensive analysis
    analysis_results = performance_manager.run_comprehensive_performance_analysis(args.days)

    analysis_time = time.time() - start_time

    if "error" in analysis_results:
        print(f"❌ Analysis failed: {analysis_results['error']}")
        return

    # Display results
    metadata = analysis_results.get("analysis_metadata", {})
    print(f"✅ Analysis completed in {analysis_time:.2f}s")
    print(f"📊 Analyzed {metadata.get('total_agents_analyzed', 0)} agents")

    # Executive summary
    summary = analysis_results.get("executive_summary", {})
    if summary:
        print(f"\n📋 Executive Summary:")
        health_status = summary.get("overall_health_status", "unknown")
        health_icon = {
            "excellent": "🟢",
            "good": "🟡",
            "needs_attention": "🟠",
            "critical": "🔴",
        }.get(health_status, "❓")

        print(f"   System Health: {health_icon} {health_status.upper()}")

        # Key metrics
        key_metrics = summary.get("key_metrics", {})
        for metric, value in key_metrics.items():
            metric_name = metric.replace("_", " ").title()
            print(f"   {metric_name}: {value}")

        # Attention required
        attention = summary.get("attention_required", {})
        critical_agents = attention.get("critical_agents", 0)
        high_priority = attention.get("high_priority_recommendations", 0)

        if critical_agents > 0 or high_priority > 0:
            print(f"\n⚠️  Attention Required:")
            if critical_agents > 0:
                print(f"   🚨 {critical_agents} agents in critical state")
            if high_priority > 0:
                print(f"   📋 {high_priority} high-priority recommendations")

        # Top recommendations
        top_recs = summary.get("top_recommendations", [])
        if top_recs:
            print(f"\n🎯 Top Recommendations:")
            for i, rec in enumerate(top_recs[:5], 1):
                priority_icon = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "💡"}.get(
                    rec.get("priority", "low"), "📋"
                )

                print(
                    f"   {i}. {priority_icon} {rec.get('agent', 'unknown')}: {rec.get('description', 'No description')}"
                )

    # Save detailed results if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(analysis_results, f, indent=2)
        print(f"📄 Detailed results saved to: {output_path}")


def execute_coordination_command(args):
    """Execute coordination analysis command."""
    print("\n" + "=" * 60)
    print("🤝 CROSS-AGENT COORDINATION ANALYSIS")
    print("=" * 60)

    from common.agent_coordination_optimizer import get_coordination_optimizer
    from common.hrbp_performance_manager import get_hrbp_performance_manager

    performance_manager = get_hrbp_performance_manager()
    optimizer = get_coordination_optimizer()

    print(f"📅 Analyzing coordination patterns for last {args.days} days...")

    # Analyze coordination patterns
    coordination_metrics = performance_manager.analyze_coordination_patterns(args.days)
    optimization_metrics = optimizer.get_coordination_metrics()

    print(f"✅ Analysis completed")
    print(f"🔗 Coordination patterns analyzed: {len(coordination_metrics)}")

    # Overall coordination health
    avg_effectiveness = optimization_metrics.get("average_success_rate", 0)
    effectiveness_icon = (
        "🟢" if avg_effectiveness > 0.8 else "🟡" if avg_effectiveness > 0.6 else "🔴"
    )

    print(f"\n📊 Coordination Effectiveness: {effectiveness_icon} {avg_effectiveness:.1%}")

    # Capacity utilization
    capacity_util = optimization_metrics.get("capacity_utilization", {})
    if capacity_util:
        print(f"\n⚡ Agent Capacity Utilization:")
        for agent, utilization in capacity_util.items():
            util_icon = "🔴" if utilization > 0.9 else "🟡" if utilization > 0.7 else "🟢"
            print(f"   {util_icon} {agent}: {utilization:.1%}")

    # Coordination patterns
    if coordination_metrics:
        print(f"\n🔗 Recent Coordination Patterns:")

        effective_count = len(
            [
                m
                for m in coordination_metrics
                if m.effectiveness_level in ["highly_effective", "effective"]
            ]
        )
        ineffective_count = len(coordination_metrics) - effective_count

        print(f"   ✅ Effective coordinations: {effective_count}")
        print(f"   ⚠️  Needs improvement: {ineffective_count}")

        # Show coordination issues
        all_issues = set()
        for metrics in coordination_metrics:
            all_issues.update(metrics.issues_identified)

        if all_issues:
            print(f"\n⚠️  Common Issues Identified:")
            for issue in sorted(all_issues)[:5]:  # Show top 5 issues
                print(f"   - {issue}")

    # Resource allocation efficiency
    resource_efficiency = optimization_metrics.get("resource_allocation_efficiency", 0)
    efficiency_icon = (
        "🟢" if resource_efficiency > 0.8 else "🟡" if resource_efficiency > 0.6 else "🔴"
    )
    print(f"\n🎯 Resource Allocation Efficiency: {efficiency_icon} {resource_efficiency:.1%}")

    # Coordination overhead
    overhead_ms = optimization_metrics.get("coordination_overhead_ms", 0)
    print(f"⏱️  Average Coordination Overhead: {overhead_ms:.0f}ms")


def execute_optimize_command(args):
    """Execute optimization recommendations command."""
    print("\n" + "=" * 60)
    print("🎯 PERFORMANCE OPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)

    from common.hrbp_performance_manager import get_hrbp_performance_manager

    performance_manager = get_hrbp_performance_manager()

    print(f"🔍 Generating optimization recommendations...")

    # Get performance and coordination data
    performance_data = performance_manager.collect_agent_performance_data(args.days)
    coordination_data = performance_manager.analyze_coordination_patterns(args.days)

    # Generate recommendations
    recommendations = performance_manager.generate_optimization_recommendations(
        performance_data, coordination_data
    )

    # Filter by priority if specified
    if args.priority != "all":
        recommendations = [r for r in recommendations if r.priority == args.priority]

    print(f"✅ Generated {len(recommendations)} recommendations")

    if not recommendations:
        print("🎉 No optimization recommendations needed!")
        return

    # Group by priority
    by_priority = {}
    for rec in recommendations:
        if rec.priority not in by_priority:
            by_priority[rec.priority] = []
        by_priority[rec.priority].append(rec)

    # Display by priority
    priority_order = ["critical", "high", "medium", "low"]
    for priority in priority_order:
        if priority not in by_priority:
            continue

        priority_recs = by_priority[priority]
        priority_icon = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "💡"}.get(
            priority, "📋"
        )

        print(
            f"\n{priority_icon} {priority.upper()} PRIORITY ({len(priority_recs)} recommendations):"
        )

        for i, rec in enumerate(priority_recs, 1):
            print(f"\n   {i}. Agent: {rec.agent_name}")
            print(f"      Category: {rec.category}")
            print(f"      Description: {rec.description}")
            print(f"      Impact: {rec.estimated_impact}")

            if args.verbose:
                print(f"      Implementation Steps:")
                for j, step in enumerate(rec.implementation_steps, 1):
                    print(f"         {j}. {step}")

    # Summary
    total_critical = len(by_priority.get("critical", []))
    total_high = len(by_priority.get("high", []))

    if total_critical > 0:
        print(f"\n🚨 CRITICAL: {total_critical} issues require immediate attention")
    elif total_high > 0:
        print(f"\n⚠️  HIGH: {total_high} issues should be addressed soon")
    else:
        print(f"\n✅ System performing well with minor optimization opportunities")


def execute_workflow_command(args):
    """Execute workflow management commands."""
    if args.subcommand == "manual":
        execute_manual_workflow(args)
    elif args.subcommand == "history":
        execute_workflow_history(args)
    else:
        print("❌ Invalid workflow subcommand. Use 'manual' or 'history'")


def execute_manual_workflow(args):
    """Execute manual workflow trigger."""
    print("\n" + "=" * 60)
    print("🔄 MANUAL WORKFLOW EXECUTION")
    print("=" * 60)

    from common.hrbp_integration_framework import get_hrbp_integration_framework

    framework = get_hrbp_integration_framework()

    # Confirm with user
    print("⚠️  You are about to manually trigger HRBP workflows")
    print("   This will execute all enabled workflows outside the normal 20-PR cycle.")

    if not args.verbose:  # Skip confirmation in verbose mode for automation
        confirmation = input("\nProceed with manual workflow execution? [y/N]: ").strip().lower()
        if confirmation not in ["y", "yes"]:
            print("❌ Manual workflow execution cancelled")
            return

    print(f"\n🚀 Starting manual workflow execution...")
    start_time = time.time()

    # Execute workflows
    results = framework.manual_trigger_workflow()

    execution_time = time.time() - start_time

    # Display results
    status = results.get("status", "unknown")
    status_icon = "✅" if status == "completed" else "❌"

    print(f"\n{status_icon} Workflow execution {status} in {execution_time:.2f}s")
    print(f"🔄 Trigger ID: {results.get('trigger_id', 'unknown')}")

    workflow_results = results.get("workflow_results", {})
    print(f"📊 Workflows executed: {len(workflow_results)}")

    # Show workflow results
    for workflow_name, result in workflow_results.items():
        workflow_status = result.get("status", "unknown")
        workflow_icon = "✅" if workflow_status == "completed" else "❌"
        print(f"   {workflow_icon} {workflow_name}: {workflow_status}")

        if args.verbose and workflow_status == "completed":
            # Show key metrics from each workflow
            if "agents_analyzed" in result:
                print(f"      - Agents analyzed: {result['agents_analyzed']}")
            if "recommendations_generated" in result:
                print(f"      - Recommendations: {result['recommendations_generated']}")

    # Show summary
    summary = results.get("summary", {})
    if summary:
        print(f"\n📋 Execution Summary:")
        print(f"   ✅ Completed: {summary.get('workflows_completed', 0)}")
        print(f"   ❌ Failed: {summary.get('workflows_failed', 0)}")
        print(f"   📊 Total Recommendations: {summary.get('total_recommendations', 0)}")
        print(f"   🚨 Critical Issues: {summary.get('critical_issues_identified', 0)}")


def execute_workflow_history(args):
    """Execute workflow history display."""
    print("\n" + "=" * 60)
    print("📜 WORKFLOW EXECUTION HISTORY")
    print("=" * 60)

    from common.hrbp_pr_tracker import get_hrbp_tracker

    tracker = get_hrbp_tracker()

    # Get recent history
    history = tracker.get_trigger_history(limit=10)

    if not history:
        print("📭 No workflow execution history found")
        return

    print(f"📊 Showing {len(history)} recent workflow executions:")

    for i, trigger in enumerate(reversed(history), 1):
        status = trigger.get("status", "unknown")
        status_icon = {"completed": "✅", "failed": "❌", "running": "🔄", "pending": "⏳"}.get(
            status, "❓"
        )

        print(f"\n{i}. {status_icon} {trigger.get('trigger_id', 'unknown')}")
        print(f"   Status: {status}")
        print(
            f"   PR Range: {trigger.get('starting_pr', '')}-{trigger.get('ending_pr', '')} ({trigger.get('pr_count', 0)} PRs)"
        )
        print(f"   Timestamp: {trigger.get('timestamp', 'unknown')}")
        print(f"   Workflows: {', '.join(trigger.get('workflows_triggered', []))}")

        if trigger.get("completion_timestamp"):
            print(f"   Completed: {trigger['completion_timestamp']}")

        if trigger.get("error_message"):
            print(f"   Error: {trigger['error_message']}")


def execute_data_command(args):
    """Execute data management commands."""
    if args.subcommand == "agents":
        execute_agents_data(args)
    elif args.subcommand == "metrics":
        execute_metrics_data(args)
    elif args.subcommand == "export":
        execute_export_data(args)
    else:
        print("❌ Invalid data subcommand. Use 'agents', 'metrics', or 'export'")


def execute_agents_data(args):
    """Display agent registry and capabilities."""
    print("\n" + "=" * 60)
    print("🤖 AGENT REGISTRY AND CAPABILITIES")
    print("=" * 60)

    from common.hrbp_performance_manager import get_hrbp_performance_manager

    performance_manager = get_hrbp_performance_manager()
    agent_registry = performance_manager.agent_registry
    performance_data = performance_manager._load_performance_data()

    print(f"📊 Total Agents Registered: {len(agent_registry)}")
    print(f"📈 Agents with Performance Data: {len(performance_data)}")

    if args.format == "json":
        # Output as JSON
        output = {"agent_registry": agent_registry, "performance_data": performance_data}
        print(json.dumps(output, indent=2))
    else:
        # Table format
        print(f"\n🤖 Agent Details:")

        for agent_name, agent_info in agent_registry.items():
            print(f"\n   📋 {agent_name}")
            print(f"      Description: {agent_info.get('description', 'No description available')}")

            # Performance metrics if available
            if agent_name in performance_data:
                perf_data = performance_data[agent_name]
                success_rate = perf_data.get("success_rate", 0)
                success_icon = "🟢" if success_rate > 0.9 else "🟡" if success_rate > 0.7 else "🔴"

                print(f"      Performance: {success_icon} {success_rate:.1%} success rate")
                print(f"      Executions: {perf_data.get('total_executions', 0)}")
                print(f"      Capability: {perf_data.get('capability_level', 'unknown')}")


def execute_metrics_data(args):
    """Display performance metrics summary."""
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE METRICS SUMMARY")
    print("=" * 60)

    from common.hrbp_performance_manager import get_hrbp_performance_manager

    performance_manager = get_hrbp_performance_manager()
    performance_data = performance_manager.collect_agent_performance_data(args.days)

    if not performance_data:
        print("📭 No performance data available")
        return

    # Calculate summary statistics
    total_agents = len(performance_data)
    active_agents = len([a for a in performance_data.values() if a.total_executions > 0])

    success_rates = [a.success_rate for a in performance_data.values() if a.total_executions > 0]
    avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0

    execution_times = [
        a.average_execution_time_ms
        for a in performance_data.values()
        if a.average_execution_time_ms > 0
    ]
    avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

    # Capability distribution
    capability_counts = {}
    for agent in performance_data.values():
        level = agent.capability_level
        capability_counts[level] = capability_counts.get(level, 0) + 1

    print(f"📊 System Overview:")
    print(f"   Total Agents: {total_agents}")
    print(f"   Active Agents: {active_agents}")
    print(f"   Average Success Rate: {avg_success_rate:.1%}")
    print(f"   Average Execution Time: {avg_execution_time:.0f}ms")

    print(f"\n🎯 Capability Distribution:")
    for level, count in capability_counts.items():
        level_icon = {
            "excellent": "🟢",
            "good": "🟡",
            "needs_improvement": "🟠",
            "critical": "🔴",
        }.get(level, "❓")
        print(f"   {level_icon} {level.replace('_', ' ').title()}: {count}")


def execute_export_data(args):
    """Export HRBP data for analysis."""
    print("\n" + "=" * 60)
    print("📤 HRBP DATA EXPORT")
    print("=" * 60)

    if not args.output:
        print("❌ Output file path required for export (use --output)")
        return

    from common.hrbp_performance_manager import get_hrbp_performance_manager
    from common.hrbp_pr_tracker import get_hrbp_tracker

    performance_manager = get_hrbp_performance_manager()
    pr_tracker = get_hrbp_tracker()

    print(f"📊 Collecting HRBP data for export...")

    # Collect all data
    export_data = {
        "export_metadata": {
            "timestamp": time.time(),
            "export_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_days": args.days,
            "version": "1.0.0",
        },
        "agent_performance": {
            name: asdict(metrics)
            for name, metrics in performance_manager.collect_agent_performance_data(
                args.days
            ).items()
        },
        "coordination_metrics": [
            asdict(coord) for coord in performance_manager.analyze_coordination_patterns(args.days)
        ],
        "pr_cycle_status": pr_tracker.get_cycle_status(),
        "workflow_history": pr_tracker.get_trigger_history(limit=50),
        "system_configuration": performance_manager.config,
    }

    # Export to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"✅ HRBP data exported successfully")
    print(f"📄 Export file: {output_path}")
    print(f"📊 Data includes:")
    print(f"   - {len(export_data['agent_performance'])} agent performance profiles")
    print(f"   - {len(export_data['coordination_metrics'])} coordination metrics")
    print(f"   - {len(export_data['workflow_history'])} workflow history entries")


def format_bytes(bytes_value):
    """Format bytes as human readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_value < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} TB"


if __name__ == "__main__":
    main()
