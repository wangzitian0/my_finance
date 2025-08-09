# 数据模型设计

## Neo4j 图数据库扩展Schema

基于现有的 `ETL/models.py`，扩展支持SEC文件和DCF计算的完整数据模型。

### 核心实体节点

#### 1. Stock（股票）- 已有
```python
class Stock(StructuredNode):
    ticker = StringProperty(unique_index=True)
    period = StringProperty()
    interval = StringProperty()
    fetched_at = DateTimeProperty()
```

#### 2. 新增：SECFiling（SEC文件）
```python
class SECFiling(StructuredNode):
    cik = StringProperty(required=True)
    accession_number = StringProperty(unique_index=True)
    filing_type = StringProperty()  # 10-K, 10-Q, 8-K, etc.
    filing_date = DateTimeProperty()
    period_end_date = DateTimeProperty()
    document_url = StringProperty()
    parsed_content = JSONProperty()  # 解析后的结构化内容
    sections = JSONProperty()  # 各章节内容索引
```

#### 3. 新增：FinancialMetrics（财务指标）
```python
class FinancialMetrics(StructuredNode):
    metric_name = StringProperty(required=True)
    value = FloatProperty()
    unit = StringProperty()  # millions, billions, etc.
    period = StringProperty()  # quarterly, annual
    source = StringProperty()  # SEC, Yahoo, Analyst
    confidence_score = FloatProperty()  # 0-1 数据置信度
    calculation_date = DateTimeProperty()
```

#### 4. 新增：DCFValuation（DCF估值）
```python
class DCFValuation(StructuredNode):
    valuation_date = DateTimeProperty()
    intrinsic_value = FloatProperty()
    current_price = FloatProperty()
    upside_downside = FloatProperty()  # 上涨/下跌空间
    bankruptcy_probability = FloatProperty()  # 破产概率
    model_assumptions = JSONProperty()  # 模型假设
    sensitivity_analysis = JSONProperty()  # 敏感性分析结果
```

#### 5. 新增：NewsEvent（新闻事件）
```python
class NewsEvent(StructuredNode):
    title = StringProperty()
    content = StringProperty()
    source = StringProperty()
    published_date = DateTimeProperty()
    sentiment_score = FloatProperty()  # -1 to 1
    impact_categories = JSONProperty()  # 影响类别
    relevance_score = FloatProperty()  # 相关性评分
```

#### 6. 新增：AnalystReport（分析师报告）
```python
class AnalystReport(StructuredNode):
    analyst_firm = StringProperty()
    analyst_name = StringProperty()
    report_date = DateTimeProperty()
    target_price = FloatProperty()
    rating = StringProperty()  # Buy, Hold, Sell
    eps_estimate = FloatProperty()
    revenue_estimate = FloatProperty()
    key_points = JSONProperty()
```

### 关系定义

#### Stock 中心的关系网络
```python
class Stock(StructuredNode):
    # 现有关系
    info = RelationshipTo(Info, 'HAS_INFO')
    fast_info = RelationshipTo(FastInfo, 'HAS_FAST_INFO')
    prices = RelationshipTo(PriceData, 'HAS_PRICE')
    recommendations = RelationshipTo(Recommendations, 'HAS_RECOMMENDATIONS')
    sustainability = RelationshipTo(Sustainability, 'HAS_SUSTAINABILITY')
    
    # 新增关系
    sec_filings = RelationshipTo(SECFiling, 'HAS_FILING')
    financial_metrics = RelationshipTo(FinancialMetrics, 'HAS_METRIC')
    dcf_valuations = RelationshipTo(DCFValuation, 'HAS_VALUATION')
    news_events = RelationshipTo(NewsEvent, 'MENTIONED_IN')
    analyst_reports = RelationshipTo(AnalystReport, 'COVERED_BY')
```

#### 跨实体关系
```python
# SEC文件包含财务指标
SECFiling.metrics = RelationshipTo(FinancialMetrics, 'CONTAINS_METRIC')

# 财务指标用于DCF估值
FinancialMetrics.used_in_valuation = RelationshipTo(DCFValuation, 'USED_IN')

# 新闻事件影响估值
NewsEvent.impacts_valuation = RelationshipTo(DCFValuation, 'IMPACTS')

# 分析师报告包含预测指标
AnalystReport.provides_estimates = RelationshipTo(FinancialMetrics, 'PROVIDES_ESTIMATE')
```

## 数据优先级和校验规则

### 数据源优先级（从高到低）
1. **SEC官方文件** - 最高优先级，法律文件
2. **多源一致数据** - 2个以上来源相同的数据
3. **Yahoo Finance** - 单一来源但历史可靠
4. **分析师报告** - 预测性数据，置信度较低

### 置信度计算公式
```python
def calculate_confidence_score(metric_value, sources):
    base_score = 0.5
    
    # SEC数据 +0.4
    if 'SEC' in sources:
        base_score += 0.4
    
    # 多源验证 +0.1 * (源数量-1)
    source_bonus = min(0.3, 0.1 * (len(sources) - 1))
    base_score += source_bonus
    
    # 历史一致性加分
    consistency_bonus = calculate_historical_consistency(metric_value)
    base_score += consistency_bonus
    
    return min(1.0, base_score)
```

### 冲突解决策略
1. **直接替换**：SEC数据覆盖其他所有源
2. **加权平均**：多个非SEC源按置信度加权
3. **标记异常**：差异超过阈值的数据标记为需人工审核

## DCF模型集成

### 基于知识库的参数确定
- **折现率**：从同行业公司历史数据和债券收益率推算
- **永续增长率**：基于GDP长期增长预期和行业特性
- **预测年数**：标准5年，特殊情况10年
- **破产概率**：基于财务健康度指标和行业风险

### 计算流程
1. **数据收集**：从图数据库获取最新财务指标
2. **参数推算**：使用知识库中的基准参数
3. **现金流预测**：基于历史趋势和分析师预期
4. **敏感性分析**：测试关键参数变动影响
5. **结果存储**：将计算结果存回图数据库

---

*数据模型会随着实现过程中的发现持续优化*