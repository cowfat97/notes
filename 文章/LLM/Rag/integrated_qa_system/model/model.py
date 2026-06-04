"""
模型工厂：LLM / Embedding 统一入口
所有模块需要 LLM 或 Embedding 时，统一从这里获取，不自己 new 客户端
"""
import os
import sys

# LangChain 封装好的 API 客户端
from langchain_openai import ChatOpenAI                     # 调 LLM（兼容 OpenAI 协议）
from langchain_community.embeddings import DashScopeEmbeddings  # 调阿里云 Embedding

# 为了让 from base.config import Config 能找到，把项目根目录加入搜索路径
_current_dir = os.path.dirname(os.path.abspath(__file__))   # model/ 目录
sys.path.insert(0, os.path.join(_current_dir, ".."))         # 上级 = integrated_qa_system/

from base.config import Config
# 统一配置实例，读 config.ini
conf = Config()

# ============================================================
# 1. LLM — 大语言模型
# ============================================================
def get_llm():
    """获取 LLM 客户端：阿里 DashScope qwen-turbo，兼容 OpenAI API 调用方式

    用法：
        llm = get_llm()
        answer = llm.invoke("你好")
    """
    return ChatOpenAI(
        model=conf.LLM_MODEL,           # qwen-turbo
        api_key=conf.DASHSCOPE_API_KEY, # sk-f876dcc...
        base_url=conf.DASHSCOPE_BASE_URL,  # https://dashscope.aliyuncs.com/compatible-mode/v1
    )


# ============================================================
# 2. Embedding — 文本向量化
# ============================================================
def get_embeddings():
    """获取 Embedding 客户端：阿里 DashScope text-embedding-v3

    输出维度：1024
    用法：
        emb = get_embeddings()
        vec = emb.embed_query("JVM内存模型")           # 单条，返回 List[float]
        vecs = emb.embed_documents(["文本1", "文本2"])  # 批量，返回 List[List[float]]
    """
    return DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=conf.DASHSCOPE_API_KEY,
    )


# 命令行测试：python model/model.py → 调用 LLM 看是否通
if __name__ == "__main__":
    llm = get_llm()
    res = llm.invoke("你是什么模型？")
    print(res)
