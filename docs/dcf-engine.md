# DCF计算引擎

## 核心设计理念

基于知识库驱动的DCF估值系统，不依赖用户配置参数，而是通过历史数据、同行业基准和市场共识来智能确定估值参数。

## 引擎架构

### 1. 参数智能确定模块

#### 折现率（WACC）计算
```python
def calculate_wacc(stock_ticker, knowledge_base):
    """基于知识库智能计算加权平均资本成本"""
    
    # 1. 获取无风险利率（10年期国债收益率）
    risk_free_rate = get_treasury_rate(period='10Y')
    
    # 2. 行业风险溢价（从知识库获取）
    industry = get_company_industry(stock_ticker)
    industry_risk_premium = knowledge_base.get_industry_risk_premium(industry)
    
    # 3. 公司特定风险调整
    company_beta = calculate_company_beta(stock_ticker)
    company_risk_adjustment = assess_company_specific_risk(stock_ticker)
    
    # 4. 债务成本
    debt_cost = estimate_debt_cost(stock_ticker)
    
    # 5. 计算WACC
    equity_weight, debt_weight = get_capital_structure(stock_ticker)
    tax_rate = get_effective_tax_rate(stock_ticker)
    
    wacc = (equity_weight * (risk_free_rate + company_beta * industry_risk_premium + company_risk_adjustment) + 
            debt_weight * debt_cost * (1 - tax_rate))
    
    return wacc
```

#### 永续增长率确定
```python
def determine_terminal_growth_rate(stock_ticker, knowledge_base):
    """基于宏观经济和行业特性确定永续增长率"""
    
    # GDP长期增长预期
    gdp_growth = knowledge_base.get_long_term_gdp_growth()
    
    # 行业成熟度调整
    industry = get_company_industry(stock_ticker)
    industry_maturity = knowledge_base.get_industry_maturity_factor(industry)
    
    # 公司规模调整（大公司增长更慢）
    company_size_factor = calculate_size_adjustment(stock_ticker)
    
    terminal_growth = gdp_growth * industry_maturity * company_size_factor
    
    # 上限为GDP增长率
    return min(terminal_growth, gdp_growth)
```

### 2. 破产概率评估模块

#### Altman Z-Score增强版
```python
def calculate_bankruptcy_probability(stock_ticker):
    """计算公司破产概率，考虑现代市场特征"""
    
    # 获取财务指标
    metrics = get_latest_financial_metrics(stock_ticker)
    
    # 传统Altman Z-Score
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
    
    # 现代调整因子
    cash_cushion = metrics['cash'] / metrics['total_assets']
    debt_maturity_risk = assess_debt_maturity_profile(stock_ticker)
    industry_stability = get_industry_stability_score(stock_ticker)
    
    # 综合破产概率
    if z_score > 2.99:
        base_probability = 0.02  # 健康公司
    elif z_score > 1.81:
        base_probability = 0.15  # 灰色地带
    else:
        base_probability = 0.35  # 风险较高
    
    # 调整因子
    adjusted_probability = base_probability * (1 - cash_cushion) * debt_maturity_risk * (2 - industry_stability)
    
    return min(0.95, max(0.01, adjusted_probability))
```

### 3. 现金流预测模块

#### 智能预测算法
```python
def forecast_free_cash_flows(stock_ticker, years=5):
    """基于多源数据预测自由现金流"""
    
    # 历史现金流数据
    historical_fcf = get_historical_free_cash_flows(stock_ticker, years=10)
    
    # 分析师预期（如果有）
    analyst_estimates = get_analyst_fcf_estimates(stock_ticker)
    
    # 行业增长趋势
    industry_growth = get_industry_growth_trends(stock_ticker)
    
    # 公司特定因素
    company_factors = analyze_company_growth_drivers(stock_ticker)
    
    forecasted_fcf = []
    
    for year in range(1, years + 1):
        # 基准增长率（历史平均）
        historical_growth = calculate_growth_rate(historical_fcf)
        
        # 分析师调整
        if analyst_estimates and year <= len(analyst_estimates):
            analyst_weight = 0.4
            base_weight = 0.6
        else:
            analyst_weight = 0
            base_weight = 1.0
        
        # 行业趋势调整
        industry_adjustment = industry_growth[min(year-1, len(industry_growth)-1)]
        
        # 综合预测
        if analyst_estimates and year <= len(analyst_estimates):
            predicted_growth = (base_weight * historical_growth + 
                              analyst_weight * analyst_estimates[year-1]['growth_rate'])
        else:
            predicted_growth = historical_growth * industry_adjustment
        
        # 应用递减增长（成熟效应）
        maturity_decay = 0.95 ** (year - 1)
        final_growth = predicted_growth * maturity_decay
        
        if year == 1:
            base_fcf = historical_fcf[-1]
        else:
            base_fcf = forecasted_fcf[-1]
        
        forecasted_fcf.append(base_fcf * (1 + final_growth))
    
    return forecasted_fcf
```

### 4. DCF估值计算

#### 核心计算逻辑
```python
def calculate_dcf_valuation(stock_ticker):
    """执行完整DCF估值计算"""
    
    # 1. 获取参数
    wacc = calculate_wacc(stock_ticker, knowledge_base)
    terminal_growth_rate = determine_terminal_growth_rate(stock_ticker, knowledge_base)
    bankruptcy_prob = calculate_bankruptcy_probability(stock_ticker)
    
    # 2. 预测现金流
    projected_fcf = forecast_free_cash_flows(stock_ticker)
    terminal_fcf = projected_fcf[-1] * (1 + terminal_growth_rate)
    
    # 3. 计算现值
    pv_explicit_period = sum([fcf / ((1 + wacc) ** i) 
                             for i, fcf in enumerate(projected_fcf, 1)])
    
    terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
    pv_terminal_value = terminal_value / ((1 + wacc) ** len(projected_fcf))
    
    # 4. 企业价值
    enterprise_value = pv_explicit_period + pv_terminal_value
    
    # 5. 股权价值
    net_debt = get_net_debt(stock_ticker)
    equity_value = enterprise_value - net_debt
    
    # 6. 每股价值
    shares_outstanding = get_shares_outstanding(stock_ticker)
    intrinsic_value_per_share = equity_value / shares_outstanding
    
    # 7. 破产调整
    survival_adjusted_value = intrinsic_value_per_share * (1 - bankruptcy_prob)
    
    # 8. 当前价格对比
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

### 5. 敏感性分析

#### 关键参数敏感性测试
```python
def perform_sensitivity_analysis(stock_ticker):
    """对关键参数进行敏感性分析"""
    
    base_valuation = calculate_dcf_valuation(stock_ticker)
    base_value = base_valuation['intrinsic_value']
    
    sensitivity_results = {}
    
    # WACC敏感性 (±1%)
    wacc_scenarios = [-0.02, -0.01, 0, 0.01, 0.02]
    wacc_results = []
    for delta in wacc_scenarios:
        modified_valuation = calculate_dcf_with_wacc_adjustment(stock_ticker, delta)
        value_change = (modified_valuation - base_value) / base_value
        wacc_results.append({'wacc_change': delta, 'value_change_pct': value_change * 100})
    
    sensitivity_results['wacc_sensitivity'] = wacc_results
    
    # 增长率敏感性
    growth_scenarios = [-0.02, -0.01, 0, 0.01, 0.02]
    growth_results = []
    for delta in growth_scenarios:
        modified_valuation = calculate_dcf_with_growth_adjustment(stock_ticker, delta)
        value_change = (modified_valuation - base_value) / base_value
        growth_results.append({'growth_change': delta, 'value_change_pct': value_change * 100})
    
    sensitivity_results['growth_sensitivity'] = growth_results
    
    return sensitivity_results
```

## 知识库集成

### 基准数据管理
- **行业风险溢价数据库**：定期更新各行业历史风险溢价
- **宏观经济指标**：GDP增长、通胀、利率环境
- **同行业比较数据**：估值倍数、财务比率基准
- **专家共识**：分析师预期的统计汇总

### 学习机制
- **预测准确性跟踪**：记录历史预测vs实际结果
- **参数优化**：基于历史表现调整模型参数
- **异常检测**：识别和标记异常估值情况

---

*DCF引擎会持续学习和优化，以提高估值准确性*