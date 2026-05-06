# 为什么需要 Agent？

Agent 是为了解决 LLM 的瓶颈。

LLM 本质是一个"文本生成器"——给它输入，它预测下一个 token。这个机制决定了它有三个无法靠自身突破的瓶颈：

1. **知识** — 时效性不够（训练有截止）、幻觉（不知道就瞎编）、上下文限制（窗口有限，塞多了丢注意力）
2. **行动** — LLM 只能输出文本，不能执行
3. **复杂任务推理** — 面对错综复杂的任务，LLM 很难通过一次"端到端"的生成给出完美答案

Agent 的思路不是在模型层面解决这些问题，而是在**系统层面**给 LLM 装上"手"和"眼"——让它能调用外部工具获取信息、执行操作，从"只会说"变成"会说也会做"。

## 三个瓶颈对应的解决方案

| 瓶颈     | 解决思路                         | 关键技术                       |
| -------- | -------------------------------- | ------------------------------ |
| 知识     | 按需检索 + 持久记忆          | RAG / Function Call / MCP / Memory |
| 行动     | 模型决定调什么工具，外部执行     | Function Call / Tool Use       |
| 复杂任务 | 拆解为子步骤逐步推进；单 Agent 不够时多 Agent 分工协作 | Plan-and-Solve / ReAct / Multi-Agent |

- **知识**分两条路——实时信息靠检索（RAG / MCP），历史信息靠记忆（Memory），而不是全塞进 prompt
- **行动**靠工具调用——模型输出的是"我要调哪个函数、什么参数"，外部代码执行
- **复杂任务**靠 Plan-and-Solve——科学拆解，逐步推进。当单个 Agent 到上限时，引入多 Agent 分工协作

## Agent 的典型应用场景

- 旅行助手：查天气 → 查票务 → 订票（多步骤协作）
- 数据分析 Agent：理解自然语言 → 生成 SQL → 执行查询 → 可视化
- 客服系统：知识库检索 + 工单系统 + 人工转接

# 什么是 Agent？

## Agent 的定义

Agent（智能体）是能够感知环境、进行决策和执行动作的智能实体。

> **Agent = LLM + 工具 + 记忆 + 规划**

从大模型视角看，Agent 就是基于 LLM 的语义理解和推理能力，让其拥有解决复杂问题的任务规划能力，调用外部工具执行任务，并保留"记忆"的智能体。

## Agentic 的含义

Agentic 描述一个系统"像 Agent 一样的程度"——自主性、目标导向性、主动性越强，Agentic 程度越高。

## Agent 的核心组件

| 组件 | 作用 | 实现方式 |
|------|------|----------|
| LLM | 大脑，语义理解与推理 | GPT / Qwen / DeepSeek |
| 工具 | 外部能力扩展，解决知识+行动瓶颈 | Function Call / MCP |
| 记忆 | 上下文与历史记录，解决上下文限制 | 对话历史 / 向量数据库 |
| 规划 | 任务分解与多步骤执行，解决复杂任务 | ReAct / Planning / Multi-Agent |

# 怎么实现 Agent？

## 一、Function Call（工具调用基础）

Function Call 是 Agent 调用工具的底层机制。大模型根据任务智能决策何时调用哪个函数，返回符合函数参数的 JSON 对象。

**不是所有模型都有 Function Call 能力，这是训练得到的。**

### 工作流程

1. 客户端发送提示词 + 可用函数列表给 LLM
2. LLM 判断：用普通文本回复 or 返回函数调用指令（JSON）
3. 如果是函数调用，客户端执行函数，将结果返回 LLM
4. LLM 整合结果，生成最终自然语言回复

### 三种定义工具的方式

| 方式 | 适用场景 | 特点 |
|------|----------|------|
| JSON Schema（手动字典） | 需要最大灵活性、与其他系统集成 | 完全手动，繁琐但可控 |
| `@tool` 装饰器 | 快速开发、简单工具（推荐） | 自动生成 Schema，最简洁 |
| Pydantic BaseModel | 需要复杂数据校验 | 强大验证，需手动实现 `invoke` |

### 核心代码模式

```python
# 1. 定义工具
@tool
def add(a: int, b: int) -> int:
    """将数字 a 与数字 b 相加"""
    return a + b

# 2. 绑定工具到模型
llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

# 3. 第一次调用 — LLM 决定是否调用工具
ai_msg = llm_with_tools.invoke(messages)

# 4. 如果 LLM 返回了 tool_calls，执行工具，将结果追加到 messages
if ai_msg.tool_calls:
    for tool_call in ai_msg.tool_calls:
        result = execute_tool(tool_call)
        messages.append(ToolMessage(content=result, ...))

# 5. 第二次调用 — LLM 基于工具结果生成最终回复
final_response = llm_with_tools.invoke(messages)
```

详见 [Function Call](FunctionCall.md)

## 二、MCP 协议（标准化工具接入）

MCP（Model Context Protocol）由 Anthropic 提出，目标是统一 LLM 与外部工具的集成方式，解决每个 AI 都要重写一遍工具接入逻辑的问题。

### 核心角色

- **MCP Server（工具提供者）**：将本地函数包装为标准 MCP 接口暴露出去
- **MCP Client（工具消费者）**：连接 MCP Server，自动发现工具列表，按需调用

### 三种传输方式

| 传输方式 | 通信方向 | 适用场景 |
|----------|----------|----------|
| stdio | 双向 | 本地命令行工具，进程间通信 |
| SSE | 单向（服务器→客户端） | 局域网/远程，简单数据推送 |
| Streamable HTTP | 双向流 | 复杂网络环境，实时双向通信 |

### 标准 MCP Server 创建（FastMCP）

```python
from mcp.server import FastMCP

mcp = FastMCP('my_server', log_level='ERROR', host="127.0.0.1", port=8001)

@mcp.tool(name="get_weather", description="查询天气")
async def get_weather(city: str) -> str:
    return f"{city}的天气是多云"

mcp.run(transport="streamable-http")  # or "sse" / "stdio"
```

### 客户端调用

```python
# 加载 MCP 工具，转换成 LangChain 可用工具
tools = await load_mcp_tools(session)

# 或直接通过 session 调用
result = await session.call_tool("get_weather", {"city": "北京"})
```

详见 [MCP](MCP.md)

## 三、Agent 五种模式

### 3.1 工具使用模式（Tool Use）

Agent 自动完成工具的选择和调用，基于工具结果生成回答。最基础的模式。

### 3.2 ReAct 模式（Reasoning + Acting）

**边想边做**：Thought → Action → Observation → Thought → ... → Final Answer

这是 Agent 的核心循环模式，让决策过程有迹可循。

### 3.3 反思模式（Reflection）

Agent 完成任务后进行自我评估，根据反馈修正结果。相当于"做完检查一遍"。

### 3.4 规划模式（Planning）

先将复杂目标分解为有序的子任务列表，再逐一执行（每个子任务可能是 ReAct 循环）。

### 3.5 多智能体模式（Multi-Agent）

多个不同角色的 Agent 协同工作，各自负责擅长的子任务。

### 演进关系

```
Tool Use → ReAct → Planning → Reflection → Multi-Agent
 (基础)    (核心循环)  (宏观规划)   (质量保证)    (规模化协作)
```

真正的强 Agent 系统会**灵活组合**这些模式，根据任务复杂度嵌套使用。

详见 [Agent 模式](AgentPatterns.md)

## 四、A2A 协议（Agent 间通信）

A2A（Agent-to-Agent）是 Google 提出的协议，解决不同 Agent 之间的通信与协作问题。

### 核心概念

| 概念 | 说明 |
|------|------|
| AgentCard | Agent 的"名片"，声明身份、能力(AgentSkill)、接口信息 |
| AgentSkill | Agent 可被调用的具体功能 |
| Task | 要完成的目标，包含 session_id、状态、内容、结果 |
| TaskState | 任务状态：SUBMITTED → PROCESSING → COMPLETED / FAILED |
| AgentNetwork | Agent 网络管理，集中管理和发现 A2A Server |
| AIAgentRouter | 根据任务需求和 AgentCard 信息，将任务路由到最合适的 Agent |

### A2A + MCP 协作架构

```
客户端 → A2A Server (主控 Agent) → MCP Server (工具层)
           ↓                              ↓
       LLM 决策                       执行具体操作
```

### 多意图并行处理

1. LLM 分解用户复杂查询 → 多个子查询
2. 分别路由到不同专家 Agent
3. `asyncio.gather()` 并行执行
4. 收集结果、整合输出

详见 [A2A](A2A.md)

# Agent 技术栈总结

| 层级         | 技术             | 解决的瓶颈               |
| ------------ | ---------------- | ------------------------ |
| 工具调用     | Function Call    | 知识（查信息）+ 行动（执行） |
| 工具标准化   | MCP              | 知识 + 行动（统一工具接口） |
| 智能决策     | Agent 五种模式   | 复杂任务（推理、规划、执行） |
| Agent 间协作 | A2A              | 复杂任务（多 Agent 协同）   |
| 框架         | LangChain / LangGraph | —（提供开发抽象和编排能力） |

# Agent 发展

## 当前趋势

- **MCP 成为标准** — OpenAI、Anthropic、Google 都已支持 MCP
- **A2A 协议推广** — Google 主推，解决多 Agent 协作
- **Agentic RAG** — RAG + Agent，检索过程由 Agent 自主决策
- **多 Agent 编排** — 从单 Agent 到 Agent 网络的演进

## 与 RAG 的关系

- RAG 是 Agent 的一种工具（检索工具）
- Agent 可以决定何时检索、检索什么、如何整合检索结果
- Agentic RAG = Agent 自主决策的 RAG 流程
