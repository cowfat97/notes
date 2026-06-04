"""
使用 LangGraph 实现人工干预（Human-in-the-Loop）
在 LLM 决定调用工具后，暂停执行，等待人工确认后再执行工具调用。
"""
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

load_dotenv()

# ===== 工具定义 =====
@tool(description="根据公司名称和职位，查询对应的负责人姓名。")
def getKeyNames(company, title):
    keyNames = {
        "大连大通电器有限公司": {
            "董事长": "王建国", "总经理": "李海峰", "副总经理": "赵晋瑞",
            "财务总监": "张明华", "技术总监": "刘志强",
            "市场总监": "陈晓红", "生产总监": "孙宏伟", "人事总监": "周雪梅"
        },
        "深圳华创科技有限公司": {
            "CEO": "马凌云", "CTO": "吴天宇", "CFO": "郑晓雯",
            "COO": "林志远", "产品总监": "黄思颖",
            "研发总监": "徐浩然", "市场总监": "欧阳雪", "HRD": "冯佳怡"
        },
        "北京四方物流集团": {
            "集团总裁": "赵振国", "副总裁": "钱卫东", "财务总经理": "孙丽娜",
            "运营总监": "李建军", "仓储总监": "周伟明",
            "运输总监": "吴晓峰", "信息总监": "郑晓龙", "安全总监": "王海燕"
        },
        "杭州云智数据有限公司": {
            "创始人": "马云飞", "CEO": "张一鸣", "技术副总裁": "李开复",
            "数据总监": "王志东", "算法总监": "刘强",
            "产品总监": "陈一丹", "市场总监": "徐小平", "行政总监": "雷军"
        },
        "广州美嘉食品集团": {
            "董事长": "李嘉诚", "总裁": "王永庆", "生产副总裁": "张瑞敏",
            "质量总监": "董明珠", "研发总监": "任正非",
            "供应链总监": "马化腾", "营销总监": "丁磊", "财务总监": "柳传志"
        }
    }
    tempName = "unknown"
    if company in keyNames:
        tempNameList = keyNames[company]
        if title in tempNameList:
            tempName = tempNameList[title]
    return tempName

tools = [getKeyNames]

# ===== 模型 =====
llm = ChatOpenAI(
    base_url=os.getenv("DeepSeek_BASE_URL"),
    api_key=os.getenv("DeepSeek_API_KEY"),
    model=os.getenv("DeepSeek_MODEL_ID"),
    temperature=0.2
)
llm_with_tools = llm.bind_tools(tools, tool_choice="auto")


# ===== LangGraph State =====
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ===== 节点定义 =====
def llm_node(state: State) -> State:
    """LLM 接收用户消息，决定是否调用工具"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def human_review_node(state: State) -> State:
    """人工干预节点：LLM 决定调用工具后，暂停等人工确认"""
    last_msg = state["messages"][-1]

    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
        return state

    # 展示工具调用详情，暂停等待人工确认
    user_decision = interrupt({
        "type": "human_review",
        "tool_name": last_msg.tool_calls[0]["name"],
        "tool_args": last_msg.tool_calls[0]["args"],
        "message": "是否执行此工具调用？"
    })

    if user_decision == "y":
        return state  # 通过，继续执行 tool_node
    else:
        # 拒绝，用 AIMessage 替代 tool_calls，跳过工具执行
        return {"messages": [
            AIMessage(content="人工拒绝了工具调用。")
        ]}


def tool_node(state: State) -> State:
    """执行工具调用"""
    last_msg = state["messages"][-1]
    func_map = {"getKeyNames": getKeyNames}

    for tool_call in last_msg.tool_calls:
        func = func_map[tool_call["name"]]
        tool_result = func.invoke(tool_call["args"])
        return {"messages": [ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"]
        )]}


def llm_final_node(state: State) -> State:
    """LLM 根据工具结果生成最终回复"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# ===== 构建 Graph =====
graph = StateGraph(State)

graph.add_node("llm", llm_node)
graph.add_node("human_review", human_review_node)
graph.add_node("tool", tool_node)
graph.add_node("llm_final", llm_final_node)

graph.add_edge(START, "llm")
graph.add_edge("llm", "human_review")
graph.add_conditional_edges(
    "human_review",
    lambda state: "tool" if (hasattr(state["messages"][-1], "tool_calls") and state["messages"][-1].tool_calls) else "end",
    {"tool": "tool", "end": END}
)
graph.add_edge("tool", "llm_final")
graph.add_edge("llm_final", END)

# ===== 编译 =====
checkpointer = MemorySaver()
app = graph.compile()

# ===== 运行 =====
if __name__ == "__main__":
    query = "深圳华创科技有限公司的CTO是谁？"
    config = {"configurable": {"thread_id": "session-1"}}

    # 第一次运行：到 human_review 节点会暂停
    print("=" * 50)
    print("第一次运行 - 等待人工干预")
    for event in app.stream(
        {"messages": [HumanMessage(content=query)]},
        config=config,
        stream_mode="values"
    ):
        last_msg = event["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            tc = last_msg.tool_calls[0]
            print(f"\n🔔 模型要调用工具: {tc['name']}")
            print(f"   参数: {tc['args']}")

    # 第二次运行：人工确认 (resume=y)，继续执行
    print("\n" + "=" * 50)
    print("第二次运行 - 人工确认通过 (resume='y')")
    for event in app.stream(
        Command(resume="y"),
        config=config,
        stream_mode="values"
    ):
        last_msg = event["messages"][-1]
        if hasattr(last_msg, "content") and last_msg.content:
            print(f"\n📩 {type(last_msg).__name__}: {last_msg.content}")
