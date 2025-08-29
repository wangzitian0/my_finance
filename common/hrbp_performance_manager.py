#!/usr/bin/env python3
"""
HRBP Performance Management System

Comprehensive agent performance tracking, analytics, and coordination optimization.
Implements core HRBP automation framework for agent performance management.

Features:
- Agent capability assessment and performance tracking
- Cross-agent coordination effectiveness measurement
- Performance analytics and reporting
- Automated optimization recommendations
- Integration with 20-PR cycle automation
"""
import json
import logging
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class AgentCapabilityLevel(Enum):
    """Agent capability assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good" 
    NEEDS_IMPROVEMENT = "needs_improvement"
    CRITICAL = "critical"


class CoordinationEffectiveness(Enum):
    """Cross-agent coordination effectiveness levels."""
    HIGHLY_EFFECTIVE = "highly_effective"
    EFFECTIVE = "effective"
    MODERATELY_EFFECTIVE = "moderately_effective"
    INEFFECTIVE = "ineffective"


@dataclass
class AgentPerformanceMetrics:
    """Individual agent performance metrics."""
    agent_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time_ms: float
    success_rate: float
    error_categories: Dict[str, int]
    capability_level: str
    last_updated: str
    performance_trends: List[Dict[str, Any]]
    

@dataclass
class CoordinationMetrics:
    """Cross-agent coordination metrics."""
    coordination_id: str
    primary_agent: str
    secondary_agents: List[str]
    coordination_success: bool
    coordination_time_ms: int
    complexity_score: float
    effectiveness_level: str
    timestamp: str
    issues_identified: List[str]


@dataclass
class PerformanceOptimizationRecommendation:
    """Performance optimization recommendation."""
    recommendation_id: str
    agent_name: str
    priority: str  # "critical", "high", "medium", "low"
    category: str  # "performance", "coordination", "capability", "reliability"
    description: str
    current_metrics: Dict[str, Any]
    target_metrics: Dict[str, Any]
    implementation_steps: List[str]
    estimated_impact: str
    timestamp: str


class HRBPPerformanceManager:
    """
    Comprehensive HRBP Performance Management System.
    
    Manages agent performance tracking, coordination optimization,
    and automated performance analytics for the multi-agent ecosystem.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize HRBP Performance Manager."""
        # Use centralized DirectoryManager for SSOT compliance
        from .directory_manager import directory_manager
        
        self.logs_dir = directory_manager.get_logs_path()
        self.config_dir = directory_manager.get_config_path()
        
        # Load configuration
        if config_path is None:
            config_path = self.config_dir / "hrbp_automation.yml"
        
        self.config = self._load_config(config_path)
        
        # Initialize file paths
        self.performance_data_file = self.logs_dir / "agent_performance_data.json"
        self.coordination_data_file = self.logs_dir / "coordination_metrics.json" 
        self.optimization_history_file = self.logs_dir / "optimization_history.json"
        
        # Performance thresholds from config
        self.performance_thresholds = self.config.get('agent_performance', {})
        
        # Setup logging
        self._setup_logging()
        
        # Ensure data directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Agent registry (loaded from agent configurations)
        self.agent_registry = self._load_agent_registry()
    
    def _load_config(self, config_path: Path) -> Dict:
        """Load HRBP automation configuration."""
        if not YAML_AVAILABLE:
            return self._get_default_config()
            
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"⚠️  HRBP config file not found: {config_path}, using defaults")
            return self._get_default_config()
        except Exception as e:
            print(f"⚠️  Failed to load HRBP config: {e}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration."""
        return {
            'agent_performance': {
                'success_rate_minimum': 0.85,
                'average_execution_time_max': 30000,
                'error_categories': {
                    'critical_max': 0,
                    'high_max': 2,
                    'medium_max': 5
                }
            },
            'coordination': {
                'max_coordination_time_ms': 60000,
                'min_effectiveness_threshold': 0.80,
                'parallel_execution_optimization': True
            },
            'optimization': {
                'recommendation_retention_days': 90,
                'auto_optimization_enabled': True,
                'performance_monitoring_interval_hours': 6
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.logs_dir / "hrbp_performance_manager.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_agent_registry(self) -> Dict[str, Dict]:
        """Load agent registry from .claude/agents/ directory."""
        agents_dir = Path(self.config_dir).parent.parent / ".claude" / "agents"
        agent_registry = {}
        
        if not agents_dir.exists():
            self.logger.warning(f"Agents directory not found: {agents_dir}")
            return {}
        
        for agent_file in agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            try:
                with open(agent_file, 'r') as f:
                    content = f.read()
                    # Parse basic agent info from markdown frontmatter
                    if content.startswith('---'):
                        frontmatter_end = content.find('---', 3)
                        if frontmatter_end > 0:
                            frontmatter = content[3:frontmatter_end]
                            agent_info = {}
                            for line in frontmatter.split('\n'):
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    agent_info[key.strip()] = value.strip()
                            agent_registry[agent_name] = agent_info
            except Exception as e:
                self.logger.error(f"Failed to parse agent file {agent_file}: {e}")
        
        self.logger.info(f"Loaded {len(agent_registry)} agents from registry")
        return agent_registry
    
    def collect_agent_performance_data(self, days: int = 30) -> Dict[str, AgentPerformanceMetrics]:
        """
        Collect comprehensive performance data for all agents.
        
        Args:
            days: Number of days of historical data to analyze
            
        Returns:
            Dict mapping agent names to their performance metrics
        """
        self.logger.info(f"Collecting agent performance data for last {days} days")
        
        try:
            from .execution_monitor import get_monitor
            monitor = get_monitor()
            
            # Get execution statistics
            stats = monitor.get_execution_stats(days=days)
            
            # Process per-agent performance
            agent_performance = {}
            agent_stats = stats.get('agent_performance', {})
            
            for agent_name in self.agent_registry.keys():
                if agent_name in agent_stats:
                    agent_data = agent_stats[agent_name]
                    total = agent_data['total']
                    success = agent_data['success']
                    failure = agent_data['failure']
                    success_rate = success / max(total, 1)
                    
                    # Calculate average execution time (placeholder - needs actual timing data)
                    avg_time = stats.get('average_execution_time_ms', 0)
                    
                    # Determine capability level
                    capability_level = self._assess_capability_level(success_rate, avg_time)
                    
                    # Generate performance trends (placeholder)
                    performance_trends = self._generate_performance_trends(agent_name, days)
                    
                    metrics = AgentPerformanceMetrics(
                        agent_name=agent_name,
                        total_executions=total,
                        successful_executions=success,
                        failed_executions=failure,
                        average_execution_time_ms=avg_time,
                        success_rate=success_rate,
                        error_categories=stats.get('error_categories', {}),
                        capability_level=capability_level.value,
                        last_updated=datetime.now().isoformat(),
                        performance_trends=performance_trends
                    )
                    
                    agent_performance[agent_name] = metrics
                else:
                    # Create placeholder metrics for agents with no execution data
                    metrics = AgentPerformanceMetrics(
                        agent_name=agent_name,
                        total_executions=0,
                        successful_executions=0,
                        failed_executions=0,
                        average_execution_time_ms=0,
                        success_rate=0.0,
                        error_categories={},
                        capability_level=AgentCapabilityLevel.NEEDS_IMPROVEMENT.value,
                        last_updated=datetime.now().isoformat(),
                        performance_trends=[]
                    )
                    
                    agent_performance[agent_name] = metrics
            
            # Save performance data
            self._save_performance_data(agent_performance)
            
            return agent_performance
            
        except Exception as e:
            self.logger.error(f"Failed to collect agent performance data: {e}")
            return {}
    
    def _assess_capability_level(self, success_rate: float, avg_time_ms: float) -> AgentCapabilityLevel:
        """Assess agent capability level based on performance metrics."""
        min_success_rate = self.performance_thresholds.get('success_rate_minimum', 0.85)
        max_avg_time = self.performance_thresholds.get('average_execution_time_max', 30000)
        
        # Critical: Very low success rate or extremely slow
        if success_rate < 0.5 or avg_time_ms > max_avg_time * 2:
            return AgentCapabilityLevel.CRITICAL
        
        # Needs improvement: Below thresholds
        if success_rate < min_success_rate or avg_time_ms > max_avg_time:
            return AgentCapabilityLevel.NEEDS_IMPROVEMENT
        
        # Good: Meets basic requirements
        if success_rate >= min_success_rate and avg_time_ms <= max_avg_time:
            # Excellent: Exceeds requirements significantly
            if success_rate > 0.95 and avg_time_ms < max_avg_time * 0.5:
                return AgentCapabilityLevel.EXCELLENT
            return AgentCapabilityLevel.GOOD
        
        return AgentCapabilityLevel.NEEDS_IMPROVEMENT
    
    def _generate_performance_trends(self, agent_name: str, days: int) -> List[Dict[str, Any]]:
        """Generate performance trend data for an agent."""
        # Placeholder implementation - would need historical data collection
        trends = []
        for i in range(min(days, 30)):  # Last 30 data points max
            date = datetime.now() - timedelta(days=i)
            trends.append({
                'date': date.isoformat().split('T')[0],
                'success_rate': 0.85 + (i * 0.01),  # Placeholder trend
                'execution_time_ms': 25000 - (i * 100),  # Placeholder trend
                'total_executions': max(1, 10 - i)  # Placeholder
            })
        return trends
    
    def _save_performance_data(self, performance_data: Dict[str, AgentPerformanceMetrics]):
        """Save performance data to file."""
        try:
            serializable_data = {}
            for agent_name, metrics in performance_data.items():
                serializable_data[agent_name] = asdict(metrics)
            
            with open(self.performance_data_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'agent_performance': serializable_data
                }, f, indent=2)
                
            self.logger.info(f"Saved performance data for {len(performance_data)} agents")
        except Exception as e:
            self.logger.error(f"Failed to save performance data: {e}")
    
    def analyze_coordination_patterns(self, days: int = 30) -> List[CoordinationMetrics]:
        """
        Analyze cross-agent coordination patterns and effectiveness.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of coordination metrics
        """
        self.logger.info(f"Analyzing coordination patterns for last {days} days")
        
        # Placeholder implementation - would need actual coordination tracking
        coordination_metrics = []
        
        # Simulate coordination analysis based on common agent interactions
        common_interactions = [
            ("agent-coordinator", ["git-ops-agent", "dev-quality-agent"]),
            ("git-ops-agent", ["dev-quality-agent", "infra-ops-agent"]),
            ("data-engineer-agent", ["monitoring-agent", "infra-ops-agent"]),
            ("quant-research-agent", ["data-engineer-agent", "compliance-risk-agent"]),
            ("hrbp-agent", ["agent-coordinator", "revops-agent"])
        ]
        
        for primary, secondaries in common_interactions:
            if primary in self.agent_registry:
                # Simulate coordination metrics
                coordination_id = f"coord_{primary}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Calculate effectiveness based on success rates
                effectiveness = self._calculate_coordination_effectiveness(primary, secondaries)
                
                metrics = CoordinationMetrics(
                    coordination_id=coordination_id,
                    primary_agent=primary,
                    secondary_agents=secondaries,
                    coordination_success=effectiveness > 0.75,
                    coordination_time_ms=int(45000 * (1.1 - effectiveness)),  # Better coordination = faster
                    complexity_score=len(secondaries) * 0.3,
                    effectiveness_level=self._get_effectiveness_level(effectiveness).value,
                    timestamp=datetime.now().isoformat(),
                    issues_identified=self._identify_coordination_issues(effectiveness)
                )
                
                coordination_metrics.append(metrics)
        
        # Save coordination data
        self._save_coordination_data(coordination_metrics)
        
        return coordination_metrics
    
    def _calculate_coordination_effectiveness(self, primary: str, secondaries: List[str]) -> float:
        """Calculate coordination effectiveness between agents."""
        # Load current performance data
        performance_data = self._load_performance_data()
        
        # Base effectiveness on success rates of involved agents
        all_agents = [primary] + secondaries
        success_rates = []
        
        for agent in all_agents:
            if agent in performance_data:
                success_rates.append(performance_data[agent]['success_rate'])
            else:
                success_rates.append(0.5)  # Default for unknown agents
        
        if not success_rates:
            return 0.5
        
        # Coordination effectiveness is based on minimum success rate (weakest link)
        # and average success rate (overall capability)
        min_success = min(success_rates)
        avg_success = sum(success_rates) / len(success_rates)
        
        # Weight: 60% minimum (bottleneck), 40% average (overall)
        effectiveness = 0.6 * min_success + 0.4 * avg_success
        
        return min(1.0, max(0.0, effectiveness))
    
    def _get_effectiveness_level(self, effectiveness: float) -> CoordinationEffectiveness:
        """Convert effectiveness score to level."""
        if effectiveness >= 0.90:
            return CoordinationEffectiveness.HIGHLY_EFFECTIVE
        elif effectiveness >= 0.75:
            return CoordinationEffectiveness.EFFECTIVE
        elif effectiveness >= 0.60:
            return CoordinationEffectiveness.MODERATELY_EFFECTIVE
        else:
            return CoordinationEffectiveness.INEFFECTIVE
    
    def _identify_coordination_issues(self, effectiveness: float) -> List[str]:
        """Identify potential coordination issues based on effectiveness."""
        issues = []
        
        if effectiveness < 0.5:
            issues.append("Critical coordination failure - requires immediate attention")
        
        if effectiveness < 0.7:
            issues.append("Agent performance disparity affecting coordination")
        
        if effectiveness < 0.8:
            issues.append("Communication delays between agents")
        
        if effectiveness < 0.9:
            issues.append("Minor optimization opportunities available")
        
        return issues
    
    def _save_coordination_data(self, coordination_data: List[CoordinationMetrics]):
        """Save coordination metrics to file."""
        try:
            serializable_data = [asdict(metrics) for metrics in coordination_data]
            
            with open(self.coordination_data_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'coordination_metrics': serializable_data
                }, f, indent=2)
                
            self.logger.info(f"Saved coordination data for {len(coordination_data)} interactions")
        except Exception as e:
            self.logger.error(f"Failed to save coordination data: {e}")
    
    def _load_performance_data(self) -> Dict:
        """Load saved performance data."""
        if not self.performance_data_file.exists():
            return {}
        
        try:
            with open(self.performance_data_file, 'r') as f:
                data = json.load(f)
                return data.get('agent_performance', {})
        except Exception as e:
            self.logger.error(f"Failed to load performance data: {e}")
            return {}
    
    def generate_optimization_recommendations(
        self, 
        performance_data: Dict[str, AgentPerformanceMetrics],
        coordination_data: List[CoordinationMetrics]
    ) -> List[PerformanceOptimizationRecommendation]:
        """
        Generate comprehensive performance optimization recommendations.
        
        Args:
            performance_data: Agent performance metrics
            coordination_data: Coordination effectiveness metrics
            
        Returns:
            List of optimization recommendations
        """
        self.logger.info("Generating performance optimization recommendations")
        
        recommendations = []
        recommendation_counter = 0
        
        # Agent-specific performance recommendations
        for agent_name, metrics in performance_data.items():
            recommendation_counter += 1
            
            # Performance-based recommendations
            if metrics.success_rate < self.performance_thresholds.get('success_rate_minimum', 0.85):
                rec_id = f"perf_rec_{recommendation_counter:03d}"
                
                recommendations.append(PerformanceOptimizationRecommendation(
                    recommendation_id=rec_id,
                    agent_name=agent_name,
                    priority="high" if metrics.success_rate < 0.7 else "medium",
                    category="performance",
                    description=f"Improve success rate from {metrics.success_rate:.2%} to meet minimum threshold",
                    current_metrics={"success_rate": metrics.success_rate},
                    target_metrics={"success_rate": self.performance_thresholds['success_rate_minimum']},
                    implementation_steps=[
                        "Analyze recent failure patterns and error categories",
                        "Review agent configuration and capability definitions",
                        "Implement additional error handling and retry logic",
                        "Enhance agent testing and validation procedures",
                        "Monitor performance improvements over next 2 weeks"
                    ],
                    estimated_impact=f"Reduce failure rate by {(self.performance_thresholds['success_rate_minimum'] - metrics.success_rate) * 100:.1f}%",
                    timestamp=datetime.now().isoformat()
                ))
                
                recommendation_counter += 1
            
            # Response time recommendations
            max_time = self.performance_thresholds.get('average_execution_time_max', 30000)
            if metrics.average_execution_time_ms > max_time:
                rec_id = f"perf_rec_{recommendation_counter:03d}"
                
                recommendations.append(PerformanceOptimizationRecommendation(
                    recommendation_id=rec_id,
                    agent_name=agent_name,
                    priority="medium",
                    category="performance",
                    description=f"Reduce execution time from {metrics.average_execution_time_ms:.0f}ms to under {max_time}ms",
                    current_metrics={"execution_time_ms": metrics.average_execution_time_ms},
                    target_metrics={"execution_time_ms": max_time},
                    implementation_steps=[
                        "Profile agent execution to identify bottlenecks",
                        "Optimize expensive operations and reduce I/O overhead",
                        "Implement caching for frequently used data",
                        "Review and optimize agent algorithms",
                        "Consider parallel processing for suitable tasks"
                    ],
                    estimated_impact=f"Reduce execution time by {metrics.average_execution_time_ms - max_time:.0f}ms",
                    timestamp=datetime.now().isoformat()
                ))
                
                recommendation_counter += 1
        
        # Coordination-based recommendations
        ineffective_coordinations = [
            coord for coord in coordination_data 
            if coord.effectiveness_level in ['ineffective', 'moderately_effective']
        ]
        
        for coord_metrics in ineffective_coordinations:
            recommendation_counter += 1
            rec_id = f"coord_rec_{recommendation_counter:03d}"
            
            recommendations.append(PerformanceOptimizationRecommendation(
                recommendation_id=rec_id,
                agent_name=coord_metrics.primary_agent,
                priority="high" if coord_metrics.effectiveness_level == 'ineffective' else "medium",
                category="coordination",
                description=f"Improve coordination effectiveness with {', '.join(coord_metrics.secondary_agents)}",
                current_metrics={"coordination_time_ms": coord_metrics.coordination_time_ms},
                target_metrics={"coordination_time_ms": coord_metrics.coordination_time_ms * 0.8},
                implementation_steps=[
                    "Review coordination protocols between agents",
                    "Implement parallel execution where possible",
                    "Optimize data sharing and communication patterns",
                    "Add coordination monitoring and metrics",
                    "Test coordination improvements with sample workflows"
                ],
                estimated_impact=f"Improve coordination effectiveness by 20-30%",
                timestamp=datetime.now().isoformat()
            ))
        
        # System-wide recommendations
        if recommendations:
            recommendation_counter += 1
            rec_id = f"system_rec_{recommendation_counter:03d}"
            
            recommendations.append(PerformanceOptimizationRecommendation(
                recommendation_id=rec_id,
                agent_name="system-wide",
                priority="low",
                category="capability",
                description="Implement systematic performance monitoring and alerting",
                current_metrics={"monitored_agents": len(performance_data)},
                target_metrics={"monitored_agents": len(self.agent_registry)},
                implementation_steps=[
                    "Enable real-time performance dashboards",
                    "Set up automated alerting for performance degradation",
                    "Implement trending analysis for early problem detection",
                    "Create performance baseline documentation",
                    "Schedule regular performance review cycles"
                ],
                estimated_impact="Proactive identification of performance issues",
                timestamp=datetime.now().isoformat()
            ))
        
        # Save recommendations
        self._save_optimization_recommendations(recommendations)
        
        self.logger.info(f"Generated {len(recommendations)} optimization recommendations")
        return recommendations
    
    def _save_optimization_recommendations(self, recommendations: List[PerformanceOptimizationRecommendation]):
        """Save optimization recommendations to file."""
        try:
            serializable_data = [asdict(rec) for rec in recommendations]
            
            # Load existing history
            history = []
            if self.optimization_history_file.exists():
                with open(self.optimization_history_file, 'r') as f:
                    history_data = json.load(f)
                    history = history_data.get('recommendations_history', [])
            
            # Add new recommendations to history
            history.append({
                'timestamp': datetime.now().isoformat(),
                'recommendations': serializable_data
            })
            
            # Keep only recent history (90 days by default)
            retention_days = self.config.get('optimization', {}).get('recommendation_retention_days', 90)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            history = [
                entry for entry in history
                if datetime.fromisoformat(entry['timestamp']) > cutoff_date
            ]
            
            # Save updated history
            with open(self.optimization_history_file, 'w') as f:
                json.dump({
                    'last_updated': datetime.now().isoformat(),
                    'recommendations_history': history
                }, f, indent=2)
                
            self.logger.info(f"Saved {len(recommendations)} optimization recommendations to history")
            
        except Exception as e:
            self.logger.error(f"Failed to save optimization recommendations: {e}")
    
    def run_comprehensive_performance_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Run comprehensive performance analysis covering all HRBP responsibilities.
        
        Args:
            days: Number of days of historical data to analyze
            
        Returns:
            Comprehensive analysis report
        """
        self.logger.info("Starting comprehensive HRBP performance analysis")
        
        analysis_start_time = time.time()
        
        try:
            # 1. Collect agent performance data
            performance_data = self.collect_agent_performance_data(days)
            
            # 2. Analyze coordination patterns  
            coordination_data = self.analyze_coordination_patterns(days)
            
            # 3. Generate optimization recommendations
            recommendations = self.generate_optimization_recommendations(performance_data, coordination_data)
            
            # 4. Calculate system-wide metrics
            system_metrics = self._calculate_system_metrics(performance_data, coordination_data)
            
            # 5. Generate executive summary
            executive_summary = self._generate_executive_summary(
                performance_data, coordination_data, recommendations, system_metrics
            )
            
            analysis_time = time.time() - analysis_start_time
            
            # Compile comprehensive report
            report = {
                'analysis_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'analysis_period_days': days,
                    'analysis_duration_seconds': round(analysis_time, 2),
                    'total_agents_analyzed': len(performance_data),
                    'total_coordination_patterns': len(coordination_data),
                    'total_recommendations': len(recommendations)
                },
                'executive_summary': executive_summary,
                'system_metrics': system_metrics,
                'agent_performance': {name: asdict(metrics) for name, metrics in performance_data.items()},
                'coordination_analysis': [asdict(coord) for coord in coordination_data],
                'optimization_recommendations': [asdict(rec) for rec in recommendations]
            }
            
            # Save comprehensive report
            report_file = self.logs_dir / f"hrbp_comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Comprehensive performance analysis completed in {analysis_time:.2f}s")
            self.logger.info(f"Report saved to: {report_file}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Comprehensive performance analysis failed: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'analysis_status': 'failed'
            }
    
    def _calculate_system_metrics(
        self, 
        performance_data: Dict[str, AgentPerformanceMetrics],
        coordination_data: List[CoordinationMetrics]
    ) -> Dict[str, Any]:
        """Calculate system-wide performance metrics."""
        if not performance_data:
            return {'error': 'No performance data available'}
        
        # Overall success rates
        success_rates = [metrics.success_rate for metrics in performance_data.values()]
        overall_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        
        # Execution time statistics
        execution_times = [metrics.average_execution_time_ms for metrics in performance_data.values() if metrics.average_execution_time_ms > 0]
        avg_execution_time = statistics.mean(execution_times) if execution_times else 0
        median_execution_time = statistics.median(execution_times) if execution_times else 0
        
        # Capability distribution
        capability_distribution = {}
        for metrics in performance_data.values():
            level = metrics.capability_level
            capability_distribution[level] = capability_distribution.get(level, 0) + 1
        
        # Coordination effectiveness
        coordination_effectiveness = []
        if coordination_data:
            coordination_effectiveness = [
                1.0 if coord.coordination_success else 0.0 
                for coord in coordination_data
            ]
        
        avg_coordination_effectiveness = (
            sum(coordination_effectiveness) / len(coordination_effectiveness) 
            if coordination_effectiveness else 0
        )
        
        return {
            'overall_success_rate': overall_success_rate,
            'average_execution_time_ms': avg_execution_time,
            'median_execution_time_ms': median_execution_time,
            'capability_distribution': capability_distribution,
            'coordination_effectiveness': avg_coordination_effectiveness,
            'total_agents_active': len([m for m in performance_data.values() if m.total_executions > 0]),
            'total_agents_registered': len(self.agent_registry),
            'agents_needing_attention': len([
                m for m in performance_data.values() 
                if m.capability_level in ['critical', 'needs_improvement']
            ])
        }
    
    def _generate_executive_summary(
        self,
        performance_data: Dict[str, AgentPerformanceMetrics],
        coordination_data: List[CoordinationMetrics],
        recommendations: List[PerformanceOptimizationRecommendation],
        system_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary for HRBP report."""
        # Count high-priority issues
        high_priority_recs = len([r for r in recommendations if r.priority in ['critical', 'high']])
        critical_agents = len([
            m for m in performance_data.values() 
            if m.capability_level == 'critical'
        ])
        
        # Performance highlights
        best_performers = sorted(
            performance_data.values(),
            key=lambda x: x.success_rate,
            reverse=True
        )[:3]
        
        # Areas needing attention
        needs_attention = [
            m for m in performance_data.values()
            if m.capability_level in ['critical', 'needs_improvement']
        ]
        
        return {
            'overall_health_status': self._determine_overall_health(system_metrics),
            'key_metrics': {
                'system_success_rate': f"{system_metrics.get('overall_success_rate', 0):.1%}",
                'average_response_time': f"{system_metrics.get('average_execution_time_ms', 0):.0f}ms",
                'coordination_effectiveness': f"{system_metrics.get('coordination_effectiveness', 0):.1%}",
                'agents_active': system_metrics.get('total_agents_active', 0)
            },
            'performance_highlights': [
                f"{agent.agent_name}: {agent.success_rate:.1%} success rate"
                for agent in best_performers
            ],
            'attention_required': {
                'critical_agents': critical_agents,
                'high_priority_recommendations': high_priority_recs,
                'agents_needing_improvement': [agent.agent_name for agent in needs_attention]
            },
            'top_recommendations': [
                {
                    'agent': rec.agent_name,
                    'priority': rec.priority,
                    'description': rec.description
                }
                for rec in sorted(recommendations, key=lambda x: ['critical', 'high', 'medium', 'low'].index(x.priority))[:5]
            ]
        }
    
    def _determine_overall_health(self, system_metrics: Dict[str, Any]) -> str:
        """Determine overall system health status."""
        success_rate = system_metrics.get('overall_success_rate', 0)
        coordination_effectiveness = system_metrics.get('coordination_effectiveness', 0)
        agents_needing_attention = system_metrics.get('agents_needing_attention', 0)
        
        if success_rate >= 0.95 and coordination_effectiveness >= 0.90 and agents_needing_attention == 0:
            return "excellent"
        elif success_rate >= 0.85 and coordination_effectiveness >= 0.80 and agents_needing_attention <= 2:
            return "good"
        elif success_rate >= 0.70 and coordination_effectiveness >= 0.60 and agents_needing_attention <= 5:
            return "needs_attention"
        else:
            return "critical"


# Global manager instance
_global_performance_manager = None


def get_hrbp_performance_manager() -> HRBPPerformanceManager:
    """Get global HRBP performance manager instance."""
    global _global_performance_manager
    if _global_performance_manager is None:
        _global_performance_manager = HRBPPerformanceManager()
    return _global_performance_manager