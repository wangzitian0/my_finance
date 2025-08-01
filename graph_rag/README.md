# Graph RAG System for Financial Analysis

## 概述

本系统实现了一个基于图数据库的检索增强生成（Graph RAG）系统，专门用于M7公司的财务分析和投资决策支持。

## 核心功能

### 1. 语义嵌入（Semantic Embedding）
- 使用 Sentence Transformers 生成文档语义向量
- 支持SEC文件、新闻内容的分块处理和嵌入
- 实现向量相似性计算和检索

### 2. 结构化查询生成（Structured Query Generation）
- 自然语言问题分类和意图识别
- 自动提取股票代码和关键实体
- 生成对应的 Cypher 查询语句

### 3. 语义检索（Semantic Retrieval）
- 基于向量相似性的内容检索
- 结合时效性和相关性的智能排序
- 支持多种文档类型的综合检索

### 4. 智能回答生成（Intelligent Answer Generation）
- 基于意图的上下文感知回答
- 支持DCF估值、风险分析、对比分析等多种场景
- 自动生成数据来源引用

### 5. 多步推理（Multi-step Reasoning）
- 复杂问题的自动分解
- 多步骤推理链执行
- 综合分析结果合成

### 6. 数据摄取管道（Data Ingestion Pipeline）
- M7公司数据的自动化摄取
- Yahoo Finance和SEC数据的结构化存储
- 语义嵌入的批量生成和存储

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户问题       │ -> │  查询生成器      │ -> │   Neo4j图数据库  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         v                                              v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   语义检索       │ <- │   推理处理器     │ <- │   结构化数据     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         v                       v                       
┌─────────────────┐    ┌─────────────────┐              
│   相关内容       │ -> │   答案生成器     │              
└─────────────────┘    └─────────────────┘              
                                │                       
                                v                       
                       ┌─────────────────┐              
                       │   最终答案       │              
                       └─────────────────┘              
```

## 支持的查询类型

1. **DCF估值查询**: "Apple的DCF估值是多少？"
2. **财务对比分析**: "比较Apple和Microsoft的财务表现"
3. **风险分析**: "Tesla的主要风险因素是什么？"
4. **新闻影响分析**: "最近的新闻事件如何影响Netflix股价？"
5. **行业分析**: "Meta与其他科技公司相比表现如何？"
6. **历史趋势分析**: "Google过去3年的收入增长趋势如何？"
7. **复杂推理**: "基于最近的财务表现和市场条件，我应该投资Amazon吗？"

## Neo4j 数据模型

### 核心节点类型
- **Stock**: 股票基本信息
- **SECFiling**: SEC文件（10-K, 10-Q, 8-K）
- **NewsEvent**: 新闻事件
- **DCFValuation**: DCF估值数据
- **FinancialMetrics**: 财务指标
- **DocumentChunk**: 文档片段（用于语义检索）

### 关系类型
- **HAS_FILING**: 股票 -> SEC文件
- **MENTIONED_IN**: 股票 -> 新闻事件
- **HAS_VALUATION**: 股票 -> DCF估值
- **HAS_METRIC**: 股票 -> 财务指标
- **IMPACTS**: 新闻事件 -> DCF估值
- **USES**: DCF估值 -> 财务指标

## 使用方法

### 快速开始

```bash
# 1. 安装依赖
pixi run install-extras

# 2. 运行系统测试
pixi run test-graph-rag

# 3. 运行交互式演示
pixi run demo-graph-rag

# 4. 设置Graph RAG系统
pixi run setup-graph-rag
```

### 程序化使用

```python
from graph_rag import GraphRAGSystem

# 初始化系统
graph_rag = GraphRAGSystem()

# 回答问题
result = graph_rag.answer_question("What is Apple's DCF valuation?")
print(result['answer'])
```

### 数据摄取

```python
from graph_rag.data_ingestion import GraphRAGDataIngestion
from graph_rag.semantic_embedding import SemanticEmbedding

# 初始化数据摄取管道
embedding = SemanticEmbedding()
ingestion = GraphRAGDataIngestion(embedding)

# 摄取M7数据
stats = ingestion.ingest_m7_data()
print(f"处理了 {stats['companies_processed']} 家公司")
```

## 配置选项

### 语义嵌入模型
```python
# 默认使用 all-MiniLM-L6-v2
graph_rag = GraphRAGSystem(
    embedding_model='sentence-transformers/all-MiniLM-L6-v2'
)

# 或使用其他模型
graph_rag = GraphRAGSystem(
    embedding_model='sentence-transformers/all-mpnet-base-v2'
)
```

### 检索参数
```python
# 调整检索数量和相似性阈值
semantic_content = retriever.retrieve_relevant_content(
    question="Your question",
    graph_data=data,
    top_k=10,           # 返回前10个相关内容
    min_similarity=0.3  # 最小相似性阈值
)
```

## M7 公司支持

系统专门为以下"Magnificent 7"公司优化：

- **Apple (AAPL)**: CIK 0000320193
- **Microsoft (MSFT)**: CIK 0000789019  
- **Amazon (AMZN)**: CIK 0001018724
- **Alphabet (GOOGL)**: CIK 0001652044
- **Meta (META)**: CIK 0001326801
- **Tesla (TSLA)**: CIK 0001318605
- **Netflix (NFLX)**: CIK 0001065280

## 技术栈

- **Python 3.12+**: 主要开发语言
- **Neo4j**: 图数据库
- **neomodel**: Python ORM for Neo4j
- **Sentence Transformers**: 语义嵌入
- **PyTorch**: 机器学习框架
- **BeautifulSoup**: HTML/XML解析
- **pandas/numpy**: 数据处理

## 性能考虑

### 内存要求
- **最小**: 4GB RAM（基本功能）
- **推荐**: 8GB+ RAM（完整功能）
- **生产**: 16GB+ RAM（大规模数据）

### 存储要求
- **M7数据**: ~500MB
- **向量索引**: ~1GB
- **Neo4j数据库**: ~2GB

## 扩展指南

### 添加新的查询类型

1. 在 `QueryIntent` 枚举中添加新意图
2. 在 `StructuredQueryGenerator` 中添加模式匹配
3. 在 `IntelligentAnswerGenerator` 中实现相应的答案生成逻辑

### 支持新的数据源

1. 扩展 `ETL/models.py` 中的数据模型
2. 在 `data_ingestion.py` 中添加新的摄取方法
3. 更新语义嵌入处理逻辑

### 自定义嵌入模型

```python
from graph_rag.semantic_embedding import SemanticEmbedding

# 使用自定义模型
embedding = SemanticEmbedding('your-custom-model')
graph_rag = GraphRAGSystem(embedding_system=embedding)
```

## 故障排除

### 常见问题

1. **NumPy兼容性警告**: 正常现象，不影响功能
2. **句子嵌入模型下载**: 首次运行时会自动下载模型
3. **Neo4j连接**: 确保Neo4j服务正在运行

### 日志分析

```bash
# 查看详细日志
tail -f graph_rag_test.log

# 查看数据摄取日志  
tail -f data/log/ingestion.log
```

## 贡献指南

1. Fork项目仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](../LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 [GitHub Issue](https://github.com/wangzitian0/my_finance/issues)
- 参考项目文档 [docs/](../docs/)

---

*Graph RAG系统持续优化以提供更准确、更有洞察力的投资分析*