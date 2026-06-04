# RAG 系统

个人学习笔记的在线检索系统（integrated_qa_system 综合问答系统），分两部分：
- **离线**：笔记 .md → 切分 → embedding → Milvus
- **在线**：分两路 — MySQL（热点 FAQ）+ Milvus（语义检索）

## 目录结构

```
LLM/Rag/
├── CLAUDE.md
├── integrated_qa_system/
│   ├── config.ini                 # 统一配置文件
│   ├── requirements.txt           # Python 依赖
│   │
│   ├── base/                      # 公共基础设施
│   │   ├── config.py              # 配置管理，加载 config.ini
│   │   └── logger.py              # 日志设置
│   │
│   ├── model/                     # LLM + Embedding 初始化
│   │   ├── __init__.py
│   │   └── model.py               # DashScope llm + text-embedding-v3
│   │
│   ├── mysql_qa/                  # 在线- MySQL 热点 FAQ + BM25L
│   │   ├── data/JP学科知识问答.csv
│   │   ├── db/mysql_client.py     # MySQL 连接 + FAQ CRUD
│   │   ├── cache/redis_client.py  # Redis 缓存
│   │   ├── retrieval/bm25_search.py # BM25L 检索
│   │   ├── utils/                 # （待建- 文本预处理）
│   │   └── main.py                # （待建- MySQL 系统独立入口）
│   │
│   ├── rag_qa/                    # 在线- Milvus 向量检索 + RAG 生成
│   │   ├── core/
│   │   │   ├── prompts.py         # RAG / HyDE / 子查询 / 回溯 prompt
│   │   │   ├── query_classifier.py # BERT 二分类
│   │   │   ├── document_processor.py # 文档加载 + 父子块切分
│   │   │   └── rag_system.py      # RAG 引擎核心
│   │   └── main.py                # （待建- RAG 系统独立入口）
│   │
│   └── cli/                       # 连接测试脚本
│       ├── milvus_cli.py
│       └── ollama_cli.py
│
└── requirements.txt
```

## 核心模块

### mysql_qa（MySQL 热点 FAQ）

| 文件 | 职责 |
|------|------|
| `db/mysql_client.py` | MySQL 连接 + FAQ CRUD |
| `retrieval/bm25_search.py` | BM25L + jieba 中文关键词检索 |
| `cache/redis_client.py` | Redis 缓存热点查询 |

### rag_qa（Milvus 向量检索）

| 文件 | 职责 |
|------|------|
| `core/prompts.py` | RAG / HyDE / 子查询 / 回溯 四种 prompt |
| `core/query_classifier.py` | BERT 二分类：通用知识 / 专业咨询 |
| `core/document_processor.py` | 文档加载 + 父子块切分 |
| `core/rag_system.py` | RAG 引擎：分类 → 策略选择 → 检索 → LLM 生成 |

## 环境

- conda 环境：`/Users/haoxinlei/Desktop/开发/学习/envs/conda/LLM_Rag`
- 配置文件：`integrated_qa_system/config.ini`（已 gitignore）
- .env：项目根目录

## 服务器

| 服务 | 地址 | 端口 |
|------|------|------|
| Milvus | 192.168.3.36 | 19530 |
| MySQL | 192.168.3.36 | 3306 |
| Redis | 192.168.3.36 | 6379 |

## 检索策略

| 策略 | 方法 |
|------|------|
| 直接检索 | query 直搜 Milvus |
| 回溯问题 | LLM 去噪简化 → 检索 |
| 子查询 | LLM 拆复合查询 → 逐条检索 → 去重 |
| HyDE | LLM 生成假设答案 → 检索 |
