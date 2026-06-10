# LangGraph

LangChain 做不了的，LangGraph 做——循环、条件分支、状态持久化。

## LangChain 的局限

Chain 是固定流程：A → B → C，一步到底。Agent 需要循环——思考→行动→观察→思考，直到找到答案。Chain 做不到。

## 核心概念

LangGraph 用图来编排 LLM 流程：

1. State

共享字典，图的每个节点都能读写。定义一次，全局可见。

2. Node

图中的节点，每个 Node 是一个函数。可能是调 LLM、调工具、做判断，什么都能干。

3. Edge

节点之间的连线。普通边（A 完了直接到 B）和条件边（根据输出决定去哪个节点）。

4. Conditional Edge

根据当前 State 的值决定下一步。ReAct 循环就是靠它——如果还有工具要调，回到 Action 节点；如果够了，进 Final 节点。

## 完整流程

```text
State 定义 → 创建 StateGraph → add_node → add_edge(条件边) → compile → invoke
```

一个 ReAct Agent 的图：

```text
START → Agent(LLM 决策) → 条件判断 → Tool(执行工具) → Agent(继续思考)
                                       → END(输出最终答案)
```

核心在于**循环**——Agent 可以反复调用工具，直到找到答案。

## Checkpointing

状态持久化。图上每一步的状态自动保存：

- 挂了能恢复，不用从头跑
- 人机交互——用户可以中断、修改 State、继续跑
- 支持容错、流式输出

## Tool 集成

在 Node 里可以：

1. 绑定工具给 LLM（跟普通 Function Call 一样）
2. 在 Action Node 里执行工具调用
3. 结果写回 State，继续循环

```

