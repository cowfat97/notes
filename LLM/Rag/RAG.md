<!--
 * @Author: haoxinlei howxl97@163.com
 * @Date: 2026-05-05 15:05:25
 * @LastEditors: haoxinlei howxl97@163.com
 * @LastEditTime: 2026-05-05 20:26:05
 * @FilePath: /notes/LLM/Rag/RAG.md
 * @Description: RAG 检索增强生成 — 从概念到实现的完整笔记
-->
# 为什么会有RAG？

## LLM 的三大局限


## RAG 解决的核心问题

## RAG 的典型应用场景

# 什么是RAG？

## RAG 的定义

## RAG 的基本架构

## RAG 的工作流程

## RAG vs 微调

# 怎么实现RAG？

## 离线阶段：文档索引

### 文档加载

### 文档切分（父子块策略）

### 向量化（Embedding）

### 向量存储（Milvus）

## 在线阶段：检索生成

### 意图识别 / 查询分类

### Query 改写

### 检索策略

### 混合检索

### 重排序

### 答案生成

## 技术选型对比

# RAG发展

## Naive RAG → Advanced RAG → Agentic RAG

## RAG + MCP

## RAG 的局限性