from langchain_ollama import ChatOllama

# 初始化模型，连接到本地 Ollama 服务
llm = ChatOllama(
    model="deepseek-r1:7b",  # 确保此模型名与你用 `ollama pull` 下载的完全一致
    temperature=0,   # 控制生成文本的随机性，0 表示更确定性的输出
)

# 现在可以像使用其他 LangChain 聊天模型一样使用它
messages = [
    ("system", "你是一个乐于助人的助手。"),
    # ("human", "请用一句话解释人工智能是什么。"),
    ("human", "详细讲一下langchain_ollama 依赖"),
]

response = llm.invoke(messages)
print(response.content)