# 评估框架

## 核心评估理念

建立多维度的质量评估体系，通过自动化评估和人工验证相结合，持续优化投资分析系统的准确性和可用性。

## 评估维度

### 1. DCF估值准确性评估

#### 历史回测验证
```python
class DCFAccuracyEvaluator:
    def backtest_valuation_accuracy(self, ticker, lookback_years=3):
        """回测DCF估值准确性"""
        
        results = []
        historical_dates = self.get_historical_evaluation_dates(ticker, lookback_years)
        
        for eval_date in historical_dates:
            # 重建历史时点的DCF模型
            historical_dcf = self.reconstruct_historical_dcf(ticker, eval_date)
            
            # 获取后续实际股价表现
            actual_performance = self.get_actual_performance(
                ticker, 
                start_date=eval_date,
                horizon_months=[3, 6, 12, 24]
            )
            
            # 计算预测准确性
            accuracy_metrics = {
                'prediction_date': eval_date,
                'predicted_value': historical_dcf['intrinsic_value'],
                'predicted_upside': historical_dcf['upside_downside_pct'],
                'actual_returns': actual_performance,
                'direction_accuracy': self.calculate_direction_accuracy(
                    historical_dcf['upside_downside_pct'], 
                    actual_performance
                ),
                'magnitude_accuracy': self.calculate_magnitude_accuracy(
                    historical_dcf['upside_downside_pct'], 
                    actual_performance
                )
            }
            
            results.append(accuracy_metrics)
        
        return self.aggregate_accuracy_results(results)
    
    def calculate_direction_accuracy(self, predicted_upside, actual_returns):
        """计算方向预测准确性"""
        direction_scores = {}
        
        for horizon, actual_return in actual_returns.items():
            predicted_direction = 1 if predicted_upside > 0 else -1
            actual_direction = 1 if actual_return > 0 else -1
            
            direction_scores[horizon] = (predicted_direction == actual_direction)
        
        return direction_scores
```

#### 同行业对比基准
```python
def evaluate_vs_industry_benchmark(self, predictions, industry_ticker_list):
    """与行业基准对比评估"""
    
    industry_performance = {}
    
    for ticker in industry_ticker_list:
        if ticker in predictions:
            actual_returns = self.get_actual_returns(ticker)
            industry_performance[ticker] = {
                'predicted_upside': predictions[ticker]['upside_downside_pct'],
                'actual_return_6m': actual_returns['6_month'],
                'actual_return_12m': actual_returns['12_month']
            }
    
    # 计算行业整体准确性
    industry_metrics = {
        'average_direction_accuracy_6m': np.mean([
            (p['predicted_upside'] > 0) == (p['actual_return_6m'] > 0)
            for p in industry_performance.values()
        ]),
        'average_magnitude_error_6m': np.mean([
            abs(p['predicted_upside'] - p['actual_return_6m'])
            for p in industry_performance.values()
        ]),
        'correlation_6m': np.corrcoef(
            [p['predicted_upside'] for p in industry_performance.values()],
            [p['actual_return_6m'] for p in industry_performance.values()]
        )[0,1]
    }
    
    return industry_metrics
```

### 2. 问答系统质量评估

#### 自动化评估指标
```python
class QASystemEvaluator:
    def __init__(self):
        self.evaluation_metrics = [
            'relevance_score',
            'factual_accuracy', 
            'completeness_score',
            'citation_quality',
            'reasoning_coherence'
        ]
    
    def evaluate_answer_quality(self, question, generated_answer, ground_truth=None):
        """评估问答质量"""
        
        evaluation_results = {}
        
        # 1. 相关性评估
        evaluation_results['relevance_score'] = self.assess_relevance(
            question, generated_answer
        )
        
        # 2. 事实准确性检查
        evaluation_results['factual_accuracy'] = self.verify_factual_accuracy(
            generated_answer
        )
        
        # 3. 完整性评估
        evaluation_results['completeness_score'] = self.assess_completeness(
            question, generated_answer
        )
        
        # 4. 引用质量
        evaluation_results['citation_quality'] = self.evaluate_citations(
            generated_answer
        )
        
        # 5. 推理连贯性
        evaluation_results['reasoning_coherence'] = self.assess_reasoning_quality(
            generated_answer
        )
        
        # 计算综合分数
        evaluation_results['overall_score'] = self.calculate_overall_score(
            evaluation_results
        )
        
        return evaluation_results
    
    def assess_relevance(self, question, answer):
        """评估答案与问题的相关性"""
        # 使用语义相似度模型
        question_embedding = self.embedding_model.encode(question)
        answer_embedding = self.embedding_model.encode(answer)
        
        similarity = cosine_similarity([question_embedding], [answer_embedding])[0][0]
        
        # 关键词匹配增强
        question_keywords = self.extract_financial_keywords(question)
        answer_keywords = self.extract_financial_keywords(answer)
        
        keyword_overlap = len(set(question_keywords) & set(answer_keywords)) / len(question_keywords)
        
        # 综合相关性分数
        relevance_score = 0.7 * similarity + 0.3 * keyword_overlap
        
        return min(1.0, relevance_score)
```

#### 人工评估工作流
```python
class HumanEvaluationWorkflow:
    def create_evaluation_tasks(self, qa_samples, evaluation_criteria):
        """创建人工评估任务"""
        
        evaluation_tasks = []
        
        for sample in qa_samples:
            task = {
                'task_id': generate_evaluation_task_id(),
                'question': sample['question'],
                'generated_answer': sample['answer'],
                'context_data': sample['context'],
                'evaluation_criteria': evaluation_criteria,
                'created_at': datetime.now().isoformat(),
                'status': 'PENDING',
                'assigned_reviewer': None
            }
            
            evaluation_tasks.append(task)
        
        # 保存到评估队列
        self.save_evaluation_tasks(evaluation_tasks)
        
        return evaluation_tasks
    
    def record_human_feedback(self, task_id, reviewer_scores, reviewer_comments):
        """记录人工评估反馈"""
        
        feedback_record = {
            'task_id': task_id,
            'reviewer_scores': reviewer_scores,  # {metric: score} 形式
            'reviewer_comments': reviewer_comments,
            'review_date': datetime.now().isoformat(),
            'reviewer_confidence': reviewer_scores.get('reviewer_confidence', 0.8)
        }
        
        # 保存反馈记录
        self.save_feedback_record(feedback_record)
        
        # 更新系统性能指标
        self.update_system_performance_metrics(feedback_record)
        
        return feedback_record
```

### 3. 数据质量评估

#### 实时数据质量监控
```python
class DataQualityContinuousMonitor:
    def __init__(self):
        self.quality_thresholds = {
            'completeness_threshold': 0.95,
            'timeliness_threshold_hours': 24,
            'accuracy_threshold': 0.90,
            'consistency_threshold': 0.85
        }
    
    def monitor_data_streams(self):
        """持续监控数据流质量"""
        
        quality_report = {
            'timestamp': datetime.now().isoformat(),
            'data_sources': {}
        }
        
        # 监控各数据源
        for source in ['sec_edgar', 'yfinance', 'news_apis', 'analyst_reports']:
            source_quality = self.evaluate_data_source_quality(source)
            quality_report['data_sources'][source] = source_quality
            
            # 检查是否触发告警
            if source_quality['overall_score'] < 0.8:
                self.trigger_quality_alert(source, source_quality)
        
        return quality_report
    
    def evaluate_data_source_quality(self, source_name):
        """评估单个数据源质量"""
        
        recent_data = self.get_recent_data(source_name, hours=24)
        
        quality_metrics = {
            'completeness': self.calculate_completeness(recent_data),
            'timeliness': self.calculate_timeliness(recent_data),
            'accuracy': self.calculate_accuracy(recent_data),
            'consistency': self.calculate_consistency(recent_data)
        }
        
        # 加权计算总分
        weights = {'completeness': 0.3, 'timeliness': 0.2, 'accuracy': 0.3, 'consistency': 0.2}
        overall_score = sum(quality_metrics[metric] * weights[metric] 
                           for metric in quality_metrics)
        
        return {
            'source_name': source_name,
            'quality_metrics': quality_metrics,
            'overall_score': overall_score,
            'last_evaluated': datetime.now().isoformat()
        }
```

### 4. 用户体验评估

#### 响应时间和性能监控
```python
class PerformanceMonitor:
    def track_response_times(self, endpoint, response_time_ms):
        """跟踪API响应时间"""
        
        performance_record = {
            'endpoint': endpoint,
            'response_time_ms': response_time_ms,
            'timestamp': datetime.now().isoformat(),
            'user_session': self.get_current_session_id()
        }
        
        # 保存性能记录
        self.save_performance_record(performance_record)
        
        # 检查是否需要性能告警
        if response_time_ms > self.get_response_time_threshold(endpoint):
            self.trigger_performance_alert(endpoint, response_time_ms)
    
    def generate_performance_report(self, time_period='24h'):
        """生成性能报告"""
        
        performance_data = self.get_performance_data(time_period)
        
        report = {
            'time_period': time_period,
            'total_requests': len(performance_data),
            'average_response_time_ms': np.mean([r['response_time_ms'] for r in performance_data]),
            'p95_response_time_ms': np.percentile([r['response_time_ms'] for r in performance_data], 95),
            'error_rate': self.calculate_error_rate(performance_data),
            'endpoint_breakdown': self.breakdown_by_endpoint(performance_data)
        }
        
        return report
```

## 评估数据管理

### 1. 评估结果存储
```python
class EvaluationDataManager:
    def save_evaluation_result(self, evaluation_type, result_data):
        """保存评估结果到数据库"""
        
        evaluation_record = {
            'evaluation_id': generate_evaluation_id(),
            'evaluation_type': evaluation_type,  # 'dcf_accuracy', 'qa_quality', etc.
            'result_data': result_data,
            'evaluation_timestamp': datetime.now().isoformat(),
            'system_version': self.get_current_system_version(),
            'evaluator': result_data.get('evaluator', 'automatic')
        }
        
        # 保存到评估历史表
        self.db.evaluation_history.insert(evaluation_record)
        
        # 更新当前性能指标
        self.update_current_performance_metrics(evaluation_type, result_data)
    
    def get_performance_trends(self, metric_name, time_range='30d'):
        """获取性能趋势数据"""
        
        historical_data = self.db.evaluation_history.find({
            'evaluation_timestamp': {'$gte': self.calculate_start_date(time_range)},
            f'result_data.{metric_name}': {'$exists': True}
        }).sort('evaluation_timestamp', 1)
        
        trend_data = []
        for record in historical_data:
            trend_data.append({
                'timestamp': record['evaluation_timestamp'],
                'value': record['result_data'][metric_name]
            })
        
        return trend_data
```

### 2. 评估报告生成
```python
class EvaluationReportGenerator:
    def generate_weekly_report(self):
        """生成周度评估报告"""
        
        report_data = {
            'report_period': f"{datetime.now() - timedelta(days=7)} to {datetime.now()}",
            'dcf_accuracy_metrics': self.get_dcf_accuracy_summary('7d'),
            'qa_quality_metrics': self.get_qa_quality_summary('7d'),
            'data_quality_metrics': self.get_data_quality_summary('7d'),
            'performance_metrics': self.get_performance_summary('7d'),
            'key_insights': self.generate_key_insights(),
            'recommendations': self.generate_improvement_recommendations()
        }
        
        # 生成报告文件
        report_file = self.generate_report_file(report_data)
        
        # 发送给相关人员
        self.distribute_report(report_file)
        
        return report_data
```

## 持续改进机制

### 1. A/B测试框架
```python
class ABTestingFramework:
    def create_ab_experiment(self, experiment_name, variants, traffic_split):
        """创建A/B测试实验"""
        
        experiment = {
            'experiment_id': generate_experiment_id(),
            'name': experiment_name,
            'variants': variants,  # {'A': config_A, 'B': config_B}
            'traffic_split': traffic_split,  # {'A': 0.5, 'B': 0.5}
            'start_date': datetime.now().isoformat(),
            'status': 'ACTIVE',
            'success_metrics': ['accuracy_score', 'response_time', 'user_satisfaction']
        }
        
        self.save_experiment(experiment)
        return experiment
    
    def evaluate_experiment_results(self, experiment_id):
        """评估A/B测试结果"""
        
        experiment = self.get_experiment(experiment_id)
        results = {}
        
        for variant_name in experiment['variants'].keys():
            variant_metrics = self.get_variant_metrics(experiment_id, variant_name)
            results[variant_name] = variant_metrics
        
        # 统计显著性检验
        statistical_results = self.perform_statistical_tests(results)
        
        return {
            'experiment_id': experiment_id,
            'variant_results': results,
            'statistical_significance': statistical_results,
            'recommendation': self.generate_experiment_recommendation(statistical_results)
        }
```

---

*评估框架持续优化，确保投资分析系统的质量和可靠性*