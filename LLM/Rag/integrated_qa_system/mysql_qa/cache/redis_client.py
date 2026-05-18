'''
Author: haoxinlei biohow@163.com
Date: 2026-04-14 21:33:42
LastEditors: haoxinlei biohow@163.com
LastEditTime: 2026-04-14 21:33:45
FilePath: /python/LLM_AI/LLM/Rag/在线检索/redsi_con.py
Description: Redis 连接示例
'''
import os
from dotenv import load_dotenv
import redis

# 第1步：加载 .env 文件
load_dotenv()

# 第2步：获取环境变量（统一使用服务器 HOST）
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

print(f"Redis 连接地址: {SERVER_HOST}:{REDIS_PORT}")

# 连接到 Redis
client = redis.Redis(host=SERVER_HOST, port=int(REDIS_PORT), decode_responses=True)

# 测试读写
client.set("test_key", "Hello, Redis!")
value = client.get("test_key")
print(f"Redis value: {value}")
