# -*- coding:utf-8 -*-
"""
MySQL 客户端
用于连接MySQL数据库，存储和管理问答数据

功能：
- 连接MySQL数据库
- 创建问答表（jpkb）
- 从CSV导入问答数据
- 获取所有问题（用于BM25初始化）
- 根据问题获取答案
"""

# ============================================================
# 第1部分：导包
# ============================================================
import os  # 系统环境变量读取
import pymysql  # MySQL数据库驱动
import logging  # 日志记录
import pandas as pd  # CSV数据处理
from dotenv import load_dotenv  # 从 .env 文件加载环境变量

import jieba  # 中文分词工具
from rank_bm25 import BM25L  # BM25 算法实现库（提供 BM25, BM25L, BM25Okapi 等变体）

# ============================================================
# 第2部分：参数和配置
# ============================================================
# 加载环境变量配置（从 .env 文件读取）
load_dotenv()

# ---------- MySQL 连接配置 ----------
MYSQL_HOST = os.getenv("SERVER_HOST", "localhost")  # MySQL 服务地址（复用 SERVER_HOST）
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))  # MySQL 端口
MYSQL_USER = os.getenv("MYSQL_USER", "hxl")  # MySQL 用户名
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "hxl")  # MySQL 密码
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "EduRag")  # MySQL 数据库名

# ---------- 表名配置 ----------
TABLE_NAME = "jpkb"  # 知识问答表名称

# ---------- 日志配置 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
LOGGER = logging.getLogger(__name__)  # 获取日志记录器


# ============================================================
# 第3部分：MySQLClient 类
# ============================================================
class MySQLClient:
    """
    MySQL数据库客户端

    用于管理问答数据的存储和检索

    表结构（jpkb）：
    - id: 主键，自增
    - subject_name: 学科名称
    - question: 问题
    - answer: 答案
    """

    def __init__(self):
        """初始化MySQL连接

        创建数据库连接和游标对象

        Raises:
            pymysql.MySQLError: 连接失败时抛出异常
        """
        self.logger = LOGGER
        try:
            # 连接 MySQL 数据库
            self.connection = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
            )
            # 创建游标（用于执行SQL语句）
            self.cursor = self.connection.cursor()
            self.logger.info(f"MySQL 连接成功: {MYSQL_HOST}:{MYSQL_PORT}")
        except pymysql.MySQLError as e:
            self.logger.error(f"MySQL 连接失败: {e}")
            raise

    def create_table(self):
        """创建知识问答表

        表名: jpkb
        字段:
            - id: INT, 主键，自增
            - subject_name: VARCHAR(20), 学科名称
            - question: VARCHAR(1000), 问题
            - answer: VARCHAR(1000), 答案

        Raises:
            pymysql.MySQLError: 创建失败时抛出异常
        """
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            subject_name VARCHAR(20),
            question VARCHAR(1000),
            answer VARCHAR(1000))
        """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            self.logger.info("表创建成功")
        except pymysql.MySQLError as e:
            self.logger.error(f"表创建失败: {e}")
            raise

    def insert_data(self, csv_path):
        """从CSV文件插入数据

        Args:
            csv_path: CSV文件路径

        CSV格式要求：
            - 学科名称: 学科分类
            - 问题: 问题内容
            - 答案: 答案内容

        Raises:
            Exception: 插入失败时回滚事务并抛出异常
        """
        try:
            # 读取CSV文件
            data = pd.read_csv(csv_path)
            print(data.head())

            # 遍历插入数据
            for _, row in data.iterrows():
                insert_query = f"INSERT INTO {TABLE_NAME} (subject_name, question, answer) VALUES (%s, %s, %s)"
                self.cursor.execute(
                    insert_query, (row["学科名称"], row["问题"], row["答案"])
                )

            # 提交事务
            self.connection.commit()
            self.logger.info("MySQL数据插入成功")
        except Exception as e:
            self.logger.error(f"MySQL数据插入失败: {e}")
            # 回滚事务（撤销所有操作）
            self.connection.rollback()
            raise

    def fetch_questions(self):
        """获取所有问题

        用于BM25模型初始化，获取表中所有问题

        Returns:
            list: 问题列表，格式为 [(问题1,), (问题2,), ...]
        """
        try:
            self.cursor.execute(f"SELECT question FROM {TABLE_NAME}")
            results = self.cursor.fetchall()
            self.logger.info("成功获取问题")
            return results
        except pymysql.MySQLError as e:
            self.logger.error(f"查询失败: {e}")
            return []

    def fetch_answer(self, question):
        """获取指定问题的答案

        Args:
            question: 问题内容

        Returns:
            str: 答案内容，未找到时返回 None
        """
        try:
            # 参数化查询（防止SQL注入）
            self.cursor.execute(
                f"SELECT answer FROM {TABLE_NAME} WHERE question=%s", (question,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except pymysql.MySQLError as e:
            self.logger.error(f"答案获取失败: {e}")
            return None

    def close(self):
        """关闭数据库连接

        释放数据库资源
        """
        try:
            self.connection.close()
            self.logger.info("MySQL 连接已关闭")
        except pymysql.MySQLError as e:
            self.logger.error(f"关闭连接失败: {e}")


class BM25Search:
    """
    BM25L 搜索引擎

    BM25L 是 BM25 的变体，解决了 BM25 对长文档惩罚过重的问题。
    区别：BM25L 使用 (tf + delta) / (tf + k1 + delta) 替代 BM25 的词频公式。

    BM25 核心公式：
        score(D, Q) = Σ IDF(qi) × (tf × (k1+1)) / (tf + k1×(1-b+b×dl/avgdl))

    参数说明：
        - IDF: 逆文档频率，衡量词的稀有程度
        - tf: 词频，词在文档中出现的次数
        - k1: 词频饱和参数（默认1.5）
        - b: 文档长度归一化参数（默认0.75）
        - dl: 当前文档长度，avgdl: 平均文档长度

    BM25 vs TF-IDF：
        - 词频饱和：出现10次和100次差别不大，防止词频堆砌作弊
        - 文档长度归一化：长文档不会因为词多就得分高

    BM25L 的改进：
        - BM25 对长文档惩罚过重（b 参数让长文档分数偏低）
        - BM25L 通过 delta 参数缓解这个问题，更适合长文档检索
    """

    def __init__(self, documents: list):
        """
        初始化 BM25L 搜索引擎

        Args:
            documents: 文档列表，每个文档是字符串

        流程：
            1. 保存原始文档
            2. 对每个文档进行中文分词
            3. 初始化 BM25L 模型
        """
        self.documents = documents
        self.tokenized_docs = [jieba.lcut(doc) for doc in documents]
        self.bm25 = BM25L(self.tokenized_docs)
        logging.info(f"BM25L模型已初始化，文档数量: {len(documents)}")

    def search(self, query: str, top_k: int = 5) -> list:
        """
        搜索与查询最相关的文档

        Args:
            query: 查询字符串
            top_k: 返回前 k 个最相关文档

        Returns:
            list: [(文档内容, 分数), ...] 按分数降序排列

        流程：
            1. 对查询进行分词
            2. 计算每个文档的 BM25L 分数
            3. 返回分数最高的 top_k 个文档
        """
        tokenized_query = jieba.lcut(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = [(self.documents[i], scores[i]) for i in top_indices]
        return results

# ============================================================
# 第4部分：主入口
# ============================================================
if __name__ == "__main__":
    """
    测试入口

    使用示例：
        1. 创建表: mysql_client.create_table()
        2. 导入数据: mysql_client.insert_data(csv_path)
        3. 获取问题: mysql_client.fetch_questions()
        4. 获取答案: mysql_client.fetch_answer(question)
        5. 关闭连接: mysql_client.close()
    """
    mysql_client = MySQLClient()

    # mysql_client.create_table()
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # csv_path = os.path.join(script_dir, '..', 'data', 'JP学科知识问答.csv')
    # mysql_client.insert_data(csv_path=csv_path)
    # results = mysql_client.fetch_questions()
    # print(f'results: {results}')

    # 测试获取答案
    answer = mysql_client.fetch_answer(question="在磁盘中无法新建文本文档")
    print(f"answer: {answer}")

    # 测试BM25搜索
    all_answer = mysql_client.fetch_questions()  # 获取所有问题进行BM25初始化

    # 查询全量数据进行BM25初始化
    bm25 = BM25Search(documents=[row[0] for row in all_answer])
    results = bm25.search(query="VMware安装VMware Tools时显示灰色如何解决")
    logging.info(f"BM25搜索结果: {results}")

    #查询BM25 结果获取答案
    for question, score in results:
        answer = mysql_client.fetch_answer(question=question)
        logging.info(f"问题: {question}, 答案: {answer}, BM25分数: {score}")

    mysql_client.close()
