<!--
 * @Author: haoxinlei howxl97@163.com
 * @Date: 2026-05-05 15:05:25
 * @LastEditors: haoxinlei howxl97@163.com
 * @LastEditTime: 2026-05-05 20:26:05
 * @FilePath: /notes/LLM/Rag/RAG.md
 * @Description: RAG 检索增强生成 — 从概念到实现的完整笔记
-->
# 为什么会有RAG？

## LLM 的三大局限

### 1. 知识截止日期

LLM 的训练数据有截止时间。比如 GPT-4 的知识截止到 2023 年，之后的新闻、技术文档、论文它完全不知道。问它"2025 年 Python 最新版本是多少"，它只能瞎编。

### 2. 幻觉（Hallucination）

LLM 本质是下一个 token 的概率预测，它不"知道"自己不知道。当训练数据中没有答案时，它会编造听起来合理但完全错误的内容。而且编得越像真的，危害越大。

### 3. 无法访问私有数据

企业内部文档、个人笔记、数据库里的业务数据——这些 LLM 训练时从未见过，也不可能见过。直接问它"我上个月的 Kafka 消费延迟是多少"，它不可能答出来。

**三句话总结：LLM 的知识是冻结的、不可信的、与外部隔绝的。**

## RAG 解决的核心问题

RAG（Retrieval-Augmented Generation，检索增强生成）的核心思路：**先检索，再生成。**

```
用户提问 → 从外部知识库检索相关文档 → 把文档+问题一起送给 LLM → LLM 基于文档生成答案
```

RAG 不改变模型本身，而是改变模型的输入——把"外部知识"塞进 prompt 里让 LLM 参考。这样做有三个好处：

| 优势 | 说明 |
|------|------|
| 知识实时更新 | 改文档即改答案，不需要重新训练模型 |
| 答案可溯源 | 每个回答都能追溯到具体文档，减少幻觉 |
| 保护数据隐私 | 外部文档不出本地，不需要发给模型训练 |

**RAG 的本质不是新技术，而是一种架构模式：用检索系统弥补 LLM 的知识盲区。**

## RAG 的典型应用场景

| 场景 | 说明 | 例子 |
|------|------|------|
| 企业知识库问答 | 员工问公司内部文档 | "年假怎么申请？"→ 检索 HR 制度文档 |
| 客服系统 | 用户问产品问题 | "怎么退货？"→ 检索帮助中心 |
| 个人知识管理 | 问自己的笔记 | 你正在做的：Agent 检索你的学习笔记 |
| 法律/医疗咨询 | 专业领域需要准确引用 | 检索法规条文 + LLM 解释 |
| 代码助手 | 检索私有代码库 | 检索公司内部 SDK 用法 |

你的 `integrated_qa_system` 就是场景 3（个人知识管理）的雏形——通过 Milvus 检索笔记，再让 DashScope 基于检索结果回答。

# 什么是RAG？

## RAG 的定义

RAG（Retrieval-Augmented Generation）= 检索 + 增强 + 生成。三个词拆开：

- **检索（Retrieval）**：从外部知识库中找到与用户问题最相关的文档片段
- **增强（Augmented）**：把检索到的文档作为上下文，注入 LLM 的 prompt
- **生成（Generation）**：LLM 基于"问题 + 检索到的文档"生成答案

简单说：**给 LLM 配一个"外挂大脑"，回答问题前先去查资料。**

## RAG 的基本架构

```
┌─────────────────────────────────────────────────────┐
│                    离线阶段（建库）                     │
│                                                       │
│  文档(.md/.pdf/...)                                   │
│    → 加载（Document Loader）                           │
│    → 切分（Chunking）                                  │
│    → 向量化（Embedding）                               │
│    → 存入向量数据库（Milvus/ChromaDB/...）              │
│                                                       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                    在线阶段（问答）                     │
│                                                       │
│  用户提问                                             │
│    → 向量化（用同一个 Embedding 模型）                  │
│    → 向量检索（找最相似的文档块）                       │
│    → 重排序（Reranker 精选 top-N）                     │
│    → 拼入 Prompt（问题 + 检索结果）                     │
│    → LLM 生成答案                                     │
│                                                       │
└─────────────────────────────────────────────────────┘
```

**两个核心思想：**
1. **离线和在线分离**——建库慢无所谓（离线跑），问答必须快（在线跑）
2. **语义匹配而非关键词匹配**——"怎么学 Java"能匹配到"Java 学习路线"，因为向量空间中语义相近

## RAG 的工作流程

用你的 `integrated_qa_system` 代码走一遍完整流程（[main.py](integrated_qa_system/main.py) + [rag_system.py](integrated_qa_system/rag_qa/core/rag_system.py)）：

**第一步：查询分类**（[query_classifier.py](integrated_qa_system/rag_qa/core/query_classifier.py)）

```python
query_category = self.query_classifier.predict_category(query)
# 返回 "通用知识" 或 "专业咨询"
```

用 BERT 二分类判断：如果是"今天天气怎么样"这种通用问题，直接让 LLM 回答，不走检索（节省延迟）。如果是专业问题，走下面的流程。

**第二步：策略选择**（[strategy_selector.py](integrated_qa_system/rag_qa/core/strategy_selector.py)）

```python
strategy = self.strategy_selector.select_strategy(query)
# 返回 "直接检索" / "HyDE" / "子查询检索" / "回溯问题检索"
```

用 LLM 自动判断该用哪种检索策略。

**第三步：混合检索 + 重排序**（[vector_store.py](integrated_qa_system/rag_qa/core/vector_store.py)）

```python
docs = self.vector_store.hybrid_search_with_rerank(query, k=5)
# 稠密向量(语义) + 稀疏向量(关键词) → BGE-Reranker 重排序
```

**第四步：LLM 生成**（[prompts.py](integrated_qa_system/rag_qa/core/prompts.py)）

```python
prompt = self.rag_prompt.format(context=context, question=query)
answer = self.llm(prompt)
# 把检索到的文档 + 问题一起给 LLM，生成最终答案
```

## RAG vs 微调

| 维度 | RAG | 微调（Fine-tuning） |
|------|-----|---------------------|
| 原理 | 改输入（注入外部知识） | 改模型（更新参数权重） |
| 知识更新 | 改文档即可，实时生效 | 需要重新训练 |
| 成本 | 检索+推理，成本低 | GPU 训练，成本高 |
| 可解释性 | 答案可追溯到文档 | 黑盒，不知道模型为什么这么说 |
| 幻觉控制 | 有文档约束，幻觉少 | 可能学到错误模式 |
| 适用场景 | 知识问答、实时信息 | 风格适配、领域术语、特定格式输出 |

**不是二选一，而是组合使用。** 常见做法：微调让模型学会领域术语和输出格式，RAG 提供实时知识。

# 怎么实现RAG？

## 离线阶段：文档索引

离线阶段就是把文档变成向量存起来，供后续检索使用。你的代码在 [document_processor.py](integrated_qa_system/rag_qa/core/document_processor.py) + [vector_store.py](integrated_qa_system/rag_qa/core/vector_store.py)。

### 文档加载

```python
# document_processor.py — load_documents()
DOCUMENT_LOADERS = {
    ".txt": TextLoader,
    ".md":  UnstructuredMarkdownLoader,
    ".pdf": OCRPDFLoader,
    ".docx": OCRDOCLoader,
    # ...
}
```

根据文件扩展名选择对应的 Loader，加载后给每个文档打标（source、file_path、timestamp）。

**关键点：** 不同格式用不同 Loader，但最终都变成统一的 `Document` 对象（`page_content` + `metadata`），后续流程不关心原始格式。

### 父子块切分（Parent-Child Chunking）

这是你的系统中最值得理解的设计。普通 RAG 直接切块→检索→返回，但有个问题：**检索需要小块（精准匹配），LLM 需要大块（完整上下文）。**

父子块策略把这个矛盾拆开解决：

```
原始文档
  └── 父块（1200 token）  ← 给 LLM 看的，保证上下文完整
        ├── 子块1（300 token）← 向量检索用
        ├── 子块2（300 token）← 命中哪个子块，
        ├── 子块3（300 token）← 就返回它所属的整个父块
        └── 子块4（300 token）
```

```python
# document_processor.py — process_documents()
# 第一步：父块切分（1200 token）
parent_docs = parent_splitter.split_documents([doc])
for parent_doc in parent_docs:
    parent_id = f"doc_{i}_parent_{j}"
    # 第二步：子块切分（300 token），每个子块携带父块信息
    for sub_chunk in child_splitter.split_documents([parent_doc]):
        sub_chunk.metadata["parent_id"] = parent_id
        sub_chunk.metadata["parent_content"] = parent_doc.page_content
```

**检索时：** 用子块匹配 query → 返回子块对应的父块 → LLM 看到的是完整的 1200 token 上下文，而不是零碎的 300 token 片段。

**另外注意：** 你的代码对 `.md` 文件使用 `MarkdownTextSplitter`，它会识别 `##`、`###` 标题边界，避免在标题中间断开。`.txt` 用 `ChineseRecursiveTextSplitter`，按 `\n\n` → `\n` → `。` → `，` 优先级逐级断句。

### 向量化（Embedding）

把文本变成数字向量。你的系统使用 **BGE-M3**（[vector_store.py](integrated_qa_system/rag_qa/core/vector_store.py)）：

```python
# BGE-M3 同时生成两种向量
self.embedding_function = BGEM3EmbeddingFunction(model_name_or_path=m3_path)

# 输入文本 → embeddings
embeddings = self.embedding_function(texts)
dense_vector = embeddings["dense"][i]   # 稠密向量 (1024维) — 语义
sparse_vector = embeddings["sparse"][i]  # 稀疏向量 — 关键词
```

| 向量类型 | 原理 | 优势 |
|----------|------|------|
| 稠密向量（Dense） | 1024 维浮点数，语义相近的文本向量距离近 | 泛化好，"学 Java"能匹配"Java 入门教程" |
| 稀疏向量（Sparse） | 类似 BM25，高维但大部分为 0 | 精准匹配专有名词、术语 |

BGE-M3 一个模型同时出两种向量，这是它的核心卖点。

### 向量存储（Milvus）

向量数据库存的是 `<id, 向量, 元数据>`。你的系统用 Milvus，建了两个索引：

```python
# vector_store.py — _create_or_load_collection()
# 稠密向量 → IVF_FLAT 索引（聚类加速 + 精确搜索）
index_params.add_index(field_name="dense_vector", index_type="IVF_FLAT",
                       metric_type="IP", params={"nlist": 128})
# 稀疏向量 → SPARSE_INVERTED_INDEX（倒排索引）
index_params.add_index(field_name="sparse_vector",
                       index_type="SPARSE_INVERTED_INDEX", metric_type="IP")
```

额外存储了 `parent_id`、`parent_content`、`source` 字段，方便检索后还原父块内容和按学科过滤。

## 在线阶段：检索生成

### 意图识别 / 查询分类

不是所有问题都需要走 RAG。你的系统用 BERT 做二分类（[query_classifier.py](integrated_qa_system/rag_qa/core/query_classifier.py)）：

```python
category = self.query_classifier.predict_category(query)
# "通用知识" → 直接 LLM 回答（"今天天气怎么样"）
# "专业咨询" → 走 RAG 流程（"AI 学科的课程大纲是什么"）
```

这样可以**避免无意义的检索**，节省延迟和计算资源。

### Query 改写

用户的问题往往不够"检索友好"。比如口语化、表意不清。你的系统用了三种改写策略：

| 策略 | 做法 | 适用场景 |
|------|------|---------|
| 回溯问题 | LLM 简化复杂查询 | "我有一个 100 亿条记录的数据集，MongoDB 还是 Milvus？"→ "Milvus 支持的数据规模" |
| 子查询 | LLM 拆复合查询→逐条检索→去重 | "比较 Milvus 和 Zilliz Cloud 的优缺点" → ["Milvus 优点","Milvus 缺点","Zilliz Cloud 特点"] |
| HyDE | LLM 生成假设答案→用答案检索 | 查询抽象、直接检索效果差时使用 |

策略选择也由 LLM 自动完成（[strategy_selector.py](integrated_qa_system/rag_qa/core/strategy_selector.py)），不用人手动指定。

### 混合检索 + 重排序

你的系统核心亮点——**稠密 + 稀疏混合检索 + BGE-Reranker 重排序**：

```python
# vector_store.py — hybrid_search_with_rerank()
# 1. 稠密检索（语义匹配）
dense_request = AnnSearchRequest(data=[dense_vector], anns_field="dense_vector",
                                  limit=k)
# 2. 稀疏检索（关键词匹配）
sparse_request = AnnSearchRequest(data=[sparse_vector], anns_field="sparse_vector",
                                   limit=k)
# 3. 加权融合（稠密:稀疏 = 1.0:0.7）
ranker = WeightedRanker(1.0, 0.7)
results = self.client.hybrid_search(reqs=[dense_request, sparse_request],
                                     ranker=ranker, limit=k)
# 4. 子块去重 → 取父块
parent_docs = self._get_unique_parent_docs(sub_chunks)
# 5. BGE-Reranker Cross-Encoder 重排序
scores = self.reranker.predict([[query, doc.page_content] for doc in parent_docs])
ranked = [doc for _, doc in sorted(zip(scores, parent_docs), reverse=True)]
```

**为什么需要重排序？**

混合检索用的是 Bi-Encoder（query 和 doc 分别编码→计算相似度），速度快但不够精细。Reranker 用 Cross-Encoder（query + doc 一起编码→打分），更准但更慢。所以流程是：**混合检索粗筛 top-K → Reranker 精选 top-M。**

### 答案生成

最后一步最简单——把检索到的文档 + 用户问题拼进 prompt，让 LLM 生成答案（[prompts.py](integrated_qa_system/rag_qa/core/prompts.py)）：

```python
prompt = """
你是一个智能助手，帮助用户回答问题。
如果提供了上下文，请基于上下文回答。
上下文: {context}
问题: {question}
如果无法回答，请回复："信息不足，请联系人工客服，电话：{phone}。"
"""
answer = self.llm(prompt.format(context=context, question=query, phone=phone))
```

**关键：** prompt 里要明确告诉 LLM"基于上下文回答"，否则它可能忽略检索结果，自由发挥。

## 技术选型对比

| 环节 | 你的选择 | 替代方案 | 选择理由 |
|------|---------|---------|---------|
| Embedding | BGE-M3（本地） | OpenAI Embedding / Cohere | 免费 + 稠密稀疏双向量 |
| 向量库 | Milvus | ChromaDB / Pinecone / Weaviate | 支持混合检索 + 千万级数据 |
| Reranker | BGE-Reranker-large（本地） | Cohere Rerank | 免费 + 与 BGE-M3 配套 |
| LLM | DashScope qwen-turbo | GPT-4 / DeepSeek | 阿里百炼便宜，中文效果好 |
| 查询分类 | BERT-base-Chinese | LLM few-shot | 速度快（毫秒级），成本低 |
| 文档切分 | 父子块 | 普通切片 / 语义分块 | 检索精准 + 上下文完整

# RAG 评估

RAG 系统有两段：**检索**和**生成**。评估必须拆开看——检索不好，生成一定不好；检索好，生成也可能出问题。

## 一、检索评估

核心问题只有一个：**用户问的东西，知识库里有没有？搜到了没有？**

### 基础指标（不需要 LLM）

这些指标需要一个标注好的测试集：每条 query 标注了哪些文档是相关的。

| 指标 | 含义 | 计算 |
|------|------|------|
| Hit Rate@K | top-K 中至少命中一个相关文档 | 命中的查询数 / 总查询数 |
| MRR | 第一个相关文档排在什么位置 | avg(1 / 第一个相关文档的排名) |
| Recall@K | top-K 中命中了全部相关文档的多大比例 | 命中相关数 / 全部相关数 |
| Precision@K | top-K 中有多大比例是相关的 | 命中相关数 / K |
| NDCG@K | 考虑排名位置（排前面的相关文档得分更高） | 相关文档排名越靠前分越高 |

**实战建议：** Hit Rate@5 和 MRR 最常用。Hit Rate 告诉你"能不能搜到"（及格线 > 0.8），MRR 告诉你"搜到的排第几"（及格线 > 0.6）。

### RAGAS 检索指标（需要 LLM 或 ground truth）

#### Context Recall（上下文召回率）— 搜全了吗

**问的是：** 标准答案里的信息，检索结果覆盖了多少。

```
Ground truth:
  s1: "corePoolSize 控制核心线程数"
  s2: "maximumPoolSize 是最大线程数"
  s3: "keepAliveTime 是空闲线程存活时间"

检索结果: "ThreadPoolExecutor 有 corePoolSize 和 maximumPoolSize..."
  s1 → 有 ✓
  s2 → 有 ✓
  s3 → 无 ✗

Context Recall = 2/3 = 0.67  ⚠️ keepAliveTime 没检索到
```

**需要 ground truth。** 低分 → 调大 K、优化切分策略、加强混合检索的关键词权重。

#### Context Precision（上下文精确度）— 搜准了吗

**问的是：** 检索出来的文档，有多少是真正相关的。

```
检索结果 top-3:
  rank 1: "ThreadPoolExecutor 构造函数参数详解" → 相关 ✓
  rank 2: "Java NIO Selector 原理" → 无关 ✗
  rank 3: "线程池拒绝策略" → 相关 ✓

Context Precision ≈ 0.5  ⚠️ 混入了无关文档
```

RAGAS 的 Precision 考虑了排名——排前面的相关文档加分多，排后面的无关文档扣分少。

**需要 ground truth。** 低分 → 加 Reranker、检查 Embedding 模型是否适合你的领域、减少检索 K 值。

### 检索评估示例代码

```python
# 基础检索评估
hits, mrr_sum = 0, 0
for query, expected_docs in test_set:
    results = vector_store.hybrid_search_with_rerank(query, k=5)
    result_ids = [doc.metadata["parent_id"] for doc in results]

    if any(eid in result_ids for eid in expected_docs):
        hits += 1

    for rank, rid in enumerate(result_ids, 1):
        if rid in expected_docs:
            mrr_sum += 1.0 / rank
            break

print(f"Hit Rate@5: {hits / len(test_set):.2%}")
print(f"MRR@5: {mrr_sum / len(test_set):.3f}")
```

## 二、生成评估

检索没问题后，评估 LLM 生成的答案质量。核心两个指标：

### Faithfulness（忠实度）⭐⭐⭐ — 编造了吗

RAG 最重要的指标。**问的是：** LLM 有没有说检索文档里不存在的话。

```
答案: "Java 线程池有 7 个参数。最好使用 CachedThreadPool。"
  ├── "Java 线程池有 7 个参数" → 检索文档中有 → ✓
  └── "最好使用 CachedThreadPool" → 检索文档中无 → ✗ (LLM 自己编的)

Faithfulness = 1/2 = 0.5  ⚠️
```

**计算方式：**
1. 把答案拆成独立陈述句（claims）
2. 用 LLM 逐句检查是否能从检索的 contexts 中找到依据
3. 分数 = 有依据的陈述数 / 总陈述数

**不需要 ground truth，LLM 自行评判。** 低分 → 强化 prompt 约束、换更听话的模型。

### Answer Relevancy（答案相关性）— 跑题了吗

**问的是：** 答案是否真正回答了用户的问题。

```
用户: "RAG 的混合检索怎么做？"

答案 A: "混合检索同时使用稠密向量和稀疏向量..."
  → LLM 反向生成问题: "混合检索怎么实现？"
  → 语义相似度 0.95 ✅

答案 B: "RAG 是检索增强生成，2020 年由 Facebook 提出..."
  → LLM 反向生成问题: "RAG 是什么？"
  → 语义相似度 0.45 ⚠️ 问的是怎么做，不是是什么
```

**计算方式：**
1. LLM 根据答案反向生成问题
2. 计算反向生成的问题与原问题的语义相似度
3. 分数 = 余弦相似度，越接近 1 越切题

**不需要 ground truth。** 低分 → 检查上下文是否太长淹没了问题。

## 四个指标关系图

```
           Context Recall    Context Precision
              (够全吗)          (够精吗)
                ↓                 ↓
           ┌──────────────────────────┐
用户问题 → │      检索到的上下文        │ → LLM → 答案
           └──────────────────────────┘            ↓
                                        Faithfulness  Answer Relevancy
                                         (编造了吗)    (跑题了吗)

            ←── 检索评估 ──→              ←──── 生成评估 ────→
```

## 评估框架

评估指标需要框架来落地——自动执行评估流程、调用 LLM 评判、汇总结果。以下是四个主流框架。

### 框架对比

| 框架 | 定位 | 优势 | 劣势 |
|------|------|------|------|
| RAGAS | 专注 RAG 评估 | 指标全、社区活跃、论文背书 | 只做评估不做监控 |
| DeepEval | 通用 LLM 评估 | 指标最多、CI/CD 集成好 | 配置稍复杂 |
| TruLens | RAG 可观测性 | 可视化链路追踪 + 评估一体 | 较重，学习成本高 |
| LangSmith | 全流程 LLMOps | 调试+评估+监控一站式 | 付费，开源部分功能有限 |

### RAGAS — 专注 RAG，最推荐

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

eval_dataset = Dataset.from_dict({
    "question": ["Java 线程池的核心参数有哪些？"],
    "answer": ["核心线程数、最大线程数、存活时间、工作队列、拒绝策略"],
    "contexts": [["线程池 ThreadPoolExecutor 的构造函数..."]],
    "ground_truth": ["corePoolSize, maximumPoolSize, keepAliveTime, workQueue, handler"]
})

result = evaluate(eval_dataset, metrics=[
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
])
# result["faithfulness"] → 0.85
```

**适用场景：** 只需要 RAG 评估，不想引入重型平台。pip install 就能用，5 分钟上手。

### DeepEval — 指标最全，CI/CD 友好

```python
from deepeval import evaluate
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input="Java 线程池的核心参数？",
    actual_output="核心线程数、最大线程数...",
    retrieval_context=["ThreadPoolExecutor 构造函数..."],
)

FaithfulnessMetric().measure(test_case)    # → score: 0.9, reason: "..."
AnswerRelevancyMetric().measure(test_case) # → score: 0.85, reason: "..."
```

比 RAGAS 多了更多指标（Toxicity、Bias、Hallucination），支持 pytest 集成：
```python
@deepeval.log_hyperparameters(model="qwen-turbo")
def test_rag_faithfulness():
    assert_test(test_case, [FaithfulnessMetric()])
```

**适用场景：** 需要 CI/CD 自动化评估、需要更多指标类型。

### TruLens — 可视化链路追踪

```python
from trulens_eval import Tru, Feedback, TruChain
from trulens_eval.feedback import Groundedness

tru = Tru()
# 定义反馈函数
feedback = Feedback(Groundedness()).on_input().on_output()

# 包装 RAG 链路
tru_chain = TruChain(rag_chain,
    feedbacks=[feedback],
    app_name="PersonalRAG",
)

with tru_chain as recording:
    result = rag_chain.invoke("Java 线程池？")
# 自动记录：检索了哪些文档 → 耗时 → 各阶段得分
```

TruLens 的核心价值在于**链路追踪**——能看到每条 query 的检索结果是什么、花了多少时间、每步得分。适合调试和优化。

**适用场景：** 需要排查"这条 query 为什么答得不好"，需要可视化调试。

### LangSmith — 全流程平台（付费）

LangChain 官方的 LLMOps 平台。不只是评估，还覆盖：
- 调试：查看每次调用的完整链路（prompt → 检索 → 生成）
- 数据集管理：上传测试集，一键跑评估
- 回归测试：发版前自动对比新旧版本
- 线上监控：追踪用户真实 query 的质量

**适用场景：** 团队协作、生产环境上线后的持续监控。个人项目成本偏高（免费额度有限）。

### 选型建议

| 场景 | 推荐 |
|------|------|
| 个人项目、快速评估 | RAGAS |
| 需要 CI/CD 自动化 | DeepEval |
| 排查检索质量瓶颈 | TruLens |
| 生产环境、团队协作 | LangSmith |

**实战建议：** 先用 RAGAS 跑通基本评估，如果发现检索指标低、需要定位问题，再引入 TruLens 看链路。

## 评估流程

| 阶段 | 做什么 | 工具 |
|------|--------|------|
| 1. 构建测试集 | 20-50 条 query + ground_truth + 相关文档标注 | 人工 |
| 2. 检索评估 | Hit Rate / MRR / Context Recall / Context Precision | 代码 + RAGAS |
| 3. 生成评估 | Faithfulness / Answer Relevancy | RAGAS（LLM-as-Judge） |

**核心原则：先检索后生成。检索指标不过关，不要去调生成——先去修 Embedding、切分、Reranker。**

# RAG发展

## Naive RAG → Advanced RAG → Agentic RAG

RAG 的演进分为三个阶段：

### Naive RAG（朴素 RAG）

```
用户提问 → 向量化 → 检索 top-K → 拼入 prompt → LLM 生成
```

最基础的流程，问题很明显：
- 检索质量差：只靠向量相似度，专有名词搜不到
- 没有 query 理解：用户问什么就搜什么，不做改写
- 没有重排序：top-K 结果可能不相关

### Advanced RAG（增强 RAG）

你的 `integrated_qa_system` 就是这一层：

```
用户提问 → 查询分类 → 策略选择 → Query改写
  → 混合检索(稠密+稀疏) → 重排序 → 拼入prompt → LLM生成
```

相比 Naive RAG 多了：查询分类、策略选择、Query 改写、混合检索、重排序、父子块切分。**目前工业界大部分 RAG 系统在这一层。**

### Agentic RAG（智能体 RAG）

不是固定的检索→生成流水线，而是由 Agent 动态决策：

```
用户提问 → Agent 分析
  ├── 需要检索 → 选择检索工具（向量库/搜索引擎/数据库）
  ├── 信息不足 → 换策略重新检索
  ├── 多跳推理 → 检索A → 从A中提取关键信息 → 再去检索B
  └── 生成答案 or 继续迭代
```

核心变化：**从"一条固定流水线"变成"Agent 自主决策的多轮循环"。**

## RAG + MCP

你现在做的 P0 目标就是这个方向。

**MCP（Model Context Protocol）** 让 RAG 系统以标准化 tool 的形式暴露给 Agent：

```
Claude Agent
  ├── tool: search_notes(query) → Milvus 检索笔记
  ├── tool: read_note(path) → 读取完整笔记内容
  └── tool: list_notes(topic) → 按主题浏览笔记

Agent 自主决定什么时候检索、检索什么、怎么用结果
```

和传统 RAG 的区别：
- 传统 RAG：固定的输入输出管道
- RAG + MCP：Agent 把 RAG 当作一个**可组合的工具**，可以和其他工具（数据库查询、代码执行、API 调用）配合使用

## RAG 的局限和优化方向

| 问题 | 现象 | 优化方向 |
|------|------|---------|
| 检索质量瓶颈 | 检索回来的文档不相关，LLM 再强也没用 | 更好的 Embedding、混合检索、Reranker |
| 文档切分难题 | 切太大检索不准，切太小上下文缺失 | 父子块、语义分块、Small-to-Big |
| 多跳推理弱 | "A 和 B 什么关系"需要先查 A 再查 B | Agentic RAG、Graph RAG |
| 表格/图片难处理 | 多模态文档的语义丢失 | 多模态 Embedding、Table QA |
| 答案幻觉 | 检索到了但 LLM 不用，或编造不存在的内容 | prompt 约束、引用溯源、人工审核 |

**RAG 不是银弹**——它的上限由检索质量决定。检索不行，后面的一切都白费。这也是为什么你的系统在检索环节投入最多（混合检索 + Reranker + 多策略 + 父子块）。