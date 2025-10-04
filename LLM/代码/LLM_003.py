from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# 初始化模型，连接到本地 Ollama 服务
llm = ChatOllama(
    model="deepseek-r1:7b",  # 确保此模型名与你用 `ollama pull` 下载的完全一致
    temperature=0,  # 控制生成文本的随机性，0 表示更确定性的输出
)

# 现在可以像使用其他 LangChain 聊天模型一样使用它

# 提示词模版
# 最简单的用法 - 单轮对话
chat_template = [
    SystemMessagePromptTemplate.from_template("你是一个专业的翻译官，擅长将中文翻译成英文。"),  # 系统角色设定
    HumanMessagePromptTemplate.from_template("请将以下中文句子翻译成英文：{sentence}"),  # 用户输入
]

prompt_template = ChatPromptTemplate.from_messages(chat_template)

chain = prompt_template.pipe(llm)

response = chain.invoke({
        "sentence": "今天天气真好，阳光明媚。"  # 替换成你想翻译的句子
    })
print(response.content)
