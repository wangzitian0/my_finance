#!/usr/bin/env python3
"""
HRBP PR Cycle Tracker

Tracks PR merges to main branch and triggers HRBP automation after every 20 PRs.
Implements 20-PR cycle automation for HRBP triggers as specified in task requirements.
"""
import json
import logging
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class PRRecord:
    """Record of a PR merge for HRBP tracking."""

    pr_number: int
    title: str
    merge_timestamp: str
    merge_sha: str
    author: str
    issue_number: Optional[int] = None
    branch_name: Optional[str] = None


@dataclass
class HRBPTrigger:
    """Record of an HRBP cycle trigger."""

    trigger_id: str
    timestamp: str
    pr_count: int
    starting_pr: int
    ending_pr: int
    status: str  # 'pending', 'running', 'completed', 'failed'
    workflows_triggered: List[str]
    completion_timestamp: Optional[str] = None
    error_message: Optional[str] = None


class HRBPPRTracker:
    """
    Tracks PR merges to main branch and manages HRBP automation cycles.

    Provides:
    - Persistent PR counting and tracking
    - Automatic HRBP cycle triggering after 20 PRs
    - Integration with existing git workflow and p3 system
    - Configuration management via common/config/
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize HRBP PR tracker."""
        # Use centralized DirectoryManager for SSOT compliance
        from .directory_manager import directory_manager

        self.logs_dir = directory_manager.get_logs_path()
        self.config_dir = directory_manager.get_config_path()

        # Load configuration
        if config_path is None:
            config_path = self.config_dir / "hrbp_automation.yml"

        # Use SSOT config_manager instead of loading directly
        from .core.config_manager import config_manager
        try:
            self.config = config_manager.get_config("hrbp_automation")
        except Exception:
            self.config = self._get_default_config()
        self.pr_threshold = self.config["hrbp_automation"]["pr_cycle_threshold"]
        self.enabled = self.config["hrbp_automation"]["enabled"]

        # Initialize file paths
        counter_filename = self.config["hrbp_automation"]["tracking"]["counter_file"]
        history_filename = self.config["hrbp_automation"]["tracking"]["history_file"]

        self.counter_file = self.logs_dir / counter_filename
        self.history_file = self.logs_dir / history_filename

        # Setup logging
        try:
            self._setup_logging()
        except Exception as e:
            print(f"⚠️  Could not setup logging: {e}")
            # Create a simple logger fallback
            self.logger = self._create_simple_logger()

        # Ensure data directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: Path) -> Dict:
        """Load HRBP automation configuration."""
        if not YAML_AVAILABLE:
            print("⚠️  YAML module not available, using default configuration")
            return self._get_default_config()

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"⚠️  HRBP config file not found: {config_path}, using defaults")
            return self._get_default_config()
        except Exception as e:
            print(f"⚠️  Failed to load HRBP config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default configuration if config file is missing."""
        return {
            "hrbp_automation": {
                "pr_cycle_threshold": 20,
                "enabled": True,
                "tracking": {
                    "counter_file": "hrbp_pr_counter.json",
                    "history_file": "hrbp_trigger_history.json",
                },
                "workflows": {
                    "agent_performance_analysis": True,
                    "documentation_consolidation": True,
                    "cross_agent_evaluation": True,
                    "performance_optimization": True,
                },
                "notifications": {"console_output": True, "log_file": True},
            }
        }

    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.logs_dir / "hrbp_pr_tracker.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        self.logger = logging.getLogger(__name__)

    def _create_simple_logger(self):
        """Create a simple logger fallback when logging setup fails."""

        class SimpleLogger:
            def info(self, msg):
                print(f"INFO: {msg}")

            def warning(self, msg):
                print(f"WARNING: {msg}")

            def error(self, msg):
                print(f"ERROR: {msg}")

        return SimpleLogger()

    def _load_pr_counter(self) -> Dict:
        """Load PR counter data from file."""
        if not self.counter_file.exists():
            return {
                "total_prs": 0,
                "cycle_prs": 0,
                "last_pr_number": 0,
                "last_hrbp_trigger": None,
                "pr_records": [],
            }

        try:
            with open(self.counter_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load PR counter: {e}")
            return {
                "total_prs": 0,
                "cycle_prs": 0,
                "last_pr_number": 0,
                "last_hrbp_trigger": None,
                "pr_records": [],
            }

    def _save_pr_counter(self, counter_data: Dict):
        """Save PR counter data to file."""
        try:
            with open(self.counter_file, "w") as f:
                json.dump(counter_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save PR counter: {e}")

    def _load_trigger_history(self) -> List[Dict]:
        """Load HRBP trigger history from file."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load trigger history: {e}")
            return []

    def _save_trigger_history(self, history: List[Dict]):
        """Save HRBP trigger history to file."""
        try:
            # Limit history size
            max_entries = self.config["hrbp_automation"]["tracking"]["max_history_entries"]
            if len(history) > max_entries:
                history = history[-max_entries:]

            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save trigger history: {e}")

    def get_pr_info_from_git(self, pr_number: int) -> Optional[PRRecord]:
        """Extract PR information from git history."""
        try:
            # Get PR merge commit info
            cmd = f'git log --grep="Merge pull request #{pr_number}" --oneline --format="%H|%an|%s|%ct" -1'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0 or not result.stdout.strip():
                self.logger.warning(f"Could not find git info for PR #{pr_number}")
                return None

            # Parse git output
            parts = result.stdout.strip().split("|")
            if len(parts) < 4:
                return None

            merge_sha = parts[0]
            author = parts[1]
            commit_message = parts[2]
            timestamp = datetime.fromtimestamp(int(parts[3])).isoformat()

            # Extract PR title and branch from commit message
            # Format: "Merge pull request #123 from branch-name"
            title = "Unknown"
            branch_name = None

            if " from " in commit_message:
                parts = commit_message.split(" from ")
                if len(parts) >= 2:
                    branch_name = parts[1]

            return PRRecord(
                pr_number=pr_number,
                title=title,
                merge_timestamp=timestamp,
                merge_sha=merge_sha,
                author=author,
                branch_name=branch_name,
            )

        except Exception as e:
            self.logger.error(f"Failed to get PR info from git: {e}")
            return None

    def record_pr_merge(self, pr_number: int) -> bool:
        """
        Record a PR merge and check if HRBP cycle should be triggered.

        Args:
            pr_number: GitHub PR number that was merged

        Returns:
            bool: True if HRBP cycle was triggered, False otherwise
        """
        if not self.enabled:
            self.logger.info("HRBP automation is disabled")
            return False

        self.logger.info(f"Recording PR #{pr_number} merge")

        # Load current counter
        counter_data = self._load_pr_counter()

        # Check if this PR was already recorded
        existing_prs = [record["pr_number"] for record in counter_data.get("pr_records", [])]
        if pr_number in existing_prs:
            self.logger.info(f"PR #{pr_number} already recorded")
            return False

        # Get PR information from git
        pr_record = self.get_pr_info_from_git(pr_number)
        if pr_record is None:
            self.logger.warning(
                f"Could not get complete info for PR #{pr_number}, using minimal record"
            )
            pr_record = PRRecord(
                pr_number=pr_number,
                title=f"PR #{pr_number}",
                merge_timestamp=datetime.now().isoformat(),
                merge_sha="unknown",
                author="unknown",
            )

        # Update counters
        counter_data["total_prs"] += 1
        counter_data["cycle_prs"] += 1
        counter_data["last_pr_number"] = pr_number

        # Add PR record
        if "pr_records" not in counter_data:
            counter_data["pr_records"] = []
        counter_data["pr_records"].append(asdict(pr_record))

        # Save updated counter
        self._save_pr_counter(counter_data)

        self.logger.info(
            f"PR #{pr_number} recorded. Total PRs: {counter_data['total_prs']}, Cycle PRs: {counter_data['cycle_prs']}"
        )

        # Check if we've hit the threshold
        if counter_data["cycle_prs"] >= self.pr_threshold:
            self.logger.info(f"HRBP cycle threshold reached ({self.pr_threshold} PRs)")
            return self._trigger_hrbp_cycle(counter_data)
        else:
            remaining = self.pr_threshold - counter_data["cycle_prs"]
            self.logger.info(f"HRBP cycle: {remaining} PRs remaining until next trigger")

        return False

    def _trigger_hrbp_cycle(self, counter_data: Dict) -> bool:
        """
        Trigger HRBP automation cycle using integrated framework.

        Args:
            counter_data: Current PR counter data

        Returns:
            bool: True if successfully triggered, False otherwise
        """
        timestamp = datetime.now().isoformat()
        trigger_id = f"hrbp_{timestamp.replace(':', '').replace('-', '').split('.')[0]}"

        # Calculate PR range for this cycle
        ending_pr = counter_data["last_pr_number"]
        starting_pr = ending_pr - self.pr_threshold + 1

        self.logger.info(f"Triggering HRBP cycle {trigger_id} for PRs {starting_pr}-{ending_pr}")

        # Determine which workflows to trigger
        workflow_config = self.config["hrbp_automation"]["workflows"]
        workflows_to_trigger = [
            workflow for workflow, enabled in workflow_config.items() if enabled
        ]

        # Create trigger record
        trigger = HRBPTrigger(
            trigger_id=trigger_id,
            timestamp=timestamp,
            pr_count=counter_data["cycle_prs"],
            starting_pr=starting_pr,
            ending_pr=ending_pr,
            status="pending",
            workflows_triggered=workflows_to_trigger,
        )

        # Save trigger to history
        history = self._load_trigger_history()
        history.append(asdict(trigger))
        self._save_trigger_history(history)

        # NEW: Execute HRBP workflows through integration framework
        success = self._execute_hrbp_workflows_integrated(trigger, workflows_to_trigger)

        # Update trigger status
        trigger.status = "completed" if success else "failed"
        trigger.completion_timestamp = datetime.now().isoformat()

        # Update history with final status
        history[-1] = asdict(trigger)
        self._save_trigger_history(history)

        # Reset cycle counter
        counter_data["cycle_prs"] = 0
        counter_data["last_hrbp_trigger"] = trigger_id
        self._save_pr_counter(counter_data)

        if success:
            self.logger.info(f"HRBP cycle {trigger_id} completed successfully")
        else:
            self.logger.error(f"HRBP cycle {trigger_id} failed")

        return success

    def _execute_hrbp_workflows(self, trigger: HRBPTrigger, workflows: List[str]) -> bool:
        """
        Execute HRBP automation workflows.

        Args:
            trigger: HRBP trigger record
            workflows: List of workflows to execute

        Returns:
            bool: True if all workflows succeeded, False otherwise
        """
        self.logger.info(f"Executing HRBP workflows: {', '.join(workflows)}")

        all_success = True

        for workflow in workflows:
            try:
                if workflow == "agent_performance_analysis":
                    success = self._run_agent_performance_analysis(trigger)
                elif workflow == "documentation_consolidation":
                    success = self._run_documentation_consolidation(trigger)
                elif workflow == "cross_agent_evaluation":
                    success = self._run_cross_agent_evaluation(trigger)
                elif workflow == "performance_optimization":
                    success = self._run_performance_optimization(trigger)
                else:
                    self.logger.warning(f"Unknown workflow: {workflow}")
                    success = False

                if not success:
                    all_success = False
                    self.logger.error(f"Workflow {workflow} failed")
                else:
                    self.logger.info(f"Workflow {workflow} completed successfully")

            except Exception as e:
                self.logger.error(f"Exception in workflow {workflow}: {e}")
                all_success = False

        return all_success

    def _execute_hrbp_workflows_integrated(
        self, trigger: HRBPTrigger, workflows: List[str]
    ) -> bool:
        """
        Execute HRBP workflows using the integrated framework.

        This method delegates to the comprehensive HRBP integration framework
        for enhanced workflow execution with better coordination and reporting.

        Args:
            trigger: HRBP trigger record
            workflows: List of workflows to execute

        Returns:
            bool: True if all workflows succeeded, False otherwise
        """
        try:
            # Import and use the integration framework
            from .hrbp_integration_framework import get_hrbp_integration_framework

            integration_framework = get_hrbp_integration_framework()

            # Convert trigger to format expected by integration framework
            trigger_data = {
                "trigger_id": trigger.trigger_id,
                "trigger_timestamp": trigger.timestamp,
                "starting_pr": trigger.starting_pr,
                "ending_pr": trigger.ending_pr,
                "pr_count": trigger.pr_count,
                "workflows_requested": workflows,
            }

            # Execute through integration framework
            results = integration_framework.handle_pr_cycle_trigger(trigger_data)

            # Check if execution was successful
            success = results.get("status") == "completed"

            if success:
                self.logger.info(f"Integrated HRBP workflow execution completed successfully")
                self.logger.info(
                    f"Workflows executed: {', '.join(results.get('workflows_executed', []))}"
                )

                # Log summary information
                summary = results.get("summary", {})
                if summary:
                    self.logger.info(
                        f"Summary: {summary.get('workflows_completed', 0)} completed, "
                        f"{summary.get('total_recommendations', 0)} recommendations generated"
                    )
            else:
                self.logger.error(
                    f"Integrated HRBP workflow execution failed: {results.get('error', 'Unknown error')}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Integrated HRBP workflow execution failed: {e}")
            # Fallback to original workflow execution
            self.logger.info("Falling back to original workflow execution method")
            return self._execute_hrbp_workflows(trigger, workflows)

    def _run_agent_performance_analysis(self, trigger: HRBPTrigger) -> bool:
        """Run agent performance analysis workflow."""
        try:
            # Import execution monitor for performance data
            from .execution_monitor import get_monitor

            monitor = get_monitor()

            # Get execution statistics for the last 20 PRs worth of time
            # Estimate: 20 PRs over ~2-4 weeks, so analyze last 30 days
            stats = monitor.get_execution_stats(days=30)

            # Generate performance report
            report = self._generate_performance_report(stats, trigger)

            # Save performance report
            report_file = self.logs_dir / f"hrbp_performance_report_{trigger.trigger_id}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"Agent performance analysis completed: {report_file}")
            return True

        except Exception as e:
            self.logger.error(f"Agent performance analysis failed: {e}")
            return False

    def _generate_performance_report(self, stats: Dict, trigger: HRBPTrigger) -> Dict:
        """Generate comprehensive performance report for HRBP review."""
        # Apply performance thresholds from config
        performance_config = self.config.get("agent_performance", {})
        min_success_rate = performance_config.get("success_rate_minimum", 0.85)
        max_avg_time = performance_config.get("average_execution_time_max", 30000)

        report = {
            "trigger_id": trigger.trigger_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "pr_range": f"{trigger.starting_pr}-{trigger.ending_pr}",
            "raw_stats": stats,
            "performance_evaluation": {
                "overall_success_rate": stats.get("success_rate", 0),
                "meets_success_threshold": stats.get("success_rate", 0) >= min_success_rate,
                "average_execution_time_ms": stats.get("average_execution_time_ms", 0),
                "meets_time_threshold": stats.get("average_execution_time_ms", 0) <= max_avg_time,
                "total_executions": stats.get("total_executions", 0),
                "error_analysis": stats.get("error_categories", {}),
                "agent_breakdown": stats.get("agent_performance", {}),
            },
            "recommendations": self._generate_performance_recommendations(
                stats, performance_config
            ),
        }

        return report

    def _generate_performance_recommendations(self, stats: Dict, config: Dict) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        success_rate = stats.get("success_rate", 0)
        min_success_rate = config.get("success_rate_minimum", 0.85)

        if success_rate < min_success_rate:
            recommendations.append(
                f"Overall success rate ({success_rate:.2%}) below threshold ({min_success_rate:.2%})"
            )

        avg_time = stats.get("average_execution_time_ms", 0)
        max_avg_time = config.get("average_execution_time_max", 30000)

        if avg_time > max_avg_time:
            recommendations.append(
                f"Average execution time ({avg_time}ms) exceeds threshold ({max_avg_time}ms)"
            )

        # Check error categories
        error_limits = config.get("error_categories", {})
        error_categories = stats.get("error_categories", {})

        for category, limit in error_limits.items():
            count = error_categories.get(category.replace("_max", ""), 0)
            if count > limit:
                recommendations.append(
                    f"Too many {category.replace('_max', '')} errors: {count} > {limit}"
                )

        # Agent-specific recommendations
        agent_performance = stats.get("agent_performance", {})
        for agent, metrics in agent_performance.items():
            agent_success_rate = metrics["success"] / max(metrics["total"], 1)
            if agent_success_rate < min_success_rate:
                recommendations.append(
                    f"Agent {agent} success rate ({agent_success_rate:.2%}) needs improvement"
                )

        if not recommendations:
            recommendations.append("All performance metrics within acceptable ranges")

        return recommendations

    def _run_documentation_consolidation(self, trigger: HRBPTrigger) -> bool:
        """Run documentation consolidation workflow."""
        try:
            # This would integrate with agent-coordinator for documentation workflows
            # For now, create a placeholder that logs the action

            consolidation_report = {
                "trigger_id": trigger.trigger_id,
                "timestamp": datetime.now().isoformat(),
                "status": "placeholder_implementation",
                "message": "Documentation consolidation workflow triggered",
                "next_steps": [
                    "Implement agent-coordinator integration",
                    "Scan source directories for documentation",
                    "Create GitHub issues from local documentation",
                    "Consolidate similar topics",
                    "Update cross-references",
                ],
            }

            report_file = (
                self.logs_dir / f"hrbp_documentation_consolidation_{trigger.trigger_id}.json"
            )
            with open(report_file, "w") as f:
                json.dump(consolidation_report, f, indent=2)

            self.logger.info(f"Documentation consolidation workflow triggered: {report_file}")
            return True

        except Exception as e:
            self.logger.error(f"Documentation consolidation failed: {e}")
            return False

    def _run_cross_agent_evaluation(self, trigger: HRBPTrigger) -> bool:
        """Run cross-agent performance evaluation workflow."""
        try:
            # Placeholder for cross-agent evaluation
            evaluation_report = {
                "trigger_id": trigger.trigger_id,
                "timestamp": datetime.now().isoformat(),
                "status": "placeholder_implementation",
                "message": "Cross-agent evaluation workflow triggered",
                "evaluation_areas": [
                    "Agent collaboration effectiveness",
                    "Task delegation patterns",
                    "Communication quality",
                    "Resource utilization",
                    "Conflict resolution",
                ],
                "next_steps": [
                    "Implement agent interaction tracking",
                    "Analyze delegation patterns",
                    "Measure collaboration success rates",
                    "Identify optimization opportunities",
                ],
            }

            report_file = self.logs_dir / f"hrbp_cross_agent_evaluation_{trigger.trigger_id}.json"
            with open(report_file, "w") as f:
                json.dump(evaluation_report, f, indent=2)

            self.logger.info(f"Cross-agent evaluation workflow triggered: {report_file}")
            return True

        except Exception as e:
            self.logger.error(f"Cross-agent evaluation failed: {e}")
            return False

    def _run_performance_optimization(self, trigger: HRBPTrigger) -> bool:
        """Run performance optimization workflow."""
        try:
            # Placeholder for performance optimization
            optimization_report = {
                "trigger_id": trigger.trigger_id,
                "timestamp": datetime.now().isoformat(),
                "status": "placeholder_implementation",
                "message": "Performance optimization workflow triggered",
                "optimization_targets": [
                    "Agent response times",
                    "Resource utilization efficiency",
                    "Error rate reduction",
                    "Workflow streamlining",
                    "System integration improvements",
                ],
                "next_steps": [
                    "Analyze performance bottlenecks",
                    "Implement optimization strategies",
                    "Update agent configurations",
                    "Test performance improvements",
                    "Deploy optimizations",
                ],
            }

            report_file = self.logs_dir / f"hrbp_performance_optimization_{trigger.trigger_id}.json"
            with open(report_file, "w") as f:
                json.dump(optimization_report, f, indent=2)

            self.logger.info(f"Performance optimization workflow triggered: {report_file}")
            return True

        except Exception as e:
            self.logger.error(f"Performance optimization failed: {e}")
            return False

    def manual_trigger_hrbp_cycle(self) -> bool:
        """
        Manually trigger HRBP cycle (for emergency use).

        Returns:
            bool: True if successfully triggered, False otherwise
        """
        self.logger.info("Manual HRBP cycle trigger requested")

        counter_data = self._load_pr_counter()

        # Force trigger regardless of count
        original_cycle_count = counter_data["cycle_prs"]
        counter_data["cycle_prs"] = self.pr_threshold

        success = self._trigger_hrbp_cycle(counter_data)

        if not success:
            # Restore original count if trigger failed
            counter_data["cycle_prs"] = original_cycle_count
            self._save_pr_counter(counter_data)

        return success

    def get_cycle_status(self) -> Dict:
        """
        Get current HRBP cycle status.

        Returns:
            Dict: Current status information
        """
        counter_data = self._load_pr_counter()
        history = self._load_trigger_history()

        # Get last trigger info
        last_trigger = None
        if history:
            last_trigger = history[-1]

        status = {
            "enabled": self.enabled,
            "pr_threshold": self.pr_threshold,
            "total_prs_tracked": counter_data.get("total_prs", 0),
            "current_cycle_prs": counter_data.get("cycle_prs", 0),
            "prs_until_next_trigger": max(0, self.pr_threshold - counter_data.get("cycle_prs", 0)),
            "last_pr_number": counter_data.get("last_pr_number", 0),
            "last_trigger": last_trigger,
            "total_triggers": len(history),
        }

        return status

    def get_trigger_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent HRBP trigger history.

        Args:
            limit: Maximum number of triggers to return

        Returns:
            List[Dict]: Recent trigger records
        """
        history = self._load_trigger_history()
        return history[-limit:] if len(history) > limit else history


# Global tracker instance
_global_tracker = None


def get_hrbp_tracker() -> HRBPPRTracker:
    """Get global HRBP PR tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = HRBPPRTracker()
    return _global_tracker
