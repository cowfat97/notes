# PostgreSQL

## What — 是什么

开源关系型数据库。Ingres 演化，30+ 年历史。MySQL 是"够用就好"，PG 是"做对"——标准兼容、扩展性强。

```text
PG vs MySQL 一句话：
  MySQL → 简单场景快，互联网标配
  PG   → 复杂查询强，功能多，标准 SQL 支持更好
```

| | MySQL | PostgreSQL |
|------|-------|-----------|
| 存储引擎 | 插件式（InnoDB/MyISAM） | 统一（heap + WAL） |
| MVCC | Undo Log | 多版本元组直接存储 |
| JSON | JSON 类型，函数少 | JSONB（二进制 JSON），索引 + 查询强 |
| 全文搜索 | 支持但简单 | 内置 tsvector，中文需 zhparser |
| 扩展 | 插件有限 | 丰富（PostGIS、pgvector、TimescaleDB） |
| 并发 | 读写兼容 | MVCC + 无读锁 |
| 适合 | OLTP Web 应用 | OLTP + OLAP + GIS + 向量 |

---

## How — 怎么用

### MVCC 原理

```text
MySQL (InnoDB):
  UPDATE → 原行进 Undo Log → 新行写数据页 → 读通过 Undo Log 回溯历史版本

PG:
  UPDATE → INSERT 新行（新版本）→ 标记旧行为过期 → 读只看满足 xmin/xmax 的版本
           ↓
     旧行不马上删，VACUUM 清理
```

PG 的 MVCC 是"追加新版本"而不是"回滚到旧版本"。好处是读不加锁，坏处是需要 VACUUM 清理过期行。

**xmin / xmax**：每行两个隐藏列，`xmin`=创建这行的事务 ID，`xmax`=删除/更新这行的事务 ID。读时根据快照判断该行是否可见。

### 索引类型

| 索引 | 原理 | 什么时候用 |
|------|------|-----------|
| **B-tree** | 平衡多路搜索树 | 默认，范围查询、等值查询 |
| **Hash** | 哈希表 | 等值查询（`=`），不支持范围 |
| **GIN** | Generalized Inverted Index | 全文搜索、JSONB、数组 |
| **GiST** | Generalized Search Tree | 自定义索引（PostGIS 空间索引） |
| **BRIN** | Block Range Index | 超大表（十亿级），按块范围粗略索引 |

**如何选择**：默认 B-tree 够用。JSONB 用 GIN。地理位置用 GiST。超大规模日志表用 BRIN。

### pgvector — 向量检索

```sql
CREATE EXTENSION vector;
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1024)  -- BGE-M3 维度
);

-- IVFFlat 索引（先聚类，后检索）
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 相似度搜索
SELECT content, 1 - (embedding <=> '[0.1, 0.2, ...]') AS similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 20;
```

pgvector 让 PG 可以做向量检索。适合小规模（百万级），大规模（千万级）还是专用向量库（Milvus）更合适。优势是不用额外部署一个服务——向量检索和业务数据在一个库。

### JSONB vs JSON

| | JSON | JSONB |
|------|------|-------|
| 存储 | 原文，保留空白和顺序 | 二进制解析后存储 |
| 写入 | 快（不需解析） | 慢（需解析） |
| 查询 | 每次都解析 | 已解析，快 |
| 索引 | 不支持 | GIN 索引 |

结论：能用 JSONB 就用 JSONB。存原文用 JSON，查内容用 JSONB。

### EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 123 AND status = 'active';
```

输出：

```text
Seq Scan（全表扫 → 建索引）
Index Scan（索引查 → 正常）
Bitmap Index Scan + Bitmap Heap Scan（先扫索引建 bitmap，再批量取行 → 区分度不高时用）
Nested Loop / Hash Join / Merge Join（连表方式）
```

面试要求：看一眼知道哪种 scan、是否走了索引、瓶颈在哪。

---

## Why — 为什么大模型开发要学 PG

### RAG 系统的数据库

```text
你的笔记本上 PG 做的事：
  - Agent 记忆存储（会话记录、提取的事实）
  - 元数据管理（文档来源、切分版本、用户信息）
  - 向量检索辅助（pgvector，小规模直接用，大规模配合 Milvus）
```

### pgvector + Milvus 组合

```text
小规模（< 百万向量）：pgvector 直接上，零额外依赖
大规模（> 百万向量）：PG 存元数据 + Milvus 存向量 + 关联查询
```

PG 原生向量检索缺少 IVF 索引优化（比不上 Milvus 的 IVF_FLAT + HNSW），但省了多一个服务的运维成本。

---

## 面试追问

### MySQL 和 PG 怎么选？

MySQL：简单 OLTP Web 应用、主从复制方便、DBA 多好招。PG：复杂查询、GIS、JSON、向量检索、标准 SQL。互联网公司用 MySQL 多，数据/算法团队用 PG 多。

### PG 的 VACUUM 是干什么的？

清理被 UPDATE/DELETE 标记过期的旧行、回收空间、更新统计信息。长时间不 VACUUM 的表会膨胀（死行占空间）和事务 ID 回卷风险。PG 13+ 有 autovacuum 自动执行。

### pgvector 的 IVFFlat 原理？

K-means 聚类，查询时只搜最近的 `probe`（默认 1）个中心对应的向量组。list 值 ≈ sqrt(总行数)。牺牲一点精度换速度——和 Milvus 的 IVF_FLAT 同思想。
