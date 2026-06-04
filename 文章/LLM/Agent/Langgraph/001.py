'''
Author: haoxinlei biohow@163.com
Date: 2026-04-28 20:41:00
LastEditors: haoxinlei biohow@163.com
LastEditTime: 2026-04-28 21:17:54
FilePath: /python/LLM_AI/LLM/Agent/Langgraph/001.py
Description: LangGraph create_react_agent 基础示例
'''

# ========== 导包 ==========
import os
import logging

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# ========== 环境变量 ==========
load_dotenv()
api_base = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
api_key = os.getenv("LLM_API_KEY")
model_name = os.getenv("MODEL_NAME", "qwen-turbo")

# ========== 日志配置 ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== 创建 Agent ==========
logger.info("Creating the agent...")
logger.info(f"Using API Key: {api_key}")

agent = create_react_agent(
    model=ChatOpenAI(
        model=model_name,
        openai_api_base=api_base,
        openai_api_key=api_key,
    ),
    tools=[],
    prompt="你是一个有用的助手",
)

# ========== 运行 Agent ==========
result = agent.invoke({"messages": [{"role": "user", "content": "你是谁？"}]})
logger.info("Agent invocation result: %s", result["messages"][-1].content)
logger.info("Agent invocation completed.")