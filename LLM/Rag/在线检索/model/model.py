"""
Author: haoxinlei biohow@163.com
Date: 2026-04-14 15:47:37
LastEditors: haoxinlei biohow@163.com
LastEditTime: 2026-04-14 16:42:21
FilePath: /python/LLM_AI/LLM/Rag/离线知识库/model.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI

# 加载项目根目录的 .env 文件
# 优先使用环境变量 ENV_FILE 指定的路径，否则使用项目根目录
_env_path = os.getenv("ENV_FILE")
load_dotenv(_env_path)

# 初始化 llm 对象
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID", "qwen-max"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)

# 初始化 embeddings 对象
embeddings = DashScopeEmbeddings(
    model="text-embedding-v3", dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
)

if __name__ == "__main__":
    res = llm.invoke("你是什么模型？")
    print(res)
