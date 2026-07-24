# Kafka

## What — 是什么

高吞吐分布式消息队列。LinkedIn 开源，Scala/Java 编写。核心模型：

```text
Producer → Broker (分区日志) → Consumer
             ↓
          ZooKeeper / KRaft (元数据管理)
```

| 术语 | 说明 |
|------|------|
| Broker | Kafka 服务器节点 |
| Topic | 消息逻辑分类（类似数据库的表） |
| Partition | Topic 的物理分区，有序、不可变的消息序列 |
| Producer | 消息生产者 |
| Consumer | 消息消费者，属于 Consumer Group |
| Consumer Group | 消费者组，组内竞争消费（一个分区只能被组内一个消费者消费） |
| Offset | 消息在分区内的位置（id），消费者自己维护消费进度 |

---

## How — 怎么用

### 分区机制

```text
Topic: "order-events" (3 partitions)

Partition 0: [msg0][msg1][msg2][msg3] → 顺序写
Partition 1: [msg0][msg1][msg2]       → 顺序写
Partition 2: [msg0][msg1][msg2][msg3][msg4] → 顺序写

Producer 发消息 → key 相同 → hash(key) % partition数 → 同一个 partition
                 → key=null → 轮询
```

**分区的作用**：并行读写（多分区 = 多并发）、顺序保证（同一分区内有序）、水平扩展。

### 消费者组模型

```text
Consumer Group "order-service"
  ├─ Consumer A → 消费 Partition 0, 1
  └─ Consumer B → 消费 Partition 2

消费者数 ≤ 分区数 → 多了的消费者空闲（一个分区只能被组内一个消费者消费）
消费者数 > 分区数 → 有人闲着
```

**Rebalance**：消费者加入/退出组，Kafka 重新分配分区。Rebalance 期间组内所有消费者暂停消费。避免频繁 Rebalance——调整 `max.poll.interval.ms` 和 `session.timeout.ms`。

### 存储原理

```text
Partition 在磁盘上是一个目录：
  /kafka-logs/order-events-0/
    ├─ 00000000000000000000.log    ← 消息数据（顺序写）
    ├─ 00000000000000000000.index  ← 稀疏索引（offset → 文件位置）
    └─ 00000000000000000000.timeindex ← 时间索引

Segment 文件，到达阈值后滚动新文件。
删除策略：按时间（retention.ms，默认 7 天）或按大小（retention.bytes）
```

**为什么快**：顺序写磁盘（不是随机写）、Page Cache（OS 级缓存）、sendfile 零拷贝（数据不经过用户态，直接内核到网卡）、批量 + 压缩。

### 生产者可靠性

```text
acks=0   → 不等确认，最快，可能丢
acks=1   → Leader 写入即确认（默认），Leader 宕机可能丢
acks=all(-1) → 所有 ISR 副本写入才确认，最安全，最慢
```

**ISR（In-Sync Replicas）**：和 Leader 保持同步的副本集合。`acks=all` + `min.insync.replicas=2` 是最安全的配置。`min.insync.replicas` 是至少要多少个 ISR 确认。

### 消费者 Offset 管理

```text
旧版：Offset 存在 ZooKeeper
新版（0.9+）：存在 Kafka 内部 Topic __consumer_offsets

enable.auto.commit=true  → 自动提交（默认 5s），可能重复消费
enable.auto.commit=false → 手动提交，更可控
```

**消费语义**：

| 语义 | 实现 | 适用 |
|------|------|------|
| At-most-once | 先提交 offset，再处理 | 允许丢、不允许重复 |
| At-least-once | 先处理，再提交 offset | 允许重复、不允许丢（默认） |
| Exactly-once | 事务 API（幂等 Producer + 事务 Consumer）| 两个都不允许 |

---

## Why — 为什么这样设计

### Kafka vs 其他 MQ

| | Kafka | RabbitMQ | RocketMQ |
|------|-------|---------|----------|
| 吞吐量 | 百万/秒 | 万/秒 | 十万/秒 |
| 消息模型 | Pull（消费者拉） | Push（Broker 推） | Pull |
| 消息回溯 | 支持（按 offset 重放） | 不支持（消费即删） | 支持 |
| 持久化 | 磁盘顺序写 | 内存 + 磁盘 | 磁盘 |
| 延迟 | 毫秒级 | 微秒级 | 毫秒级 |
| 适合场景 | 日志、流处理、大数据 | 业务消息、RPC | 电商、金融 |

**Kafka 的核心优势是回溯**——消息消费后不删除，可重复消费、重放历史数据。这是 RabbitMQ 做不到的。

### 在 LLM/Agent 系统中的应用

```text
Agent 事件流：
  user query → Kafka → RAG Service 消费 → 生成结果 → Kafka → 返回

实时数据处理：
  Agent 日志 → Kafka → Logstash → ES → Kibana（可观测）

异步解耦：
  Agent 对话结束 → 发事件到 Kafka → 记忆提取服务消费 → 写 Memory
```

---

## 面试追问

### Kafka 为什么快？

顺序写磁盘、Page Cache、sendfile 零拷贝、批量 + 压缩、分区并行。不需要 B-tree 索引（MySQL），只是追加写。

### 消息丢失和重复怎么办？

丢失：`acks=all` + `min.insync.replicas=2` 保证写不丢。重复：消费端等幂处理（唯一 ID 去重、Redis 判重、数据库唯一键）。Kafka 保证至少一次，等幂靠自己。

### Leader 挂了怎么办？

Controller 从 ISR 中选新 Leader，Follower 追上 Leader 的 LEO（Log End Offset）后成为新 Leader。新 Leader 的 offset 不会比旧 Leader 多——没同步完的消息丢了。

### 消息积压怎么办？

紧急：加消费者实例（不超过分区数）。长期：加分区 + 加消费者、限制生产者速率、监控消费 lag 告警。
