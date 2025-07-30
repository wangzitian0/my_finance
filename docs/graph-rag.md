# Graph RAG系统设计

## 核心理念

结合图数据库的关系优势和RAG的语义检索能力，构建专业的投资分析问答系统，支持复杂的多步推理和跨实体关联查询。

## 系统架构

### 1. 图结构语义层

#### 实体关系图谱
```
[公司] --HAS_FILING--> [SEC文件] --CONTAINS--> [财务指标]
  |                                                    |
  |--HAS_VALUATION--> [DCF估值] <--USES-- [财务指标]
  |
  |--MENTIONED_IN--> [新闻事件] --IMPACTS--> [DCF估值]
  |
  |--COVERED_BY--> [分析师报告] --PROVIDES--> [预测指标]
```

#### 语义向量嵌入
```python
class SemanticEmbedding:
    def __init__(self, embedding_model='sentence-transformers/all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(embedding_model)
        
    def embed_document_sections(self, sec_filing):
        """为SEC文件各章节生成语义嵌入"""
        sections = {
            'business_overview': sec_filing.sections.get('item_1', ''),
            'risk_factors': sec_filing.sections.get('item_1a', ''),
            'financial_statements': sec_filing.sections.get('item_8', ''),
            'md_and_a': sec_filing.sections.get('item_7', '')
        }
        
        embeddings = {}
        for section_name, content in sections.items():
            if content:
                # 分块处理长文本
                chunks = self.chunk_text(content, max_length=512)
                chunk_embeddings = self.model.encode(chunks)
                embeddings[section_name] = {
                    'chunks': chunks,
                    'embeddings': chunk_embeddings,
                    'aggregate_embedding': np.mean(chunk_embeddings, axis=0)
                }
        
        return embeddings
```

### 2. 多模态检索引擎

#### 结构化查询生成器
```python
class StructuredQueryGenerator:
    def generate_cypher_query(self, natural_question):
        """将自然语言问题转换为Cypher查询"""
        
        # 意图识别
        intent = self.classify_question_intent(natural_question)
        
        if intent == 'dcf_valuation':
            return self.generate_dcf_query(natural_question)
        elif intent == 'financial_comparison':
            return self.generate_comparison_query(natural_question)
        elif intent == 'risk_analysis':
            return self.generate_risk_query(natural_question)
        else:
            return self.generate_general_query(natural_question)
    
    def generate_dcf_query(self, question):
        """生成DCF相关查询"""
        # 提取公司ticker
        ticker = self.extract_ticker_from_question(question)
        
        cypher = f"""
        MATCH (s:Stock {{ticker: '{ticker}'}})
        OPTIONAL MATCH (s)-[:HAS_VALUATION]->(dcf:DCFValuation)
        OPTIONAL MATCH (s)-[:HAS_FILING]->(filing:SECFiling)
        OPTIONAL MATCH (s)-[:HAS_METRIC]->(metric:FinancialMetrics)
        WHERE dcf.valuation_date >= date() - duration({{days: 90}})
        RETURN s, dcf, filing, metric
        ORDER BY dcf.valuation_date DESC
        LIMIT 1
        """
        return cypher
```

#### 语义相似性检索
```python
class SemanticRetriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        
    def retrieve_relevant_content(self, question, top_k=5):
        """基于语义相似性检索相关内容"""
        
        # 生成问题向量
        question_embedding = self.embed_question(question)
        
        # 检索相似文档片段
        similar_chunks = self.vector_store.similarity_search(
            question_embedding, 
            top_k=top_k
        )
        
        # 按相关性和时效性排序
        ranked_chunks = self.rank_by_relevance_and_recency(similar_chunks)
        
        return ranked_chunks
    
    def rank_by_relevance_and_recency(self, chunks):
        """综合相关性和时效性排序"""
        current_date = datetime.now()
        
        for chunk in chunks:
            # 相关性分数 (0-1)
            relevance_score = chunk['similarity_score']
            
            # 时效性分数 (越新越高)
            days_old = (current_date - chunk['document_date']).days
            recency_score = max(0, 1 - days_old / 365)  # 一年后权重为0
            
            # 综合分数
            chunk['final_score'] = 0.7 * relevance_score + 0.3 * recency_score
        
        return sorted(chunks, key=lambda x: x['final_score'], reverse=True)
```

### 3. 智能问答生成器

#### 上下文感知的回答生成
```python
class IntelligentAnswerGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        
    def generate_dcf_analysis_answer(self, question, graph_data, semantic_content):
        """生成DCF分析回答"""
        
        # 构建上下文
        context = self.build_dcf_context(graph_data, semantic_content)
        
        prompt = f"""
        你是一个专业的投资分析师，基于以下信息回答用户关于DCF估值的问题。
        
        用户问题: {question}
        
        图数据库信息:
        {context['structured_data']}
        
        相关文档内容:
        {context['document_content']}
        
        请提供详细的分析，包括:
        1. 当前估值情况
        2. 关键假设和风险因素
        3. 敏感性分析
        4. 投资建议
        
        引用具体的数据源和计算过程。
        """
        
        response = self.llm_client.generate(prompt, max_tokens=1000)
        
        # 添加引用信息
        enriched_response = self.add_citations(response, context['sources'])
        
        return enriched_response
    
    def build_dcf_context(self, graph_data, semantic_content):
        """构建DCF分析上下文"""
        context = {
            'structured_data': {},
            'document_content': [],
            'sources': []
        }
        
        # 处理图数据库结果
        if graph_data.get('dcf_valuation'):
            dcf = graph_data['dcf_valuation']
            context['structured_data']['current_valuation'] = {
                'intrinsic_value': dcf.intrinsic_value,
                'current_price': dcf.current_price,
                'upside_downside': dcf.upside_downside,
                'bankruptcy_probability': dcf.bankruptcy_probability,
                'valuation_date': dcf.valuation_date.isoformat()
            }
        
        # 处理语义检索内容
        for chunk in semantic_content:
            context['document_content'].append({
                'content': chunk['text'],
                'source': chunk['source'],
                'section': chunk['section'],
                'relevance_score': chunk['final_score']
            })
            context['sources'].append(chunk['source'])
        
        return context
```

### 4. 复杂推理链

#### 多步推理处理器
```python
class MultiStepReasoning:
    def process_complex_question(self, question):
        """处理需要多步推理的复杂问题"""
        
        # 分解问题
        sub_questions = self.decompose_question(question)
        
        reasoning_chain = []
        accumulated_context = {}
        
        for sub_q in sub_questions:
            # 获取子问题答案
            sub_answer = self.answer_sub_question(sub_q, accumulated_context)
            
            reasoning_chain.append({
                'question': sub_q,
                'answer': sub_answer,
                'evidence': sub_answer['evidence']
            })
            
            # 更新累积上下文
            accumulated_context.update(sub_answer['context'])
        
        # 综合最终答案
        final_answer = self.synthesize_final_answer(question, reasoning_chain)
        
        return {
            'answer': final_answer,
            'reasoning_chain': reasoning_chain,
            'confidence_score': self.calculate_confidence(reasoning_chain)
        }
    
    def decompose_question(self, complex_question):
        """分解复杂问题为子问题"""
        
        # 示例：根据较新的各种新闻来帮我按照DCF计算估值
        decomposition_prompt = f"""
        将以下复杂问题分解为可以独立回答的子问题：
        
        原问题: {complex_question}
        
        请按逻辑顺序列出子问题，每个子问题应该可以通过查询数据库或文档来回答。
        """
        
        # 使用LLM分解问题
        sub_questions = self.llm_client.generate_structured_output(
            decomposition_prompt, 
            output_format='list'
        )
        
        return sub_questions
```

### 5. 实时数据整合

#### 新闻事件影响分析
```python
class NewsImpactAnalyzer:
    def analyze_news_impact_on_valuation(self, stock_ticker, days_back=30):
        """分析最近新闻对估值的影响"""
        
        # 获取最近新闻
        recent_news = self.get_recent_news_events(stock_ticker, days_back)
        
        impact_analysis = []
        
        for news in recent_news:
            # 分析新闻对财务指标的潜在影响
            financial_impact = self.assess_financial_impact(news)
            
            # 更新DCF模型参数
            adjusted_dcf = self.adjust_dcf_for_news_impact(
                stock_ticker, 
                news, 
                financial_impact
            )
            
            impact_analysis.append({
                'news_title': news.title,
                'published_date': news.published_date,
                'sentiment_score': news.sentiment_score,
                'financial_impact': financial_impact,
                'valuation_adjustment': adjusted_dcf['adjustment'],
                'confidence': financial_impact['confidence']
            })
        
        return impact_analysis
    
    def assess_financial_impact(self, news_event):
        """评估新闻事件的财务影响"""
        
        # 关键词匹配影响类别
        impact_categories = {
            'revenue': ['sales', 'revenue', 'contract', 'partnership'],
            'costs': ['layoffs', 'restructuring', 'efficiency'],
            'risk': ['lawsuit', 'regulatory', 'investigation'],
            'growth': ['expansion', 'acquisition', 'investment']
        }
        
        detected_impacts = {}
        
        for category, keywords in impact_categories.items():
            relevance = sum(1 for keyword in keywords 
                          if keyword.lower() in news_event.content.lower())
            if relevance > 0:
                detected_impacts[category] = {
                    'relevance_score': relevance / len(keywords),
                    'sentiment_modifier': news_event.sentiment_score
                }
        
        return detected_impacts
```

### 6. 问答质量保证

#### 答案验证和置信度评估
```python
class AnswerQualityAssurance:
    def validate_answer_quality(self, question, answer, evidence):
        """验证答案质量并计算置信度"""
        
        quality_metrics = {
            'evidence_strength': self.assess_evidence_strength(evidence),
            'logical_consistency': self.check_logical_consistency(answer),
            'data_recency': self.assess_data_recency(evidence),
            'source_reliability': self.assess_source_reliability(evidence)
        }
        
        # 计算综合置信度
        confidence_score = (
            0.3 * quality_metrics['evidence_strength'] +
            0.25 * quality_metrics['logical_consistency'] +
            0.25 * quality_metrics['data_recency'] +
            0.2 * quality_metrics['source_reliability']
        )
        
        # 生成质量报告
        quality_report = {
            'confidence_score': confidence_score,
            'quality_metrics': quality_metrics,
            'recommendations': self.generate_improvement_recommendations(quality_metrics)
        }
        
        return quality_report
```

## 用户交互界面

### 问答模式
- **简单问答**：直接回答具体指标查询
- **深度分析**：提供多角度分析和推理过程
- **对比分析**：支持多公司横向对比
- **时间序列分析**：历史趋势和预测

### 可视化展示
- **DCF计算过程**：分步骤展示计算逻辑
- **敏感性分析图表**：参数变化对估值的影响
- **数据来源标注**：清晰标示每个数据的来源和置信度

---

*Graph RAG系统持续优化以提供更准确、更有洞察力的投资分析*