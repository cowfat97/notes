'''
Author: haoxinlei biohow@163.com
Date: 2026-04-29 09:27:35
LastEditors: haoxinlei biohow@163.com
LastEditTime: 2026-04-29 10:23:36
FilePath: /python/LLM_AI/LLM/Rag/在线检索/mysql/fqa.py
Description: mysql BM25 FQA问答系统 
'''

# ========== 导包 ==========
# OS 和日志
import os
import logging

# mysql

# redis

# BM25
from jieba import cut


# ========== 环境变量 ==========


# ========== 日志配置 ==========


# ========== 创建 BM25 实体 ==========
class BM25Search:
    def __init__(self, mysql_cli,redis_cli):
        # 初始化 MySQL 连接
        self.mysql_cli = mysql_cli
        # 初始化 Redis 连接
        self.redis_cli = redis_cli
        # 初始化 BM25 模型
        self.bm25_model = None  # 这里需要根据实际情况初始化 BM25 模型

    def search(self, query):

        # 1.加载高频问答数据

        # 1.1 Redis 获取缓存结果
        
        # 1.2 Reds没有 MySQL 获取数据

        # 2. BM25 相似度
        # 2.1 query 分词
        query_tokens = self.tokenize(query)
        # 2.2 BM25 分数
        bm25_score = self.getScore(query_tokens, self.bm25_model)
        # 2.3 softmax 分数
        softmax_score = self.softMax(bm25_score)
        # 2.4. top-k 结果
        
        # 3. 高频热点问题

        # 返回结果
        pass

    # query 分词
    def tokenize(self, query):
        # 实现分词逻辑
        pass    

    # 计算 BM25 分数
    def getScore(self, query, document):
        # 计算 BM25 分数
        pass    

    # 计算 softmax 分数
    def softMax(self, scores):
        # 计算 softmax 分数
        pass

# ========== 运行 BM25 实体 ==========

if __name__ == "__main__":
    bm25 = BM25Search()
    

    ...


