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

RAG 系统有两段可能出错：**检索可能找不到**、**生成可能不忠于文档**。评估需要把两者拆开看，也要一起看。

## 为什么需要专门的评估

普通 LLM 评估只看输出质量（流畅度、准确性）。RAG 多了检索环节，会引入独有的问题：

| 问题类型 | 例子 | 根因 |
|----------|------|------|
| 检索漏了 | 知识库有答案但没搜到 | Embedding 模型不够好 / 切分策略有问题 |
| 检索偏了 | 搜到了但不相关 | 纯向量检索，关键词匹配弱 |
| 幻觉 | LLM 编造了文档里不存在的内容 | prompt 约束不够 / 模型本身幻觉 |
| 答非所问 | 检索对了但 LLM 没回答用户的问题 | prompt 设计问题 |

## 评估的三个维度

### 1. 检索质量（Retrieval）

衡量"搜得对不对"：

| 指标 | 含义 | 怎么算 |
|------|------|--------|
| Hit Rate | top-K 结果中至少有一个相关 | 有相关 / 总查询数 |
| Recall@K | top-K 中相关文档占全部相关文档的比例 | 命中相关数 / 全部相关数 |
| Precision@K | top-K 中相关文档的比例 | 命中相关数 / K |
| MRR | 第一个相关文档排在第几位（倒数均值） | avg(1/排名) |
| NDCG@K | 考虑排名位置的检索质量 | 相关文档排越前分越高 |

**实战建议：** Hit Rate 和 MRR 最常用。Hit Rate 告诉你"能不能搜到"，MRR 告诉你"搜到的排第几"。

### 2. 生成质量（Generation）

衡量"回答得好不好"。这是 RAG 评估的核心难点——既要忠于文档，又要回答用户问题。

| 指标 | 含义 | 评估方式 |
|------|------|---------|
| Faithfulness（忠实度） | 答案是否完全基于检索到的文档 | LLM 逐句拆解→检查每句话是否能在文档中找到依据 |
| Answer Relevance（答案相关性） | 答案是否回答了用户的问题 | LLM 根据答案反向生成问题→看生成的问题和原始问题语义是否一致 |
| Context Relevance（上下文相关性） | 检索到的文档是否与问题相关 | LLM 检查检索结果中是否有无关内容 |
| Context Recall（上下文召回） | 检索结果是否覆盖了答案所需的所有信息 | 需要标注数据（ground truth） |

### 3. 端到端质量

直接评价最终答案的正确性。需要对每个 query 准备标准答案（ground truth），然后比较 RAG 输出和标准答案的相似度（BLEU、ROUGE、语义相似度等）。

## RAGAS 框架

RAGAS（**R**etrieval **A**ugmented **G**eneration **A**ssessment）是目前最主流的 RAG 评估框架。

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

# 准备评估数据：question, answer, contexts, ground_truth
eval_dataset = Dataset.from_dict({
    "question": ["Java 线程池的核心参数有哪些？"],
    "answer": ["核心线程数、最大线程数、存活时间、工作队列、拒绝策略"],
    "contexts": [["线程池 ThreadPoolExecutor 的构造函数..."]],  # 检索到的文档
    "ground_truth": ["corePoolSize, maximumPoolSize, keepAliveTime, workQueue, handler"]
})

result = evaluate(eval_dataset, metrics=[
    faithfulness,         # 答案是否忠于上下文
    answer_relevancy,     # 答案是否切题
    context_precision,    # 上下文是否精简相关
    context_recall,       # 上下文是否覆盖全面
])
```

**四个核心指标：**

| 指标 | 满分含义 | 用 LLM 评？ |
|------|---------|------------|
| Faithfulness | 答案每句话都能在检索文档中找到 | 是 |
| Answer Relevancy | 答案直接回答了用户问题 | 是 |
| Context Precision | 检索结果中没有无关文档 | 是 |
| Context Recall | 检索结果覆盖了答案所需全部信息 | 否（需要 ground truth） |

**注意：** 前三个指标用 LLM 做评判（LLM-as-Judge），不需要人工标注。Context Recall 需要 ground truth，成本最高但最可靠。

## 怎么评估你的 integrated_qa_system

你现在没有评估数据。要建立评估体系，分三步：

**第一步：构建测试集（20-50 条）**

```
每条包含：
  - question: "RAG 的混合检索怎么做？"
  - ground_truth: "混合检索同时使用稠密向量和稀疏向量..."
  - 预期检索文档: [doc_id1, doc_id2]
```

从你的笔记中抽 20-50 个问题，自己写标准答案。

**第二步：跑检索评估**

```python
# 对每个 query 执行检索，计算 Hit Rate 和 MRR
hits = 0
mrr_sum = 0
for query, expected_docs in test_set:
    results = vector_store.hybrid_search_with_rerank(query, k=5)
    result_ids = [doc.metadata["parent_id"] for doc in results]
    # Hit Rate: 至少命中一个就算对
    if any(eid in result_ids for eid in expected_docs):
        hits += 1
    # MRR: 第一个命中的排名
    for rank, rid in enumerate(result_ids, 1):
        if rid in expected_docs:
            mrr_sum += 1.0 / rank
            break

print(f"Hit Rate@5: {hits / len(test_set):.2%}")
print(f"MRR@5: {mrr_sum / len(test_set):.3f}")
```

**第三步：跑生成评估**

用 RAGAS 或直接让一个更强的 LLM（如 GPT-4）评判你的答案质量。核心看两点：
- 答案有没有编造文档里不存在的内容（Faithfulness）
- 答案有没有真正回答用户的问题（Answer Relevancy）

## 评估策略

| 阶段 | 做什么 | 频率 |
|------|--------|------|
| 开发阶段 | 跑检索指标（Hit Rate/MRR），快速迭代 Embedding 和切分策略 | 每次改动 |
| 上线前 | 全量 RAGAS 评估，确保生成质量 | 发版前 |
| 上线后 | 用户反馈 + 人工抽检 | 持续 |

**RAG 评估的核心原则：先检索后生成。检索指标差，后面的生成评估没有意义。**

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