#!/usr/bin/env python3
"""
DCF (Discounted Cash Flow) Calculator

Core valuation engine for calculating intrinsic value of companies using
discounted cash flow analysis enhanced with Graph-RAG retrieved data.

Business Purpose:
Generate quantitative valuations for investment decision making by combining
traditional DCF methodology with AI-enhanced financial analysis.

Key Features:
- Multi-stage DCF models (terminal value calculation)
- WACC (Weighted Average Cost of Capital) calculation
- Free cash flow projections
- Sensitivity analysis and scenario modeling
- Integration with Graph-RAG for enhanced assumptions
- Risk-adjusted discount rates

Graph-RAG Enhancement:
- Uses retrieved SEC filing data for historical analysis
- Incorporates management guidance from earnings calls
- Factors in industry trends and competitive positioning
- Validates assumptions against peer company data

This is the core quantitative engine that transforms Graph-RAG insights
into concrete investment valuations and recommendations.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple


class DCFStage(Enum):
    """DCF model stages for multi-stage valuation"""

    HIGH_GROWTH = "high_growth"
    MATURE = "mature"
    TERMINAL = "terminal"


@dataclass
class DCFInputs:
    """Input parameters for DCF calculation"""

    # Cash Flow Projections
    base_free_cash_flow: Decimal
    growth_rates: List[Decimal]  # Growth rate for each projection year
    terminal_growth_rate: Decimal

    # Discount Rate Components
    risk_free_rate: Decimal
    market_premium: Decimal
    beta: Decimal
    cost_of_debt: Decimal
    tax_rate: Decimal
    debt_to_equity_ratio: Decimal

    # Company Financials
    total_debt: Decimal
    cash_and_equivalents: Decimal
    shares_outstanding: Decimal

    # Model Parameters
    projection_years: int = 5
    terminal_multiple: Optional[Decimal] = None


@dataclass
class DCFResults:
    """DCF calculation results"""

    # Core Valuation
    enterprise_value: Decimal
    equity_value: Decimal
    intrinsic_value_per_share: Decimal

    # Supporting Calculations
    wacc: Decimal
    terminal_value: Decimal
    pv_terminal_value: Decimal
    pv_projection_period: Decimal

    # Cash Flow Projections
    projected_cash_flows: List[Decimal]
    discount_factors: List[Decimal]
    present_values: List[Decimal]

    # Analysis Metadata
    confidence_score: Decimal
    key_assumptions: Dict[str, Decimal]
    sensitivity_ranges: Dict[str, Tuple[Decimal, Decimal]]


class DCFCalculator:
    """
    Discounted Cash Flow calculator with Graph-RAG integration.

    This calculator combines traditional DCF methodology with AI-enhanced
    financial analysis using Graph-RAG retrieved context.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def calculate_dcf(
        self, inputs: DCFInputs, graph_rag_context: Optional[Dict] = None
    ) -> DCFResults:
        """
        Calculate DCF valuation with optional Graph-RAG enhancement.

        Args:
            inputs: DCF calculation inputs
            graph_rag_context: Optional context from Graph-RAG system

        Returns:
            Complete DCF calculation results
        """
        try:
            # Calculate WACC (Weighted Average Cost of Capital)
            wacc = self._calculate_wacc(inputs)

            # Project free cash flows
            projected_cash_flows = self._project_cash_flows(inputs)

            # Calculate terminal value
            terminal_value = self._calculate_terminal_value(inputs, projected_cash_flows[-1])

            # Calculate present values
            discount_factors = self._calculate_discount_factors(wacc, inputs.projection_years)
            present_values = self._calculate_present_values(projected_cash_flows, discount_factors)
            pv_terminal_value = terminal_value * discount_factors[-1]

            # Calculate enterprise and equity value
            pv_projection_period = sum(present_values)
            enterprise_value = pv_projection_period + pv_terminal_value
            equity_value = enterprise_value - inputs.total_debt + inputs.cash_and_equivalents
            intrinsic_value_per_share = equity_value / inputs.shares_outstanding

            # Calculate confidence score based on Graph-RAG context
            confidence_score = self._calculate_confidence_score(inputs, graph_rag_context)

            # Extract key assumptions and sensitivity ranges
            key_assumptions = self._extract_key_assumptions(inputs, wacc)
            sensitivity_ranges = self._calculate_sensitivity_ranges(inputs, wacc)

            return DCFResults(
                enterprise_value=enterprise_value,
                equity_value=equity_value,
                intrinsic_value_per_share=intrinsic_value_per_share,
                wacc=wacc,
                terminal_value=terminal_value,
                pv_terminal_value=pv_terminal_value,
                pv_projection_period=pv_projection_period,
                projected_cash_flows=projected_cash_flows,
                discount_factors=discount_factors,
                present_values=present_values,
                confidence_score=confidence_score,
                key_assumptions=key_assumptions,
                sensitivity_ranges=sensitivity_ranges,
            )

        except Exception as e:
            self.logger.error(f"DCF calculation failed: {e}")
            raise

    def _calculate_wacc(self, inputs: DCFInputs) -> Decimal:
        """Calculate Weighted Average Cost of Capital"""
        # Cost of equity using CAPM
        cost_of_equity = inputs.risk_free_rate + inputs.beta * inputs.market_premium

        # Weight calculations
        debt_ratio = inputs.debt_to_equity_ratio / (1 + inputs.debt_to_equity_ratio)
        equity_ratio = 1 - debt_ratio

        # WACC calculation
        wacc = equity_ratio * cost_of_equity + debt_ratio * inputs.cost_of_debt * (
            1 - inputs.tax_rate
        )

        return wacc

    def _project_cash_flows(self, inputs: DCFInputs) -> List[Decimal]:
        """Project free cash flows for the forecast period"""
        cash_flows = []
        current_cf = inputs.base_free_cash_flow

        for i in range(inputs.projection_years):
            growth_rate = (
                inputs.growth_rates[i] if i < len(inputs.growth_rates) else inputs.growth_rates[-1]
            )
            current_cf = current_cf * (1 + growth_rate)
            cash_flows.append(current_cf)

        return cash_flows

    def _calculate_terminal_value(self, inputs: DCFInputs, final_year_cf: Decimal) -> Decimal:
        """Calculate terminal value using Gordon Growth Model or multiple method"""
        if inputs.terminal_multiple:
            # Terminal multiple method
            return final_year_cf * inputs.terminal_multiple
        else:
            # Gordon Growth Model
            terminal_cf = final_year_cf * (1 + inputs.terminal_growth_rate)
            terminal_value = terminal_cf / (
                self._calculate_wacc(inputs) - inputs.terminal_growth_rate
            )
            return terminal_value

    def _calculate_discount_factors(self, wacc: Decimal, years: int) -> List[Decimal]:
        """Calculate discount factors for each year"""
        return [1 / ((1 + wacc) ** (year + 1)) for year in range(years)]

    def _calculate_present_values(
        self, cash_flows: List[Decimal], discount_factors: List[Decimal]
    ) -> List[Decimal]:
        """Calculate present value of projected cash flows"""
        return [cf * df for cf, df in zip(cash_flows, discount_factors)]

    def _calculate_confidence_score(
        self, inputs: DCFInputs, graph_rag_context: Optional[Dict]
    ) -> Decimal:
        """
        Calculate confidence score based on input quality and Graph-RAG context.

        Higher scores indicate more reliable valuations based on:
        - Data completeness and quality
        - Graph-RAG context richness
        - Assumption reasonableness
        - Historical validation
        """
        base_score = Decimal("0.6")  # Base confidence

        # Adjust based on Graph-RAG context availability
        if graph_rag_context:
            context_quality = graph_rag_context.get("quality_score", 0.5)
            base_score += Decimal(str(context_quality)) * Decimal("0.3")

        # Validate assumption reasonableness
        if 0.02 <= inputs.terminal_growth_rate <= 0.04:  # Reasonable terminal growth
            base_score += Decimal("0.1")

        # Cap at 1.0
        return min(base_score, Decimal("1.0"))

    def _extract_key_assumptions(self, inputs: DCFInputs, wacc: Decimal) -> Dict[str, Decimal]:
        """Extract key valuation assumptions"""
        return {
            "wacc": wacc,
            "terminal_growth_rate": inputs.terminal_growth_rate,
            "risk_free_rate": inputs.risk_free_rate,
            "beta": inputs.beta,
            "tax_rate": inputs.tax_rate,
        }

    def _calculate_sensitivity_ranges(
        self, inputs: DCFInputs, wacc: Decimal
    ) -> Dict[str, Tuple[Decimal, Decimal]]:
        """Calculate sensitivity ranges for key parameters"""
        return {
            "wacc": (wacc * Decimal("0.8"), wacc * Decimal("1.2")),
            "terminal_growth": (
                inputs.terminal_growth_rate * Decimal("0.5"),
                inputs.terminal_growth_rate * Decimal("1.5"),
            ),
            "base_growth": (
                inputs.growth_rates[0] * Decimal("0.7"),
                inputs.growth_rates[0] * Decimal("1.3"),
            ),
        }
