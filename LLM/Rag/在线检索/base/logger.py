'''
Author: haoxinlei biohow@163.com
Date: 2026-04-29 14:26:40
LastEditors: haoxinlei biohow@163.com
LastEditTime: 2026-04-29 14:26:49
FilePath: /python/LLM_AI/LLM/Rag/在线检索/log/logger.py
Description: 日志配置模块 - 提供统一的日志记录功能
'''

# ========== 导包 ==========
import os
import logging

from config import Config


# ========== 日志配置 ==========
def setup_logging(log_file=Config().LOG_FILE):
    """
    配置日志器

    Args:
        log_file: 日志文件路径，默认从 Config 读取

    Returns:
        logging.Logger: 配置好的日志器
    """
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 获取日志器
    logger = logging.getLogger("EduRAG")
    logger.setLevel(logging.INFO)

    # 避免重复添加处理器
    if not logger.handlers:
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# ========== 初始化 ==========
logger = setup_logging()