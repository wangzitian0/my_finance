#!/usr/bin/env python3
"""
Agent Execution Monitoring Dashboard

Provides comprehensive monitoring and reporting capabilities for the
Agent Execution Monitoring System (Issue #180).
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from .execution_monitor import get_monitor
from .agent_task_tracker import get_tracker
from .agent_delegation_logger import get_delegation_logger


class MonitoringDashboard:
    """
    Comprehensive monitoring dashboard for agent execution analytics.
    
    Provides unified view of:
    - Agent performance metrics
    - Error patterns and trends
    - Delegation efficiency
    - System health indicators
    """
    
    def __init__(self):
        """Initialize monitoring dashboard."""
        self.monitor = get_monitor()
        self.tracker = get_tracker()
        self.delegation_logger = get_delegation_logger()
    
    def generate_comprehensive_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive monitoring report.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with complete monitoring analytics
        """
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "analysis_period_days": days,
                "analysis_start_date": (datetime.now() - timedelta(days=days)).isoformat()
            },
            "executive_summary": {},
            "execution_metrics": {},
            "agent_performance": {},
            "error_analysis": {},
            "delegation_metrics": {},
            "system_health": {},
            "recommendations": []
        }
        
        # Get raw data
        execution_stats = self.monitor.get_execution_stats(days)
        agent_performance = self.tracker.get_agent_performance(days)
        error_patterns = self.tracker.get_error_patterns(days)
        delegation_stats = self.delegation_logger.get_delegation_stats(days)
        
        # Executive Summary
        report["executive_summary"] = self._generate_executive_summary(
            execution_stats, agent_performance, delegation_stats
        )
        
        # Execution Metrics
        report["execution_metrics"] = execution_stats
        
        # Agent Performance
        report["agent_performance"] = agent_performance
        
        # Error Analysis
        report["error_analysis"] = {
            "error_patterns": error_patterns,
            "error_trends": self._analyze_error_trends(error_patterns),
            "critical_issues": self._identify_critical_issues(error_patterns)
        }
        
        # Delegation Metrics
        report["delegation_metrics"] = delegation_stats
        
        # System Health
        report["system_health"] = self._assess_system_health(
            execution_stats, agent_performance, error_patterns
        )
        
        # Recommendations
        report["recommendations"] = self._generate_recommendations(
            execution_stats, agent_performance, error_patterns, delegation_stats
        )
        
        return report
    
    def _generate_executive_summary(
        self, 
        execution_stats: Dict[str, Any], 
        agent_performance: Dict[str, Any],
        delegation_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary."""
        total_executions = execution_stats.get("total_executions", 0)
        success_rate = execution_stats.get("success_rate", 0)
        avg_execution_time = execution_stats.get("average_execution_time_ms", 0)
        
        # Calculate agent efficiency
        agent_count = len(agent_performance)
        avg_agent_success_rate = 0
        if agent_count > 0:
            agent_success_rates = [
                perf.get("success_rate", 0) for perf in agent_performance.values()
            ]
            avg_agent_success_rate = sum(agent_success_rates) / len(agent_success_rates)
        
        return {
            "total_executions": total_executions,
            "overall_success_rate": success_rate,
            "average_execution_time_ms": avg_execution_time,
            "active_agents": agent_count,
            "average_agent_success_rate": avg_agent_success_rate,
            "total_delegations": delegation_stats.get("total_delegations", 0),
            "delegation_success_rate": delegation_stats.get("success_rate", 0),
            "status": self._get_overall_status(success_rate, avg_agent_success_rate)
        }
    
    def _analyze_error_trends(self, error_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze error trends and patterns."""
        if not error_patterns:
            return {"trends": [], "insights": []}
        
        # Group errors by category
        category_counts = {}
        agent_error_counts = {}
        recurring_errors = []
        
        for error in error_patterns:
            category = error.get("error_category", "unknown")
            agent = error.get("agent_type", "unknown")
            frequency = error.get("frequency", 0)
            
            category_counts[category] = category_counts.get(category, 0) + frequency
            agent_error_counts[agent] = agent_error_counts.get(agent, 0) + frequency
            
            if frequency >= 3:  # Consider recurring if 3+ occurrences
                recurring_errors.append(error)
        
        insights = []
        
        # Critical insights
        if category_counts.get("critical", 0) > 0:
            insights.append(f"⚠️  {category_counts['critical']} critical errors detected")
        
        if recurring_errors:
            insights.append(f"🔄 {len(recurring_errors)} recurring error patterns identified")
        
        # Most error-prone agent
        if agent_error_counts:
            most_errors_agent = max(agent_error_counts.items(), key=lambda x: x[1])
            insights.append(f"📈 {most_errors_agent[0]} has highest error count ({most_errors_agent[1]})")
        
        return {
            "category_breakdown": category_counts,
            "agent_error_breakdown": agent_error_counts,
            "recurring_errors": recurring_errors,
            "insights": insights
        }
    
    def _identify_critical_issues(self, error_patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify critical issues requiring immediate attention."""
        critical_issues = []
        
        for error in error_patterns:
            if error.get("error_category") == "critical" or error.get("frequency", 0) >= 5:
                critical_issues.append({
                    "type": "critical_error" if error.get("error_category") == "critical" else "high_frequency",
                    "agent_type": error.get("agent_type"),
                    "error_message": error.get("error_message"),
                    "frequency": error.get("frequency"),
                    "first_occurrence": error.get("first_occurrence"),
                    "last_occurrence": error.get("last_occurrence"),
                    "urgency": "immediate" if error.get("error_category") == "critical" else "high"
                })
        
        return sorted(critical_issues, key=lambda x: x["frequency"], reverse=True)
    
    def _assess_system_health(
        self,
        execution_stats: Dict[str, Any],
        agent_performance: Dict[str, Any],
        error_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess overall system health."""
        success_rate = execution_stats.get("success_rate", 0)
        avg_execution_time = execution_stats.get("average_execution_time_ms", 0)
        critical_errors = len([e for e in error_patterns if e.get("error_category") == "critical"])
        
        # Health score calculation (0-100)
        health_score = 100
        
        # Deduct for low success rate
        if success_rate < 0.95:
            health_score -= (0.95 - success_rate) * 100
        
        # Deduct for slow execution
        if avg_execution_time > 5000:  # 5 seconds threshold
            health_score -= min(20, (avg_execution_time - 5000) / 1000)
        
        # Deduct for critical errors
        health_score -= critical_errors * 10
        
        health_score = max(0, min(100, health_score))
        
        # Determine status
        if health_score >= 90:
            status = "excellent"
            color = "green"
        elif health_score >= 80:
            status = "good"
            color = "lightgreen"
        elif health_score >= 70:
            status = "fair"
            color = "yellow"
        elif health_score >= 60:
            status = "poor"
            color = "orange"
        else:
            status = "critical"
            color = "red"
        
        return {
            "health_score": round(health_score, 1),
            "status": status,
            "color": color,
            "metrics": {
                "success_rate": success_rate,
                "avg_execution_time_ms": avg_execution_time,
                "critical_errors": critical_errors,
                "active_agents": len(agent_performance)
            },
            "thresholds": {
                "min_success_rate": 0.95,
                "max_execution_time_ms": 5000,
                "max_critical_errors": 0
            }
        }
    
    def _generate_recommendations(
        self,
        execution_stats: Dict[str, Any],
        agent_performance: Dict[str, Any],
        error_patterns: List[Dict[str, Any]],
        delegation_stats: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        success_rate = execution_stats.get("success_rate", 0)
        avg_execution_time = execution_stats.get("average_execution_time_ms", 0)
        
        # Success rate recommendations
        if success_rate < 0.95:
            recommendations.append({
                "priority": "high",
                "category": "reliability",
                "title": "Improve Success Rate",
                "description": f"Current success rate ({success_rate:.1%}) is below target (95%)",
                "action": "Review failing executions and implement error handling improvements"
            })
        
        # Performance recommendations
        if avg_execution_time > 5000:
            recommendations.append({
                "priority": "medium",
                "category": "performance",
                "title": "Optimize Execution Time",
                "description": f"Average execution time ({avg_execution_time:.0f}ms) exceeds target (5s)",
                "action": "Profile slow executions and optimize critical paths"
            })
        
        # Agent-specific recommendations
        for agent_type, performance in agent_performance.items():
            agent_success_rate = performance.get("success_rate", 0)
            if agent_success_rate < 0.90:
                recommendations.append({
                    "priority": "high",
                    "category": "agent_performance",
                    "title": f"Improve {agent_type} Reliability",
                    "description": f"{agent_type} success rate ({agent_success_rate:.1%}) needs improvement",
                    "action": f"Review {agent_type} error patterns and enhance error handling"
                })
        
        # Error pattern recommendations
        critical_patterns = [e for e in error_patterns if e.get("error_category") == "critical"]
        if critical_patterns:
            recommendations.append({
                "priority": "critical",
                "category": "error_handling",
                "title": "Address Critical Error Patterns",
                "description": f"Found {len(critical_patterns)} critical error patterns",
                "action": "Immediately investigate and fix critical errors"
            })
        
        # Delegation recommendations
        delegation_success_rate = delegation_stats.get("success_rate", 0)
        if delegation_success_rate < 0.95:
            recommendations.append({
                "priority": "medium",
                "category": "delegation",
                "title": "Improve Agent Delegation Reliability",
                "description": f"Delegation success rate ({delegation_success_rate:.1%}) needs improvement",
                "action": "Review agent coordination patterns and add fallback mechanisms"
            })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return recommendations
    
    def _get_overall_status(self, success_rate: float, avg_agent_success_rate: float) -> str:
        """Get overall system status."""
        if success_rate >= 0.95 and avg_agent_success_rate >= 0.90:
            return "healthy"
        elif success_rate >= 0.90 and avg_agent_success_rate >= 0.85:
            return "warning"
        else:
            return "critical"
    
    def print_summary_report(self, days: int = 7):
        """Print a concise summary report to console."""
        report = self.generate_comprehensive_report(days)
        
        print("\n" + "="*60)
        print("🤖 AGENT EXECUTION MONITORING REPORT")
        print("="*60)
        
        # Executive Summary
        summary = report["executive_summary"]
        print(f"\n📊 EXECUTIVE SUMMARY ({days} days)")
        print("-" * 30)
        print(f"Total Executions:     {summary['total_executions']}")
        print(f"Success Rate:         {summary['overall_success_rate']:.1%}")
        print(f"Avg Execution Time:   {summary['average_execution_time_ms']:.0f}ms")
        print(f"Active Agents:        {summary['active_agents']}")
        print(f"System Status:        {summary['status'].upper()}")
        
        # System Health
        health = report["system_health"]
        status_emoji = {"excellent": "🟢", "good": "🟡", "fair": "🟠", "poor": "🔴", "critical": "💀"}
        print(f"\n🏥 SYSTEM HEALTH")
        print("-" * 20)
        print(f"Health Score:         {health['health_score']}/100 {status_emoji.get(health['status'], '❓')}")
        print(f"Status:               {health['status'].upper()}")
        
        # Top Recommendations
        recommendations = report["recommendations"]
        if recommendations:
            print(f"\n🎯 TOP RECOMMENDATIONS")
            print("-" * 25)
            for i, rec in enumerate(recommendations[:3], 1):
                priority_emoji = {"critical": "🚨", "high": "❗", "medium": "⚠️", "low": "💡"}
                print(f"{i}. {priority_emoji.get(rec['priority'], '•')} {rec['title']}")
                print(f"   {rec['description']}")
        
        # Agent Performance Overview
        agent_perf = report["agent_performance"]
        if agent_perf:
            print(f"\n🤖 AGENT PERFORMANCE")
            print("-" * 22)
            for agent, perf in sorted(agent_perf.items(), key=lambda x: x[1]['success_rate'], reverse=True):
                success_rate = perf['success_rate']
                total_tasks = perf['total_tasks']
                status_emoji = "🟢" if success_rate >= 0.95 else "🟡" if success_rate >= 0.90 else "🔴"
                print(f"{status_emoji} {agent:<20} {success_rate:>6.1%} ({total_tasks} tasks)")
        
        print("\n" + "="*60)
        
        return report
    
    def export_report(self, days: int = 7, output_file: Optional[Path] = None) -> Path:
        """
        Export comprehensive report to JSON file.
        
        Args:
            days: Number of days to analyze
            output_file: Output file path (optional)
            
        Returns:
            Path to exported report file
        """
        report = self.generate_comprehensive_report(days)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config_dir = Path(__file__).parent / "config" / "monitoring"
            output_file = config_dir / f"monitoring_report_{timestamp}.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📄 Report exported to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Failed to export report: {e}")
            raise


# Global dashboard instance
_global_dashboard = None


def get_dashboard() -> MonitoringDashboard:
    """Get global monitoring dashboard instance."""
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = MonitoringDashboard()
    return _global_dashboard


# CLI command integration
def print_monitoring_summary(days: int = 7):
    """Print monitoring summary (for p3 command integration)."""
    dashboard = get_dashboard()
    dashboard.print_summary_report(days)


def export_monitoring_report(days: int = 7, output_file: Optional[str] = None) -> str:
    """Export monitoring report (for p3 command integration)."""
    dashboard = get_dashboard()
    output_path = dashboard.export_report(days, Path(output_file) if output_file else None)
    return str(output_path)