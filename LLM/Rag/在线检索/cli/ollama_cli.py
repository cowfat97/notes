"""
Author: haoxinlei biohow@163.com
Date: 2026-04-14 21:40:33
LastEditors: haoxinlei biohow@163.com
LastEditTime: 2026-04-14 21:41:48
FilePath: /python/LLM_AI/LLM/Rag/在线检索/conn/ollama.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""
import ollama
from dotenv import load_dotenv

load_dotenv()

# 聊天式
response = ollama.chat(
    model="qwen3.5:9b",
    messages=[
        {
            "role": "user",
            "content": "为什么天空是蓝色的？",
        }
    ],
)
print(response)
print(response["message"]["content"])
