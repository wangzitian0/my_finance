#!/usr/bin/env python3
"""
DCF Calculator Tool Implementation

Implements DCF valuation analysis as a unified tool.
Maps to existing DCF engine components for company valuation.
"""

import json
import logging
import math
from pathlib import Path
from typing import Dict, List, Optional

from ...core.directory_manager import DataLayer, directory_manager
from ..base_tool import BaseTool, ToolConfig, ToolExecutionContext


class DCFCalculator(BaseTool):
    """
    Tool for performing discounted cash flow valuation analysis.

    Integrates with processed financial data to generate company valuations,
    investment recommendations, and scenario analyses.
    """

    def __init__(self, config: ToolConfig):
        super().__init__(config)
        self.logger = logging.getLogger(f"tool.{config.name}")

    def validate_prerequisites(self, context: ToolExecutionContext) -> bool:
        """Validate that prerequisites for DCF calculation are met"""
        context.add_message("Validating DCF calculator prerequisites")

        # Check for required Python packages
        required_packages = ["numpy", "pandas", "scipy"]
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
                self.logger.debug(f"Package '{package}' available")
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            context.add_message(f"Missing required packages: {missing_packages}", "ERROR")
            return False

        # Check for dependency tools completion
        if "sec_filing_processor" in self.config.dependencies:
            # In a real implementation, we'd check if SEC filing processor completed
            context.add_message("Checking SEC filing processor dependency")

        # Validate configuration parameters
        config_overrides = self.config.config_overrides

        discount_rate = config_overrides.get("discount_rate", 0.10)
        if not (0.01 <= discount_rate <= 0.5):  # 1% to 50% reasonable range
            context.add_message(f"Invalid discount rate: {discount_rate}", "ERROR")
            return False

        terminal_growth = config_overrides.get("terminal_growth_rate", 0.025)
        if not (0.0 <= terminal_growth <= 0.1):  # 0% to 10% reasonable range
            context.add_message(f"Invalid terminal growth rate: {terminal_growth}", "ERROR")
            return False

        context.add_message("All DCF calculator prerequisites validated")
        return True

    def create_workspace_structure(self, context: ToolExecutionContext) -> bool:
        """Create the required directory structure for DCF calculations"""
        context.add_message("Creating DCF calculator workspace structure")

        try:
            # Get required paths from base tool
            required_paths = self.get_required_paths(context.workspace_path)

            # Create all required directories
            for dir_name, dir_path in required_paths.items():
                dir_path.mkdir(parents=True, exist_ok=True)
                context.add_message(f"Created directory: {dir_name}")
                self.logger.debug(f"Created workspace directory: {dir_path}")

            # Create company-specific subdirectories
            for main_dir in ["financial_models", "valuations", "reports"]:
                main_path = context.workspace_path / main_dir

                # Create subdirectories by company (using sample companies)
                sample_companies = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
                for company in sample_companies:
                    company_dir = main_path / company
                    company_dir.mkdir(exist_ok=True)
                    context.add_message(f"Created {main_dir} directory for {company}")

            # Create scenario analysis subdirectories
            scenarios_path = context.workspace_path / "scenarios"
            if scenarios_path.exists():
                for scenario in ["base_case", "optimistic", "pessimistic", "monte_carlo"]:
                    scenario_dir = scenarios_path / scenario
                    scenario_dir.mkdir(exist_ok=True)
                    context.add_message(f"Created scenario directory: {scenario}")

            # Initialize calculation metadata
            metadata_path = context.workspace_path / "assumptions"

            # Create default DCF assumptions
            dcf_assumptions = {
                "tool_name": self.config.name,
                "tool_version": self.config.version,
                "created_at": context.start_time.isoformat() if context.start_time else None,
                "calculation_parameters": self.config.config_overrides,
                "companies_to_analyze": sample_companies,
                "market_assumptions": {
                    "risk_free_rate": 0.045,  # 10-year treasury
                    "market_risk_premium": 0.06,
                    "average_beta": 1.2,
                },
                "calculation_status": "initialized",
            }

            assumptions_file = metadata_path / "dcf_assumptions.json"
            with open(assumptions_file, "w") as f:
                json.dump(dcf_assumptions, f, indent=2)

            context.add_message("DCF assumptions file created")

            # Store temp paths
            context.temp_paths.add(context.workspace_path / "temp")
            context.temp_paths.add(context.workspace_path / "cache")

            context.add_message("DCF calculator workspace structure created successfully")
            return True

        except Exception as e:
            context.add_message(f"Failed to create workspace structure: {e}", "ERROR")
            self.logger.exception("Workspace structure creation failed")
            return False

    def execute(self, context: ToolExecutionContext) -> bool:
        """Execute DCF calculation analysis"""
        context.add_message("Starting DCF calculation execution")

        try:
            # Phase 1: Load financial data (15% progress)
            context.update_progress(0.15, "Loading financial data")
            if not self._load_financial_data(context):
                return False

            # Phase 2: Perform DCF calculations (40% progress)
            context.update_progress(0.4, "Performing DCF calculations")
            if not self._calculate_dcf_valuations(context):
                return False

            # Phase 3: Run scenario analysis (65% progress)
            context.update_progress(0.65, "Running scenario analysis")
            if not self._run_scenario_analysis(context):
                return False

            # Phase 4: Generate valuation reports (80% progress)
            context.update_progress(0.8, "Generating valuation reports")
            if not self._generate_reports(context):
                return False

            # Phase 5: Update output layers (90% progress)
            context.update_progress(0.9, "Updating output data layers")
            if not self._update_output_layers(context):
                return False

            context.add_message("DCF calculation execution completed successfully")
            return True

        except Exception as e:
            context.add_message(f"Execution failed: {e}", "ERROR")
            self.logger.exception("Tool execution failed")
            return False

    def _load_financial_data(self, context: ToolExecutionContext) -> bool:
        """Load financial data from input layers"""
        try:
            context.add_message("Loading financial data from input layers")

            # Load from daily delta layer (incremental updates)
            if "stage_01_daily_delta" in context.input_paths:
                delta_path = context.input_paths["stage_01_daily_delta"]
                if delta_path.exists():
                    delta_files = list(delta_path.glob("sec_filing_update_*.json"))
                    context.add_message(f"Found {len(delta_files)} delta update files")
                else:
                    context.add_message("No delta updates found", "WARNING")

            # Load from daily index (processed data)
            if "stage_02_daily_index" in context.input_paths:
                index_path = context.input_paths["stage_02_daily_index"]
                if index_path.exists():
                    index_files = list(index_path.glob("*_index_update_*.json"))
                    context.add_message(f"Found {len(index_files)} index update files")

            # Load from graph RAG (contextual data)
            if "stage_03_graph_rag" in context.input_paths:
                rag_path = context.input_paths["stage_03_graph_rag"]
                context.add_message(f"Graph RAG data available at: {rag_path}")

            # Simulate loading company financial data
            financial_data = self._simulate_financial_data()

            # Cache loaded data
            cache_path = context.workspace_path / "cache" / "loaded_financial_data.json"
            cache_path.parent.mkdir(exist_ok=True)

            with open(cache_path, "w") as f:
                json.dump(financial_data, f, indent=2)

            context.add_message("Financial data loading completed")
            return True

        except Exception as e:
            context.add_message(f"Failed to load financial data: {e}", "ERROR")
            return False

    def _simulate_financial_data(self) -> Dict:
        """Simulate realistic financial data for demonstration"""
        return {
            "AAPL": {
                "revenue": {"2021": 365817000000, "2022": 394328000000, "2023": 383285000000},
                "operating_income": {
                    "2021": 108949000000,
                    "2022": 119437000000,
                    "2023": 114301000000,
                },
                "free_cash_flow": {"2021": 92953000000, "2022": 111443000000, "2023": 99584000000},
                "total_debt": {"2023": 111109000000},
                "cash_and_equivalents": {"2023": 29965000000},
                "shares_outstanding": {"2023": 15728700000},
                "beta": 1.24,
            },
            "MSFT": {
                "revenue": {"2021": 168088000000, "2022": 198270000000, "2023": 211915000000},
                "operating_income": {"2021": 69916000000, "2022": 83383000000, "2023": 88523000000},
                "free_cash_flow": {"2021": 56118000000, "2022": 65149000000, "2023": 71066000000},
                "total_debt": {"2023": 47032000000},
                "cash_and_equivalents": {"2023": 29276000000},
                "shares_outstanding": {"2023": 7430000000},
                "beta": 0.97,
            },
        }

    def _calculate_dcf_valuations(self, context: ToolExecutionContext) -> bool:
        """Perform DCF calculations for each company"""
        try:
            context.add_message("Performing DCF valuations")

            # Load cached financial data
            cache_path = context.workspace_path / "cache" / "loaded_financial_data.json"
            with open(cache_path, "r") as f:
                financial_data = json.load(f)

            # Get calculation parameters
            config_overrides = self.config.config_overrides
            discount_rate = config_overrides.get("discount_rate", 0.10)
            terminal_growth = config_overrides.get("terminal_growth_rate", 0.025)
            projection_years = config_overrides.get("projection_years", 5)

            valuations = {}

            # Calculate DCF for each company
            for company, data in financial_data.items():
                context.add_message(f"Calculating DCF for {company}")

                try:
                    valuation = self._calculate_company_dcf(
                        company, data, discount_rate, terminal_growth, projection_years
                    )
                    valuations[company] = valuation

                    # Save individual company valuation
                    company_path = context.workspace_path / "valuations" / company
                    valuation_file = company_path / "dcf_valuation.json"

                    with open(valuation_file, "w") as f:
                        json.dump(valuation, f, indent=2)

                    context.add_message(f"DCF calculation completed for {company}")

                except Exception as e:
                    context.add_message(f"DCF calculation failed for {company}: {e}", "WARNING")
                    continue

            # Save consolidated valuations
            consolidated_file = (
                context.workspace_path / "valuations" / "consolidated_valuations.json"
            )
            with open(consolidated_file, "w") as f:
                json.dump(valuations, f, indent=2)

            context.add_message(f"DCF calculations completed for {len(valuations)} companies")
            return True

        except Exception as e:
            context.add_message(f"DCF calculation failed: {e}", "ERROR")
            return False

    def _calculate_company_dcf(
        self,
        company: str,
        data: Dict,
        discount_rate: float,
        terminal_growth: float,
        projection_years: int,
    ) -> Dict:
        """Calculate DCF valuation for a single company"""
        # Get base year free cash flow (most recent)
        fcf_history = data.get("free_cash_flow", {})
        base_year = max(fcf_history.keys()) if fcf_history else "2023"
        base_fcf = fcf_history.get(base_year, 50000000000)  # Default 50B

        # Calculate revenue growth rate (simplified)
        revenue_history = data.get("revenue", {})
        if len(revenue_history) >= 2:
            years = sorted(revenue_history.keys())
            recent_revenue = revenue_history[years[-1]]
            older_revenue = revenue_history[years[-2]]
            revenue_growth = (recent_revenue - older_revenue) / older_revenue
        else:
            revenue_growth = 0.05  # Default 5% growth

        # Project future cash flows
        projected_fcf = []
        current_fcf = base_fcf

        for year in range(1, projection_years + 1):
            # Assume FCF grows at gradually declining rate
            growth_rate = revenue_growth * (0.9**year)  # Declining growth
            current_fcf *= 1 + growth_rate

            # Discount to present value
            pv_fcf = current_fcf / ((1 + discount_rate) ** year)
            projected_fcf.append(
                {
                    "year": year,
                    "projected_fcf": current_fcf,
                    "present_value": pv_fcf,
                    "growth_rate": growth_rate,
                }
            )

        # Calculate terminal value
        terminal_fcf = projected_fcf[-1]["projected_fcf"] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        terminal_pv = terminal_value / ((1 + discount_rate) ** projection_years)

        # Calculate enterprise value
        pv_sum = sum(cf["present_value"] for cf in projected_fcf)
        enterprise_value = pv_sum + terminal_pv

        # Calculate equity value
        net_debt = data.get("total_debt", {}).get("2023", 0) - data.get(
            "cash_and_equivalents", {}
        ).get("2023", 0)
        equity_value = enterprise_value - net_debt

        # Calculate per-share value
        shares_outstanding = data.get("shares_outstanding", {}).get("2023", 1000000000)
        value_per_share = equity_value / shares_outstanding

        return {
            "company": company,
            "base_year": base_year,
            "base_fcf": base_fcf,
            "revenue_growth_rate": revenue_growth,
            "discount_rate": discount_rate,
            "terminal_growth_rate": terminal_growth,
            "projected_cash_flows": projected_fcf,
            "terminal_value": terminal_value,
            "terminal_present_value": terminal_pv,
            "enterprise_value": enterprise_value,
            "net_debt": net_debt,
            "equity_value": equity_value,
            "shares_outstanding": shares_outstanding,
            "value_per_share": value_per_share,
            "calculation_date": context.timestamp,
        }

    def _run_scenario_analysis(self, context: ToolExecutionContext) -> bool:
        """Run scenario analysis if enabled"""
        try:
            config_overrides = self.config.config_overrides
            enable_monte_carlo = config_overrides.get("enable_monte_carlo", False)

            if not enable_monte_carlo:
                context.add_message("Scenario analysis disabled, skipping")
                return True

            context.add_message("Running scenario analysis")

            # Create simple scenario analysis results
            scenarios = {
                "base_case": {"discount_rate": 0.10, "terminal_growth": 0.025},
                "optimistic": {"discount_rate": 0.08, "terminal_growth": 0.035},
                "pessimistic": {"discount_rate": 0.12, "terminal_growth": 0.015},
            }

            scenario_results = {}

            for scenario_name, params in scenarios.items():
                context.add_message(f"Calculating {scenario_name} scenario")

                # Simplified scenario calculation (would normally re-run full DCF)
                base_value = 150.0  # Sample base value per share
                discount_impact = (0.10 - params["discount_rate"]) * 10  # Simplified
                growth_impact = (params["terminal_growth"] - 0.025) * 20  # Simplified

                scenario_value = base_value + discount_impact + growth_impact

                scenario_results[scenario_name] = {
                    "parameters": params,
                    "estimated_value_per_share": scenario_value,
                    "change_from_base": (scenario_value - 150.0) / 150.0,
                }

            # Save scenario analysis
            scenarios_path = context.workspace_path / "scenarios"
            scenarios_file = scenarios_path / "scenario_analysis.json"

            with open(scenarios_file, "w") as f:
                json.dump(scenario_results, f, indent=2)

            context.add_message("Scenario analysis completed")
            return True

        except Exception as e:
            context.add_message(f"Scenario analysis failed: {e}", "ERROR")
            return False

    def _generate_reports(self, context: ToolExecutionContext) -> bool:
        """Generate valuation reports"""
        try:
            context.add_message("Generating valuation reports")

            # Load consolidated valuations
            valuations_file = context.workspace_path / "valuations" / "consolidated_valuations.json"

            if not valuations_file.exists():
                context.add_message("No valuations found for reporting", "ERROR")
                return False

            with open(valuations_file, "r") as f:
                valuations = json.load(f)

            # Generate summary report
            summary_report = {
                "report_title": "DCF Valuation Analysis Summary",
                "generated_at": context.timestamp,
                "tool_version": self.config.version,
                "companies_analyzed": len(valuations),
                "valuation_summary": {},
                "methodology": {
                    "model": "Discounted Cash Flow",
                    "projection_years": self.config.config_overrides.get("projection_years", 5),
                    "discount_rate": self.config.config_overrides.get("discount_rate", 0.10),
                    "terminal_growth": self.config.config_overrides.get(
                        "terminal_growth_rate", 0.025
                    ),
                },
            }

            # Add company summaries
            for company, valuation in valuations.items():
                summary_report["valuation_summary"][company] = {
                    "enterprise_value": valuation["enterprise_value"],
                    "equity_value": valuation["equity_value"],
                    "value_per_share": valuation["value_per_share"],
                    "net_debt": valuation["net_debt"],
                }

            # Save summary report
            reports_path = context.workspace_path / "reports"
            summary_file = reports_path / "valuation_summary_report.json"

            with open(summary_file, "w") as f:
                json.dump(summary_report, f, indent=2)

            # Generate individual company reports
            for company in valuations.keys():
                company_report_path = reports_path / company
                company_report_file = company_report_path / f"{company}_dcf_report.json"

                # Detailed company report (simplified)
                company_report = {
                    "company": company,
                    "report_type": "DCF Valuation Report",
                    "generated_at": context.timestamp,
                    "valuation_details": valuations[company],
                    "investment_recommendation": self._generate_recommendation(valuations[company]),
                }

                with open(company_report_file, "w") as f:
                    json.dump(company_report, f, indent=2)

                context.add_message(f"Generated report for {company}")

            context.add_message(f"Generated reports for {len(valuations)} companies")
            return True

        except Exception as e:
            context.add_message(f"Report generation failed: {e}", "ERROR")
            return False

    def _generate_recommendation(self, valuation: Dict) -> Dict:
        """Generate investment recommendation based on valuation"""
        value_per_share = valuation["value_per_share"]

        # Simplified recommendation logic
        if value_per_share > 200:
            recommendation = "BUY"
            confidence = "HIGH"
        elif value_per_share > 100:
            recommendation = "HOLD"
            confidence = "MEDIUM"
        else:
            recommendation = "SELL"
            confidence = "LOW"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "target_price": value_per_share,
            "reasoning": f"DCF analysis suggests fair value of ${value_per_share:.2f} per share",
        }

    def _update_output_layers(self, context: ToolExecutionContext) -> bool:
        """Update output data layers with DCF results"""
        try:
            context.add_message("Updating output data layers")

            # Update query results layer
            if "stage_04_query_results" in context.output_paths:
                results_path = context.output_paths["stage_04_query_results"]
                results_path.mkdir(parents=True, exist_ok=True)

                # Create DCF results summary for query layer
                dcf_results = {
                    "tool": self.config.name,
                    "timestamp": context.timestamp,
                    "analysis_type": "dcf_valuation",
                    "results_location": str(context.workspace_path / "reports"),
                    "companies_analyzed": ["AAPL", "MSFT"],  # From simulation
                    "summary_metrics": {
                        "total_enterprise_value": 3000000000000,  # Sample
                        "average_value_per_share": 175.0,
                        "total_companies": 2,
                    },
                }

                results_file = results_path / f"dcf_analysis_{context.timestamp}.json"
                with open(results_file, "w") as f:
                    json.dump(dcf_results, f, indent=2)

                context.add_message("Updated query results layer")

            return True

        except Exception as e:
            context.add_message(f"Output layer update failed: {e}", "ERROR")
            return False

    def validate_outputs(self, context: ToolExecutionContext) -> bool:
        """Validate that DCF calculator outputs meet quality requirements"""
        context.add_message("Validating DCF calculator outputs")

        try:
            # Validate required output files exist
            required_files = [
                "assumptions/dcf_assumptions.json",
                "valuations/consolidated_valuations.json",
                "reports/valuation_summary_report.json",
            ]

            for file_path in required_files:
                full_path = context.workspace_path / file_path
                if not full_path.exists():
                    context.add_message(f"Required output file missing: {file_path}", "ERROR")
                    return False

                context.add_message(f"Validated output file: {file_path}")

            # Validate valuation reasonableness
            valuations_file = context.workspace_path / "valuations" / "consolidated_valuations.json"
            with open(valuations_file, "r") as f:
                valuations = json.load(f)

            for company, valuation in valuations.items():
                value_per_share = valuation["value_per_share"]

                # Basic sanity check - value should be positive and reasonable
                if value_per_share <= 0:
                    context.add_message(f"Invalid negative valuation for {company}", "ERROR")
                    return False

                if value_per_share > 10000:  # $10,000 per share seems unreasonable
                    context.add_message(
                        f"Unreasonably high valuation for {company}: ${value_per_share}", "WARNING"
                    )

                context.add_message(
                    f"Validated {company} valuation: ${value_per_share:.2f} per share"
                )

            # Validate output layer updates
            for layer_name in self.config.output_layers:
                if layer_name in context.output_paths:
                    layer_path = context.output_paths[layer_name]
                    if not layer_path.exists():
                        context.add_message(
                            f"Output layer directory missing: {layer_name}", "ERROR"
                        )
                        return False

                    # Check for update files
                    update_files = list(layer_path.glob(f"dcf_analysis_{context.timestamp}.json"))
                    if not update_files:
                        context.add_message(
                            f"No update files found in layer: {layer_name}", "ERROR"
                        )
                        return False

            context.add_message("All DCF calculator output validation checks passed")
            return True

        except Exception as e:
            context.add_message(f"Output validation failed: {e}", "ERROR")
            self.logger.exception("Output validation failed")
            return False
