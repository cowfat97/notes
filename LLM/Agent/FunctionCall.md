# Function Call（函数调用）

## 什么是 Function Call

Function Call 是一种让大模型根据任务自动决策是否调用函数、调用哪个函数、传什么参数的能力。模型返回的不是最终答案，而是一个结构化的函数调用指令（JSON）。

**不是所有模型都具备 Function Call 能力，这是通过专门训练获得的。** 不具备的模型只能生成纯文本。

## 为什么需要 Function Call

| 问题 | 说明 |
|------|------|
| 信息实时性 | LLM 训练数据有截止日期，无法获取实时信息 |
| 数据局限性 | 无法访问私有数据库、企业内部系统 |
| 功能扩展性 | 不能执行计算、发邮件、操作数据库等操作 |

Function Call 让 LLM 从"聊天机器人"变成"行动者"。

## 工作流程

```
用户请求 → LLM 判断 → 两种响应路径：
                      ├── 普通文本回复（不需要工具）
                      └── Function Call JSON（需要工具）
                            → 客户端执行函数
                            → 结果返回 LLM
                            → LLM 生成最终自然语言回复
```

1. 客户端发送提示词 + 可用函数列表给 LLM
2. LLM 根据语义判断：纯文本回复 or 函数调用
3. 如果是函数调用，返回函数名 + 参数 JSON
4. 客户端执行函数，结果传回 LLM
5. LLM 整合数据，生成自然语言回复

## 三种定义方式

### 方式一：JSON Schema（手动字典）

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "将数字a与数字b相加",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "第一个数字"},
                    "b": {"type": "integer", "description": "第二个数字"}
                },
                "required": ["a", "b"]
            }
        }
    }
]
```

- **优点**：完全手动控制，跨框架兼容
- **缺点**：繁琐，易出错
- **适用**：需要与第三方系统集成、对 Schema 有精确控制

### 方式二：`@tool` 装饰器（推荐）

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """
    将数字a与数字b相加
    Args:
        a: 第一个数字
        b: 第二个数字
    """
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """将数字a与数字b相乘"""
    return a * b

tools = [add, multiply]
```

- **优点**：最简洁，自动从函数签名和 docstring 生成 Schema
- **注意**：调用时要用 `func.invoke(tool_call["args"])`，因为 LangChain 做了包装
- **适用**：90% 的场景，快速开发首选

### 方式三：Pydantic BaseModel

```python
from pydantic.v1 import BaseModel, Field

class Add(BaseModel):
    """将两个数字相加"""
    a: int = Field(..., description="第一个数字")
    b: int = Field(..., description="第二个数字")

    def invoke(self, args):
        tool_instance = self.__class__(**args)
        return tool_instance.a + tool_instance.b

tools = [Add, Multiply]
```

- **优点**：强大数据验证，结构清晰
- **缺点**：需要手动实现 `invoke`，代码量最大
- **适用**：参数复杂、需要严格校验的场景

## 完整调用代码

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage

# 1. 定义工具
@tool
def add(a: int, b: int) -> int:
    """将数字a与数字b相加"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """将数字a与数字b相乘"""
    return a * b

# 2. 初始化模型 + 绑定工具
llm = ChatOpenAI(...)
llm_with_tools = llm.bind_tools([add, multiply], tool_choice="auto")

# 3. 第一次调用
messages = [HumanMessage("2+1等于多少？")]
ai_msg = llm_with_tools.invoke(messages)

# 4. 处理工具调用
if ai_msg.tool_calls:
    for tool_call in ai_msg.tool_calls:
        func = {"add": add, "multiply": multiply}[tool_call["name"].lower()]
        result = func.invoke(tool_call["args"])
        messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

    # 5. 第二次调用 — 生成最终回复
    final_response = llm_with_tools.invoke(messages)
```

## `bind_tools` vs 直接传参

```python
# 方式 A：bind_tools — 绑定到模型实例，持久有效
llm_with_tools = llm.bind_tools(tools, tool_choice="auto")
llm_with_tools.invoke(messages)

# 方式 B：直接传参 — 仅当次调用有效
llm.invoke(messages, tools=tools)
```

推荐 `bind_tools`，后续多次调用不需要反复传入。

## Agent 使用 Function Call

```python
from langchain.agents import initialize_agent, AgentType

agent = initialize_agent(
    tools, llm,
    AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
result = agent.invoke("2+1等于多少？")
```

Agent 封装了 Function Call 的整个流程：判断→调用→回传→生成，开发者只需定义工具即可。
