'''
Author: haoxinlei howxl97@163.com
Date: 2026-05-02 21:19:15
LastEditors: haoxinlei howxl97@163.com
LastEditTime: 2026-05-02 22:01:16
FilePath: /notes/LLM/Agent/Langgraph/002.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

@tool(description="根据公司名称和职位，查询对应的负责人姓名。")
def getKeyNames(company,title):
    keyNames = {
"大连大通电器有限公司": {
"董事长": "王建国",
"总经理": "李海峰",
"副总经理": "赵晋瑞",
"财务总监": "张明华",
"技术总监": "刘志强",
"市场总监": "陈晓红",
"生产总监": "孙宏伟",
"人事总监": "周雪梅"
},
"深圳华创科技有限公司": {
"CEO": "马凌云",
"CTO": "吴天宇",
"CFO": "郑晓雯",
"COO": "林志远",
"产品总监": "黄思颖",
"研发总监": "徐浩然",
"市场总监": "欧阳雪",
"HRD": "冯佳怡"
},
"北京四方物流集团": {
"集团总裁": "赵振国",
"副总裁": "钱卫东",
"财务总经理": "孙丽娜",
"运营总监": "李建军",
"仓储总监": "周伟明",
"运输总监": "吴晓峰",
"信息总监": "郑晓龙",
"安全总监": "王海燕"
},
"杭州云智数据有限公司": {
"创始人": "马云飞",
"CEO": "张一鸣",
"技术副总裁": "李开复",
"数据总监": "王志东",
"算法总监": "刘强",
"产品总监": "陈一丹",
"市场总监": "徐小平",
"行政总监": "雷军"
},
"广州美嘉食品集团": {
"董事长": "李嘉诚",
"总裁": "王永庆",
"生产副总裁": "张瑞敏",
"质量总监": "董明珠",
"研发总监": "任正非",
"供应链总监": "马化腾",
"营销总监": "丁磊",
"财务总监": "柳传志"
}
}
    tempName = "unknown"
    if company in keyNames:
        tempNameList = keyNames[company]
        if title in tempNameList:
            tempName = tempNameList[title]
    return tempName

tools = [getKeyNames]

# 从 .env 取环境变量构建模型
llm = ChatOpenAI(
    base_url=os.getenv("DeepSeek_BASE_URL"),
    api_key=os.getenv("DeepSeek_API_KEY"),
    model=os.getenv("DeepSeek_MODEL_ID"),
    temperature=0.2
)
llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

# 调用
query = "深圳华创科技有限公司的CTO是谁？"
messages = [HumanMessage(query)]

ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
    for tool_call in ai_msg.tool_calls:
        func = {"getKeyNames": getKeyNames}[tool_call["name"]]
        tool_result = func.invoke(tool_call["args"])
        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))

    final_response = llm_with_tools.invoke(messages)
    print(final_response.content)
else:
    print(ai_msg.content)



