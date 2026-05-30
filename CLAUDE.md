# how 的博客

Java 后端 & 大模型开发学习笔记。mkdocs 构建，部署在 https://cowfat97.github.io/notes/。

## 模块导航

| 模块 | 位置 | 说明 |
|------|------|------|
| Java | [Java/](./Java/) | 基础 / 多线程 / JVM / 框架 / 集合 |
| 中间件 | [中间件/](./中间件/) | Redis / Nginx / Kafka / ES / Docker / Nacos / PostgreSQL |
| 数据库 | [数据库/](./数据库/) | MySQL 索引 / 事务 / 特性 |
| LLM | [LLM/](./LLM/) | 通识 / Agent / Coze / Dify / RAG / 深度学习 / 微调 / LangGraph |
| 408 | [408/](./408/) | 数据结构 / 计组 / 操作系统 / 计网 |
| LeetCode | [leetcode/](./leetcode/) | Python 刷题 |
| 读书 | [book/](./book/) | 书架 / 阅读统计（微信读书集成）|
| Personal Log | [Personal Log/](./Personal%20Log/) | 日记与日常记录 |
| 时间线 | [时间线/](./时间线/) | 每日日记，模板位于 时间线/.templates/ |
| 文章 | [文章/](./文章/) | 个人专栏文章 |
| 公众号 | [公众号.md](./公众号.md) | 公众号关注页面，含二维码 |
| 软考 | [软考/](./软考/) | 软件设计师备考 |

## 环境配置

- LLM 模块 Python 环境在 `../envs/conda/`：
  - `LLM_Rag` — RAG / 文档处理 / 向量化
  - `LLM_Agent` — Agent / LangChain / LangGraph / Coze / Dify
  - `LLM_DeepLearning` — 深度学习 / 微调
- `.env` 在项目根目录，`.gitignore` 已忽略
- 图片资源放在 [Pic/](./Pic/)

## 日记规范

- 文件：`时间线/YYYY-MM-DD/☕-YYYY-MM-DD.md`
- 模板：`时间线/.templates/default.md`
- 天气用勾选格式：`- 天气：[ ] ☀️晴 [x] ⛅多云 ...`
- 身体模块含睡眠追踪：`- 睡眠：7h25m`

## 笔记规范

- 中文书写，Markdown 格式
- 概念 + 实战示例，结构清晰便于复习
