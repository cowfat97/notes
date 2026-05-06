# Function Call

## 为什么需要 Function Call？

LLM 只能输出文本，不能执行。遇上"今天北京天气怎么样"，模型要么编造（幻觉），要么说"我没有实时数据"。

Function Call 给了它第三种选择：输出一个结构化指令，让外部代码代为执行。

**Function Call 不是 LLM 的能力，是 LLM 与工具之间的交互流程。**

## 什么是 Function Call？

LLM 做的事没变——还是输出 token。变的只是输出格式：

```
普通输出：  "北京晴天，25度"  ← 编的
Function Call：{"name": "get_weather", "arguments": {"city": "北京"}}  ← 调用意图
```

LLM 输出"要调什么、传什么参数"，外部代码执行，结果返回给 LLM，LLM 再生成回复。

**LLM 是意图输出器，不是执行器。**

## 怎么用 Function Call？

### 1. 定义工具

本质就一件事：告诉 LLM **工具叫什么、能干什么、参数长什么样**。

**方式一：JSON Schema（手动字典）**

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

最灵活，最繁琐。跨框架通用。

**方式二：`@tool` 装饰器（推荐）**

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """将数字a与数字b相加"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """将数字a与数字b相乘"""
    return a * b

tools = [add, multiply]
```

框架自动从函数签名 + docstring 生成 Schema。调用时用 `func.invoke(tool_call["args"])`，LangChain 做了包装。

**方式三：Pydantic BaseModel**

```python
from pydantic.v1 import BaseModel, Field

class Add(BaseModel):
    """将两个数字相加"""
    a: int = Field(..., description="第一个数字")
    b: int = Field(..., description="第二个数字")

    def invoke(self, args):
        tool_instance = self.__class__(**args)
        return tool_instance.a + tool_instance.b
```

参数校验最强，需手动实现 invoke。适合复杂约束场景。

**选型：能用 `@tool` 就用 `@tool`，校验要求高用 Pydantic，跨框架用 JSON Schema。**

### 2. 交互流程：两次 invoke

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气"""
    if "北京" in city:
        return "北京今天是晴天，气温25摄氏度"
    return f"抱歉，没有{city}的天气数据"

@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积"""
    return a * b

llm = ChatOpenAI(...)
llm_with_tools = llm.bind_tools([get_weather, multiply])

# === 第一次 invoke — LLM 返回 tool_calls ===
messages = [HumanMessage("查一下北京的天气，然后算 30×5")]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

# ai_msg 内容：
# AIMessage(content='', tool_calls=[
#     {"name": "get_weather", "args": {"city": "北京"}, "id": "call_001"},
#     {"name": "multiply",    "args": {"a": 30, "b": 5},    "id": "call_002"}
# ])

# === 外部执行工具 — 结果包装为 ToolMessage ===
func_map = {"get_weather": get_weather, "multiply": multiply}
for tc in ai_msg.tool_calls:
    func = func_map[tc["name"]]
    result = func.invoke(tc["args"])
    messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

# messages 现在是 4 条：
# [HumanMessage, AIMessage(tool_calls), ToolMessage(天气), ToolMessage(乘法)]

# === 第二次 invoke — LLM 基于工具结果生成回复 ===
final = llm_with_tools.invoke(messages)
# "北京晴天25度。30×5等于150。"
```

流程总结：

```
HumanMessage → LLM → AIMessage(tool_calls) → 外部执行
    → ToolMessage → LLM → AIMessage(最终回复)
```

### 3. 消息体系

三种**输入**消息类型：

| 类型 | 角色 | 说明 |
|------|------|------|
| `SystemMessage` | 系统指令 | 定规则、定角色、定行为边界 |
| `HumanMessage` | 用户输入 | 用户的问题 |
| `ToolMessage` | 工具结果 | 工具执行完的结果，通过 `tool_call_id` 关联对应 tool_call |

AIMessage 是 LLM 的**输出**。tool_calls 附着在 AIMessage 上出来，ToolMessage 带着结果回去。

关键：ToolMessage 是**追加**到 messages 列表，不是替换。messages 累加，LLM 需要完整上下文。

### 4. bind_tools vs 直接传参

```python
# 方式 A：bind_tools — 绑定到模型实例，持久有效（推荐）
llm_with_tools = llm.bind_tools(tools, tool_choice="auto")
llm_with_tools.invoke(messages)

# 方式 B：invoke 直接传参 — 仅当次有效
llm.invoke(messages, tools=tools)
```
