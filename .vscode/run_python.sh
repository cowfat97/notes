#!/bin/bash
# 根据文件路径自动选择 conda 环境

FILE=$(realpath "$1" 2>/dev/null || echo "$1")
SCRIPT_DIR=$(dirname "$FILE")
CASE_DIR=$(echo "$SCRIPT_DIR" | sed 's|.*/notes/LLM/||')

case "$CASE_DIR" in
    Agent/*)
        CONDA_PYTHON="/Users/haoxinlei/Desktop/开发/学习/envs/conda/LLM_Agent/bin/python"
        ;;
    Rag/*)
        CONDA_PYTHON="/Users/haoxinlei/Desktop/开发/学习/envs/conda/LLM_Rag/bin/python"
        ;;
    深度学习/*)
        CONDA_PYTHON="/Users/haoxinlei/Desktop/开发/学习/envs/conda/LLM_DeepLearning/bin/python"
        ;;
    *)
        CONDA_PYTHON="/Users/haoxinlei/Desktop/开发/学习/envs/conda/LLM_Agent/bin/python"
        ;;
esac

exec "$CONDA_PYTHON" -u "$FILE"
