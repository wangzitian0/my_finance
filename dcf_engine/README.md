# DCF Engine - DCF估值引擎

输入输出都是数据，专注于各种策略相关的逻辑实现。

## 组件结构

### 核心引擎
- `validator.py` - 策略验证器
- `simple_m7_dcf.py` - 简化M7 DCF计算
- `m7_dcf_analysis.py` - M7 DCF分析
- `generate_dcf_report.py` - DCF报告生成

### 知识图谱
- `build_knowledge_base.py` - 知识库构建
- `demo_graph_rag.py` - Graph RAG演示
- `build_nasdaq100_simple.py` - NASDAQ100简化构建

### 策略验证
- `test_strategy_validation.py` - 策略验证测试

### 文档
- `dcf-engine.md` - DCF引擎架构文档
- `STRATEGY_RELEASE_PROCESS.md` - 策略发布流程

## 数据流

```
DTS (数据输入) → DCF Engine (策略计算) → DTS (结果输出)
                     ↓
                Common (Schema定义)
```

## 核心功能

### DCF估值计算
- 多种DCF模型实现
- 参数敏感性分析  
- 情景分析和压力测试

### 策略验证
- 历史回测
- 统计显著性检验
- 风险指标计算

### 知识图谱增强
- Graph RAG查询
- 多源数据融合
- 智能推理分析

## 使用方式

```bash
# 策略验证
pixi run validate-strategy

# DCF分析
python dcf_engine/m7_dcf_analysis.py

# 报告生成
python dcf_engine/generate_dcf_report.py
```

## 设计原则

1. **纯计算逻辑**: 不处理数据I/O，专注业务逻辑
2. **策略可配置**: 支持多种DCF模型和参数
3. **结果可追溯**: 记录计算过程和中间结果
4. **性能优化**: 支持并行计算和缓存