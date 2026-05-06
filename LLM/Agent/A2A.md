# A2A（Agent-to-Agent Protocol）

## 什么是 A2A

A2A 是 Google 提出的 Agent 间通信协议，让不同 Agent 能够互相发现、通信、协作。如果 MCP 解决了 "LLM 怎么用工具"，A2A 解决的就是 "Agent 怎么和 Agent 协作"。

## 核心作用

| 能力 | 说明 |
|------|------|
| 能力发现 | AgentCard 自动声明能力，其他 Agent 可自动发现 |
| 任务与状态管理 | 提交任务后可跟踪状态和处理结果 |
| 安全协作 | 保证 Agent 间信息传递的安全 |
| 用户体验协商 | Agent 根基反馈调整响应 |

## 核心概念

### AgentCard（Agent 名片）

```python
from python_a2a import AgentCard, AgentSkill

agent_card = AgentCard(
    name="WeatherAgentServer",
    description="一个天气预报查询的专家 Agent",
    url="http://127.0.0.1:5008",
    skills=[
        AgentSkill(
            name="query",
            description="接受天气查询",
            examples=["天气北京"]
        )
    ]
)
```

### AgentSkill（技能声明）

定义 Agent 可被外部调用的具体功能，包含名称、描述、调用示例。

### Task（任务）

```python
from python_a2a import Task, Message, TextContent, MessageRole

message = Message(
    content=TextContent(text="查询北京天气"),
    role=MessageRole.USER
)
task = Task(message=message.to_dict(), id="task-" + str(uuid.uuid4()))
```

### TaskState（任务状态）

`SUBMITTED` → `PROCESSING` → `COMPLETED` / `FAILED` / `INPUT_REQUIRED`

### AgentNetwork（代理网络）

```python
from python_a2a import AgentNetwork

network = AgentNetwork(name="TravelOrchestrator")
network.add("WeatherAgent", "http://127.0.0.1:5008")
network.add("TicketAgent", "http://127.0.0.1:5009")

# 获取某个 Agent 客户端
weather_client = network.get_agent("WeatherAgent")
```

### AIAgentRouter（智能路由）

```python
from python_a2a import AIAgentRouter, A2AClient

router = AIAgentRouter(
    llm_client=A2AClient("http://127.0.0.1:5555"),
    agent_network=network
)

agent_name, confidence = router.route_query("帮我查下北京的天气")
# → ("WeatherAgent", 0.95)
```

根据查询语义和 AgentCard，自动选择最合适的 Agent。

## A2A Server 实现

```python
from python_a2a import A2AServer, run_server, TaskStatus, TaskState

class WeatherServer(A2AServer):
    def __init__(self):
        super().__init__(agent_card=agent_card)

    def handle_task(self, task):
        # 1. 提取用户查询
        query = task.message.get("content", {}).get("text", "")

        # 2. 处理业务逻辑（可调用 MCP Server）
        weather_result = query_weather(query)

        # 3. 设置返回结果
        task.artifacts = [{"parts": [{"type": "text", "text": weather_result}]}]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        return task

# 启动
run_server(WeatherServer(), host="127.0.0.1", port=5008)
```

## A2A + MCP 协作架构

```
客户端
  └── A2A Server（主控 Agent）—— LLM 决策层
        └── MCP Client
              └── MCP Server（工具层）—— 数据库/API 实际操作
```

```
用户 "查北京天气"
  → 客户端 → A2A WeatherServer
    → WeatherServer.handle_task()
      → MCP Client → MCP Server.query_weather()
        → SQL 查询数据库
      ← 返回天气数据
    ← 格式化结果，设置 task.artifacts
  ← 返回最终答案给用户
```

## 串行协作

多个 A2A Agent 串行执行，前一个的输出作为后一个的输入：

```python
# 1. 先查天气
weather_result = await weather_client.send_task_async(weather_task)
weather_info = weather_result.artifacts[0]["parts"][0]["text"]

# 2. 根据天气结果订票
ticket_query = f"预订火车票，当前天气是：{weather_info}"
ticket_result = await ticket_client.send_task_async(ticket_task)
```

## 多意图并行处理

对于复杂查询，先分解再并行执行：

```python
# 1. LLM 分解查询
# "帮我查北京天气，预订北京到上海的火车票"
# → ["查北京天气", "预订北京到上海火车票"]

# 2. 分别路由到不同 Agent
for sub_query in sub_queries:
    agent_name, confidence = router.route_query(sub_query)
    agent_client = network.get_agent(agent_name)
    tasks.append(agent_client.send_task_async(agent_task))

# 3. 并行执行
results = await asyncio.gather(*tasks, return_exceptions=True)

# 4. 解析结果
for i, result in enumerate(results):
    # 提取 artifacts 中的 parts
    for artifact in result.artifacts:
        for part in artifact["parts"]:
            if part.get("type") == "text":
                print(part.get("text"))
```

## LangChain LLM 转 A2A Server

可以直接把一个 LangChain LLM 转换为 A2A Server：

```python
from python_a2a.langchain import to_a2a_server

llm = ChatOpenAI(...)
llm_server = to_a2a_server(llm)
run_server(llm_server, port=5555)
```

这样 LLM Server 就可以作为一个路由决策节点，被 AgentNetwork 使用。

## MCP vs A2A

| 维度 | MCP | A2A |
|------|-----|-----|
| 解决什么 | LLM ↔ 工具的通信 | Agent ↔ Agent 的通信 |
| 提出方 | Anthropic | Google |
| 核心概念 | Server/Client，Tool | AgentCard/Task/AgentNetwork |
| 典型场景 | 标准化的工具调用接口 | 多 Agent 系统的协作编排 |
| 关系 | 底层工具协议 | 上层协作协议（可调用 MCP） |
