# LangGraph

LangChain 出品的 Agent 编排框架，核心思路：**把 Agent 的决策流程建模为有向图（DAG）**，节点是操作，边是流转规则。

## 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| **StateGraph** | 状态图，定义整个 Agent 流程 | 流程图 |
| **State** | 在节点间传递的共享数据（通常是消息列表） | 上下文 |
| **Node** | 一个执行单元（LLM 调用 / 工具执行 / 人工确认） | 流程图节点 |
| **Edge** | 节点间的固定流转 | 连线 |
| **Conditional Edge** | 根据条件动态选择下一节点 | 菱形判断 |
| **interrupt()** | 暂停执行，等待外部输入 | 断点 |
| **Command(resume=...)** | 外部输入后恢复执行 | 继续 |

## create_react_agent（快速版）

一行构建 ReAct Agent，LangGraph 内部自动搭 LLM → Tool → LLM 循环：

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=ChatOpenAI(...),
    tools=[...],
    prompt="你是一个有用的助手",
)

result = agent.invoke({"messages": [{"role": "user", "content": "你是谁？"}]})
```

适合简单场景，不需要自定义流程。

## 手动构建 Graph（自定义版）

复杂场景需要自己搭节点和边：

### 1. 定义 State

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]  # add_messages 实现消息累加
```

### 2. 定义节点

```python
def llm_node(state: State) -> State:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: State) -> State:
    last_msg = state["messages"][-1]
    for tc in last_msg.tool_calls:
        func = tool_map[tc["name"]]
        result = func.invoke(tc["args"])
        return {"messages": [ToolMessage(content=str(result), tool_call_id=tc["id"])]}
```

### 3. 构建 Graph

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(State)

graph.add_node("llm", llm_node)
graph.add_node("tool", tool_node)

graph.add_edge(START, "llm")
graph.add_conditional_edges(
    "llm",
    lambda state: "tool" if state["messages"][-1].tool_calls else END,
    {"tool": "tool", END: END}
)
graph.add_edge("tool", "llm")  # 工具执行后回到 LLM

app = graph.compile()
```

### 标准 ReAct 图结构

```
START → LLM ──(有tool_calls)──→ Tool
           │                       │
           └──(无tool_calls)──→ END ←┘
```

## Human-in-the-Loop（人工干预）

工具调用前暂停，等人工确认后再执行。

### 定义干预节点

```python
from langgraph.types import interrupt, Command

def human_review_node(state: State) -> State:
    last_msg = state["messages"][-1]
    if not last_msg.tool_calls:
        return state

    user_decision = interrupt({
        "type": "human_review",
        "tool_name": last_msg.tool_calls[0]["name"],
        "tool_args": last_msg.tool_calls[0]["args"],
        "message": "是否执行此工具调用？"
    })

    if user_decision == "y":
        return state                       # 继续执行
    else:
        return {"messages": [AIMessage(content="人工拒绝")]}  # 跳过工具
```

### 调用方式

```python
# 第一次运行：到 human_review 节点自动暂停
for event in app.stream(
    {"messages": [HumanMessage(content=query)]},
    config={"configurable": {"thread_id": "session-1"}},
    stream_mode="values"
):
    last_msg = event["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        print(f"模型要调用: {last_msg.tool_calls[0]['name']}")

# 第二次运行：人工确认后恢复
for event in app.stream(
    Command(resume="y"),           # resume 传给 interrupt() 的返回值
    config={"configurable": {"thread_id": "session-1"}},  # 同一个 thread_id
    stream_mode="values"
):
    ...
```

关键：两次调用用同一个 `thread_id`，LangGraph 通过 MemorySaver 记住上次暂停的位置。

### 干预版图结构

```
START → LLM → human_review ──(通过)──→ tool → LLM_final → END
                       │
                       └──(拒绝)──→ LLM_final → END
```

## create_react_agent vs 手动构建

| | create_react_agent | 手动 StateGraph |
|---|-------------------|----------------|
| 代码量 | 3 行 | 50+ 行 |
| 自定义流程 | ❌ | ✓ |
| 人工干预 | ❌ | ✓ interrupt() |
| 多步骤编排 | ❌ | ✓ |
| 适用场景 | 简单问答+工具 | 复杂审批/多Agent协作 |

## 与 A2A + MCP 的关系

```
LangGraph  = 编排引擎（控制 Agent 内部流程怎么走）
MCP        = 工具协议（Agent 能调什么工具）
A2A        = Agent 间协议（多个 Agent 如何协作）
```

LangGraph 图中的一个 tool_node，底层可以接 MCP Server 获取工具，而多个 LangGraph Agent 之间可以通过 A2A 协议通信。
