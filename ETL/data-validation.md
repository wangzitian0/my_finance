# 多源数据校验机制

## 核心理念

构建可信的投资分析数据集，通过多源验证、规则策略和智能检测确保数据质量，为DCF估值提供可靠的数据基础。

## 数据源优先级体系

### 1. 优先级定义

#### 第一优先级：SEC官方文件
- **优先级权重**: 1.0（最高）
- **数据类型**: 财务报表、管理层讨论、风险因素
- **更新频率**: 季度/年度
- **可信度**: 法律文件，最高可信度

```python
SEC_PRIORITY_METRICS = {
    'revenue': 1.0,
    'net_income': 1.0, 
    'total_assets': 1.0,
    'total_liabilities': 1.0,
    'cash_flow_from_operations': 1.0,
    'shares_outstanding': 1.0
}
```

#### 第二优先级：多源一致数据
- **优先级权重**: 0.8-0.9
- **验证机制**: 2个以上源相同数据
- **置信度计算**: 基于源数量和历史一致性

```python
def calculate_multi_source_confidence(data_sources, metric_value):
    """计算多源数据置信度"""
    source_count = len(data_sources)
    
    # 基础置信度（基于源数量）
    base_confidence = min(0.9, 0.5 + 0.1 * source_count)
    
    # 源质量调整
    quality_weights = {
        'yahoo_finance': 0.8,
        'bloomberg': 0.9,
        'refinitiv': 0.85,
        'analyst_consensus': 0.7
    }
    
    weighted_quality = sum(quality_weights.get(source, 0.5) 
                          for source in data_sources) / source_count
    
    # 历史一致性加分
    historical_consistency = get_historical_consistency_score(data_sources, metric_value)
    
    final_confidence = base_confidence * weighted_quality * historical_consistency
    
    return min(0.9, final_confidence)
```

#### 第三优先级：单一可靠源
- **优先级权重**: 0.6-0.7
- **主要来源**: Yahoo Finance, Bloomberg, Refinitiv
- **验证策略**: 历史一致性检验

#### 第四优先级：预测性数据
- **优先级权重**: 0.3-0.5
- **数据类型**: 分析师预期、市场预测
- **不确定性**: 高，需要持续验证

## 冲突解决策略

### 1. 直接替换策略
```python
def resolve_sec_conflicts(metric_name, data_sources):
    """SEC数据直接替换其他来源"""
    
    sec_value = None
    other_values = []
    
    for source, value in data_sources.items():
        if source.startswith('SEC'):
            sec_value = value
        else:
            other_values.append((source, value))
    
    if sec_value is not None:
        return {
            'final_value': sec_value,
            'confidence': 0.95,
            'resolution_method': 'SEC_OVERRIDE',
            'discarded_sources': other_values
        }
    
    # 如果没有SEC数据，使用其他策略
    return resolve_multi_source_conflicts(metric_name, dict(other_values))
```

### 2. 加权平均策略
```python
def resolve_multi_source_conflicts(metric_name, data_sources):
    """多源数据加权平均"""
    
    if len(data_sources) < 2:
        source, value = list(data_sources.items())[0]
        return {
            'final_value': value,
            'confidence': get_single_source_confidence(source),
            'resolution_method': 'SINGLE_SOURCE'
        }
    
    # 计算加权平均
    weighted_sum = 0
    total_weight = 0
    
    source_weights = get_source_weights(metric_name)
    
    for source, value in data_sources.items():
        weight = source_weights.get(source, 0.5)
        weighted_sum += value * weight
        total_weight += weight
    
    final_value = weighted_sum / total_weight if total_weight > 0 else 0
    
    # 计算置信度
    variance = calculate_source_variance(data_sources)
    consistency_penalty = min(0.3, variance / final_value) if final_value > 0 else 0
    base_confidence = 0.8
    final_confidence = base_confidence - consistency_penalty
    
    return {
        'final_value': final_value,
        'confidence': max(0.3, final_confidence),
        'resolution_method': 'WEIGHTED_AVERAGE',
        'variance': variance,
        'source_weights': source_weights
    }
```

### 3. 异常检测和标记
```python
class DataAnomalyDetector:
    def __init__(self):
        self.anomaly_thresholds = {
            'revenue_growth_yoy': {'min': -0.5, 'max': 2.0},  # -50%到200%
            'profit_margin': {'min': -0.3, 'max': 0.5},      # -30%到50%
            'debt_to_equity': {'min': 0, 'max': 10},          # 0到10倍
            'current_ratio': {'min': 0.1, 'max': 20}          # 0.1到20
        }
    
    def detect_anomalies(self, metric_name, current_value, historical_values):
        """检测数据异常"""
        anomalies = []
        
        # 1. 绝对值范围检查
        if metric_name in self.anomaly_thresholds:
            threshold = self.anomaly_thresholds[metric_name]
            if current_value < threshold['min'] or current_value > threshold['max']:
                anomalies.append({
                    'type': 'ABSOLUTE_RANGE',
                    'message': f'{metric_name} value {current_value} outside normal range',
                    'severity': 'HIGH'
                })
        
        # 2. 历史趋势检查
        if len(historical_values) >= 3:
            trend_anomaly = self.detect_trend_anomaly(current_value, historical_values)
            if trend_anomaly:
                anomalies.append(trend_anomaly)
        
        # 3. 同行业对比检查
        industry_benchmark = self.get_industry_benchmark(metric_name)
        if industry_benchmark:
            industry_anomaly = self.detect_industry_anomaly(
                current_value, industry_benchmark
            )
            if industry_anomaly:
                anomalies.append(industry_anomaly)
        
        return anomalies
    
    def detect_trend_anomaly(self, current_value, historical_values):
        """检测趋势异常"""
        # 计算历史平均和标准差
        hist_mean = np.mean(historical_values)
        hist_std = np.std(historical_values)
        
        # Z-score异常检测
        z_score = abs(current_value - hist_mean) / hist_std if hist_std > 0 else 0
        
        if z_score > 3:  # 3个标准差之外
            return {
                'type': 'TREND_DEVIATION',
                'message': f'Value {current_value} deviates significantly from historical trend',
                'z_score': z_score,
                'severity': 'MEDIUM' if z_score < 4 else 'HIGH'
            }
        
        return None
```

## 数据质量评分体系

### 1. 综合质量评分
```python
class DataQualityScorer:
    def calculate_overall_quality_score(self, data_point):
        """计算数据点的综合质量评分"""
        
        scores = {
            'source_reliability': self.score_source_reliability(data_point.source),
            'data_freshness': self.score_data_freshness(data_point.timestamp),
            'validation_status': self.score_validation_status(data_point),
            'consistency_score': self.score_historical_consistency(data_point),
            'completeness': self.score_data_completeness(data_point)
        }
        
        # 加权计算总分
        weights = {
            'source_reliability': 0.3,
            'data_freshness': 0.2,
            'validation_status': 0.25,
            'consistency_score': 0.15,
            'completeness': 0.1
        }
        
        total_score = sum(scores[metric] * weights[metric] 
                         for metric in scores)
        
        return {
            'overall_score': total_score,
            'component_scores': scores,
            'quality_grade': self.assign_quality_grade(total_score)
        }
    
    def assign_quality_grade(self, score):
        """分配质量等级"""
        if score >= 0.9:
            return 'A+'  # 优秀
        elif score >= 0.8:
            return 'A'   # 良好
        elif score >= 0.7:
            return 'B'   # 一般
        elif score >= 0.6:
            return 'C'   # 较差
        else:
            return 'D'   # 差
```

## 实时监控和预警

### 1. 数据质量监控
```python
class DataQualityMonitor:
    def __init__(self):
        self.quality_thresholds = {
            'minimum_confidence': 0.6,
            'maximum_anomaly_count': 3,
            'source_availability_threshold': 0.8
        }
    
    def monitor_data_quality(self, stock_ticker):
        """监控股票数据质量"""
        
        current_metrics = self.get_current_metrics(stock_ticker)
        quality_report = {
            'stock_ticker': stock_ticker,
            'timestamp': datetime.now().isoformat(),
            'issues': [],
            'recommendations': []
        }
        
        for metric_name, metric_data in current_metrics.items():
            # 检查置信度
            if metric_data['confidence'] < self.quality_thresholds['minimum_confidence']:
                quality_report['issues'].append({
                    'type': 'LOW_CONFIDENCE',
                    'metric': metric_name,
                    'confidence': metric_data['confidence'],
                    'severity': 'MEDIUM'
                })
            
            # 检查异常数量
            anomaly_count = len(metric_data.get('anomalies', []))
            if anomaly_count > self.quality_thresholds['maximum_anomaly_count']:
                quality_report['issues'].append({
                    'type': 'EXCESSIVE_ANOMALIES',
                    'metric': metric_name,
                    'anomaly_count': anomaly_count,
                    'severity': 'HIGH'
                })
        
        # 生成改进建议
        quality_report['recommendations'] = self.generate_quality_recommendations(
            quality_report['issues']
        )
        
        return quality_report
```

## 人工审核工作流

### 1. 审核任务生成
```python
class HumanReviewWorkflow:
    def generate_review_tasks(self, data_quality_issues):
        """生成需要人工审核的任务"""
        
        review_tasks = []
        
        for issue in data_quality_issues:
            if issue['severity'] == 'HIGH':
                priority = 'URGENT'
            elif issue['severity'] == 'MEDIUM':
                priority = 'NORMAL'
            else:
                priority = 'LOW'
            
            task = {
                'task_id': generate_task_id(),
                'type': 'DATA_QUALITY_REVIEW',
                'priority': priority,
                'issue_details': issue,
                'created_at': datetime.now().isoformat(),
                'status': 'PENDING'
            }
            
            review_tasks.append(task)
        
        return review_tasks
    
    def save_review_decision(self, task_id, reviewer_decision):
        """保存审核决定并更新数据质量规则"""
        
        # 记录审核结果
        review_record = {
            'task_id': task_id,
            'reviewer_decision': reviewer_decision,
            'reviewed_at': datetime.now().isoformat(),
            'reviewer_notes': reviewer_decision.get('notes', '')
        }
        
        # 更新质量规则（学习机制）
        if reviewer_decision['action'] == 'APPROVE':
            self.update_quality_rules_positive(review_record)
        elif reviewer_decision['action'] == 'REJECT':
            self.update_quality_rules_negative(review_record)
```

## 持续改进机制

### 1. 质量规则学习
- **正向反馈**: 人工确认的高质量数据特征学习
- **负向反馈**: 人工标记的低质量数据模式识别
- **规则自动调优**: 基于历史准确性调整阈值参数

### 2. 数据源评估
- **源可靠性跟踪**: 长期跟踪各数据源的准确性
- **响应速度监控**: 监控数据源的更新及时性
- **覆盖范围评估**: 评估数据源的数据完整性

---

*数据校验机制持续优化，确保投资分析的数据基础可靠*