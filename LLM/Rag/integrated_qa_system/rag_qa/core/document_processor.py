# ============================================================
# 1. 导包
# ============================================================
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from datetime import datetime
from langchain_text_splitters import MarkdownTextSplitter
try:
    from langchain_community.document_loaders import TextLoader
    from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
except ImportError:
    TextLoader = None
    UnstructuredMarkdownLoader = None
try:
    from edu_text_spliter import ChineseRecursiveTextSplitter
    from edu_document_loaders import OCRPDFLoader, OCRDOCLoader, OCRPPTLoader, OCRIMGLoader
except ImportError:
    ChineseRecursiveTextSplitter = None
    OCRPDFLoader = OCRDOCLoader = OCRPPTLoader = OCRIMGLoader = None
from base import logger, Config

# 通用文本切分的回退方案
if ChineseRecursiveTextSplitter is None:
    from langchain_text_splitters import RecursiveCharacterTextSplitter as ChineseRecursiveTextSplitter

# ============================================================
# 2. 配置
# ============================================================
conf = Config()

DOCUMENT_LOADERS = {
    ".md": UnstructuredMarkdownLoader,
    ".txt": TextLoader,
    ".pdf": OCRPDFLoader,
    ".docx": OCRDOCLoader,
    ".ppt": OCRPPTLoader,
    ".pptx": OCRPPTLoader,
    ".jpg": OCRIMGLoader,
    ".png": OCRIMGLoader,
}
# 过滤掉未安装的加载器
DOCUMENT_LOADERS = {k: v for k, v in DOCUMENT_LOADERS.items() if v is not None}

# ============================================================
# 3. 代码逻辑
# ============================================================

def load_documents(directory_path):
    """加载目录下所有支持的文档

    Args:
        directory_path: 文档目录路径，目录名格式为 {学科}_data，如 ai_data

    Returns:
        List[Document]: page_content=文档正文，metadata={source, file_path, timestamp}
    """
    documents = []
    # 从目录名提取学科标签：ai_data → ai，java_data → java
    source = os.path.basename(directory_path).replace("_data", "")

    for root, _, files in os.walk(directory_path):          # 递归遍历目录
        for file in files:
            file_path = os.path.join(root, file)             # 拼接完整路径
            ext = os.path.splitext(file_path)[1].lower()     # 取扩展名 → 匹配加载器

            if ext not in DOCUMENT_LOADERS:                  # 不支持的类型跳过
                logger.warning(f"不支持的文件类型: {file_path}")
                continue

            try:
                loader_cls = DOCUMENT_LOADERS[ext]            # 扩展名 → 加载器类
                loader = loader_cls(file_path, encoding="utf-8") if ext == ".txt" else loader_cls(file_path)
                loaded_docs = loader.load()                   # 加载文档内容
                for doc in loaded_docs:
                    doc.metadata.update({                    # 打标：学科、来源、时间
                        "source": source,
                        "file_path": file_path,
                        "timestamp": datetime.now().isoformat(),
                    })
                documents.extend(loaded_docs)                 # 追加到总列表
                logger.info(f"成功加载文件: {file_path}")
            except Exception as e:
                logger.error(f"加载文件 {file_path} 失败: {e}")

    return documents


def process_documents(directory_path,
                      parent_chunk_size=conf.PARENT_CHUNK_SIZE,
                      child_chunk_size=conf.CHILD_CHUNK_SIZE,
                      chunk_overlap=conf.CHUNK_OVERLAP):
    """文档分层切分：先切父块(大块，给LLM看) → 再切子块(小块，向量检索用)

    每个子块携带 parent_id + parent_content，检索时返回子块匹配，LLM 用父块内容生成答案

    Args:
        directory_path: 文档目录路径
        parent_chunk_size: 父块大小（默认 1200 token）
        child_chunk_size: 子块大小（默认 300 token）
        chunk_overlap: 块重叠大小（默认 50 token）

    Returns:
        List[Document]: 子块列表，metadata={id, parent_id, parent_content, source, file_path}
    """
    # 第一步：加载目录下所有文档
    documents = load_documents(directory_path)
    logger.info(f"加载的文档数量: {len(documents)}")

    # 第二步：准备切分器 — 通用文本用 ChineseRecursive，md 文件用 MarkdownTextSplitter
    # ChineseRecursiveTextSplitter：按 "\n\n" → "\n" → "。" → "，" 优先级逐级断句
    # MarkdownTextSplitter：额外识别 ##、### 标题边界，避免在标题中间断开
    parent_splitter = ChineseRecursiveTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    child_splitter = ChineseRecursiveTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)
    md_parent_splitter = MarkdownTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    md_child_splitter = MarkdownTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)

    # 第三步：逐文档切分
    child_chunks = []
    for i, doc in enumerate(documents):
        # 根据文件扩展名选择对应切分器
        is_md = os.path.splitext(doc.metadata.get("file_path", ""))[1].lower() == ".md"
        parent_splitter_use = md_parent_splitter if is_md else parent_splitter
        child_splitter_use = md_child_splitter if is_md else child_splitter

        # 3.1 父块切分：文档 → 大块（1200 token），给 LLM 看的完整上下文
        parent_docs = parent_splitter_use.split_documents([doc])
        for j, parent_doc in enumerate(parent_docs):
            # 父块 ID：doc_{文档序号}_parent_{父块序号}
            parent_id = f"doc_{i}_parent_{j}"
            parent_doc.metadata["parent_id"] = parent_id
            parent_doc.metadata["parent_content"] = parent_doc.page_content

            # 3.2 子块切分：父块 → 小块（300 token），向量检索用
            # 检索时用子块匹配 query，LLM 回答时用父块内容
            for k, sub_chunk in enumerate(child_splitter_use.split_documents([parent_doc])):
                sub_chunk.metadata["parent_id"] = parent_id                      # 指向所属父块
                sub_chunk.metadata["parent_content"] = parent_doc.page_content   # 携带父块完整文本
                sub_chunk.metadata["id"] = f"{parent_id}_child_{k}"             # 子块唯一 ID
                child_chunks.append(sub_chunk)

    logger.info(f"子块数量: {len(child_chunks)}")
    return child_chunks
