# DCF Calculation Engine

## Core Design Philosophy

A knowledge base-driven DCF valuation system that doesn't rely on user-configured parameters, but intelligently determines valuation parameters through historical data, industry benchmarks, and market consensus.

## Engine Architecture

### 1. Intelligent Parameter Determination Module

#### Discount Rate (WACC) Calculation
```python
def calculate_wacc(stock_ticker, knowledge_base):
    """Intelligently calculate weighted average cost of capital based on knowledge base"""
    
    # 1. Get risk-free rate (10-year treasury yield)
    risk_free_rate = get_treasury_rate(period='10Y')
    
    # 2. Industry risk premium (from knowledge base)
    industry = get_company_industry(stock_ticker)
    industry_risk_premium = knowledge_base.get_industry_risk_premium(industry)
    
    # 3. Company-specific risk adjustment
    company_beta = calculate_company_beta(stock_ticker)
    company_risk_adjustment = assess_company_specific_risk(stock_ticker)
    
    # 4. Cost of debt
    debt_cost = estimate_debt_cost(stock_ticker)
    
    # 5. Calculate WACC
    equity_weight, debt_weight = get_capital_structure(stock_ticker)
    tax_rate = get_effective_tax_rate(stock_ticker)
    
    wacc = (equity_weight * (risk_free_rate + company_beta * industry_risk_premium + company_risk_adjustment) + 
            debt_weight * debt_cost * (1 - tax_rate))
    
    return wacc
```

#### Terminal Growth Rate Determination
```python
def determine_terminal_growth_rate(stock_ticker, knowledge_base):
    """Determine terminal growth rate based on macroeconomic and industry characteristics"""
    
    # Long-term GDP growth expectation
    gdp_growth = knowledge_base.get_long_term_gdp_growth()
    
    # Industry maturity adjustment
    industry = get_company_industry(stock_ticker)
    industry_maturity = knowledge_base.get_industry_maturity_factor(industry)
    
    # Company size adjustment (larger companies grow slower)
    company_size_factor = calculate_size_adjustment(stock_ticker)
    
    terminal_growth = gdp_growth * industry_maturity * company_size_factor
    
    # Cap at GDP growth rate
    return min(terminal_growth, gdp_growth)
```

### 2. Bankruptcy Probability Assessment Module

#### Enhanced Altman Z-Score
```python
def calculate_bankruptcy_probability(stock_ticker):
    """Calculate company bankruptcy probability considering modern market characteristics"""
    
    # Get financial metrics
    metrics = get_latest_financial_metrics(stock_ticker)
    
    # Traditional Altman Z-Score
    working_capital_ratio = metrics['working_capital'] / metrics['total_assets']
    retained_earnings_ratio = metrics['retained_earnings'] / metrics['total_assets']
    ebit_ratio = metrics['ebit'] / metrics['total_assets']
    market_cap_ratio = metrics['market_cap'] / metrics['total_liabilities']
    sales_ratio = metrics['revenue'] / metrics['total_assets']
    
    z_score = (1.2 * working_capital_ratio + 
               1.4 * retained_earnings_ratio + 
               3.3 * ebit_ratio + 
               0.6 * market_cap_ratio + 
               1.0 * sales_ratio)
    
    # Modern adjustment factors
    cash_cushion = metrics['cash'] / metrics['total_assets']
    debt_maturity_risk = assess_debt_maturity_profile(stock_ticker)
    industry_stability = get_industry_stability_score(stock_ticker)
    
    # Comprehensive bankruptcy probability
    if z_score > 2.99:
        base_probability = 0.02  # Healthy company
    elif z_score > 1.81:
        base_probability = 0.15  # Gray zone
    else:
        base_probability = 0.35  # Higher risk
    
    # Adjustment factors
    adjusted_probability = base_probability * (1 - cash_cushion) * debt_maturity_risk * (2 - industry_stability)
    
    return min(0.95, max(0.01, adjusted_probability))
```

### 3. Cash Flow Forecasting Module

#### Intelligent Forecasting Algorithm
```python
def forecast_free_cash_flows(stock_ticker, years=5):
    """Forecast free cash flows based on multi-source data"""
    
    # Historical cash flow data
    historical_fcf = get_historical_free_cash_flows(stock_ticker, years=10)
    
    # Analyst estimates (if available)
    analyst_estimates = get_analyst_fcf_estimates(stock_ticker)
    
    # Industry growth trends
    industry_growth = get_industry_growth_trends(stock_ticker)
    
    # Company-specific factors
    company_factors = analyze_company_growth_drivers(stock_ticker)
    
    forecasted_fcf = []
    
    for year in range(1, years + 1):
        # Baseline growth rate (historical average)
        historical_growth = calculate_growth_rate(historical_fcf)
        
        # Analyst adjustment
        if analyst_estimates and year <= len(analyst_estimates):
            analyst_weight = 0.4
            base_weight = 0.6
        else:
            analyst_weight = 0
            base_weight = 1.0
        
        # Industry trend adjustment
        industry_adjustment = industry_growth[min(year-1, len(industry_growth)-1)]
        
        # Comprehensive forecast
        if analyst_estimates and year <= len(analyst_estimates):
            predicted_growth = (base_weight * historical_growth + 
                              analyst_weight * analyst_estimates[year-1]['growth_rate'])
        else:
            predicted_growth = historical_growth * industry_adjustment
        
        # Apply declining growth (maturity effect)
        maturity_decay = 0.95 ** (year - 1)
        final_growth = predicted_growth * maturity_decay
        
        if year == 1:
            base_fcf = historical_fcf[-1]
        else:
            base_fcf = forecasted_fcf[-1]
        
        forecasted_fcf.append(base_fcf * (1 + final_growth))
    
    return forecasted_fcf
```

### 4. DCF Valuation Calculation

#### Core Calculation Logic
```python
def calculate_dcf_valuation(stock_ticker):
    """Execute complete DCF valuation calculation"""
    
    # 1. Get parameters
    wacc = calculate_wacc(stock_ticker, knowledge_base)
    terminal_growth_rate = determine_terminal_growth_rate(stock_ticker, knowledge_base)
    bankruptcy_prob = calculate_bankruptcy_probability(stock_ticker)
    
    # 2. Forecast cash flows
    projected_fcf = forecast_free_cash_flows(stock_ticker)
    terminal_fcf = projected_fcf[-1] * (1 + terminal_growth_rate)
    
    # 3. Calculate present values
    pv_explicit_period = sum([fcf / ((1 + wacc) ** i) 
                             for i, fcf in enumerate(projected_fcf, 1)])
    
    terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
    pv_terminal_value = terminal_value / ((1 + wacc) ** len(projected_fcf))
    
    # 4. Enterprise value
    enterprise_value = pv_explicit_period + pv_terminal_value
    
    # 5. Equity value
    net_debt = get_net_debt(stock_ticker)
    equity_value = enterprise_value - net_debt
    
    # 6. Per-share value
    shares_outstanding = get_shares_outstanding(stock_ticker)
    intrinsic_value_per_share = equity_value / shares_outstanding
    
    # 7. Bankruptcy adjustment
    survival_adjusted_value = intrinsic_value_per_share * (1 - bankruptcy_prob)
    
    # 8. Current price comparison
    current_price = get_current_stock_price(stock_ticker)
    upside_downside = (survival_adjusted_value - current_price) / current_price
    
    return {
        'intrinsic_value': survival_adjusted_value,
        'current_price': current_price,
        'upside_downside_pct': upside_downside * 100,
        'bankruptcy_probability': bankruptcy_prob,
        'wacc': wacc,
        'terminal_growth_rate': terminal_growth_rate,
        'enterprise_value': enterprise_value,
        'model_assumptions': {
            'projection_years': len(projected_fcf),
            'projected_fcf': projected_fcf,
            'terminal_value': terminal_value
        }
    }
```

### 5. Sensitivity Analysis

#### Key Parameter Sensitivity Testing
```python
def perform_sensitivity_analysis(stock_ticker):
    """Perform sensitivity analysis on key parameters"""
    
    base_valuation = calculate_dcf_valuation(stock_ticker)
    base_value = base_valuation['intrinsic_value']
    
    sensitivity_results = {}
    
    # WACC sensitivity (±2%)
    wacc_scenarios = [-0.02, -0.01, 0, 0.01, 0.02]
    wacc_results = []
    for delta in wacc_scenarios:
        modified_valuation = calculate_dcf_with_wacc_adjustment(stock_ticker, delta)
        value_change = (modified_valuation - base_value) / base_value
        wacc_results.append({'wacc_change': delta, 'value_change_pct': value_change * 100})
    
    sensitivity_results['wacc_sensitivity'] = wacc_results
    
    # Growth rate sensitivity
    growth_scenarios = [-0.02, -0.01, 0, 0.01, 0.02]
    growth_results = []
    for delta in growth_scenarios:
        modified_valuation = calculate_dcf_with_growth_adjustment(stock_ticker, delta)
        value_change = (modified_valuation - base_value) / base_value
        growth_results.append({'growth_change': delta, 'value_change_pct': value_change * 100})
    
    sensitivity_results['growth_sensitivity'] = growth_results
    
    return sensitivity_results
```

## Knowledge Base Integration

### Benchmark Data Management
- **Industry Risk Premium Database**: Regularly updated historical risk premiums by industry
- **Macroeconomic Indicators**: GDP growth, inflation, interest rate environment
- **Peer Comparison Data**: Valuation multiples and financial ratio benchmarks
- **Expert Consensus**: Statistical aggregation of analyst expectations

### Learning Mechanism
- **Forecast Accuracy Tracking**: Record historical predictions vs actual results
- **Parameter Optimization**: Adjust model parameters based on historical performance
- **Anomaly Detection**: Identify and flag unusual valuation situations

---

*The DCF engine continuously learns and optimizes to improve valuation accuracy*