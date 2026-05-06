# SmartVoyage — 基于 A2A + MCP 的旅行智能助手

## 项目架构

```
用户 → Streamlit 前端
         ↓
    main.py（意图识别 + 查询改写 + 路由分发）
         ↓
    A2A 层（Agent Server）
    ├── WeatherQueryAssistant（天气查询）→ 调用 MCP
    ├── TicketQueryAssistant（票务查询）→ 调用 MCP
    └── TicketOrderAssistant（票务预定）→ 调用 MCP + 票务查询 Agent
         ↓
    MCP 层（工具 Server）
    ├── WeatherTools（天气 MCP）→ MySQL 查询
    ├── TicketTools（票务 MCP）→ MySQL 查询
    └── OrderTools（订票 MCP）→ API 调用
         ↓
    数据层
    ├── MySQL（天气表 + 票务表）
    └── spider_weather（定时从和风天气爬取）
```

**调用链路**：客户端 → A2A Server → MCP Server → MySQL/API

---

## 一、数据层

### 天气数据爬取

- 数据来源：和风天气 API
- 更新策略：每隔 1 小时检查每个城市的最新更新时间，超过 1 天则拉取新数据
- 存储方式：MySQL `weather_data` 表，使用 `INSERT ... ON DUPLICATE KEY UPDATE`（upsert）
- **直接查数据库而非每次调 API**：减少 API 成本、降低网络延迟

### 票务数据

- 火车票、机票、演唱会票预先存储在 MySQL
- **注意**：实际生产中票务信息变化快，应通过 API 实时查询，而非从数据库查静态数据

---

## 二、MCP 层

### 天气 MCP Server

工具函数接收 SQL 查询，查询 MySQL，返回格式化 JSON：

```python
weather_mcp = FastMCP(name="WeatherTools", host="127.0.0.1", port=8002)

@weather_mcp.tool(name="query_weather", description="查询天气数据，输入 SQL")
def query_weather(sql: str) -> str:
    return service.execute_query(sql)  # 查 MySQL → 返回 JSON

weather_mcp.run(transport="streamable-http")
```

### 票务 MCP Server

同样模式：接收 SQL → 查询 `train_tickets` / `flight_tickets` / `concert_tickets` 表 → 返回 JSON。

### 订票 MCP Server

工具函数直接接收订票参数，模拟调用 API：

```python
@order_mcp.tool(name="order_train", description="预定火车票")
def order_train(departure_date: str, train_number: str, seat_type: str, number: int) -> str:
    return "恭喜，火车票预定成功！"
```

---

## 三、A2A 层

### A2A Server + MCP 结合模式

```python
class WeatherServer(A2AServer):
    def __init__(self):
        super().__init__(agent_card=agent_card)
        self.mcp_client = MCPClient('http://127.0.0.1:6005')

    def handle_task(self, task):
        query = task.message.get("content", {}).get("text", "")
        result = asyncio.run(self.mcp_client.call_tool(tool_name="get_weather", city=city))
        task.artifacts = [{"parts": [{"type": "text", "text": result}]}]
        task.status = TaskStatus(TaskState.COMPLETED)
        return task
```

### NLP2SQL（天气/票务 Agent Server 的核心）

LLM + 表结构 schema → 生成 SQL。不是简单的"把字段填进去"，核心挑战是**信息不足时不能瞎查**。

**提示词结构**（以天气查询为例）：

```
系统提示：你是天气 SQL 生成器。从对话历史中提取城市和时间，生成 SELECT。
- 信息齐全 → 输出纯 SQL
- 信息不足 → 输出追问 JSON

示例：
- user: 北京 2025-07-30
  → SELECT city, fx_date, temp_max, temp_min, text_day ... FROM weather_data WHERE city='北京' AND fx_date='2025-07-30'
- user: 北京的天气
  → {"status": "input_required", "message": "请提供具体日期，例如 '2025-07-30'"}

表结构：{table_schema_string}
对话历史：{conversation}
当前日期：{current_date}
```

**决策流程**：

```
LLM 输出判断：
├── 以 "{" 开头 → 追问 JSON → TaskState.INPUT_REQUIRED → 返回追问给用户
├── 纯 SQL → 调用 MCP → 查 MySQL → 格式化结果 → TaskState.COMPLETED
└── 解析失败 → TaskState.FAILED
```

**追问机制的价值**：不是简单的 if-else 判断参数够不够，而是让 LLM 理解对话上下文——"后天呢"隐含了"同一个城市"——LLM 从历史对话中推断城市后追问日期，而不是硬编码校验。

**票务查询的额外复杂度**：需要先识别票务类型（train / flight / concert），不同类型查不同表、不同字段。提示词先输出 `{"type": "train"}` 再输出 SQL，分两行。

---

## 四、客户端层

### 意图识别 + 查询改写

**为什么这两个要一起做？**

用户说话天然缺上下文：
- "后天呢" → 什么后天？哪个城市？
- "订一张" → 订什么？从哪到哪？

如果只做意图识别不补全，后面 Agent 拿到的是残缺问题。如果只补全不做意图识别，路由不知道发给谁。

所以同一个 LLM 调用同时完成两件事：识别意图 + 从历史对话中提取上下文补全问题。

**提示词结构**：

```
系统提示：你是旅行意图识别专家。基于用户查询和对话历史，识别意图并改写查询。
- 支持意图：['weather', 'flight', 'train', 'order', 'concert', 'attraction']
- 意图超出范围 → 返回 'out_of_scope'，直接回复 follow_up_message
- 意图不明确 → 生成追问到 follow_up_message
- 查询改写：从对话历史中提取相关上下文整合，不修改原意

输出严格 JSON：
{"intents": ["intent1"], "user_queries": {"intent1": "改写后的查询"}, "follow_up_message": ""}

示例：
- "后天呢" + 历史：assistant 说"北京" → {"intents":["weather"], "user_queries":{"weather":"北京2025-10-28天气"}}
- "订一张" + 历史：user 查了北京到上海火车票 → {"intents":["order"], "user_queries":{"order":"预订北京到上海火车票"}}
- "你好" → {"intents":["out_of_scope"], "user_queries":{}, "follow_up_message":"我是旅行助手，可以查天气、订票"}
```

**关键约束**：
- 改写时只补全上下文，不回答用户问题，不修改原意
- 区分订票（order）和查询（flight/train/concert）——"订"就是 order
- `out_of_scope` 不走路由，直接返回 follow_up_message

### AIAgentRouter

根据查询语义和 AgentCard，自动路由到最合适的 Agent：

```python
router = AIAgentRouter(llm_client=llm, agent_network=network)
agent_name, confidence = router.route_query("订北京去上海的火车票")
# → ("TicketOrderAssistant", 0.95)
```

### 复杂任务拆解与并行

**拆解**：

LLM + 提示词将复合查询分解为独立子查询：

```
提示词：
将以下用户查询分解为独立的子查询，每个子查询对应一个单一意图。
返回 JSON：{"sub_queries": ["子查询1", "子查询2", ...]}

示例：
查询: "预订票,查天气" → {"sub_queries": ["预订票", "查天气"]}
查询: {query}
```

```
输入："帮我查北京天气，预订北京到上海火车票"
输出：{"sub_queries": ["查北京天气", "预订北京到上海火车票"]}
```

**路由 + 并行执行**：

```
拆解后的子查询
├── "查北京天气" → AIAgentRouter → WeatherQueryAssistant → send_task_async (协程)
└── "预订北京到上海火车票" → AIAgentRouter → TicketOrderAssistant → send_task_async (协程)
    │
    └── asyncio.gather(*协程列表) → 并行执行 → 收集结果
```

关键代码：

```python
tasks = []  # 协程对象列表
for sub_query in sub_queries:
    agent_name, confidence = router.route_query(sub_query)
    agent_client = network.get_agent(agent_name)
    message = Message(content=TextContent(text=sub_query), role=MessageRole.USER)
    task = Task(message=message.to_dict(), id=str(uuid.uuid4()))
    # 不 await — 获取协程对象而非执行结果
    tasks.append(agent_client.send_task_async(task))

# 并行执行 — asyncio.gather 同时发所有请求
results = await asyncio.gather(*tasks, return_exceptions=True)

# 解析每个结果
for i, result in enumerate(results):
    for artifact in result.artifacts:
        for part in artifact["parts"]:
            if part.get("type") == "text":
                print(part.get("text"))
```

**为什么用协程而非线程**：Agent 调用的瓶颈是网络 I/O（等 A2A Server 响应），不是 CPU 计算。协程在等待时不占线程，一个事件循环可以管理大量并发请求。

---

## 五、对话管理

### 上下文存储

- **内存**：列表循环保存最近 5 轮对话，快速取用
- **持久化**：MySQL 异步存储，支持历史查询和长对话

### 上下文过长处理

两种策略：

- **简单任务**（天气/票务查询）：只取最近 3 轮对话
- **复杂任务**（路线规划/景点推荐）：使用 GLM-4-32B 进行**递归压缩**

**递归压缩流程**：

1. 将超长上下文划分为多个片段（每块 64K）
2. 问题 + 第一个片段 → LLM 压缩（只保留对问题有意义的内容）
3. 问题 + 压缩结果 + 第二个片段 → 继续压缩
4. 循环直到压缩完所有片段

---

## 架构要点总结

| 层级 | 关键设计 |
|------|----------|
| 数据 | 定时间隔爬取 + MySQL upsert，减少 API 成本 |
| MCP | 工具函数就是 SQL 查询器，统一 Streamable HTTP |
| A2A | Server 内嵌 MCPClient，handle_task 中调用 MCP 工具 |
| NLP2SQL | LLM 生成 SQL + 追问能力，Table Schema 写进 Prompt |
| 路由 | 意图识别 → 查询改写 → AIAgentRouter → 并行执行 |
| 上下文 | 5 轮内存缓存 + MySQL 持久化 + 递归压缩处理长上下文 |
