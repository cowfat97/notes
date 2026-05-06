# Agent 五种模式

## 模式概览

从简单到复杂：Tool Use → ReAct → Planning → Reflection → Multi-Agent

真正强大的 Agent 系统会**灵活组合**这些模式，而非只用一种。

---

## 1. 工具使用模式（Tool Use）

**本质**：Agent 自动完成工具选择和调用，基于工具结果生成答案。

**流程**：用户输入 → LLM 判断是否需要工具 → 调用工具 → 整合结果 → 输出

**代码**：

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent

tool_calling_agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=tool_calling_agent, tools=tools, verbose=True)
result = executor.invoke({"input": "上海天气怎么样？"})
```

**适用**：简单、单步任务。LLM 自主判断要不要用工具、用哪个。

---

## 2. ReAct 模式（Reasoning + Acting）

**本质**：将思考（Thought）和行动（Action）紧密结合，形成一个动态循环。**"边想边做"**。

**流程**：

```
Thought: 我需要查天气 → Action: search_weather("上海")
Observation: 上海阴天，22°C
Thought: 还需要计算 → Action: multiply("100,25")
Observation: 2500
Thought: 两个任务都完成了 → Final Answer: ...
```

**与 Tool Use 的关键区别**：ReAct 是**显式推理**，每一步思考过程可见，可处理多步任务。Tool Use 是隐式的一次性工具调用。

**代码**：

```python
from langchain.agents import create_react_agent

react_prompt_template = """你是一个有用的 AI 助手，可以访问以下工具：

{tools}

请根据用户输入一步步推理：
1. 每次输出只能包含一个动作或一个最终答案。
2. 格式：
   Thought: [你的思考]
   Action: [工具名称]
   Action Input: [参数]
   或
   Thought: [你的思考]
   Final Answer: [最终答案]

可用的工具名称有: {tool_names}
用户输入: {input}
{agent_scratchpad}
"""

react_prompt = ChatPromptTemplate.from_template(react_prompt_template)
react_agent = create_react_agent(llm, tools, react_prompt)
executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True,
                          handle_parsing_errors=True)

# 多任务
executor.invoke({"input": "请计算100乘以25，并查询上海的天气"})
```

**关键配置**：`handle_parsing_errors=True` — 解析失败时自动重试，避免 LLM 输出格式不规范导致的崩溃。

---

## 3. 反思模式（Reflection）

**本质**：Agent 完成回答后进行自我评估，根据反馈修正。**"做完检查一遍，不行就改"**。

**流程**：

```
1. 生成初步回答
2. 获取反馈（可以是大模型自评 / 评估模型 / 人工反馈）
3. LLM 基于反馈反思 → 生成优化后的回答
```

**代码**：

```python
# 初步回答
initial_chain = initial_prompt | llm | StrOutputParser()
initial_response = initial_chain.invoke({"question": query})

# 反思优化
reflection_chain = reflection_prompt | llm | StrOutputParser()
refined_response = reflection_chain.invoke({
    "previous_response": initial_response,
    "user_feedback": feedback
})
```

**反馈来源**：
- 自身 LLM / 专用评估模型评分
- 调用工具进行验证
- 纯人工反馈

---

## 4. 规划模式（Planning）

**本质**：先将大目标分解为有序的子任务列表（Plan），再逐一执行。

**两个角色**：
- **Planner（规划器）**：分析任务，分解为步骤列表
- **Executor（执行器）**：按顺序执行每个步骤（通常用 ReAct）

**代码**：

```python
# 规划器
planner_prompt = ChatPromptTemplate.from_template(
    """将用户任务分解成一系列清晰、可执行的步骤，每行一个任务。
    用户任务: {user_input}
    任务列表:
    """
)
planner_chain = planner_prompt | llm | StrOutputParser()
plan = planner_chain.invoke({"user_input": query})
tasks = [t.strip() for t in plan.split('\n') if t.strip()]

# 逐一执行
for task in tasks:
    result = executor.invoke({"input": task})
```

**适用**：复杂、多步骤的任务，需要先理清思路再动手。

---

## 5. 多智能体模式（Multi-Agent）

**本质**：多个不同角色、不同能力的 Agent 协同工作。

**示例架构**：

```
用户查询 → 任务分解
              ├── 计算专家（工具：add, multiply）
              ├── 信息专家（工具：search_weather, get_date）
              └── 整合 Agent→ 最终答案
```

**代码**：

```python
# 计算专家
math_agent = create_tool_calling_agent(llm, math_tools, math_prompt)
math_executor = AgentExecutor(agent=math_agent, tools=math_tools, verbose=True)

# 信息检索专家
info_agent = create_tool_calling_agent(llm, info_tools, info_prompt)
info_executor = AgentExecutor(agent=info_agent, tools=info_tools, verbose=True)

# 协调工作流
math_result = math_executor.invoke({"input": math_task}).get("output")
info_result = info_executor.invoke({"input": info_task}).get("output")

# 最终总结
final_answer = summarize_chain.invoke({
    "query": original_query,
    "math_result": math_result,
    "info_result": info_result
})
```

**调用链**：手动分派子任务，最后用 LLM 整合。

---

## 模式演进关系

```
Tool Use ──→ ReAct ──→ Planning ──→ Reflection ──→ Multi-Agent
 (基础)      (核心循环)  (宏观规划)    (质量保证)     (规模化协作)
```

- ReAct 是 Tool Use 的显式化 → 让决策有迹可循
- Planning 是多个 ReAct 循环的高层调度
- Reflection 是对执行结果的检查与优化
- Multi-Agent 是将上述模式在不同 Agent 间组合

## LangChain 中的关键函数

| 函数 | 用途 |
|------|------|
| `create_tool_calling_agent()` | 创建工具使用/多智能体 Agent |
| `create_react_agent()` | 创建 ReAct Agent |
| `AgentExecutor` | Agent 与工具之间的协调器 |
| `initialize_agent()` | (旧版) 统一创建入口 |
