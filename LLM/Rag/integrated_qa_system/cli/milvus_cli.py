"""
Author: haoxinlei biohow@163.com
Date: 2026-04-14 21:37:20
LastEditors: haoxinlei biohow@163.com
LastEditTime: 2026-04-23 16:13:34
FilePath: /python/LLM_AI/LLM/Rag/在线检索/conn/milvus_cli.py
Description: Milvus 客户端操作示例
"""

# ============================================================
# 第1部分：导包
# ============================================================
import logging  # 日志记录
import os  # 系统环境变量读取
from dotenv import load_dotenv  # 从 .env 文件加载环境变量
from pymilvus import MilvusClient, DataType  # Milvus 客户端和数据类型定义

# ============================================================
# 第2部分：常量及配置
# ============================================================

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# 获取日志记录器
logger = logging.getLogger(__name__)

# 加载环境变量配置（从 .env 文件读取）
load_dotenv()

# ---------- Milvus 连接配置 ----------
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")  # Milvus 服务地址
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")  # Milvus 服务端口

logger.info(f"Milvus 连接地址: {SERVER_HOST}:{MILVUS_PORT}")

# ---------- 数据库和集合配置 ----------
DB_NAME = "EduRag"  # 数据库名称（命名空间，隔离不同业务）
COLLECTION_NAME = "EduRag"  # 集合名称（相当于表名）

# ---------- 字段配置 ----------
VECTOR_DIM = 5  # 向量维度（需与 Embedding 模型输出维度一致）

# ---------- 索引配置 ----------
VECTOR_INDEX_NAME = "vector_index"  # 向量索引名称
SCALAR_INDEX_NAME = "default_index"  # 标量索引名称
METRIC_TYPE = "COSINE"  # 相似度度量：COSINE(余弦)/L2(欧氏距离)/IP(内积)


# ============================================================
# 第3部分：方法定义
# ============================================================


# 3.1 数据库操作方法
def operate_db():
    # 如果uri为数据库名称路径，代表本地操作数据库
    # client = MilvusClient(uri="milvus_demo.db")
    # 如果uri为链接地址，代表Milvus属于单机服务，需要开启Milvus后台服务操作
    uri = f"http://{SERVER_HOST}:{MILVUS_PORT}"
    client = MilvusClient(uri=uri)

    logger.info(f"Milvus version: {client.get_server_version()}")

    # # # 创建名称为EduRag的数据库
    # #
    databases = client.list_databases()
    if DB_NAME not in databases:
        client.create_database(db_name=DB_NAME)
    else:
        client.using_database(db_name=DB_NAME)
    return client


# 3.2 创建 Schema
def create_schema(client):
    """创建 Collection Schema"""
    # enable_dynamic_field=True 允许插入未定义字段，存储在 $meta JSON 中
    # auto_id=False 表示主键需手动指定，不自动增长
    schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=5)
    schema.add_field(
        field_name="scalar1",
        datatype=DataType.VARCHAR,
        max_length=256,
        description="标量字段",
    )
    return schema


# 3.3 配置索引
def create_indexes(client, collection_name):
    """创建向量索引和标量索引"""
    # 向量索引：常见类型有 IVF_FLAT、HNSW
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        metric_type="COSINE",
        index_type="",  # 自动选择索引类型
        index_name="vector_index",
    )
    client.create_index(collection_name=collection_name, index_params=index_params)

    # 标量索引：用于加速过滤查询，常见类型为 INVERTED
    index_params1 = client.prepare_index_params()
    index_params1.add_index(
        field_name="scalar1",
        index_type="",
        index_name="default_index",
    )
    client.create_index(collection_name=collection_name, index_params=index_params1)

    # 查看索引信息
    res = client.list_indexes(collection_name=collection_name)
    logger.info(f"索引信息: {res}")

    res = client.describe_index(
        collection_name=collection_name, index_name="vector_index"
    )
    logger.info(f"向量索引详情: {res}")


# 3.4 创建数据
def create_data(client, collection_name):
    """创建示例数据"""
    data = [
        {"id": 1, "vector": [0.1, 0.2, 0.3, 0.4, 0.5], "scalar1": "A"},
        {"id": 2, "vector": [0.2, 0.3, 0.4, 0.5, 0.6], "scalar1": "B"},
        {"id": 3, "vector": [0.3, 0.4, 0.5, 0.6, 0.7], "scalar1": "C"},
    ]
    client.insert(collection_name=collection_name, data=data)
    client.flush(collection_name=collection_name)  # 刷新数据到磁盘
    logger.info(f"数据插入成功，当前集合统计: {client.get_collection_stats(collection_name=collection_name)}")


# 3.5 删除数据
def drop_data(client, collection_name):
    """删除数据"""
    # 按条件删除数据
    client.delete(collection_name=collection_name, ids=[1, 2, 3])
    client.flush(collection_name=collection_name)
    logger.info(f"数据删除成功，当前集合统计: {client.get_collection_stats(collection_name=collection_name)}")


# 3.6 删除索引
def drop_indexes(client, collection_name):
    """删除索引"""
    client.release_collection(collection_name=collection_name)  # 先释放集合
    client.drop_index(collection_name=collection_name, index_name=VECTOR_INDEX_NAME)
    client.drop_index(collection_name=collection_name, index_name=SCALAR_INDEX_NAME)
    logger.info(f"索引删除成功，当前索引列表: {client.list_indexes(collection_name=collection_name)}")


# 3.7 删除集合
def drop_collection(client, collection_name):
    """删除集合"""
    client.drop_collection(collection_name=collection_name)
    logger.info(f"集合删除成功，当前集合列表: {client.list_collections()}")


# 3.8 删除数据库
def drop_database(client, db_name):
    """删除数据库"""
    client.drop_database(db_name=db_name)
    logger.info(f"数据库删除成功，当前数据库列表: {client.list_databases()}")


# 3.9 Collection 集合操作方法
def operate_table(client):
    """创建 Collection 并配置索引"""
    # 1. 创建 Schema
    schema = create_schema(client)

    # 2. 创建 Collection
    client.create_collection(collection_name=COLLECTION_NAME, schema=schema)

    # 3. 配置索引
    create_indexes(client, COLLECTION_NAME)

    # 4. 加载 Collection 到内存
    client.load_collection(collection_name=COLLECTION_NAME)
    logger.info(f"加载状态: {client.get_load_state(collection_name=COLLECTION_NAME)}")

# 3.10 查询数据
def query_data(client, collection_name):
    """向量相似度查询（混合检索：向量 + 标量过滤）

    根据查询向量在集合中搜索最相似的向量，同时支持标量字段过滤

    Args:
        client: Milvus 客户端连接
        collection_name: 集合名称

    流程：
        1. 准备查询向量（实际使用时从文本embedding得到）
        2. 配置搜索参数（返回数量、过滤条件、输出字段）
        3. 执行混合检索，返回最相似的top_k条结果
    """
    # ---------- 1. 准备查询向量 ----------
    # 示例向量（实际场景中由文本通过embedding模型生成）
    query_vector = [0.15, 0.25, 0.35, 0.45, 0.55]

    # ---------- 2. 执行混合检索 ----------
    # 混合检索 = 向量检索 + 标量过滤
    results = client.search(
        collection_name=collection_name,  # 目标集合
        data=[query_vector],              # 查询向量列表（支持批量查询）
        anns_field="vector",              # 向量字段名
        limit=2,                          # 返回最相似的前2条结果
        filter="scalar1 == 'A'",          # 标量过滤条件（混合检索关键）
        output_fields=["scalar1"],        # 返回的字段（除距离和ID外）
    )
    logger.info(f"查询结果: {results}")


# ============================================================
# 第4部分：主入口
# ============================================================

if __name__ == "__main__":
    client = operate_db()

    # Create collection and index
    operate_table(client)

    # Add data
    create_data(client, COLLECTION_NAME)

    # Query data
    query_data(client, COLLECTION_NAME)

    # Drop data
    drop_data(client, COLLECTION_NAME)

    # Drop index
    drop_indexes(client, COLLECTION_NAME)

    # Drop collection
    drop_collection(client, COLLECTION_NAME)

    # 查看当前状态（在删除数据库之前）
    logger.info(f"当前数据库列表: {client.list_databases()}")
    logger.info(f"当前集合列表: {client.list_collections()}")

    # Drop database
    drop_database(client, DB_NAME)
    