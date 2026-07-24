# Elasticsearch

## What — 是什么

近实时分布式搜索和分析引擎。底层 Lucene，Java 编写，RESTful API。

```text
客户端 → ES (REST API)
           ↓
         协调节点 (Coordinator)
           ↓
         分片 (Primary Shard + Replica Shard)
           ↓
         Lucene 索引 (倒排索引 + 列存)
```

**专有名词**：

| 术语 | 类比 MySQL | 说明 |
|------|-----------|------|
| Index | Database | 索引，文档集合 |
| Type (7.x 已废弃) | Table | 索引内的逻辑分组 |
| Document | Row | JSON 文档，最小数据单元 |
| Field | Column | 文档中的字段 |
| Mapping | Schema | 字段类型定义 |
| Shard | 分表 | 索引水平拆分 |
| Replica | 从库 | 分片副本，高可用 + 读扩展 |

---

## How — 怎么用

### 倒排索引原理

```text
文档1: "信用卡逾期处理规则"
文档2: "信用卡年费减免政策"
文档3: "逾期还款的征信影响"

→ 分词 → 倒排索引：

Term     Posting List (文档ID:位置)
信用卡     [1:0, 2:0]
逾期       [1:2, 3:0]
年费       [2:2]
征信       [3:5]
```

检索"信用卡逾期" → 分别查"信用卡"和"逾期"的 posting list → 取交集 → 文档1。复杂度 O(term数)，不是 O(文档数)。

### 写流程（近实时）

```text
客户端写请求
  → 路由到对应 Primary Shard
  → 写入内存 Buffer
  → refresh (默认 1s) → 生成新 segment → 写 OS Cache
  → 此时才可被搜索（"近实时"的来源）
  → translog 同步写盘（崩溃恢复）
  → flush (默认 30min 或 translog 满) → segment 落盘 + commit
```

**为什么是近实时**：`refresh` 间隔默认 1 秒。写入的数据最多 1 秒后才能搜到。`index.refresh_interval` 可调——建完索引批量导数据时设为 -1 关闭刷新，导完再开，性能翻几倍。

### 读流程

```text
客户端搜索请求
  → 协调节点 → 发到所有相关 Shard (Primary 或 Replica)
  → 每个 Shard 本地执行 query → 返回 (id, score) 给协调节点
  → 协调节点全局排序 → 拿 doc_id 去实际 Shard 取完整文档
  → 返回给客户端
```

两阶段：Query Phase（打分排序，只有 id + score）→ Fetch Phase（拿完整文档）。

### Mapping & 分词

```json
{
  "mappings": {
    "properties": {
      "title":     { "type": "text", "analyzer": "ik_max_word" },
      "content":   { "type": "text", "analyzer": "ik_smart" },
      "price":     { "type": "float" },
      "create_at": { "type": "date" }
    }
  }
}
```

**text vs keyword**：

| | text | keyword |
|------|------|---------|
| 分词 | 是（全文搜索） | 否（精确匹配） |
| 排序 | 否 | 是 |
| 聚合 | 否 | 是 |
| 例子 | "信用卡逾期" → "信用""卡""逾期" | "order_2024001" 保持原样 |

**IK 分词器**：`ik_max_word`（最细粒度，召回率高）vs `ik_smart`（粗粒度，精度高）。中文搜索必装。

### 查询类型

```json
// match — 全文搜索，分词后匹配
{"match": {"title": "信用卡逾期"}}

// term — 精确匹配，不分词
{"term": {"status": "active"}}

// bool — 组合查询
{"bool": {
  "must":     [{"match": {"title": "信用卡"}}],
  "filter":   [{"term": {"status": "active"}}],
  "must_not": [{"term": {"deleted": true}}],
  "should":   [{"match": {"content": "年费"}}]
}}

// range — 范围查询
{"range": {"create_at": {"gte": "2024-01-01"}}}
```

**must vs filter**：must 参与评分（相关性排序），filter 只过滤不评分（更快，自动缓存）。精确条件用 filter，相关性匹配用 must。

---

## Why — 为什么这样设计

### 分布式架构

```text
Index "orders"
  ├─ Primary Shard 0 ─── Replica Shard 0
  ├─ Primary Shard 1 ─── Replica Shard 1
  └─ Primary Shard 2 ─── Replica Shard 2

分布到 3 个节点：
  Node A: P0, R2
  Node B: P1, R0
  Node C: P2, R1
```

- Primary Shard 负责写，Replica Shard 负责读 + 容灾
- Primary 和 Replica 绝不会在同一节点（避免单点故障）
- 分片数创建索引时设定，后续不可改（可改 replica 数）
- 扩容靠加节点 + 重新分配分片

### ES vs MySQL 搜索

| | MySQL | ES |
|------|-------|-----|
| 全文搜索 | LIKE '%keyword%'，全表扫 | 倒排索引，O(term数) |
| 分词 | 无 | 内置 + IK 插件 |
| 相关性排序 | 无 | BM25 打分 |
| 聚合统计 | GROUP BY | Aggregation（比 MySQL 快几十倍） |
| 适合场景 | 事务、JOIN | 搜索、日志分析、OLAP |

ES 不能替代 MySQL——ES 没有事务、JOIN 弱、不适合频繁更新。互补关系。

### 在 RAG 中的应用

```text
RAG 文档搜索（你的场景）：
  ES 做关键词检索（BM25）→ 返回候选文档
  + 向量检索（Milvus）做语义匹配 → 返回候选文档
  → 两路融合 → Reranker 精排 → LLM 答案
```

ES 不是向量库，但可以做辅助关键词检索引擎。更新的版本（8.x+）有内置 dense_vector 类型可以做向量检索，但性能和专用向量库（Milvus）差距大。

---

## 面试追问

### ES 为什么快？

倒排索引 O(term数)、内存缓存 segment、filter 自动缓存、分片并行查询。全文搜索不是全表扫，是查 posting list 取交集。

### 脑裂怎么办？

`discovery.seed_hosts` + `cluster.initial_master_nodes` 配好，master 选举 `minimum_master_nodes`（7.x 后内置）。奇数节点，至少 N/2+1 存活才选举。

### refresh 和 flush 的区别？

refresh：内存 Buffer → OS Cache，segment 可搜索（近实时的核心）。flush：OS Cache → 磁盘，segment 持久化 + translog 清空。refresh 1s 一次，flush 30min 一次。

### 大量写入怎么优化？

关闭 refresh（`index.refresh_interval: -1`）、关闭 replica（写完再加）、bulk API 批量写入、SSD。
