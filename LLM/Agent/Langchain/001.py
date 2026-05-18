'''
Author: haoxinlei howxl97@163.com
Date: 2026-05-01 11:30:12
LastEditors: haoxinlei howxl97@163.com
LastEditTime: 2026-05-06 19:30:13
FilePath: /notes/LLM/Agent/Langchain/001.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# Function Call — 工具定义 + 绑定模型 + 调用流程

# ============================================================
# 第一部分：导包
# ============================================================

from langchain_core.tools import tool                # 定义工具（@tool 装饰器）
from langchain_openai import ChatOpenAI              # LLM 客户端
from langchain_core.messages import (                 # 通信消息
    HumanMessage,     # 用户输入
    AIMessage,        # LLM 输出（可能携带 tool_calls）
    ToolMessage,      # 工具执行结果
)
import os
from dotenv import load_dotenv                       # 加载 .env 环境变量
from pydantic.v1 import BaseModel, Field             # Pydantic 方式定义工具

# ============================================================
# 第二部分：配置
# ============================================================

# 读取配置
load_dotenv()

# llm 客户端
llm = ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    api_key=os.getenv("LLM_API_KEY"),
    model="qwen-plus",
    temperature=0.1,
)

# ============================================================
# 第三部分：代码逻辑
# ============================================================

# 0. 测试 LLM 连通性
response = llm.invoke("你好")
print(f"LLM 测试: {response.content}")

# ============================================================
# 1. 三种定义工具方式
# ============================================================

# 方式一：JSON Schema（手动字典）———————————————————————————
# 完全手动描述工具，跨框架通用

add_schema = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "将两个数字相加",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "第一个数字"},
                "b": {"type": "integer", "description": "第二个数字"},
            },
            "required": ["a", "b"],
        },
    },
}


# 方式二：@tool 装饰器———————————————————————————————————
# 框架自动从函数签名 + docstring 生成 Schema，最简洁

@tool
def add(a: int, b: int) -> int:
    """将数字a与数字b相加"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """将数字a与数字b相乘"""
    return a * b

tools_annotation = [add, multiply]


# 方式三：Pydantic BaseModel—————————————————————————————
# 参数校验最强，需手动实现 invoke

class Add(BaseModel):
    """将两个数字相加"""
    a: int = Field(..., description="第一个数字")
    b: int = Field(..., description="第二个数字")

    def invoke(self, args: dict):
        validated = self.__class__(**args)
        return validated.a + validated.b

class Multiply(BaseModel):
    """将两个数字相乘"""
    a: int = Field(..., description="第一个数字")
    b: int = Field(..., description="第二个数字")

    def invoke(self, args: dict):
        validated = self.__class__(**args)
        return validated.a * validated.b

tools_pydantic = [Add, Multiply]


# ============================================================
# 2. LLM 与工具交互流程（使用 @tool 装饰器定义的工具）
# ============================================================

# 2.1 绑定工具到模型
llm_with_tools = llm.bind_tools(tools_annotation, tool_choice="auto")

# 2.2 第一次 invoke — LLM 返回 tool_calls 或直接文本
query = "2 + 1 等于多少？"
messages = [HumanMessage(query)]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

print(f"\n=== 第一次 invoke ===")
print(f"content: {ai_msg.content}")
print(f"tool_calls: {ai_msg.tool_calls}")

# 2.3 如果 LLM 返回了 tool_calls，执行工具并追加 ToolMessage
if ai_msg.tool_calls:
    func_map = {"add": add, "multiply": multiply}
    for tc in ai_msg.tool_calls:
        func = func_map[tc["name"].lower()]
        result = func.invoke(tc["args"])
        messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
        print(f"\n执行工具: {tc['name']}({tc['args']}) = {result}")

    print(f"\nmessages 数量: {len(messages)}")
    # [HumanMessage, AIMessage(tool_calls), ToolMessage(结果)]

    # 2.4 第二次 invoke — LLM 基于工具结果生成最终回复
    final = llm_with_tools.invoke(messages)
    print(f"\n=== 最终回复 ===")
    print(final.content)
else:
    print("LLM 未调用工具，直接回复")

