# 基于LangGraph的垂直领域智能体实战-1.03

## 课程目标

本课程适用于对大模型和智能体设计有初步概念的同学。

通过学习本课程，达成以下目标：

- 环境搭建：能够独立配置LangGraph开发环境。
- 掌握工具：掌握LangGraph的核心概念（图、节点、边、状态、流程控制等）
- 基础开发：完成基本的对话系统/工作流的搭建。
- 设计模式：理解和实践六种主流的智能体设计模式。
- 完成项目：使用LangGraph，完成新车型设计方案，具备构建智能体的实战能力。



## 1. LangGraph快速入门

### a. 学习目标

了解基于大模型的智能体

了解LangGraph和LangChain的区别

能够独立安装LangGraph环境

能够快速上手第一个LangGraph程序

### b. 智能体

智能体（Agent）是指能够感知环境并采取行动以实现特定目标的代理体。它可以是软件、硬件或一个系统，具备自主性、适应性和交互能力。智能体通过感知环境中的变化（如通过传感器或数据输入），根据自身学习到的知识和算法进行判断和决策，进而执行动作以影响环境或达到预定的目标。智能体在人工智能领域广泛应用，常见于自动化系统、机器人、虚拟助手和游戏角色等，其核心在于能够自主学习和持续进化，以更好地完成任务和适应复杂环境。

在本课程中谈到的智能体，特指基于大模型的智能体。基于大模型的智能体（LLM-based Agent）是以大型语言模型（LLM）为核心控制器构建的自主智能系统，通过整合感知、规划、记忆与工具调用等模块，实现复杂任务的自动化处理。

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NmMyOTBkNmNlNzY3NTFjMWE3ZTJkZDdhODVlODBlYWZfOWM2MTZjMzg1NmZjNjg3NDgwOTdkMGVhM2MwODI5YjZfSUQ6NzU5MzkyMzQzMDY4MTc0MjUzOV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

其技术架构与核心特性如下：

#### i. 核心架构

- **大脑模块（LLM核心）**  
 作为智能体的决策中枢，大模型负责任务分解、逻辑推理和策略生成，例如GPT-4、DeepSeek等模型通过海量参数实现语言理解与生成能力。
- **感知模块**  
 处理多模态输入（文本、图像、音频等），将环境信息转化为模型可理解的表征。
- **行动模块**  
 调用外部工具（如搜索引擎、API）执行具体操作，形成“感知-决策-执行”闭环。
- **记忆机制**  
 通过短期记忆（对话上下文）和长期记忆（向量数据库）实现状态持久化。

#### ii. 关键技术特性

- **自主任务分解**‌：将复杂目标拆解为可执行的子任务链，例如自动生成代码需经历需求分析、模块编写、测试验证等步骤。
- **动态工具调用**‌：根据任务需求自主选择API，如计算时调用数学工具，查询实时数据时启用搜索引擎。
- **多智能体协同**‌：多个Agent通过通信协议分工协作，如医疗诊断系统中专科Agent联合分析病例。
- **持续学习优化**‌：通过强化学习或人类反馈（RLHF）迭代改进策略。

#### iii. 典型应用场景

- **自动化办公**‌：生成投研报告、合同审核等流程自动化
- **智能开发**‌：自主完成代码编写、测试与部署（如Devin AI程序员）
- **教育医疗**‌：个性化教学助手、多专科联合诊断系统

#### iv. 常用的智能体框架

| **名称** | **是否开源** | **核心能力** |
|-|-|-|
| LangChain/LangGraph | 开源 | 模块化设计支持工具链开发，通过Chain、Agent等抽象层实现任务编排，特别适合构建带记忆的问答系统或多步骤工作流 |
| CrewAI | 开源 | 基于角色分工的多Agent协作框架，可模拟“研究员-编辑-校对员”等团队协作模式，适用于复杂任务分解 |
| AutoGen | 开源 | 支持多Agent对话与动态工具调用，内置人类反馈机制，适合需人机协同的场景（如客服工单处理） |
| Dify | 开源 | 开源低代码平台，融合LLMOps理念，支持可视化编排工作流和私有化部署，适合企业级知识管理应用 |
| 字节跳动·扣子（Coze） | 商用 | 拖拽式工作流设计，集成60+插件（如抖音数据抓取），支持一键分发至微信/飞书等生态 |
| 百度·文心智能体 | 商用 | 低代码开发工具链（AI Studio），集成500+预置API（OCR、语音合成），覆盖政务、医疗等行业 |
| 腾讯元器 | 商用 | 深度对接微信/QQ生态，支持3D虚拟形象生成，适用于教育陪练、游戏客服等场景 |

这里我们选择LangGraph作为智能体构建的框架，一个是LangGraph和Langchain类似，拥有比较好的技术生态，配合 LangSmith 做调试。另一方面选 LangGraph，它可以精细控制每个步骤、状态，适合复杂业务。

### c. LangChain

LangChain是一个专为构建基于大型语言模型(LLM)的应用程序而设计的开源框架，由Harrison Chase于2022年10月推出。该框架通过模块化组件和标准化接口，实现了语言模型与外部数据源、工具及环境的深度集成，显著降低了开发复杂度。2025年10月，LangChain发布了1.0版本，整个框架的工作逻辑发生了巨大变化，可以参照文档：

<cite doc-id="Yab2dCRRpoOQeNxJio7cEvVInNb" file-type="docx" title="01-LangChain1.x-入门篇" token="Yab2dCRRpoOQeNxJio7cEvVInNb" type="doc"></cite>

### d. LangGraph概念

在LangChain1.0版本之后，LangGraph成为了整个LangChain生态的基础。

什么是LangGraph?我们首先看一下官网：https://langchain-ai.github.io/langgraph/

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NTJhMDlkOTU5ZDYyNDYyMDkwMDZjNzkxZDhiYjA0MzNfNWEzOWEwNjlmNThhZTU0MTViMjA0ZmYwZmYzYTRiMTFfSUQ6NzU5MzkyMzY2OTQ0NTkwNTM2Nl8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

LangGraph是由LangChain团队开发的开源框架，专为构建基于大型语言模型(LLM)的有状态、多参与者应用程序而设计。其核心创新在于采用图结构(Graph)作为计算模型，突破了传统有向无环图(DAG)的限制，支持循环工作流和动态状态管理。该框架通过节点(Nodes)和边(Edges)定义工作流，节点代表LLM调用、工具函数等操作单元，边描述执行路径与条件逻辑。

通俗理解：LangGraph 是专门构建“AI工作流”的工具包，帮你把复杂的AI任务拆成步骤，像搭积木一样组装起来。

### e. LangGraph的安装

安装LangChain，我们采用的方式是创建虚拟环境，并依次安装依赖项，如下：

```Bash

#创建一个虚拟环境
conda create -n LangGraph python=3.11
#进入虚拟环境
conda activate LangGraph
#安装pytorch 使用南京大学的源比较快
pip3 install torch torchvision torchaudio --index-url https://mirrors.nju.edu.cn/pytorch/whl/cu126
#安装其他的支持包
#选用ollama作为基本的大模型工具
#LangChain是LangGraph的底层支持包
#使用LangChain_ollama调用ollama提供的大模型服务
#使用matplotlib把LangGraph中的图绘制成图片
pip3 install ollama LangChain LangChain_ollama matplotlib -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pip install LangGraph -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

### f.  LangGraph入门案例

作为入门案例，我们需要为凯瑞汽车提供一个销售助理。至少应该包含以下功能：

- 能够调用大模型，并与使用者对话。
- 客户询问销售助理的身份时，应该回答是属于凯瑞汽车的销售助理，而不是属于模型的原始训练厂商。
- 可以控制大模型的各种配置参数以提升灵活性。
- 可以动态加载提示词以适用于更多场景。
- 需要提供记忆能力，以支持多轮对话。
- 需要提供结构化输出能力，以更好地使用智能体的答案。

接下来分成6个步骤，演示整个销售助理的搭建过程

#### i. 搭建基本框架

第一步，搭建基本框架，提供最基本的调用大模型的能力和单轮对话功能。

```Python
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b"),
    tools=[],
    prompt=""
)

# Run the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "你是谁？"}]}
)
print(result["messages"][-1].content)
```

输出结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTc4MWY0NGRkYWI3OGUzNjM5NWIxNDJhZjBiNGZlZTNfOTE5OTM5Y2MyMzlmZTQ1M2Y3MDUxOTM2Yjk1NGIzOTBfSUQ6NzU5MzkyMzQyOTg5NjY4Njc5NV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

这份代码技术上可以运行，但不满足实际需求，回答的模型身份不符合预期。

#### ii. 添加工具

第二步，给agent增加一个工具，用以修正模型对于身份问题的回答。

```Python
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

def getId() -> str:
    """explain your identity"""
    return f"我是凯瑞汽车训练的智能销售助理"

agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b"),
    tools=[getId],
    prompt=""
)

# Run the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "你是谁？"}]}
)
print(result["messages"][-1].content)
```

输出结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MGNkNjliNjNhNzFlNTgwMjI5ODIyNmU5ZjkzMzRlYzBfNThmOTk5YTQ5MzVlYWQxNTJkYzY2ZTQxMzg3MDdjNTBfSUQ6NzU5MzkyMzQyNzk2MzA3OTg2NV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iii. LLM配置

第三步，指定参数配置llm，提升智能体的灵活性。比较重要的参数如下表所示：

| 参数名 | 含义 | 默认值 |
|-|-|-|
| model | 模型名称 |  |
| temperature | 温度 | 0.8 |
| num_predict | 生成长度 | 128 |
| num_ctx | 生成字符时使用的上下文窗口 | 2048 |
| num_gpu | 使用GPU的数量 | 0 |
| base_url | 调用模型的URL | http://localhost:11434 |

这里配置的是温度temperature，它的默认值是0.8。回忆一下大模型里温度参数的作用。并用下面的代码来验证。

大模型中的 temperature 参数用于控制模型输出的随机性和创造性。

- 较高的 temperature 值会增加输出的随机性，产生更多样化的结果，但也可能降低预测准确性。
- 较低的 temperature 值则会使输出更确定、更保守，更倾向于产生重复和更可预测的输出。
- 设置 temperature 时需要在随机性和准确性之间找到平衡。在测试大模型时，可以通过改变 temperature 的值来评估模型在不同情境下的表现，比如在创意生成、代码编写等任务中，观察其生成结果的变化。

控制温度的代码如下：

```Python
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

def getId() -> str:
    """explain your identity"""
    return f"我是凯瑞汽车训练的智能销售助理"

agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b",temperature = 0.0),
    tools=[getId],
    prompt=""
)

for i in range(10):
    # Run the agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "你是谁？"}]}
    )
    print(result["messages"][-1].content)
```

输出结果：

当温度=0.0时：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTQ5N2YxYWU1NTZmM2ExMjFjMTgzZDRlYzE2YTQzODlfNmJkNDY1NDZmM2UzZWFmMTEyMzExNTQ5ZWM2Mjc4YmFfSUQ6NzU5MzkyMzQyOTgwMDI1MDU5MF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

当温度=0.8时：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MzhiODg5YjZjMTBiMzE4YjY3OGJhNjMxMTk3ZTBiODdfY2NkMTc4YjRiM2VmYjY5NzM1YTJlMzlhMGE5ZDIwNjZfSUQ6NzU5MzkyMzQyOTQwNTk4NjAyMF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iv. 动态提示词

第四步，使用动态提示词。如果部署了一套大模型，但是需要灵活地适配于多个场景，可以考虑采用动态提示词。

```Python
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_core.messages import AnyMessage

def getPrompt(state,config) -> list[AnyMessage]:
    company = config["configurable"].get("company")
    systemMsg = "你是"+company+"训练的智能销售助理"
    return [{"role": "system", "content": systemMsg}] + state["messages"]


agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b",temperature = 0.8),
    tools=[],
    prompt=getPrompt
)

# Run the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "你是谁？"}]},
          config={"configurable": {"company": "诚通智能"}}
)
print(result["messages"][-1].content)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "你是谁？"}]},
          config={"configurable": {"company": "凯瑞汽车"}}
)
print(result["messages"][-1].content)
```

输出结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MjNlZGMxNWEzMjg5NTgwNzE5OWM1ZjdiY2JjYjZiODhfMWJjNjg2ZDUzZjZmN2ZiZDI1MjNmZDYwMzRhN2NjYjlfSUQ6NzU5MzkyMzQyOTk4MDU0MDA5NF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### v. 添加记忆

第五步，添加记忆功能，实现多轮对话。前面的智能体是没有记忆功能的，它仅仅根据用户当前的提问做出回应，无法联系上下文做出更全面的回答，看下面的例子：

```Python
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

def getId() -> str:
    """explain your identity"""
    return f"我是凯瑞汽车训练的智能销售助理"

def getPriceByItem(item):
    """根据车名查询价格"""
    priceTable= {"月光女神":"135000",
                 "黑猫":"243000",
                 "飞扬":"175000"}
    if item in priceTable:
        return item+"的单价是："+priceTable[item]


agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b",temperature = 0.8),
    tools=[getId,getPriceByItem]
)



prompt1 = "月光女神这款车多少钱？"
print("user:"+prompt1)
result = agent.invoke(
    {"messages": [{"role": "user", "content": prompt1}]}
)
print("assistant:"+result["messages"][-1].content)

prompt2 = "那飞扬呢？"
print("user:"+prompt2)
result = agent.invoke(
    {"messages": [{"role": "user", "content":prompt2 }]}
)
print("assistant:"+result["messages"][-1].content)
```

输出结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NWE5ZmMyNmFjNjhhNTM4YjhjNzMzODNhNjc2ZWM4MzJfNWNmOThjOGEwOTE0MjM4NTQ0MThlOTcxNjNlMmNlZjVfSUQ6NzU5MzkyMzQzMDkyNDMwNzY0Ml8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

为了实现多轮对话，需要启用记忆功能。记忆功能可以保持一段上下文，根据整个上下文而不仅仅是当前问题做出恰当的回答。

在启用记忆功能时，必须提供config，这里实现一个最简化的config，提供一个包含thread_id的配置，thread_id是对话（会话）的唯一标识符：

```Python
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

def getId() -> str:
    """explain your identity"""
    return f"我是凯瑞汽车训练的智能销售助理"

def getPriceByItem(item):
    """根据车名查询价格"""
    priceTable= {"月光女神":"135000",
                 "黑猫":"243000",
                 "飞扬":"175000"}
    if item in priceTable:
        return item+"的单价是："+priceTable[item]

checkpointer = InMemorySaver()

agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b",temperature = 0.8),
    tools=[getId,getPriceByItem],
    checkpointer=checkpointer
)


config = {"configurable": {"thread_id": "1"}}
prompt1 = "月光女神这款车多少钱？"
print("user:"+prompt1)
result = agent.invoke(
    {"messages": [{"role": "user", "content": prompt1}]},
    config
)
print("assistant:"+result["messages"][-1].content)

prompt2 = "那飞扬呢？"
print("user:"+prompt2)
result = agent.invoke(
    {"messages": [{"role": "user", "content":prompt2 }]},
    config
)
print("assistant:"+result["messages"][-1].content)
```

输出结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NWIzMzI1MmJhYzZlNDkxZjEwZmFkYTI1MWMyY2FhMGRfNTU1ZGNlYjY3OTA2NTc3NjQ3MzJhYWQxYmViOTJmMmVfSUQ6NzU5MzkyMzQyOTQwMTc0MjUyMV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### vi. 结构化输出

第六步，实现结构化输出。一般情况下，智能体的输出是一段文本，有些情况下，需要输出类似表格的结果，各数据之间有一定的对应关系，这些数据只有结构化，才方便后续使用，比如需要输出多个车型和对应的价格。

要生成符合模式的结构化响应，请使用response_format参数。模式可以用Pydantic模型或TypedDict定义。结果将通过structured_response字段访问。

```Python
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama


class PriceResponse(BaseModel):
    carType: str
    price:int

class PriceResponseList(BaseModel):
    priceResponseList: list[PriceResponse]

def getPriceByItem(item):
    """根据车名查询价格"""
    priceTable= {"月光女神":"135000",
                 "黑猫":"243000",
                 "飞扬":"175000"}
    if item in priceTable:
        return item+"的单价是："+priceTable[item]


agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b",temperature = 0.8),
    tools=[getPriceByItem],
    response_format = PriceResponseList
)

prompt1 = "月光女神和黑猫这两款车多少钱？"
print("user:"+prompt1)
result = agent.invoke(
    {"messages": [{"role": "user", "content": prompt1}]}
)
print(result["structured_response"])
```

输出结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTc5ZDRhYWIzYjJlYWU4YzEyN2MwZTg2MDc0ZmM0ODhfNGY5NzBmMTI0ZTU1ZDBmMzliM2U3YjMxZDc4NjhlMDBfSUQ6NzU5MzkyMzQyNzQ4OTIzODIzM18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

最后回顾一下我们入门案例的整体需求和实现情况。

### g. 小结

> 问题：
> 
>         1  什么是LangChain?
> 
>         2  什么是LangGraph？LangGraph有哪些优势？
> 
> 实操：
> 
>         1 搭建一个LangGraph环境
> 
>         2 写一个最简单的LangGraph入门代码
> 
>         3 在最简代码基础上添加工具，让智能体可以设定身份
> 
>         4 设置LLM配置
> 
>         5 给智能体设置动态提示词
> 
>         6 给智能体添加记忆
> 
>         7 让智能体输出结构化的结果



## 2. LangGraph的基本组件

### a. 学习目标

掌握LangGraph的核心组件：图、状态、节点、边、记忆，并能够熟练运用。

### b. 图（graph）

#### i. 什么是graph

普鲁士的柯尼斯堡市（现俄罗斯加里宁格勒）位于普雷格尔河两岸，城市中有七座桥梁相连。有人提出过一个非常有趣的问题，能不能设计一条游览路线，每座桥只需要经过一次，就能玩遍整座城市？

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NWM4M2Q2NGMyNGQzZGMxNWYzZTJiODliNzk3ZDczY2NfMGI2YTYyMGI5YjExZTgxYTA5ZjAzZGU4NzUxZTExODNfSUQ6NzU5MzkyMzQyOTQwNTkzNjg2Nl8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

无数人做出过各种努力，但都没有成功，后来引起了大数学家**莱昂哈德·欧拉（Leonhard Euler）**的注意，他是很多重要数学概念的提出者，包括函数、指数、对数、复数等。他把问题简化成下面的形式:

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTdjYmU4YmNkMDUzYjU0ZWNkMDRlZmUwNzQxNzE4ZDFfNjhiMWM2NzVkMzlhYTE3NzViNWVjMzdlZmQyMTI1NWFfSUQ6NzU5MzkyMzQzMDE1MjQ5MDE4NF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

由此引入图论（graph theory），我们今天神经网络框架pytorch、tensorflow等使用的计算图，只是图论的微不足道的小小应用，LangGraph使用的图也是这一理论体系下的产物。

#### ii. LangGraph中的graph

图是顶点和边的集合，LangGraph里的图是有向无权的全联通图。有**StateGraph**和**MessageGraph**两种形式。

StateGraph是LangGraph的核心结构，用于需要维护长期状态的场景。MessageGraph是一个轻量化的图，只用于传递消息（message）,应用场景非常狭窄。

StateGraph默认有一个START节点和一个END节点，编写一个最简化的图，代码如下：

```Python
from LangGraph.graph import START,StateGraph,END

graphBuilder = StateGraph(dict)
graph = graphBuilder.compile()
#用matplotlib输出graph
import matplotlib.pyplot as plt
import matplotlib.image as mpimg  # 导入matplotlib.image用于读取图像
try:
    # 使用 Mermaid 生成图表并保存为文件
    mermaid_code = graph.get_graph().draw_mermaid_png()
    with open("graph.jpg", "wb") as f:
        f.write(mermaid_code)

    # 使用 matplotlib 显示图像
    img = mpimg.imread("graph.jpg")
    plt.imshow(img)
    plt.axis('off')  # 关闭坐标轴
    plt.show()
except Exception as e:
    print(f"An error occurred: {e}")
```

这份代码生成一张最简化图的图片：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NDY0Y2I0NGZiZDZmZjg2NzJiZmFjYjFkZjcwODc1MGVfMjJlNzAyYzVmNzRhNDY1MjE4YWNhMmJmMDI0NGIxNWJfSUQ6NzU5MzkyMzQzMDgyNzc1Njc0NF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iii. 小结

> 问题：
> 
>        1 LangGraph默认的最小化图包含哪些元素？
> 
> 实操：
> 
>        1 构建一个最小化的LangGraph的图
> 
>        2 写代码打印LangGraph的图

### c. 状态

状态（state）是LangGraph中的核心设计，用于在复杂任务或对话系统中存储和传递上下文信息。

#### i. 用dict作为状态

状态（state）是一个结构化的数据容器，以键值对的形式存在，本质上是一个字典（dict）。

```Python
from LangGraph.graph import START,StateGraph,  END

def add(state):
    print("*"*80)
    print("before add:"+str(state))
    state["y"] = state["x"]+1
    print("after add:" + str(state))
    return state

def buildGraph():
    #定义图的时候，要指定状态的数据类型
    graphBuilder = StateGraph(dict)
    graphBuilder.add_node("add", add)
    graphBuilder.set_entry_point("add")
    graphBuilder.add_edge("add", END)
    graph = graphBuilder.compile()
    return graph

if name == "__main__":
    graph = buildGraph()

    #state本质上是一个字典，可以使用python的原生字典
    state = {"x":2}
    result = graph.invoke(state)
    print(state)
```

运行代码，输出：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTI3YjFhMTZhOGM3Nzc4ZmNiNzE3OTNhN2IzYWViMDRfZTk5ODYzMGQ3NzAxZGY0ZjM1NmVmMzgzMzc2N2VhY2FfSUQ6NzU5MzkyMzQyODIzNTgyNDM0OV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### ii. 用TypedDict作为状态

但实际工作中为了方便数据校验，一般使用TypedDict

```Python
from LangGraph.graph import StateGraph,  END
from typing_extensions import TypedDict

#定义一个类，类型是TypedDict。这种数据类型可以方便数据校验，以后我们都采用这种方式定义状态
class State(TypedDict):
    x: int
    y: int

def add(state):
    print("*"*80)
    print("before add:"+str(state))
    state["y"] = state["x"]+1
    print("after add:" + str(state))
    return state

def buildGraph():
    # 定义图的时候，要指定状态的数据类型
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("add", add)

    graphBuilder.set_entry_point("add")
    graphBuilder.add_edge("add", END)

    graph = graphBuilder.compile()
    return graph

if name == "__main__":
    graph = buildGraph()

    from tools import showGraph
    showGraph.showGraphInCode(graph,"graph.jpg")

    #实例化状态
    state:State = {'x':2}
    result = graph.invoke(state)
    print(result)
```

运行代码，输出：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZDJiYTE0NzgzODgyMTRkNTgwZGNmZWJkODFlMjZhZjJfZjdjNTI3NDExMDQ0ZGFmOTM4ZGY4ODk2ZTI5MWM1YTFfSUQ6NzU5MzkyMzQyNzk2MzExMjYzM18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iii. 小结

> 问题：
> 
>       1 什么是state?
> 
>       2 应该选用什么数据结构做state?为什么？
> 
> 实操：
> 
>       1 编写一个带有state的graph

### d. 节点（Node）

节点（node）是构建graph的核心组件，每个节点代表一个具体的任务或操作单元，一般是封装成一个函数执行业务逻辑，并与状态（state）产生交互。

#### i. 节点类型

一般来说，有以下八种节点：

<sheet sheet-id="cdYH3a" token="CDKOszgschVb5ot8gtAcynbnnce"></sheet>

这里只展示三种基本节点，流程控制类的节点放到第四章和对应的边一起介绍。

#### ii. 函数节点

函数节点本质上就是一个通用的python函数

```Python
def add(state):
    print("*"*80)
    print("before add:"+str(state))
    state["y"] = state["x"]+1
    print("after add:" + str(state))
```

#### iii. 工具节点

工具节点的作用是封装外部工具或API

```Python
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"
```

#### iv. 大模型节点

大模型节点调用大模型生成结果，如果需要使用工具，可以调用时加以说明

```Python
def configLLM(state):
    agent = create_react_agent(
        model=llm,
        #这里说明可以使用的工具
        tools=[get_weather],
        prompt="You are a helpful assistant"
    )
    #调用大模型
    result = agent.invoke(
        {"messages": [{"role": "user", "content": state["query"]}]}
    )
    state["answer"] = result["messages"][-1].content
    return state
```

v. 在图中添加节点

```Python
def buildGraph1():
    graphBuilder = StateGraph(State)

    #在图里添加一个节点
    graphBuilder.add_node("add", add)

    graphBuilder.set_entry_point("add")
    graphBuilder.add_edge("add", END)

    graph = graphBuilder.compile()
    return graph
```

```Python
def buildGraph2():
    graphBuilder = StateGraph(State)

    # 在图里添加一个节点
    graphBuilder.add_node("configLLM", configLLM)

    graphBuilder.add_edge(START, "configLLM")
    graphBuilder.add_edge("configLLM", END)

    graph = graphBuilder.compile()
    return graph
```

#### vi. 小结

> 问题：
> 
>       1 LangGraph中有哪些类型的节点？
> 
>       2 在图中添加节点用哪个函数？具体参数是什么？
> 
> 实操：
> 
>       1 编写一张图，至少包含一个函数节点和一个大模型节点

### e. 边（Edge）

边（Edge）是连接节点的逻辑通道，用来控制工作流的执行顺序和数据流向，主要有以下两种类型：

<sheet sheet-id="XeUP2c" token="CDKOszgschVb5ot8gtAcynbnnce"></sheet>

#### i. 普通边

普通边的作用是连接两个节点，包括START和END

```Shell
#用这种方式设置普通节点间的联系
#graphBuilder.add_edge("add", "multiply")

# 可以用这两种方式设置1起始节点，个人建议采用第一种，符合边的通用定义方式
graphBuilder.add_edge(START, "heatUp")
#graphBuilder.set_entry_point("add")

# 可以用这两种方式设置终止节点，个人建议采用第一种，符合边的通用定义方式
graphBuilder.add_edge("getBolidWater",END)
#graphBuilder.set_finish_point("getBolidWater")
```

#### ii. 条件边

条件边和条件节点有两种写法，第一种写法：

```Python
#条件节点的第一种方式，每个分支返回一个字符串
def processWater(state):
    if state["tempreture"]== 100:
        return "hotWaterReady"
    else:
        return "stillCode"

#条件边的第一种方式：（起点，终点，映射表），注意：终点是条件节点，不用注册。映射表是条件节点返回的字符串映射到后续节点
graphBuilder.add_conditional_edges("heatUp",processWater,{"hotWaterReady":"getBolidWater","stillCode":"heatUp"})
```

条件边和条件节点的第二种写法：

```Python
#条件节点的第二种方式，每个分支返回后续节点名
def processWater2(state):
    if state["tempreture"]== 100:
        return END
    else:
        return "heatUp"

# 条件边的第二种方式：（起点，终点），注意：终点是条件节点，不用注册。
graphBuilder.add_conditional_edges("heatUp", processWater)
```

个人建议使用第一种写法。所有节点流转全部集中在图的定义部分，方便检查。

#### iii. 整体代码

使用普通边和条件边的代码如下：

```Python
from LangGraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict

class State(TypedDict):
    tempreture: int

def heatUp(state):
    print("*"*80)
    print("before heatUp:"+str(state))
    state["tempreture"] = state["tempreture"]+10
    if state["tempreture"]>100:
        state["tempreture"] = 100
    print("after heatUp:" + str(state))
    return state

#条件节点的第一种方式，每个分支返回一个字符串
def processWater(state):
    if state["tempreture"]== 100:
        return "hotWaterReady"
    else:
        return "stillCode"

#条件节点的第二种方式，每个分支返回后续节点名
def processWater2(state):
    if state["tempreture"]== 100:
        return END
    else:
        return "heatUp"

def getBolidWater(state):
    return state

def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("heatUp", heatUp)
    graphBuilder.add_node("getBolidWater", getBolidWater)

    # 用这种方式设置普通节点间的联系
    # graphBuilder.add_edge("add", "multiply")

    # 可以用这两种方式设置起始节点，个人建议采用第一种，符合边的通用定义方式
    graphBuilder.add_edge(START, "heatUp")
    #graphBuilder.set_entry_point("add")

    #条件边和条件节点有两种写法，个人建议第一种。所有节点流转全部集中在图的定义部分，方便检查
    #条件边的第一种方式：（起点，终点，映射表），注意：终点是条件节点，不用注册。映射表是条件节点返回的字符串映射到后续节点
    graphBuilder.add_conditional_edges("heatUp",processWater,{"hotWaterReady":"getBolidWater","stillCode":"heatUp"})

    # 条件边的第二种方式：（起点，终点），注意：终点是条件节点，不用注册。
    #graphBuilder.add_conditional_edges("heatUp", processWater)

    # 可以用这两种方式设置起始节点，个人建议采用第一种，符合边的通用定义方式
    graphBuilder.add_edge("getBolidWater",END)
    #graphBuilder.set_finish_point("getBolidWater")

    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph()

    from tools import showGraph
    showGraph.showGraphInCode(graph,'graph.png')

    state:State = {"tempreture": 28}
    result = graph.invoke(state)
    print(result)
```

运行结果为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MmM1YzY0OGMxODRlMDE5YTU0NTFjNGQwMTRkZmY2ZDhfODFiMGE1NzgyNjhhYWYwZWQzNGIwNTUyMzdkMTFlZGFfSUQ6NzU5MzkyMzQzMjUwNTUxMTA5Ml8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iv. 小结

> 问题：
> 
>        1 LangGraph中有哪些类型的边？
> 
> 实操：
> 
>         1 写一份代码，至少包含一条普通边
> 
>         2 写一份代码，至少包含一条条件边

### f. 记忆（memory）

LangGraph允许带有记忆功能，是通过LangGraph.checkpoint.memory来实现的

#### i. 代码

```Python
from LangGraph.graph import StateGraph, START,END
from LangChain_ollama import ChatOllama
from typing_extensions import TypedDict
from typing import Annotated
from LangGraph.graph.message import add_messages
from LangGraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOllama(model="qwen2.5:7b")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("chatbot", chatbot)

    graphBuilder.add_edge(START, "chatbot")
    graphBuilder.add_edge("chatbot",END)

    graph = graphBuilder.compile()
    return graph

def buildGraphWithMemory():
    graphBuilder = StateGraph(State)
    #实例化memory
    memory = MemorySaver()

    graphBuilder.add_node("chatbot", chatbot)

    graphBuilder.add_edge(START, "chatbot")
    graphBuilder.add_edge("chatbot",END)

    #编译图的时候指定memory
    graph = graphBuilder.compile(checkpointer=memory)
    return graph

def singleRound(graph):
    while True:
        try:
            userInput = input("User: ")
            if userInput.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            state = {"messages": [{"role": "user", "content": userInput}]}
            result = graph.invoke(state)
            # print(result)
            print("Assitant:", result["messages"][-1].content)
        except Exception as e:
            print("发生错误："+str(e))

def multiRound(graph,config):
    while True:
        try:
            userInput = input("User: ")
            if userInput.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            state = {"messages": [{"role": "user", "content": userInput}]}
            result = graph.invoke(state, config=config)
            # print(result)
            print("Assitant:", result["messages"][-1].content)
        except Exception as e:
            print("发生错误："+str(e))

if __name__ == "__main__":
    graph = buildGraph()
    singleRound(graph)

    #graphWithMemory = buildGraphWithMemory()
    #config = {"configurable": {"thread_id": "1"}}
    #multiRound(graphWithMemory,config)
```

单论对话结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YjIwNjQ2MjJmN2MyNTdjMzIxZjRmNmYwYzYxODM3NjNfYzRkOTM4MzBlM2MzZWY2ZTQ2YzgwMWNmOTkxMWJkZTZfSUQ6NzU5MzkyMzQyOTQ4OTk4Njc4NF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

多轮对话结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZmE3YzZlOTU3OTJjOTcxMGYzMjM1NTliZTAyYTgwOWVfMjdjODJjNDM5NDcwY2IzYTZjOTA0MTZhMGE2MTNmNDhfSUQ6NzU5MzkyMzQzMzAyMTMyODU4N18xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

#### ii. 小结

> 实操：
> 
>       1 实现一个带记忆的多轮对话机器人

### g. 基本执行步骤

#### i. 基本步骤

执行一个LangGraph项目要完成以下六个基本步骤：

- 初始化模型和工具
- 初始化图和状态
- 定义节点
- 定义边和出口入口
- 编译图
- 执行图

#### ii. 代码

```Python
from langgraph.graph import StateGraph, START,END
from langchain_ollama import ChatOllama
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

#第一步：初始化模型和工具
def getID():
    """explain your identity"""
    return f"我是凯瑞汽车的档案管理助手"

llm = create_react_agent(
    model = ChatOllama(model="qwen2.5:7b"),
    tools=[getID],
    prompt=""
)

def chatbot(state):
    return llm.invoke(state)

#第二步：初始化图和状态
class State(TypedDict):
    messages: Annotated[list, add_messages]
graphBuilder = StateGraph(dict)

#第三步：定义节点
graphBuilder.add_node("chatbot", chatbot)

#第四步：定义边和出入口
graphBuilder.add_edge(START, "chatbot")
graphBuilder.add_edge("chatbot",END)

#第五步：编译图
graph = graphBuilder.compile()

#第六步：执行图
userInput = input("User: ")
state:State = {"messages": [{"role": "user", "content": userInput}]}
result = graph.invoke(state)
print("Assistant:"+str(result["messages"][-1].content))
```

运行结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MGVmZTM4ZjNkZTg5ZmY4NTZmYTQ4MGFmMzY2YzBkMWRfYzQ1OWE0MjE4ZjVlM2Y5NjYzZTEyMzg4ODk1ZTYzNmJfSUQ6NzU5MzkyMzQyOTQzNTQ0NDQwMl8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iii. 小结

> 问题：
> 
>       1 LangGraph的基本执行步骤是什么？
> 
> 实操：
> 
>        2 写一份代码，实现LangGraph的基本执行步骤

### h. 小结

> 实操：
> 
>         1 构建一个最小化的LangGraph图
> 
>         2 用mapPlotLib打印这张图
> 
>         3 使用TypedDict组织状态数据
> 
>         4 编写一张图，至少包含一个函数节点和一个大模型节点
> 
>         5 编写一张图，至少使用一条正常边
> 
>         6 编写一张图，至少使用一条条件边和一个条件节点
> 
>         7 实现一个带有记忆的多轮对话机器人
> 
>         8 实现LangGraph的基本执行步骤

## 3. LangGraph的流程控制

### a. 学习目标

能够熟练使用LangGraph的流程控制方式：分支、循环、并行、人工介入、子图。

能够使用各种流程控制工具搭建较复杂的应用。

### b. 案例全貌

#### i. 案例简介

如果要冲一杯咖啡，有下面几个步骤必须要考虑：

- **磨咖啡豆**‌
- **烧热水**‌（这里有分支和循环，如果水温不够，要继续加热，一直到水烧开为止）
- **冲咖啡**‌（把前两步结果合并）
- **决定是否加糖**‌（根据用户反馈调整输出）

这个过程可以用下图表示：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NDIxMjg2ZjlhYjY4NDkwMDA1OGFiMTIyNGEyN2EyZmRfNDFlNWVmZDk4NmY3NWZmYmE1NjdiZGExMGE4NDQ5NzVfSUQ6NzU5MzkyMzQyOTQwNjAzNTE2M18xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

#### ii. 整体代码

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver
from tools import showGraph

#合并温度值的方式，取其大者
def updateTempreture(left, right):
    return max(left, right)

#合并产物的方式，优先取工序靠后的产物
def updateProduct(left,right):
    if left=="加糖咖啡" or right == "加糖咖啡":
        return "加糖咖啡"
    elif left=="咖啡" or right == "咖啡":
        return "咖啡"
    elif left=="开水" or right == "开水":
        return "开水"
    elif left=="温水" or right == "温水":
        return "温水"
    else:
        return "凉水"

#合并咖啡固体的方式，优先取工序靠后的产物
def updateSolid(left,right):
    if left=="咖啡粉" or right == "咖啡粉":
        return "咖啡粉"
    else:
        return "咖啡豆"
def updateSugur(left,right):
    if left=="是" or right == "是":
        return "是"
    else:
        return "否"

#添加状态类
class State(TypedDict):
    水温: Annotated[int,updateTempreture]
    产物:Annotated[str,updateProduct]
    咖啡固体:Annotated[str,updateSolid]
    是否加糖:Annotated[str,updateSugur]

#磨咖啡豆函数
def 磨咖啡豆(state):
    print("*" * 80)
    print("磨咖啡豆之前:" + str(state))
    state["咖啡固体"] = "咖啡粉"
    print("磨咖啡豆之后:" + str(state))
    return state

#烧水函数
def 烧水(state):
    print("*"*80)
    print("烧水之前:"+str(state))
    state["产物"] = "没烧开的水"
    state["水温"] = state["水温"]+10
    if state["水温"]>100:
        state["水温"] = 100
        state["产物"] = "开水"
    print("烧水之后:" + str(state))
    return state

#按照温度处理水的条件函数
def 按温度处理水(state):
    if state["水温"]== 100:
        return "水烧开了"
    else:
        return "水没开"

#得到开水函数，注意这个函数没有实际作用，只是便于展示整个流程
def 得到开水(state):
    return state

#冲咖啡函数
def 冲咖啡(state):
    print("冲咖啡之前:" + str(state))
    state["产物"]="咖啡"
    print("冲咖啡之后:" + str(state))
    return state

#中断节点，里面必须包含一个interrupt
def 询问是否加糖(state):
    human_response = interrupt("")
    state["是否加糖"] = human_response
    return state

#根据人类是否加糖的反馈，选择不同分支
def 是否加糖分支(state):
    #print(state)
    if state["是否加糖"] == "是":
        return "是"
    elif state["是否加糖"] == "否":
        return "否"

#加糖函数
def 加糖(state):
    print("加糖之前:" + str(state))
    state["产物"]="加糖咖啡"
    print("加糖之后:" + str(state))
    return state

def buildGraph5():
    # 初始化图
    graphBuilder = StateGraph(State)
    checkpointer = InMemorySaver()

    graphBuilder.add_node("heat water", 烧水)
    graphBuilder.add_node("get boil water", 得到开水)
    graphBuilder.add_node("磨咖啡豆", 磨咖啡豆)
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    graphBuilder.add_node("询问是否加糖", 询问是否加糖)
    graphBuilder.add_node("加糖", 加糖)

    graphBuilder.add_edge(START, "磨咖啡豆")
    graphBuilder.add_edge(START, "heat water")
    graphBuilder.add_conditional_edges("heat water", 按温度处理水, {"水烧开了": "get boil water", "水没开": "heat water"})
    graphBuilder.add_edge(["get boil water","磨咖啡豆"], "冲咖啡")
    graphBuilder.add_edge("冲咖啡", "询问是否加糖")
    graphBuilder.add_conditional_edges("询问是否加糖", 是否加糖分支,{"是":"加糖","否":END})
    graphBuilder.add_edge("加糖", END)

    graph = graphBuilder.compile(checkpointer=checkpointer)
    return graph

def buildGraph6():
    #烧水子图
    # 初始化图
    heatWaterSubGraphBuilder = StateGraph(State)
    # 添加节点
    heatWaterSubGraphBuilder.add_node("heat water", 烧水)
    heatWaterSubGraphBuilder.add_node("get boil water", 得到开水)
    # 添加边
    heatWaterSubGraphBuilder.add_edge(START, "heat water")
    heatWaterSubGraphBuilder.add_conditional_edges("heat water", 按温度处理水,{"水烧开了": "get boil water", "水没开": "heat water"})
    # 编译图
    heatWaterSubGraph = heatWaterSubGraphBuilder.compile()

    #加糖子图
    # 初始化图
    addSugurSubGraphBuilder = StateGraph(State)
    # 初始化记忆。使用人工介入必须带有记忆，否则图中断执行后无法正常继续
    checkpointer = InMemorySaver()
    # 添加节点
    addSugurSubGraphBuilder.add_node("询问是否加糖1", 询问是否加糖)
    addSugurSubGraphBuilder.add_node("加糖", 加糖)
    # 添加边
    addSugurSubGraphBuilder.add_edge(START,"询问是否加糖1")
    addSugurSubGraphBuilder.add_conditional_edges("询问是否加糖1", 是否加糖分支, {"是": "加糖", "否": END})
    # 编译图，需要带有记忆
    addSugurSubGraph = addSugurSubGraphBuilder.compile(checkpointer=checkpointer)

    #总图
    # 初始化图
    graphBuilder = StateGraph(State)
    # 添加节点
    #注意这里把子图加入总图的方式，是把编译好的子图作为一个节点加入进来
    graphBuilder.add_node("得到热水子图",heatWaterSubGraph)
    graphBuilder.add_node("磨咖啡豆", 磨咖啡豆)
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    graphBuilder.add_node("加糖子图1", addSugurSubGraph)
    # 添加边
    graphBuilder.add_edge(START,"得到热水子图")
    graphBuilder.add_edge(START, "磨咖啡豆")
    graphBuilder.add_edge(["得到热水子图","磨咖啡豆"],"冲咖啡")
    graphBuilder.add_edge("冲咖啡","加糖子图1")
    # 编译图,需要带有记忆
    graph = graphBuilder.compile(checkpointer=checkpointer)
    return heatWaterSubGraph,addSugurSubGraph,graph


if __name__ == "__main__":
    graph = buildGraph5()
    #打印图
    showGraph.showGraphInCode(graph, "复杂流程.jpg")
    #初始化状态
    state:State = {"水温": 58,"产物":"凉水","咖啡固体":"咖啡豆"}
    #添加config
    config = {"configurable": {"thread_id": "some_id"}}
    #调用图
    state = graph.invoke(state, config)
    #中断后，接收用户输入
    userDecision = input("先生您好，请问您的咖啡需要加糖吗？(是/否):")
    while userDecision not in {"是", "否"}:
        userDecision = input("先生您好，请问您的咖啡需要加糖吗？(是/否):")
    #使用Command函数向graph提供用户输入的数据，继续工作流
    result = graph.invoke(Command(resume=userDecision), config=config)
    print(result)
```

运行结果如下：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NTdjYzRjNGIwNmY0YWFkZDAyNTEwOWNkOGM2MDdmMTZfODhjM2Y1ZDk3YzA3MTVmODUyOTk1MDllMmMyMzYwMjRfSUQ6NzU5MzkyMzQzMzAwODc3ODQ2NV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

### c. 分支

#### i. 分支简介

通过综合运用条件边和条件节点，可以控制graph的分支，我们把关注点放在案例的烧开水部分

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODhiYjFlMjViN2RmMWZjZDIyMzczNDg3YjU1ZWJiNThfZTgyZThjMGM2YjlmNWU5NDI3NzY3NDZkY2FlZDk2OTRfSUQ6NzU5MzkyMzQyOTQwMTk4ODMxOF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### ii. 实现代码

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict

#添加状态类
class State(TypedDict):
    水温: int
    产物:str

#烧水函数
def 烧水(state):
    print("*"*80)
    print("烧水之前:"+str(state))
    state["水温"] = state["水温"]+10
    if state["水温"]>100:
        state["水温"] = 100
        state["产物"] = "烧开的水"
    print("烧水之后:" + str(state))
    return state

#按照温度处理水的条件函数
def 按温度处理水(state):
    print("before processWater:"+str(state))
    if state["水温"]== 100:
        return "水烧开了"
    else:
        return "水没开"

#冲咖啡函数
def 冲咖啡(state):
    print("冲咖啡之前:" + str(state))
    state["产物"] = "咖啡"
    print("冲咖啡之后:"+str(state))
    return state

#需要继续加热函数
def 需要继续加热(state):
    state["产物"] = "没烧开的水"
    print("继续加热"+str(state))
    return state


#构建图
def buildGraph():
    #初始化图
    graphBuilder = StateGraph(State)
    #添加节点
    graphBuilder.add_node("烧水", 烧水)
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    graphBuilder.add_node("需要继续加热", 需要继续加热)
    #添加边
    graphBuilder.add_edge(START, "烧水")
    graphBuilder.add_conditional_edges("烧水",按温度处理水,{"水烧开了":"冲咖啡","水没开":"需要继续加热"})
    graphBuilder.add_edge("冲咖啡",END)
    graphBuilder.add_edge("需要继续加热", END)
    #编译图
    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph()

    #打印图
    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")

    #调用图
    state:State = {"水温": 28,"产物":"没烧开的水"}
    result = graph.invoke(state)
    print(result)
```

运行结果为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NTRkMDBiNjU0MTA1NDExNTIwMDk0NDhhNTYxYjUwNGVfYmMzYmI1OWNmYWMxZDIyN2Y5ZjMxOThmYzFhODZlNTdfSUQ6NzU5MzkyMzQzMDgyNzk1MzM1Ml8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

对应的graph是：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YjMxMGViNWVhNmQxMjcwODNiZDhiZWQwYjQ1ZGRjMjVfNmFhY2NhN2RmNDU2ZjNhZGRiNTAzZjMyMzEwZWNiODVfSUQ6NzU5MzkyMzQzMjUyMjIyMjgxNl8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

#### iii. 小结

> 实操：
> 
>        1 用代码实现LangGraph中的分支

### d. 循环

#### i. 循环简介

通过合理设置条件节点的跳转，可以构造循环。

烧开水每次增加水温10度，可能一次结束，更可能需要多次，这时就需要循环，我们继续把关注点集中在烧开水部分。

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZjEyM2FhMTdmNDlkMjRhNGZjYjg2MjY4MzU1MGZmNDFfZDkzNTZlNmZjYWRkMWUwNzZiZjAyMjBmYTBmMDlkZDhfSUQ6NzU5MzkyMzQzMzM3MzY4MjkwNl8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### ii. 实现代码

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict

#添加状态类
class State(TypedDict):
    水温: int
    产物:str

#烧水函数
def 烧水(state):
    print("*"*80)
    print("烧水之前:"+str(state))
    state["产物"] = "没烧开的水"
    state["水温"] = state["水温"]+10
    if state["水温"]>100:
        state["水温"] = 100
        state["产物"] = "开水"
    print("烧水之后:" + str(state))
    return state

#按照温度处理水的条件函数
def 按温度处理水(state):
    if state["水温"]== 100:
        return "水烧开了"
    else:
        return "水没开"

#构建图
def buildGraph():
    #初始化图
    graphBuilder = StateGraph(State)
    #添加节点
    graphBuilder.add_node("烧水", 烧水)
    #添加边
    graphBuilder.add_edge(START, "烧水")
    graphBuilder.add_conditional_edges("烧水",按温度处理水,{"水烧开了":END,"水没开":"烧水"})
    #编译图
    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph()
    #打印图
    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")
    #调用图
    state:State = {"水温": 28,"产物":"没烧开的水"}
    result = graph.invoke(state)
    print(result)
```

运行结果为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MzA5Y2YxZGMwMTYyNmJiZDg2MGEzZGI5ODA1YWM1YjhfZjM0ZTQ1ZGQ3ZDcxNzQ5ZWM3MTAzNDMyNjNiMWJiYjFfSUQ6NzU5MzkyMzQzMTgzNDQ1NTI0NV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

对应的graph是：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YWZjZTk4MGQyYzk5NzFhMDM5NDE3NjRlYWM3ZDRhN2RfNTRlNDNkNWYzOTc0OGFmM2Y2Y2RkMmE3ODEwMmJhMTdfSUQ6NzU5MzkyMzQzMTc4ODM1MDY1OF8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

#### iii. 小结

> 问题：
> 
>       1 循环使用了哪些基本组件？和分支有什么区别？
> 
> 实操：
> 
>       1 用代码实现LangGraph中的循环

### e. 并行

#### i. 并行简介

在一个graph中，某些节点可以并行，例如：在煮咖啡任务中，烧水和磨咖啡豆两个任务，互不干扰，可以同时进行。

这一小节，我们把关注点转移到烧开水和磨咖啡豆两个任务的并行执行和结果合并上

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODQ0Njk0ODdiNDEwYTJkZGRiZmQ5MDRkZDNjMGE5MDBfNGEyYmMxNjUzMDVlYzViZGI1MjA5MmM4MDZjNDFiODNfSUQ6NzU5MzkyMzQyOTk4MDY4NzU1MF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### ii. 最简单的并行版本

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict
from typing import Annotated

#合并温度值的方式，取其大者
def updateTempreture(left, right):
    return max(left, right)

#合并产物的方式，优先取工序靠后的产物
def updateProduct(left,right):
    if left=="咖啡" or right == "咖啡":
        return "咖啡"
    elif left=="开水" or right == "开水":
        return "开水"
    elif left=="温水" or right == "温水":
        return "温水"
    else:
        return "凉水"

#合并咖啡固体的方式，优先取工序靠后的产物
def updateSolid(left,right):
    if left=="咖啡粉" or right == "咖啡粉":
        return "咖啡粉"
    else:
        return "咖啡豆"

#添加状态类
#如果有并行的节点，必然涉及到并行节点输出数据的合并，使用Annotated，第一个参数是数据类型，第二个参数是合并数据的方式
class State(TypedDict):
    水温: Annotated[int,updateTempreture]
    产物:Annotated[str,updateProduct]
    咖啡固体:Annotated[str,updateSolid]

#磨咖啡豆函数
def 磨咖啡豆(state):
    print("*" * 80)
    print("磨咖啡豆之前:" + str(state))
    state["咖啡固体"] = "咖啡粉"
    print("磨咖啡豆之后:" + str(state))
    return state

#烧温水函数
def 烧温水(state):
    print("*"*80)
    print("烧温水之前:"+str(state))
    state["产物"] = "没烧开的水"
    if state["水温"]<38:
        state["水温"] = 38
        state["产物"] = "温水"
    print("烧温水之后:" + str(state))
    return state

#烧开水函数
def 烧开水(state):
    print("*"*80)
    print("烧开水之前:"+str(state))
    state["产物"] = "没烧开的水"
    if state["水温"]<100:
        state["水温"] = 100
        state["产物"] = "开水"
    print("烧开水之后:" + str(state))
    return state

#冲咖啡函数
def 冲咖啡(state):
    print("冲咖啡之前:" + str(state))
    state["产物"]="咖啡"
    print("冲咖啡之后:" + str(state))
    return state

#构建图
def buildGraph1():
    #初始化图
    graphBuilder = StateGraph(State)
    #添加节点
    graphBuilder.add_node("烧水2", 烧开水)
    graphBuilder.add_node("磨咖啡豆",磨咖啡豆)
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    # 添加边
    graphBuilder.add_edge(START, "磨咖啡豆")
    graphBuilder.add_edge(START, "烧水2")
    graphBuilder.add_edge("磨咖啡豆", "冲咖啡")
    graphBuilder.add_edge("烧水2", "冲咖啡")
    graphBuilder.add_edge("冲咖啡", END)
    #上述流程的执行顺序：
    #第一批计算的节点是 烧水2 和 磨咖啡豆
    #第二批计算的节点是 冲咖啡
    #这种写法貌似得到了正确的结果，其实是一种错觉，实际工作中不要这样写

    #编译图
    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph3()
    # 打印图
    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")
    # 调用图
    state:State = {"水温": 28,"产物":"凉水","咖啡固体":"咖啡豆"}
    result = graph.invoke(state)
    print(result)
```

运行结果为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NDAyNTFkMTliZjMwNzUxODQ4MmM5MGM4ZGU0ODNiYzBfODJmZDA4ZjBlN2RkNzJmOGJkOWE0YWM2YmJiOTU3NjFfSUQ6NzU5MzkyMzQzMzQ4MjczNDc5OF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

对应的graph为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZDUyODY5MDI4YTI2MTU2ZWNiMTliMzU5NDUxNmM0ODVfOGZiMjE4NGUyY2RlNWFjYzNlOTVlZWI2NjkwMWUyN2RfSUQ6NzU5MzkyMzQzMDc2OTE2NzU0OV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iii. 最简单并行版本的隐患

上述写法有重大隐患，前面的例子里，并行的两个分支都只有一个最简单的节点。更多情况下，并行任务中的一个分支可能含有多个节点，此时可能会引起错误。示例代码为：

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict
from typing import Annotated

#合并温度值的方式，取其大者
def updateTempreture(left, right):
    return max(left, right)

#合并产物的方式，优先取工序靠后的产物
def updateProduct(left,right):
    if left=="咖啡" or right == "咖啡":
        return "咖啡"
    elif left=="开水" or right == "开水":
        return "开水"
    elif left=="温水" or right == "温水":
        return "温水"
    else:
        return "凉水"

#合并咖啡固体的方式，优先取工序靠后的产物
def updateSolid(left,right):
    if left=="咖啡粉" or right == "咖啡粉":
        return "咖啡粉"
    else:
        return "咖啡豆"

#添加状态类
#如果有并行的节点，必然涉及到并行节点输出数据的合并，使用Annotated，第一个参数是数据类型，第二个参数是合并数据的方式
class State(TypedDict):
    水温: Annotated[int,updateTempreture]
    产物:Annotated[str,updateProduct]
    咖啡固体:Annotated[str,updateSolid]

#磨咖啡豆函数
def 磨咖啡豆(state):
    print("*" * 80)
    print("磨咖啡豆之前:" + str(state))
    state["咖啡固体"] = "咖啡粉"
    print("磨咖啡豆之后:" + str(state))
    return state

#烧温水函数
def 烧温水(state):
    print("*"*80)
    print("烧温水之前:"+str(state))
    state["产物"] = "没烧开的水"
    if state["水温"]<38:
        state["水温"] = 38
        state["产物"] = "温水"
    print("烧温水之后:" + str(state))
    return state

#烧开水函数
def 烧开水(state):
    print("*"*80)
    print("烧开水之前:"+str(state))
    state["产物"] = "没烧开的水"
    if state["水温"]<100:
        state["水温"] = 100
        state["产物"] = "开水"
    print("烧开水之后:" + str(state))
    return state

#冲咖啡函数
def 冲咖啡(state):
    print("冲咖啡之前:" + str(state))
    state["产物"]="咖啡"
    print("冲咖啡之后:" + str(state))
    return state

#构建图
def buildGraph2():
    # 初始化图
    graphBuilder = StateGraph(State)
    # 添加节点
    graphBuilder.add_node("烧水1", 烧温水)
    graphBuilder.add_node("烧水2", 烧开水)
    graphBuilder.add_node("磨咖啡豆",磨咖啡豆)
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    # 添加边
    graphBuilder.add_edge(START, "磨咖啡豆")
    graphBuilder.add_edge(START, "烧水1")
    graphBuilder.add_edge("烧水1","烧水2")
    graphBuilder.add_edge("磨咖啡豆", "冲咖啡")
    graphBuilder.add_edge("烧水2", "冲咖啡")
    graphBuilder.add_edge("冲咖啡", END)
    # 上述流程的执行顺序：
    # 第一批计算的节点是 烧水1 和 磨咖啡豆
    # 第二批计算的节点是 烧水2 和 冲咖啡
    # 第三批计算的节点是 冲咖啡
    #这里有两个错误：
    #1. 水还没彻底烧开就冲咖啡了
    #2. 冲咖啡的动作进行了两次
    # 这是因为 烧水2 和 磨咖啡豆 这两个节点的后续都是 冲咖啡。实际执行的时候，只要满足其中一个就可以了，这显然不是我们想要的执行流程

    # 编译图
    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph3()
    # 打印图
    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")
    # 调用图
    state:State = {"水温": 28,"产物":"凉水","咖啡固体":"咖啡豆"}
    result = graph.invoke(state)
    print(result)
```

运行的结果为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MGZkN2VkYjQzNzgxMmM5MzVkODdiMmM2NmIwOTU4NWRfNDQzODM4N2I5MTUxMjI4Yjc1YzM1MDllNWRiZTE5OWFfSUQ6NzU5MzkyMzQzMzI5Mzk1ODM2M18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

对应的graph为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTM2Yjg0ZWM3YTJkOTM3ZTIyMjQyYTVlYWU2NWNmODVfOWU2YTc3MzQ1ODEyMzg2YzI0M2IwOGQ1YzIzMjE3ZGJfSUQ6NzU5MzkyMzQzMDc2OTE1MTE2NV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)



值得注意的是：在完成磨咖啡豆的动作后，尽管水还没烧开，已经做了一次冲咖啡的动作；水烧开后，又做了一次冲咖啡的动作，显然这个执行顺序是有问题的。

#### iv. 正确的并行版本

graph2的写法的实质是：只要烧水2和磨咖啡豆任意一个动作完成，都应该进行一次冲咖啡动作，这不是我们我们想要的执行顺序。我们想要的执行顺序是只有烧水2和磨咖啡豆两个动作全部完成，才能执行冲咖啡动作，怎样在LangGraph中实现呢？下面是示例代码：

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict
from typing import Annotated

#合并温度值的方式，取其大者
def updateTempreture(left, right):
    return max(left, right)

#合并产物的方式，优先取工序靠后的产物
def updateProduct(left,right):
    if left=="咖啡" or right == "咖啡":
        return "咖啡"
    elif left=="开水" or right == "开水":
        return "开水"
    elif left=="温水" or right == "温水":
        return "温水"
    else:
        return "凉水"

#合并咖啡固体的方式，优先取工序靠后的产物
def updateSolid(left,right):
    if left=="咖啡粉" or right == "咖啡粉":
        return "咖啡粉"
    else:
        return "咖啡豆"

#添加状态类
#如果有并行的节点，必然涉及到并行节点输出数据的合并，使用Annotated，第一个参数是数据类型，第二个参数是合并数据的方式
class State(TypedDict):
    水温: Annotated[int,updateTempreture]
    产物:Annotated[str,updateProduct]
    咖啡固体:Annotated[str,updateSolid]

#磨咖啡豆函数
def 磨咖啡豆(state):
    print("*" * 80)
    print("磨咖啡豆之前:" + str(state))
    state["咖啡固体"] = "咖啡粉"
    print("磨咖啡豆之后:" + str(state))
    return state

#烧温水函数
def 烧温水(state):
    print("*"*80)
    print("烧温水之前:"+str(state))
    state["产物"] = "没烧开的水"
    if state["水温"]<38:
        state["水温"] = 38
        state["产物"] = "温水"
    print("烧温水之后:" + str(state))
    return state

#烧开水函数
def 烧开水(state):
    print("*"*80)
    print("烧开水之前:"+str(state))
    state["产物"] = "没烧开的水"
    if state["水温"]<100:
        state["水温"] = 100
        state["产物"] = "开水"
    print("烧开水之后:" + str(state))
    return state

#冲咖啡函数
def 冲咖啡(state):
    print("冲咖啡之前:" + str(state))
    state["产物"]="咖啡"
    print("冲咖啡之后:" + str(state))
    return state

#构建图
def buildGraph3():
    # 初始化图
    graphBuilder = StateGraph(State)
    # 添加节点
    graphBuilder.add_node("烧水1", 烧温水)
    graphBuilder.add_node("烧水2", 烧开水)
    graphBuilder.add_node("磨咖啡豆", 磨咖啡豆)
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    # 添加边
    graphBuilder.add_edge(START, "磨咖啡豆")
    graphBuilder.add_edge(START, "烧水1")
    graphBuilder.add_edge("烧水1", "烧水2")
    # 用这种方式，强制限定必须完成 烧水2 和 磨咖啡豆 这两个动作后才能 冲咖啡 ，这才是我们想要的执行流程
    graphBuilder.add_edge(["烧水2","磨咖啡豆"], "冲咖啡")
    graphBuilder.add_edge("冲咖啡", END)
    # 编译图
    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph3()
    # 打印图
    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")
    # 调用图
    state:State = {"水温": 28,"产物":"凉水","咖啡固体":"咖啡豆"}
    result = graph.invoke(state)
    print(result)

    state:State = {"水温": 28,"产物":"凉水","咖啡固体":"咖啡豆"}
    result = graph.invoke(state)
    print(result)
```

运行结果为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZGQ2ZWRmNmYzZmJhMTdkY2JiNTEzY2M4NGE5MTU3N2NfZmZiZGEyOTY3YzAwOWM5ODU1ZDkzYTYyMzgzNDI1YjFfSUQ6NzU5MzkyMzQzMTcwMDE1NTU5Ml8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

此时的graph是：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=M2E3ZTI3ZDBkZjJiZWVkNDVkZjYyYjhhMTdiNDNmYjFfNmVmZTU0MWEwMWI4OTRjNzY0MTMwY2U5ZDlmNDYzZDlfSUQ6NzU5MzkyMzQzMjU2ODM0Mzc3N18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iv. 小结

> 问题：
> 
>         1 怎样解决并行的情况下的state冲突
> 
>         2 怎样控制各个并行结构都运行完之后再运行合并节点？
> 
> 实操：
> 
>         1 实现LangGraph中的并行结构

### f. 人工介入

#### i. 人工介入简介

有些关键环节需要人工决策，这是需要引入人工介入的方式

这一小节，我们把关注点转移到案例的人工决定是否加糖的步骤上

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NmYxNDk1M2FhZTkzNTc0M2VlZDVlNjNiMTZjYzQwMDRfNDVhNWY2YzNhNDkyZmU3NmMxYTgyZTZjZDBmZjE2MjJfSUQ6NzU5MzkyMzQzMjY4MTYyMjcyOV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

人工决策的关键点有三个：

- 必须引入一个带interrupt功能的节点
- 必须人工决策后再次invoke
- graph必须带有memory

#### ii. 人工介入代码

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

#添加状态类
class State(TypedDict):
    产物:str
    是否加糖:str

#冲咖啡函数
def 冲咖啡(state):
    print("冲咖啡之前:" + str(state))
    state["产物"]="咖啡"
    print("冲咖啡之后:" + str(state))
    return state

#中断节点，里面必须包含一个interrupt
def 询问是否加糖(state):
    human_response = interrupt("")
    state["是否加糖"] = human_response
    return state

#根据人类是否加糖的反馈，选择不同分支
def 是否加糖分支(state):
    #print(state)
    if state["是否加糖"] == "是":
        return "是"
    elif state["是否加糖"] == "否":
        return "否"

#加糖函数
def 加糖(state):
    print("加糖之前:" + str(state))
    state["产物"]="加糖咖啡"
    print("加糖之后:" + str(state))
    return state


def buildGraph():
    #初始化图
    graphBuilder = StateGraph(State)
    #初始化记忆。使用人工介入必须带有记忆，否则图中断执行后无法正常继续
    checkpointer = InMemorySaver()
    #添加节点
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    graphBuilder.add_node("询问是否加糖", 询问是否加糖)
    graphBuilder.add_node("加糖", 加糖)
    #添加边
    graphBuilder.add_edge(START, "冲咖啡")
    graphBuilder.add_edge("冲咖啡", "询问是否加糖")
    graphBuilder.add_conditional_edges("询问是否加糖", 是否加糖分支,{"是":"加糖","否":END})
    graphBuilder.add_edge("加糖", END)
    #编译图
    graph = graphBuilder.compile(checkpointer=checkpointer)
    return graph

if __name__ == "__main__":
    graph = buildGraph()
    #打印图
    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")
    #调用图
    state:State = {"产物":"开水","是否加糖":""}
    config = {"configurable": {"thread_id": "some_id"}}

    #启动工作流
    state = graph.invoke(state, config)
    # 中断后，接收用户输入
    userDecision = input("先生您好，请问您的咖啡需要加糖吗？(是/否):")
    while userDecision not in {"是", "否"}:
        userDecision = input("先生您好，请问您的咖啡需要加糖吗？(是/否):")
    #使用Command函数向graph提供用户输入的数据，继续工作流
    result = graph.invoke(Command(resume=userDecision), config=config)
    print(result)
```

运行结果如下：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OWExMWUwMTVjNzIxMzc0ZDIwYTIyN2M1ZTE5NjNmM2VfODc3YjgzMGMxOTg0ZWY4NzNmMGUyMjkxOWRlODM5YmRfSUQ6NzU5MzkyMzQzMDU0MjY0MjM4Ml8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

对应的graph如下：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTNhZDExNzkxN2NkNWU3ZmExMjk0YWYyZGQ5OTJkZjBfMjJkYmVjNzdlMWY3NTU4ZjgxYWU1MGRlY2M2NzVmN2ZfSUQ6NzU5MzkyMzQzMDUyMTgwMTkxOF8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

#### iii. 小结

> 问题：
> 
>       1 怎样让图的运行中止？
> 
>       2 怎样让图继续运行？
> 
> 实操：
> 
>       1 实现LangGraph中的人工介入

### g. 子图

#### i. 完整案例

现在整个项目已经有了完整的处理流程，整体代码如下：

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver
from tools import showGraph

#合并温度值的方式，取其大者
def updateTempreture(left, right):
    return max(left, right)

#合并产物的方式，优先取工序靠后的产物
def updateProduct(left,right):
    if left=="加糖咖啡" or right == "加糖咖啡":
        return "加糖咖啡"
    elif left=="咖啡" or right == "咖啡":
        return "咖啡"
    elif left=="开水" or right == "开水":
        return "开水"
    elif left=="温水" or right == "温水":
        return "温水"
    else:
        return "凉水"

#合并咖啡固体的方式，优先取工序靠后的产物
def updateSolid(left,right):
    if left=="咖啡粉" or right == "咖啡粉":
        return "咖啡粉"
    else:
        return "咖啡豆"
def updateSugur(left,right):
    if left=="是" or right == "是":
        return "是"
    else:
        return "否"

#添加状态类
class State(TypedDict):
    水温: Annotated[int,updateTempreture]
    产物:Annotated[str,updateProduct]
    咖啡固体:Annotated[str,updateSolid]
    是否加糖:Annotated[str,updateSugur]

#磨咖啡豆函数
def 磨咖啡豆(state):
    print("*" * 80)
    print("磨咖啡豆之前:" + str(state))
    state["咖啡固体"] = "咖啡粉"
    print("磨咖啡豆之后:" + str(state))
    return state

#烧水函数
def 烧水(state):
    print("*"*80)
    print("烧水之前:"+str(state))
    state["产物"] = "没烧开的水"
    state["水温"] = state["水温"]+10
    if state["水温"]>100:
        state["水温"] = 100
        state["产物"] = "开水"
    print("烧水之后:" + str(state))
    return state

#按照温度处理水的条件函数
def 按温度处理水(state):
    if state["水温"]== 100:
        return "水烧开了"
    else:
        return "水没开"

#得到开水函数，注意这个函数没有实际作用，只是便于展示整个流程
def 得到开水(state):
    return state

#冲咖啡函数
def 冲咖啡(state):
    print("冲咖啡之前:" + str(state))
    state["产物"]="咖啡"
    print("冲咖啡之后:" + str(state))
    return state

#中断节点，里面必须包含一个interrupt
def 询问是否加糖(state):
    human_response = interrupt("")
    state["是否加糖"] = human_response
    return state

#根据人类是否加糖的反馈，选择不同分支
def 是否加糖分支(state):
    #print(state)
    if state["是否加糖"] == "是":
        return "是"
    elif state["是否加糖"] == "否":
        return "否"

#加糖函数
def 加糖(state):
    print("加糖之前:" + str(state))
    state["产物"]="加糖咖啡"
    print("加糖之后:" + str(state))
    return state

def buildGraph5():
    # 初始化图
    graphBuilder = StateGraph(State)
    checkpointer = InMemorySaver()

    graphBuilder.add_node("heat water", 烧水)
    graphBuilder.add_node("get boil water", 得到开水)
    graphBuilder.add_node("磨咖啡豆", 磨咖啡豆)
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    graphBuilder.add_node("询问是否加糖", 询问是否加糖)
    graphBuilder.add_node("加糖", 加糖)

    graphBuilder.add_edge(START, "磨咖啡豆")
    graphBuilder.add_edge(START, "heat water")
    graphBuilder.add_conditional_edges("heat water", 按温度处理水, {"水烧开了": "get boil water", "水没开": "heat water"})
    graphBuilder.add_edge(["get boil water","磨咖啡豆"], "冲咖啡")
    graphBuilder.add_edge("冲咖啡", "询问是否加糖")
    graphBuilder.add_conditional_edges("询问是否加糖", 是否加糖分支,{"是":"加糖","否":END})
    graphBuilder.add_edge("加糖", END)

    graph = graphBuilder.compile(checkpointer=checkpointer)
    return graph


if __name__ == "__main__":
    graph = buildGraph5()
    #打印图
    showGraph.showGraphInCode(graph, "复杂流程.jpg")

   
    #初始化状态
    state:State = {"水温": 58,"产物":"凉水","咖啡固体":"咖啡豆"}
    #添加config
    config = {"configurable": {"thread_id": "some_id"}}
    #调用图
    state = graph.invoke(state, config)
    #中断后，接收用户输入
    userDecision = input("先生您好，请问您的咖啡需要加糖吗？(是/否):")
    while userDecision not in {"是", "否"}:
        userDecision = input("先生您好，请问您的咖啡需要加糖吗？(是/否):")
    #使用Command函数向graph提供用户输入的数据，继续工作流
    result = graph.invoke(Command(resume=userDecision), config=config)
    print(result)"""
```

运行结果如下：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=N2UyZDg3YzBiNTE0YmQ4YjFiNTI3ZGQ0MzJhOWFmNTNfMGMxM2Q0MWQ2Nzk0ZTczMWI1ZDFmMjU3ZDAyMjExN2NfSUQ6NzU5MzkyMzQzMDY1NTk1NDExMV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

对应的graph如下：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTM1Yjk1NjdlMzJjZDhlNmRhNzlmMjc3NDRmYTg3NzBfYWFhZGFkMjcxZTM4NDY3ZjBlMGMyYTc4ZGVhMTdlY2NfSUQ6NzU5MzkyMzQzMDAzOTQ3MzM1NV8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)



#### ii. 划分子图

随着项目演进，功能不断增多，用单个graph已经太过复杂，而且也不便于调试。

有必要把部分内聚性强的功能块独立出来，做成子图

- 烧开水子图
- 询问加糖子图
- 总图

示例代码如下：

```Python
from langgraph.graph import START,StateGraph,  END
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver
from tools import showGraph

#合并温度值的方式，取其大者
def updateTempreture(left, right):
    return max(left, right)

#合并产物的方式，优先取工序靠后的产物
def updateProduct(left,right):
    if left=="加糖咖啡" or right == "加糖咖啡":
        return "加糖咖啡"
    elif left=="咖啡" or right == "咖啡":
        return "咖啡"
    elif left=="开水" or right == "开水":
        return "开水"
    elif left=="温水" or right == "温水":
        return "温水"
    else:
        return "凉水"

#合并咖啡固体的方式，优先取工序靠后的产物
def updateSolid(left,right):
    if left=="咖啡粉" or right == "咖啡粉":
        return "咖啡粉"
    else:
        return "咖啡豆"
def updateSugur(left,right):
    if left=="是" or right == "是":
        return "是"
    else:
        return "否"

#添加状态类
class State(TypedDict):
    水温: Annotated[int,updateTempreture]
    产物:Annotated[str,updateProduct]
    咖啡固体:Annotated[str,updateSolid]
    是否加糖:Annotated[str,updateSugur]

#磨咖啡豆函数
def 磨咖啡豆(state):
    print("*" * 80)
    print("磨咖啡豆之前:" + str(state))
    state["咖啡固体"] = "咖啡粉"
    print("磨咖啡豆之后:" + str(state))
    return state

#烧水函数
def 烧水(state):
    print("*"*80)
    print("烧水之前:"+str(state))
    state["产物"] = "没烧开的水"
    state["水温"] = state["水温"]+10
    if state["水温"]>100:
        state["水温"] = 100
        state["产物"] = "开水"
    print("烧水之后:" + str(state))
    return state

#按照温度处理水的条件函数
def 按温度处理水(state):
    if state["水温"]== 100:
        return "水烧开了"
    else:
        return "水没开"

#得到开水函数，注意这个函数没有实际作用，只是便于展示整个流程
def 得到开水(state):
    return state

#冲咖啡函数
def 冲咖啡(state):
    print("冲咖啡之前:" + str(state))
    state["产物"]="咖啡"
    print("冲咖啡之后:" + str(state))
    return state

#中断节点，里面必须包含一个interrupt
def 询问是否加糖(state):
    human_response = interrupt("")
    state["是否加糖"] = human_response
    return state

#根据人类是否加糖的反馈，选择不同分支
def 是否加糖分支(state):
    #print(state)
    if state["是否加糖"] == "是":
        return "是"
    elif state["是否加糖"] == "否":
        return "否"

#加糖函数
def 加糖(state):
    print("加糖之前:" + str(state))
    state["产物"]="加糖咖啡"
    print("加糖之后:" + str(state))
    return state

def buildGraph6():
    #烧水子图
    # 初始化图
    heatWaterSubGraphBuilder = StateGraph(State)
    # 添加节点
    heatWaterSubGraphBuilder.add_node("heat water", 烧水)
    heatWaterSubGraphBuilder.add_node("get boil water", 得到开水)
    # 添加边
    heatWaterSubGraphBuilder.add_edge(START, "heat water")
    heatWaterSubGraphBuilder.add_conditional_edges("heat water", 按温度处理水,{"水烧开了": "get boil water", "水没开": "heat water"})
    # 编译图
    heatWaterSubGraph = heatWaterSubGraphBuilder.compile()

    #加糖子图
    # 初始化图
    addSugurSubGraphBuilder = StateGraph(State)
    # 初始化记忆。使用人工介入必须带有记忆，否则图中断执行后无法正常继续
    checkpointer = InMemorySaver()
    # 添加节点
    addSugurSubGraphBuilder.add_node("询问是否加糖1", 询问是否加糖)
    addSugurSubGraphBuilder.add_node("加糖", 加糖)
    # 添加边
    addSugurSubGraphBuilder.add_edge(START,"询问是否加糖1")
    addSugurSubGraphBuilder.add_conditional_edges("询问是否加糖1", 是否加糖分支, {"是": "加糖", "否": END})
    # 编译图，需要带有记忆
    addSugurSubGraph = addSugurSubGraphBuilder.compile(checkpointer=checkpointer)

    #总图
    # 初始化图
    graphBuilder = StateGraph(State)
    # 添加节点
    #注意这里把子图加入总图的方式，是把编译好的子图作为一个节点加入进来
    graphBuilder.add_node("得到热水子图",heatWaterSubGraph)
    graphBuilder.add_node("磨咖啡豆", 磨咖啡豆)
    graphBuilder.add_node("冲咖啡", 冲咖啡)
    graphBuilder.add_node("加糖子图1", addSugurSubGraph)
    # 添加边
    graphBuilder.add_edge(START,"得到热水子图")
    graphBuilder.add_edge(START, "磨咖啡豆")
    graphBuilder.add_edge(["得到热水子图","磨咖啡豆"],"冲咖啡")
    graphBuilder.add_edge("冲咖啡","加糖子图1")
    # 编译图,需要带有记忆
    graph = graphBuilder.compile(checkpointer=checkpointer)
    return heatWaterSubGraph,addSugurSubGraph,graph


if __name__ == "__main__":
    heatWaterSubGraph,addSugurSubGraph,graph = buildGraph6()
    #打印图
    showGraph.showGraphInCode(heatWaterSubGraph,"烧热水子图.jpg")
    showGraph.showGraphInCode(addSugurSubGraph,"加糖子图.jpg")
    showGraph.showGraphInCode(graph,"总图.jpg")

    #初始化状态
    state:State = {"水温": 58,"产物":"凉水","咖啡固体":"咖啡豆"}
    #添加config
    config = {"configurable": {"thread_id": "some_id"}}
    #调用图
    state = graph.invoke(state, config)
    #中断后，接收用户输入
    userDecision = input("先生您好，请问您的咖啡需要加糖吗？(是/否):")
    while userDecision not in {"是", "否"}:
        userDecision = input("先生您好，请问您的咖啡需要加糖吗？(是/否):")
    #使用Command函数向graph提供用户输入的数据，继续工作流
    result = graph.invoke(Command(resume=userDecision), config=config)
    print(result)
```

运行结果如下：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OWY4ODI1MzUwMGQxMWYxMzhkOGYwOTkwNDJhMjJkYzhfYTc2OGU0Yzg3MzAxZGVhNjdkOGFhYjY5MmQwN2U1YmVfSUQ6NzU5MzkyMzQzMDgxNTMwNDg5OF8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

对应的graph如下：

                                                                    烧热水子图

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OWQyNWYzNWIxMzdiMjIzYjE2ZmM4NDJiZTQxMjBlZTdfOWJmMjRkMWY1ZGViYjgxOWE2NjRhYzJjZWQ1Nzg2NzhfSUQ6NzU5MzkyMzQzMDc2OTEzNDc4MV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

                                                                  

                                                                       加糖子图

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OGQ2YTRjODZjMTRkNTdlZDg2MzE5NDFjMTkzMjZhYzVfNDQ0MDNiMWNjNmQ2NmRhNzVlNDg2MWExMzIwNWRiMDZfSUQ6NzU5MzkyMzQzMjM0MTkwMDUxMV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)



                                                                    总图

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZmVkNmM2ZGYyYjFlN2NlOGQ0MzFjNzVkMTNmNjI4OThfYzYwMjM0YmJiMjFiMmJlNTM5M2U4ZDE5ZmFhMjQ3NjJfSUQ6NzU5MzkyMzQyOTI4NDU2NDE2OV8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

#### iii. 小结

> 问题：
> 
>       1 为什么要划分子图
> 
>       2 LangGraph中怎样把子图纳入总图中使用的？
> 
> 实操：
> 
>       1 实现LangGraph中的子图

### h. 小结

> 问题：
> 
>         1 怎样控制各个并行结构都运行完之后再运行合并节点？
> 
>         2 怎样暂停图的运行
> 
>         3  怎样继续运行图？
> 
>         4 为什么要划分子图
> 
>         5  LangGraph中怎样把子图纳入总图中使用的？
> 
> 实操：
> 
>         1 练习LangGraph中的分支结构
> 
>         2 练习LangGraph中的循环结构
> 
>         3 练习LangGraph中的并行结构
> 
>         4 练习LangGraph中的人工介入
> 
>         5 练习LangGraph中的子图
> 
>         

## 4. 项目实战

### a. 学习目标

能够使用LangGraph完成新车型设计报告

### b. 项目需求

#### i. 背景

近年来，汽车行业竞争愈发激烈，各厂商不断推出新车型，以期占领更大的市场份额，尤其是正对年轻女性这个细分市场，竞争已经到了白热化的程度。设计新车型是一项智力和经验密集型的工作，需要非常专业的设计人才，要求汽车行业的竞争格局、高新技术应用、产业链成本及产出等领域都具有深刻的理解。在以前，新车型都是由专家组设计的，这种方式有几个问题：

- 人力资源瓶颈：需要设计和评估大量新车型，企业没有这么多的专家储备，导致新车型的设计和评估工作一再推迟。
- 迭代周期长：需要对各种技术方案的组合进行反复论证，优中选优，需要大量的实践。
- 人力成本居高不下：行业专家是企业的核心人才，薪资远高于一般员工，这种设计模式会导致高昂的设计成本。
- 思维惯性导致设计固化：专家对行业的认知深刻，也会导致思维惯性很强，设计出的方案缺少新意，尤其是对新兴趋势反应滞后。

#### ii. 需求

随着大模型的不断发展，使用大模型进行新车型设计的客观条件也渐渐成熟。凯瑞汽车旗下维多利亚品牌（化名）首先提出了这方面的需求。核心要求有以下几点：

- 搭建全面的专家知识库，并要求快速更新，防止行业知识不全面或者滞后造成的影响。
- 搭建基于大模型的车型设计系统，要求能够提供完整的车型设计方案，设计新车型的时间不大于10分钟。
- 搭建新车型评估和初筛系统，从6个方面对设计出的新车型进行初步评估。

#### iii. 车型设计方案的具体要求

维多利亚品牌在多年的车型设计工作中总结了一套行之有效的设计模式，要求设计方案至少包含以下9个部分

- 方案的背景和理念
- 市场的发展趋势分析
- 客户群体与使用场景分析
- 技术方案和针对细分市场的定制
- 竞品分析和差异化竞争优势分析
- 产品卖点
- 定价策略
- 海外市场
- 销量预估

### c. 方案选型

<sheet sheet-id="jJ6wTl" token="CDKOszgschVb5ot8gtAcynbnnce"></sheet>

### d. 方案一（小参数量模型+整体输出）

#### i. 试验一

首先提供一份代码，满足基本功能：

- 调用大模型完成设计方案
- 引入参考资料
- 说明章节安排

```Python
from langchain_ollama import ChatOllama
from a_gather_infomation import getInfomation

llm = ChatOllama(model="qwen2.5:7b")

state = {}
state = getInfomation(state)
prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【竞品分析】和【女性汽车市场发展趋势】，结合你自己的思考，完成一份新车型设计方案。该方案输出的形式要遵循【章节安排】。

         【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"] + """

        【竞品分析】

        """ + state["competitorStatus"] + """
        
        【章节安排】
        第一章 新车型的设计背景和理念
        第二章 市场趋势分析
        第三章 用户人群分析与使用场景
        第四章 技术方案和细分市场定制
        第五章 竞品分析与差异化竞争优势
        第六章 产品卖点
        第七章 定价策略
        第八章 海外市场
        第九章 销量预估"""

result = llm.invoke(prompt)

print(result.content)
```

输出结果

<cite doc-id="H5XndL2bzo8OgFx45AacWxb8nJh" file-type="docx" title="designer1_1_result" token="H5XndL2bzo8OgFx45AacWxb8nJh" type="doc"></cite>

主要问题有两个：

- 新车型没有名称
- 篇幅太短了

#### ii. 试验二

需要增加车型名称，尝试过直接在第一行提示词的后面，但是这种方法无法确定车型名称首次出现的位置。我们需要在第一章就必须出现，所以直接在章节安排的第一章后面增加一个注释。

```Python
from langchain_ollama import ChatOllama
from a_gather_infomation import getInfomation

llm = ChatOllama(model="qwen2.5:7b")

state = {}
state = getInfomation(state)
prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【竞品分析】和【女性汽车市场发展趋势】，结合你自己的思考，完成一份新车型设计方案。该方案输出的形式要遵循【章节安排】。

         【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"] + """

        【竞品分析】

        """ + state["competitorStatus"] + """

        【章节安排】
        第一章 新车型的设计背景和理念 #这一章节里必须给新车型起一个符合女性汽车市场的名字
        第二章 市场趋势分析
        第三章 用户人群分析与使用场景
        第四章 技术方案和细分市场定制
        第五章 竞品分析与差异化竞争优势
        第六章 产品卖点
        第七章 定价策略
        第八章 海外市场
        第九章 销量预估"""

result = llm.invoke(prompt)

print(result.content)
```

输出结果：

<cite doc-id="LziSdLh3ao0nNmxfxODcuXz7nUf" file-type="docx" title="designer1_2_result" token="LziSdLh3ao0nNmxfxODcuXz7nUf" type="doc"></cite>

已经成功地添加了车型名称，下面设法增加篇幅

#### iii. 试验三

前面的设计方案太简单了，篇幅不够长，每章内容也不够详细，无法应用在生产环境。

尝试增加设计方案的篇幅，直接在提示词后面添加字数要求（10000字），但是第一次生成并不成功，生成的长度远小于要求的字数。为什么会出现这种结果？

在ChatOllama里添加参数num_predict=10000后，再次试验，发现生成的文档基本达到了要求的字数。

```Python
from langchain_ollama import ChatOllama
from a_gather_infomation import getInfomation

llm = ChatOllama(model="qwen2.5:7b", num_predict=10000)

state = {}
state = getInfomation(state)
prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【竞品分析】和【女性汽车市场发展趋势】，结合你自己的思考，完成一份新车型设计方案。该方案输出的形式要遵循【章节安排】，全文在10000字左右。

         【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"] + """

        【竞品分析】

        """ + state["competitorStatus"] + """

        【章节安排】
        第一章 新车型的设计背景和理念 #这一章节里必须给新车型起一个符合女性汽车市场的名字
        第二章 市场趋势分析
        第三章 用户人群分析与使用场景
        第四章 技术方案和细分市场定制
        第五章 竞品分析与差异化竞争优势
        第六章 产品卖点
        第七章 定价策略
        第八章 海外市场
        第九章 销量预估"""

result = llm.invoke(prompt)

print(result.content)
```

输出结果：

<cite doc-id="YOjKdv19zoKA0qx2WQ9cNLa9nrb" file-type="docx" title="designer1_3_result" token="YOjKdv19zoKA0qx2WQ9cNLa9nrb" type="doc"></cite>

篇幅确实增加了，但是我们需要的九章内容仍然不够详细，后面产生了很多不需要的章节。

看来小参数量模型不太适合生成较长的文本。

### e. 方案二（大参数量模型+整体输出）

为了保证模型效果，这里调用了硅基流动的DeepSeek-V3满血版，调用公开大模型服务有以下几个要点：

- 构建一个新的类，继承自Runnable
- 公共大模型的地址和密钥
- invoke方法，实质上是一次http调用，注意输入数据的格式
- 实例化
- 用invoke方法调用模型

示例代码如下：

```Python
from langchain_core.runnables import Runnable
from a_gather_infomation import getInfomation
from typing import Dict, Optional

class CustomModel(Runnable):
    def __init__(self, model_endpoint: str, api_key: str):
        self.endpoint = model_endpoint
        self.api_key = api_key

    def invoke(self, prompt: str, modelName:str="deepseek-ai/DeepSeek-V3",maxTokens:int=10000,tempreture=0.6,config: Optional[Dict] = None) -> Dict:
        """调用自定义模型API"""
        import requests

        headers = {"Authorization": f"Bearer {self.api_key}",
                   "Content-Type": "application/json"}
        payload = {
            "model":modelName,
            "messages": [{"role": "user", "content": prompt}],
            "temperature":tempreture,
            "max_tokens": maxTokens
        }

        response = requests.post(self.endpoint, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

llm = CustomModel(
        model_endpoint="https://api.siliconflow.cn/v1/chat/completions",
        api_key="sk-szevaazcpwllljvxlyddutjsjzeexsptgtkfmqesswqoldvq"
    )

state = {}
state = getInfomation(state)
prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【竞品分析】和【女性汽车市场发展趋势】，结合你自己的思考，完成一份新车型设计方案。该方案输出的形式要遵循【章节安排】，全文在10000字左右。

         【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"] + """

        【竞品分析】

        """ + state["competitorStatus"] + """

        【章节安排】
        第一章 新车型的设计背景和理念 #这一章节里必须给新车型起一个符合女性汽车市场的名字
        第二章 市场趋势分析
        第三章 用户人群分析与使用场景
        第四章 技术方案和细分市场定制
        第五章 竞品分析与差异化竞争优势
        第六章 产品卖点
        第七章 定价策略
        第八章 海外市场
        第九章 销量预估"""

result = llm.invoke(prompt)

print(result)
```

生成结果：

<cite doc-id="TVJqdEqAmoghzWx3PcjcIAQinkc" file-type="docx" title="designer2_result" token="TVJqdEqAmoghzWx3PcjcIAQinkc" type="doc"></cite>

明显比方案一更好，但是业务方反应对各章节的细节（规模、详细内容等）控制能力比较弱，不便于后续业务调整。

### e. 方案三（大参数量模型+分章节输出）

在方案二上做了加大幅度的改动，每个章节单独输出，可以非常准确地控制每章的篇幅和细节。最后把结果拼装在一起。注意：这里每章的生成内容互不干扰，可以并行

```Python
from langchain_core.runnables import Runnable
from typing import Dict, Optional
from langgraph.graph import StateGraph, START
from typing_extensions import TypedDict
from typing import Annotated
import operator
from a_gather_infomation import getInfomation


def updateReceiveDate(left, right):
    if len(left) > 0:
        return left
    else:
        return right


class State(TypedDict):
    femaleMarketTrend: Annotated[str, updateReceiveDate]
    victoriaStatus: Annotated[str, updateReceiveDate]
    competitorStatus: Annotated[str, updateReceiveDate]

    basicSettings: Annotated[str, updateReceiveDate]
    # 背景，目标，理念
    chapter1: Annotated[str, operator.add]
    # 市场趋势分析
    chapter2: Annotated[str, operator.add]
    # 用户人群分析与使用场景
    chapter3: Annotated[str, operator.add]
    # 技术方案+细分市场定制
    chapter4: Annotated[str, operator.add]
    # 竞品分析与差异化竞争
    chapter5: Annotated[str, operator.add]
    # 产品卖点
    chapter6: Annotated[str, operator.add]
    # 定价策略
    chapter7: Annotated[str, operator.add]
    # 海外市场
    chapter8: Annotated[str, operator.add]
    # 销量预估
    chapter9: Annotated[str, operator.add]

    design: Annotated[str, updateReceiveDate]


class CustomModel(Runnable):
    def __init__(self, model_endpoint: str, api_key: str):
        self.endpoint = model_endpoint
        self.api_key = api_key

    def invoke(self, prompt: str, modelName: str = "deepseek-ai/DeepSeek-V3", maxTokens: int = 3000, tempreture=0.6,
               config: Optional[Dict] = None) -> Dict:
        """调用自定义模型API"""
        import requests

        headers = {"Authorization": f"Bearer {self.api_key}",
                   "Content-Type": "application/json"}
        payload = {
            "model": modelName,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": tempreture,
            "max_tokens": maxTokens
        }

        response = requests.post(self.endpoint, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


llm = CustomModel(
    model_endpoint="https://api.siliconflow.cn/v1/chat/completions",
    api_key="sk-szevaazcpwllljvxlyddutjsjzeexsptgtkfmqesswqoldvq"
)


def generateChapter1(state):
    # 背景，理念
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【女性汽车市场发展趋势】，结合你自己的思考，完成新车型设计方案的第一章“一、设计背景和理念”，说明新车型的设计背景和理念。各级标题使用markdown格式。600字以内。

        【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"]
    result = llm.invoke(prompt)
    # print("背景和设计理念："+result)
    state["chapter1"] = result
    return state


def generateChapter2(state):
    # 市场趋势分析
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【女性汽车市场发展趋势】、【竞品资料】，结合你自己的思考，完成新车型设计方案的第二章“二、市场趋势分析”，说明当前女性汽车市场的趋势。各级标题使用markdown格式。800字以内。

        【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"] + """

        【竞品资料】
        """ + state["competitorStatus"]
    result = llm.invoke(prompt)
    # print("市场趋势分析：" + result)
    state["chapter2"] = result
    return state


def generateChapter3(state):
    # 用户人群分析和使用场景
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【女性汽车市场发展趋势】，结合你自己的思考，完成新车型设计方案的第三章“三、目标客户与场景”，分析用户人群特点和产品的适用场景。各级标题使用markdown格式。800字以内。

        【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"]
    result = llm.invoke(prompt)
    # print("用户人群分析和使用场景：" + result)
    state["chapter3"] = result
    return state


def generateChapter4(state):
    # 技术方案
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【女性汽车市场发展趋势】，结合你自己的思考，完成新车型设计方案的第四章“四、技术方案”，具体说明新车型的技术方案，尤其是针对细分市场的定制特性。各级标题使用markdown格式。1500字以内。

        【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"]
    result = llm.invoke(prompt)
    # print("技术方案：" + result)
    state["chapter4"] = result
    return state


def generateChapter5(state):
    # 竞品分析与差异化竞争
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【竞品资料】，结合你自己的思考，完成新车型设计方案的第五章“五、竞品分析”，分析竞品的特性和销售情况，并分析新车型的差异化竞争优势。各级标题使用markdown格式。1500字以内。

        【竞品资料】
        """ + state["competitorStatus"]
    result = llm.invoke(prompt)
    # print("竞品分析：" + result)
    state["chapter5"] = result
    return state


def generateChapter6(state):
    # 产品卖点
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【女性汽车市场发展趋势】、【竞品资料】，结合你自己的思考，完成新车型设计方案的第六章“六、产品卖点”，详细说明在当前市场趋势下，与竞品相比，新车型的卖点。各级标题使用markdown格式。800字以内。

         【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"] + """

        【竞品资料】
        """ + state["competitorStatus"]
    result = llm.invoke(prompt)
    # print("产品卖点：" + result)
    state["chapter6"] = result
    return state


def generateChapter7(state):
    # 定价策略
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【竞品资料】，结合你自己的思考，完成新车型设计方案的第七章“七、定价策略”，制定一个详细的新车型定价策略。各级标题使用markdown格式。800字以内。

        【竞品资料】
        """ + state["competitorStatus"]
    result = llm.invoke(prompt)
    # print("定价策略：" + result)
    state["chapter7"] = result
    return state


def generateChapter8(state):
    # 海外市场
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【女性汽车市场发展趋势】，结合你自己的思考，完成新车型设计方案的第八章“八、海外市场”，详细分析新车型在海外市场需要做哪些调整，可能的表现。各级标题使用markdown格式。800字以内。

         【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"]
    result = llm.invoke(prompt)
    # print("海外市场：" + result)
    state["chapter8"] = result
    return state


def generateChapter9(state):
    # 销量预估
    prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【女性汽车市场发展趋势】、【竞品资料】，结合你自己的思考，完成新车型设计方案的第九章“九、销量预估”，预估新车型的销量。各级标题使用markdown格式。200字以内。

         【女性汽车市场发展趋势】
        """ + state["femaleMarketTrend"] + """

        【竞品资料】
        """ + state["competitorStatus"]
    result = llm.invoke(prompt)
    # print("定价策略：" + result)
    state["chapter9"] = result
    return state


def merge(state):
    state["design"] = state["chapter1"] + "\n" + \
                      state["chapter2"] + "\n" + \
                      state["chapter3"] + "\n" + \
                      state["chapter4"] + "\n" + \
                      state["chapter5"] + "\n" + \
                      state["chapter6"] + "\n" + \
                      state["chapter7"] + "\n" + \
                      state["chapter8"] + "\n" + \
                      state["chapter9"]
    return state


def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("getInfomation", getInfomation)
    graphBuilder.add_node("generateChapter1", generateChapter1)
    graphBuilder.add_node("generateChapter2", generateChapter2)
    graphBuilder.add_node("generateChapter3", generateChapter3)
    graphBuilder.add_node("generateChapter4", generateChapter4)
    graphBuilder.add_node("generateChapter5", generateChapter5)
    graphBuilder.add_node("generateChapter6", generateChapter6)
    graphBuilder.add_node("generateChapter7", generateChapter7)
    graphBuilder.add_node("generateChapter8", generateChapter8)
    graphBuilder.add_node("generateChapter9", generateChapter9)
    graphBuilder.add_node("merge", merge)

    graphBuilder.add_edge(START, "getInfomation")
    graphBuilder.add_edge("getInfomation", "generateChapter1")
    graphBuilder.add_edge("getInfomation", "generateChapter2")
    graphBuilder.add_edge("getInfomation", "generateChapter3")
    graphBuilder.add_edge("getInfomation", "generateChapter4")
    graphBuilder.add_edge("getInfomation", "generateChapter5")
    graphBuilder.add_edge("getInfomation", "generateChapter6")
    graphBuilder.add_edge("getInfomation", "generateChapter7")
    graphBuilder.add_edge("getInfomation", "generateChapter8")
    graphBuilder.add_edge("getInfomation", "generateChapter9")

    graphBuilder.add_edge(
        ["generateChapter1", "generateChapter2", "generateChapter3", "generateChapter4", "generateChapter5",
         "generateChapter6", "generateChapter7", "generateChapter8", "generateChapter9"], "merge")

    graph = graphBuilder.compile()
    return graph


if __name__ == "__main__":
    graph = buildGraph()

    from tools import showGraph

    showGraph.showGraphInCode(graph, "graph.jpg")

    state: State = {}
    result = graph.invoke(state)
    print("新车型设计书  " + "*" * 80)
    print(result["design"])
```

生成结果：

<cite doc-id="J9DbdtompofKHYx1U4bcS1qUn8f" file-type="docx" title="designer3_result" token="J9DbdtompofKHYx1U4bcS1qUn8f" type="doc"></cite>

这一版的细节控制能力明显增强，但是各部分间的内容有冲突：

- 微型电动车定位（4.2米车身）与高性能版（零百5.8s）存在矛盾，前者强调经济实用，后者需要更大电池/电机配置，可能导致成本超出5万元价格带。
- 隐藏式毫米波雷达与超声波雷达误识别问题：方案未说明如何解决毫米波雷达对金属饰品（如项链）的干扰问题，可能引发新的误判风险。
- 可变形后排座椅（亲子模式）与应急尿布台存在空间冲突，展开尿布台需占用后排空间，此时无法同时使用旋转座椅功能。
- 莫兰迪色系强调低调，但"局部亮色模块"设计可能破坏整体哑光质感，与"反刻板印象"理念产生视觉冲突。
- 生理周期监测需持续收集健康数据，与"女性数据安全"条款中"避免功能外显"原则存在潜在伦理冲突。

### f. 方案四（大参数量模型+概要设计+分章节输出）

方案三已经很接近实用化了，唯一的障碍是设计方案各章中的冲突。

这里产生了一对非常尖锐的矛盾：

- 如果想要细节控制，就必须各章节单独生成，冲突就难以避免。
- 如果要避免冲突，最好一次生成。这样就无法准确控制各章节的生成内容

怎样解决这样的矛盾？

#### i. 方案细化

具体落地要分成以下几个步骤：

- 整体框架使用LangGraph构建一个总分结构
- 首先完成数据收集（行业趋势报告，竞品信息）
- 然后完成概要设计，包括车型名称、设计理念、设计思路、使用的新技术等关键信息
- 根据每个章节的具体情况，分别生成，必须遵照概要设计的内容，还可以参考行业趋势报告、竞品信息等资料。
- 各章节合并成完整的车型设计方案

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTc4ODcyNDI3NDBhZTQ3NGYxMTRiYjYyOGJmMDdkMGFfYTU1YTM0NTAwZjAyYTU0YjQ4MTI5ZGEwOGQ4OTBjNDhfSUQ6NzU5MzkyMzQzMzI0MzcyNDk4NV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### ii. 行业趋势和竞品信息收集

这里的行业趋势来自企业内部的RAG系统，竞品信息来自业务部门的关系型数据库，这里用一组函数代替这些操作。

```Python
def getVictoriaStatus():
    status = """凯瑞维多利亚2024年每月销售量"""
    return status

def getBenBenStatus():
    status = """长安奔奔E-Star是基于燃油车平台改造的“油改电”车型，续航能力（301km）低于维多利亚黑猫（351-405km），且在三电系统、安全配置等方面表现较弱。"""
    return status

def getHaiouStatus():
    status = """亚迪海鸥在销量和安全性上表现突出，最高续航405km，虽略低于维多利亚好猫的501km，但凭借比亚迪的刀片电池技术获得市场认可。维多利亚好猫则在智能化（如“咖啡”智能车控系统）和快充技术上更占优。"""
    return status

def getKaolaStatus():
    status = """北汽新能源推出的考拉品牌直接瞄准女性市场，细分至“妈妈”群体，与维多利亚的“更爱女人的汽车品牌”定位形成竞争。考拉计划通过场景化产品（如母婴出行需求）差异化竞争，"""
    return status

def getFemaleMarketTrend():
    trend = """面向女性客户的汽车品牌正从早期的“性别标签化”营销转向“需求驱动型”创新，未来将围绕精准需求洞察、技术平权设计、社群生态构建三大核心展开。以下是具体趋势分析："""
    return trend

def getInfomation(state):
    victoriaStatus = getVictoriaStatus()
    benbenStatus = getBenBenStatus()
    haiouStatus = getHaiouStatus()
    kaolaStatus = getKaolaStatus()
    femaleMarketTrend = getFemaleMarketTrend()
    state["victoriaStatus"] = victoriaStatus
    state["competitorStatus"] = benbenStatus+"\n"+haiouStatus+"\n"+kaolaStatus
    state["femaleMarketTrend"] = femaleMarketTrend
    return state
```

#### iii. 生成新车型的基本设定

为了保持整个报告中车型的基本设定一致，应该首先生成新车型的基本信息：名称、理念、配置、应用新技术等

```Plain Text
prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【竞品资料】和【女性汽车市场发展趋势】，结合你自己的思考，为维多利亚品牌设计一款新车型，规划这个新车型、技术方案和定价策略。300字以内。

    【竞品资料】
    """ + state["competitorStatus"] + """

    【女性汽车市场发展趋势】
    """ + state["femaleMarketTrend"]
```

#### iv. 根据基本设定和其他资料，完成每个章节

```Plain Text
prompt = """你是凯瑞汽车旗下维多利亚品牌的车型设计师，维多利亚品牌主要面向年轻的女性客户，根据【女性汽车市场发展趋势】和【新车型基本设定】，结合你自己的思考，完成新车型设计方案的第一章“一、设计背景和理念”，说明新车型的设计背景和理念。各级标题使用markdown格式。600字以内。

    【女性汽车市场发展趋势】
    """ + state["femaleMarketTrend"]+"""
    
    【新车型基本设定】
    
    """+state["basicSettings"]
```

#### v. 合并产出最终

```Python
def merge(state):
    state["design"]=state["chapter1"]+"\n"+ \
                    state["chapter2"]+"\n"+ \
                    state["chapter3"] + "\n" + \
                    state["chapter4"] + "\n" + \
                    state["chapter5"] + "\n" + \
                    state["chapter6"] + "\n" + \
                    state["chapter7"] + "\n" + \
                    state["chapter8"] + "\n" + \
                    state["chapter9"]
    return state
```

#### vi. 设置和编译图

```SQL
def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("generateBasicSettings", generateBasicSettings)
    graphBuilder.add_node("getInfomation",getInfomation)
    graphBuilder.add_node("generateChapter1",generateChapter1)
    graphBuilder.add_node("generateChapter2", generateChapter2)
    graphBuilder.add_node("generateChapter3", generateChapter3)
    graphBuilder.add_node("generateChapter4", generateChapter4)
    graphBuilder.add_node("generateChapter5", generateChapter5)
    graphBuilder.add_node("generateChapter6", generateChapter6)
    graphBuilder.add_node("generateChapter7", generateChapter7)
    graphBuilder.add_node("generateChapter8", generateChapter8)
    graphBuilder.add_node("generateChapter9", generateChapter9)
    graphBuilder.add_node("merge", merge)

    graphBuilder.add_edge(START, "getInfomation")
    graphBuilder.add_edge("getInfomation", "generateBasicSettings")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter1")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter2")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter3")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter4")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter5")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter6")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter7")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter8")
    graphBuilder.add_edge("generateBasicSettings", "generateChapter9")
 graphBuilder.add_edge(["generateChapter1","generateChapter2","generateChapter3","generateChapter4","generateChapter5","generateChapter6","generateChapter7","generateChapter8","generateChapter9"], "merge")

    graph = graphBuilder.compile()
    return graph
```

#### vii. 程序入口

```Python
if __name__ == "__main__":
    graph = buildGraph()

    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")

    state: State = {}
    result = graph.invoke(state)
    print("新车型设计书  " + "*" * 80)
    print(result["design"])
```

#### viii . 最终结果

最终生成的结果是一份完整的新车型设计书，内容比较长，下面的截图只展示开头和结尾，详细内容可以查看 <cite doc-id="XT7idNLnoo65gPxfjcXcTr9LnSc" file-type="docx" title="新车型设计说明书" token="XT7idNLnoo65gPxfjcXcTr9LnSc" type="doc"></cite>

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YzUwZWYxZjAyNjQ1Y2FhMmNiNTU4NDBkZDI4ODA5NWNfMWM1MWQ2Nzg3OWNhNzA5NGVjNzA4MDI0MzE0ZWMyZmVfSUQ6NzU5MzkyMzQzMzI5NDA4OTQzNV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODU3NmVkNjYyNTg1MjBlYzAxNjU3NzNjMzYzMjBiZjBfOTk4MmZlMTkzNDI0YzE4ZjhmZGZmNmUxMTczOWU5MzZfSUQ6NzU5MzkyMzQzMTg0Mjg0Mzg2OF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZDQ2NWMyMzU2MDMyMDRkOTk3NjcxNTJlNzFiYjZkNDJfYmNiZjE1MzBiM2VjOGJmYTM5NTYwN2YzNTg1NjViZjFfSUQ6NzU5MzkyMzQzMjQzODUxNjkzOV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

### g. LangSmith监控

#### i. 什么是LangSmith

LangSmith是LangChain生态系统中的开发者平台，专注于大语言模型（LLM）应用的开发、调试、测试和监控。

官方文档：https://docs.smith.langchain.com/?\_gl=1\*uc8w44\*\_gcl_au\*NzEzMTc1OTkyLjE3NDg2NjQ4MTU.\*\_ga\*MjA1MzMzODYwNS4xNzUyODk1ODU2\*\_ga_47WX3HKKY2\*czE3NTI5Nzk5NDYkbzUkZzEkdDE3NTI5ODAyMDQkajckbDAkaDA.

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MmU3NzJhYjZiMDBjY2YwMDRiODk4YzVmODRlZmRhZDRfMWM3NjU2MzgxYzRiY2RiYzE2ZjY5NDg2M2I0MWY1N2NfSUQ6NzU5MzkyMzQzMjUwNTU3NjYyOF8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

#### ii. 注册和登录

注册网址：https://smith.langchain.com/

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OTU4ZmFhY2NhNDAwMmE2NWRhNTFmZWFjYTc5MjhiZjlfYWE2MTBjOTg2YmZlYTJkOTAzODA3ZWYxYjgwZTU4MjRfSUQ6NzU5MzkyMzQzMzY5MjQzMzYxMF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

可以使用邮箱注册

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODIyMWI0NDQyNjAyZTlkZmM3OTdiNGU5NDc1NjBjYjRfNzlkZjYxY2EwMDFkN2FmNDk1YjZiNGFhM2VkMTlmYTNfSUQ6NzU5MzkyMzQzNTIxOTE5MzA1OF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

登录

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MmMwZTczMjVjMmE3ZmJjODZhODdlM2JhYmIxMDkwM2ZfNzY1M2JmODY1YjRlZWQ4MzllMjYxZjg5NTFlMDcyODRfSUQ6NzU5MzkyMzQzNDgxNjUwNzA2OV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

登陆后进入操作界面

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTVmZDI3ZmY3ZGI3ZTEyNGE2YmNkNDNlOTA2YjY1OWJfMmUzNWI2ZTAwNmZhNzcxOWI2OGZmYzQ3ZjYyNDVhNmRfSUQ6NzU5MzkyMzQzNDQxMzg1MzkyMl8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iii. 创建项目

首先进入项目列表页面

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTM2MDgwNjI2NTAxOGY3ZTdlNGI3ZTVjYTdiNmRjZTZfN2QxNjI5ZTNmZjYwMTEwM2ZiOTU1MTQ4N2JjM2U2NGNfSUQ6NzU5MzkyMzQzMzc4OTA4MjgxOF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

新建项目

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZWIzN2E4OWFiNTFkNmI4Mjk2N2IyN2JlMDg3NzEwMDFfNWZmMTdhMjFiZjdmNWJmNTIwM2MzM2RiNGIwNjg0ZjlfSUQ6NzU5MzkyMzQzNDA5NTE2ODcwMV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

创建项目细节

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzAwYmVlNWY3MDM5ZWEzODA4ZjNhODY4YmZmMGY4ZDRfMTI3YTRkMjhlMDJiNzI5YTE2ZWVkNzZkYTliZjdlNTlfSUQ6NzU5MzkyMzQzMzAwODg5MzE1M18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### iv. 使用LangSmith监控测试项目

注意，LangSmith里新建的项目是看不到的，至少运行一次才能在项目列表里看到。

现在开始监控一个新项目

- 引入traceable
- 引入环境变量
- 在调用方法上增加@traceable装饰器

```Python
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
import os
from langsmith import traceable

os.environ['LANGSMITH_TRACING']='true'
os.environ['LANGSMITH_ENDPOINT']='https://api.smith.langchain.com'
#os.environ['LANGSMITH_API_KEY']='<your-langsmith-api-key>'
#os.environ['LANGSMITH_PROJECT']='default'

os.environ['LANGSMITH_API_KEY']='<your-langsmith-api-key>'
os.environ['LANGSMITH_PROJECT']='test1'
os.environ['OPENAI_API_KEY']='<your-openai-api-key>'

agent = create_react_agent(
    model=ChatOllama(model="qwen2.5:7b"),
    tools=[],
    prompt=""
)

@traceable
def callAgent():
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "你是谁？"}]}
    )
    print(result["messages"][-1].content)


callAgent()
```

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NjdjYmFlZDljZGY3ZGIzMTNhNGQ4Y2ZkMTA5ZDMzNDFfMDg0YmQxOGU2ODk4ZjBjMWJjYmNiM2ZkNTg2NjY2MDNfSUQ6NzU5MzkyMzQzMjEzNjQ2MTUzM18xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

点击项目，进入项目记录页面，列出该项目的所有调用

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YzYzMDE2NzVmMTNjNmYxMjQzMzdlNDQwM2JhZDBkYjNfNTgzNmM4Y2EwZDBlMDRjNTY3YWJhOWJiZmI3ZWFkOWRfSUQ6NzU5MzkyMzQzNDU2NDk3OTkwMl8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

一次调用的细节：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZmFiNjU0YzQxZWFkZDQ2ZThhZjZjMjAxNWRmOGE5M2JfZTk0YjNhZTczZDc1MmEzOGYxZmU2MjJmYTJkN2Q5YjJfSUQ6NzU5MzkyMzQzMTczMzg1NzQ2OV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

项目运行情况监控：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NjMxOTI1NWU3YzEyNjVhZTQ3NjA0MjdhNjFjYTcwYmRfMGY5MWI1NWNlZTc1NDA5ZGI2MTZlYTI0YzVmMDVlOTBfSUQ6NzU5MzkyMzQzMTYwMzk5NzkxNF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YzViZmJhMGE3NmYyMjMwMWRjOWY0ZDY5MDBjOWQwYmNfZDc5ZTg4ZTIyNjc3ZWEyMDRmNjEwMmUzODI3NDQ2NmVfSUQ6NzU5MzkyMzQzNDQ1MTYxOTAxM18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

#### v. 使用LangSmith监控方案四

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YjBiZmZiY2E1ZTcwZWNkMmZlN2Y2NjM3N2E1N2ZhZWVfODNmNjI4NzFlNTc3NTE4OTg1ZDM4NWZkN2JmMzRjYWRfSUQ6NzU5MzkyMzQzMjIwMzY4NTA4M18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

### h. 小结

> 问题：
> 
>         1 直接调用小参数量模型有哪些问题？
> 
>         2 大参数量模型一次性生成的方案有什么问题？怎样解决？
> 
>         3 大参数量模型分章节生成的方案有什么问题？怎样解决？
> 
>         4 怎样使用公共大模型服务？
> 
>         5 为什么要生成车型基础设置？怎样使用这份基础设置？
> 
>         6 各章内容必须依次生成吗？如果可以并行生成，需要注意什么？
> 
> 实操：
> 
>         1 使用本章的工作模式，完成一份较复杂的文档



## 5. 智能体的构建块（building blocks）

### a. 学习目标

了解使用框架的情境和优缺点

掌握设计智能体的六种构建块

能够根据情况，选择合适的构建块并完成应用。

### b. 重要文章介绍

工业界和学术界对于智能体（agent）的定义和实现方式仍然由不小的争议，但其中也形成了一些比较系统性的观点。

在2024年12月20日发布的这篇文章**《Building Effective Agents》**[https://www.anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)中，Anthropic公司分享了他们在过去一年中与多个行业团队合作开发大型语言模型（Large Language Model, LLM）智能体的经验。文章的核心观点令人深思：最成功的智能体实现并非依赖于复杂的框架或专门的库，而是通过简单、可组合的构建块构建而成。

### c. 构建智能体的思路

构建智能体有两种思路：

- **工作流（workflow）**：通过预先构建的代码路径，综合运用大语言模型和工具，实现最终目标。
- **智能体（agent）**：大语言模型动态地生成工作流程，并使用工具，如果执行过程中发生意外情况，自行纠偏，保持对任务完成方式的掌控。

这两种方式都能解决高度复杂的任务。工作流的方式提供了更好的掌控能力和一致性，但必须要为特定类型的任务量身定制工作流程；智能体的方式可以不用受定制化的约束。而且能够更加灵活地解决问题，这是我们所需的终极形态，但可控性不足，在一些非常复杂的任务上，现有大模型也许还不足以给高度复杂地任务制定出最优解决方案。

### d. 所有大模型应用都需要框架吗？

在构架基于大语言模型地应用时，不是所有情况下都需要构建智能体，也不是所有的智能体都必须使用框架。有这样几个层次：

- **直接使用大模型**：如果只是简单调用大语言模型就可以解决的任务，直接部署大语言模型即可。比如通用知识问答，做数学题，代码生成等。
- **大模型+少量业务逻辑**：这种情况需要构建智能体，但是尽量不使用框架。因为框架通常会引入额外的封装和抽象层，可能会掩盖底层的提示词和响应，增加调试难度和不必要的复杂度。如果确实需要使用框架，最好明确地知道框架的底层逻辑。
- **复杂的智能体**：建议使用框架。但不要一次开发得过于复杂，应该从基础功能开始，逐步增加复杂度。

总的原则就是**如无必要，勿增实体**

### e. 智能体的六种构建块（building blocks）

#### i. 工作流：提示链（Prompt Chaining）

对于复杂工作有两个思路：

- 写一个尽可能全面的复杂提示词，一次性完成任务。
- 将工作分成多个简单步骤，逐步完成。



一次性完成的结果：<cite doc-id="ImokdSVztov5dHx170gcceyPnTe" file-type="docx" title="大参数量模型一次性完成的报告" token="ImokdSVztov5dHx170gcceyPnTe" type="doc"></cite>



后者的本质是人工拆解的思维链，实际效果要好得多。

例如写一份报告，可以这样处理：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NWIxZTA1NTQ5YzI2NTVkOTI1ODdiMTY1ZDliOTIxNTJfNWU3ZWQ5MTI2OWNkY2EwZDg0NTc3NTUzZWZhOWMxMTZfSUQ6NzU5Mzk0Mjc1ODYwMDEwMTA2M18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

LangGraph的代码实现如下：

```Python
from LangGraph.graph import StateGraph, START,END
from LangChain_ollama import ChatOllama
from typing_extensions import TypedDict

class State(TypedDict):
    topic:str
    outline:str
    draft:str
    paper:str

llm = ChatOllama(model="qwen2.5:7b")

def getOutline(state):
    prompt = """针对“"""+state["topic"]+"""”这个主题，写一份分析报告的大纲，包括历史由来，现状分析，原因分析，解决办法，趋势评估等几个主要部分。"""
    state["outline"]=llm.invoke(prompt).content
    print("outline  "+"*"*80)
    print(state["outline"])
    return state

def getDraft(state):
    prompt = """根据【大纲】，写一份完整的分析报告，要求语言流畅，逻辑清晰，主要内容围绕大纲展开，内容2000字左右。
    
    【大纲】
    """+state["outline"]
    state["draft"]=llm.invoke(prompt).content
    print("draft  "+"*"*80)
    print(state["draft"])
    return state

def getPaper(state):
    prompt = """请对下面的【分析报告】进行全文润色，包括语法检查，用词优化和句式调整，要求文章语言风格自然流畅，逻辑清晰，表达生动而简洁，避免生硬而刻板的AI习作风格，与原文的主要意思保持不变。
    
        【分析报告】
        """ + state["draft"]
    state["paper"] = llm.invoke(prompt).content
    print("paper  "+"*"*80)
    print(state["paper"])
    return state

def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("getOutline", getOutline)
    graphBuilder.add_node("getDraft", getDraft)
    graphBuilder.add_node("getPaper", getPaper)

    graphBuilder.add_edge(START, "getOutline")
    graphBuilder.add_edge("getOutline", "getDraft")
    graphBuilder.add_edge("getDraft", "getPaper")
    graphBuilder.add_edge("getPaper",END)

    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph()

    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")

    state: State = {"topic": "墨西哥毒品泛滥情况报告"}
    result = graph.invoke(state)
    print("final  " + "*" * 80)
    print(result)
```

产出文档：

 <cite doc-id="MkU6dhTdxoKpc5xNk0ScXHfVnzg" file-type="docx" title="小参数量模型使用提示链产出的报告" token="MkU6dhTdxoKpc5xNk0ScXHfVnzg" type="doc"></cite>

> 问题：
> 
>        1 提示链工作流的思路是什么？
> 
>        2 提示链工作流的优点是什么？
> 
> 实操：
> 
>        1 练习提示链工作流

#### ii. 工作流：分支（Routing）

对于特定领域的问题，不应该让大模型随意输出，如果能把大模型的输出导入相关的领域，会明显提升输出质量

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OTc2M2QxNDYxYjgwMzExM2RkOWZlZjNjZDcxNmZiNmZfNDYzYjBmYmFlZTg5YzE5MGZmOTBjYjg4MjhkOGFlN2RfSUQ6NzU5Mzk0Mjc1ODEwOTMzNDQ3M18xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

LangGraph的代码实现如下：

```Python
from LangGraph.graph import StateGraph, START, END
from LangChain_ollama import ChatOllama
from typing_extensions import TypedDict

class State(TypedDict):
    topic: str
    aspect: str
    faction:str
    debate: str

llm = ChatOllama(model="qwen2.5:7b")

def getFraction(state):
    prompt = """你是一位国学大师，你认为“"""+state["topic"]+"""”这个观点是 """+state["aspect"]+""" 的，那么在["儒家","法家","道家"]这三个学派中，你最可能持哪一派的观点？只允许使出学派的名称，不允许输出其他字符。"""
    state["faction"] = llm.invoke(prompt).content
    print("faction  " + "*" * 80)
    print(state["faction"])
    return state

def selectFraction(state):
    if state["faction"] == "儒家":
        return "Confucian"
    elif state["faction"] == "法家":
        return "Legalists"
    elif state["faction"] == "道家":
        return "Taoism"

def getDebateFromConfucian(state):
    prompt = """你是一位国学大师，你认为“"""+state["topic"]+"""”这个观点是 """+state["aspect"]+""" 的，这是儒家的观点，请使用儒家思想对这个问题详细展开论证。"""
    state["debate"] = llm.invoke(prompt).content
    print(state["debate"])
    return state

def getDebateFromLegalists(state):
    prompt = """你是一位国学大师，你认为“"""+state["topic"]+"""”这个观点是 """+state["aspect"]+""" 的，这是法家的观点，请使用法家思想对这个问题详细展开论证。"""
    state["debate"] = llm.invoke(prompt).content
    print(state["debate"])
    return state

def getDebateFromTaoism(state):
    prompt = """你是一位国学大师，你认为“"""+state["topic"]+"""”这个观点是 """+state["aspect"]+""" 的，这是道家的观点，请使用道家思想对这个问题详细展开论证。"""
    state["debate"] = llm.invoke(prompt).content
    print(state["debate"])
    return state

def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("getFraction", getFraction)
    graphBuilder.add_node("getDebateFromConfucian", getDebateFromConfucian)
    graphBuilder.add_node("getDebateFromLegalists", getDebateFromLegalists)
    graphBuilder.add_node("getDebateFromTaoism", getDebateFromTaoism)

    graphBuilder.add_edge(START, "getFraction")
    graphBuilder.add_conditional_edges("getFraction",selectFraction,{"Confucian":"getDebateFromConfucian","Legalists":"getDebateFromLegalists","Taoism":"getDebateFromTaoism"})

    graph = graphBuilder.compile()
    return graph


if __name__ == "__main__":
    graph = buildGraph()

    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")

    state: State = {"topic": "仁义不施而攻守之势异也","aspect":"错误"}
    result = graph.invoke(state)
    print("final  " + "*" * 80)
    print(result)
```

输出结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NTkwZjYxYzM1NzY2NmQ2YTYyMzdjODI0YWM2M2ZlOTZfMmQ5NzBlOTlkZGE1NmJhNTVhYmY3ZGI0ODk5OTViMGZfSUQ6NzU5Mzk0Mjc2MjAxODMyNzQ4Ml8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

> 问题：
> 
>       1 分支工作流适用于什么场景？
> 
> 实操：
> 
>        1 练习分支工作流

#### iii. 工作流：并行化（Parallelization）

在设计应用时，有些功能互补干扰，可以考虑并行化

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODgyYWE2NTAzZDI3NjczNGQ5ZDMwNGIyMWUxYTNlOWZfMzU2YjkzYzM4MWJiYWI5MTg4OTM0MWY5YjUyMzcwZTNfSUQ6NzU5Mzk0Mjc2MDMxOTc0OTA3MV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

LangGraph的代码实现如下：

```Python
from LangGraph.graph import StateGraph, START, END
from LangChain_ollama import ChatOllama
from typing_extensions import TypedDict
from typing import Annotated
import random

def updateReceiveDate(left,right):
    return left

class State(TypedDict):
    sendDate: int
    transTime: int
    receiveDate:Annotated[int,updateReceiveDate]
    returnMessage:str

llm = ChatOllama(model="qwen2.5:7b")

def getSendData(state):
    sendData = random.randint(1,25)
    state["sendDate"] = sendData
    return state

def getTransTime(state):
    transTime = random.randint(3,5)
    state["transTime"] = transTime
    return state

def sendMessage(state):
    prompt = "你是江南机械厂的销售员王钟期，顾客张董事长在我厂预定了一批机器设备，希望能9月"+str(state["receiveDate"])+"日收到货物，厂里最早的发货日期是9月"+str(state["sendDate"])+"日，运输时间是"+str(state["transTime"])+"天，给客户发出适当的回复。"
    state["returnMessage"] = llm.invoke(prompt).content
    print("returnMessage  " + "*" * 80)
    print(state["returnMessage"])
    return state

def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("getSendData", getSendData)
    graphBuilder.add_node("getTransTime", getTransTime)
    graphBuilder.add_node("sendMessage", sendMessage)

    graphBuilder.add_edge(START, "getSendData")
    graphBuilder.add_edge(START, "getTransTime")
    graphBuilder.add_edge(["getSendData","getTransTime"], "sendMessage")

    graph = graphBuilder.compile()
    return graph

if name == "__main__":
    graph = buildGraph()

    from tools import showGraph

    showGraph.showGraphInCode(graph, "graph.jpg")

    state: State = {"receiveDate": 18}
    result = graph.invoke(state)
    print("final  " + "*" * 80)
    print(result)
```

运行结果为：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=M2YxZmIwMzZlOTVlMWM1MDkwZDNiNDEwY2VhNzQzMzJfYjQwYjIwNDUwZGVhNmE3YjJiMWJjNWZlNjJmM2U4YWFfSUQ6NzU5Mzk0Mjc2MjQ1NDYwMDY2Nl8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

> 问题：
> 
>       1 并行工作流适用于什么场景？
> 
>       2 各分支合并的时候是怎样处理的？
> 
> 实操：
> 
>        1 练习并行工作流

#### iv. 工作流：计划-执行（Orchestrator-Workers）

有些工作体量较大，无法一次完成，但各部分之间有很强的关联，也不适合多次完成，可以采用计划-执行模式

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODE4ZDBlYTQzN2U5MThiMTBkMjQ5NzA1YTlmOWJmN2FfODg3ZjBjYmZkY2I1ZGRiZjA2ODVjNzJjNzQxMGMxNWFfSUQ6NzU5Mzk0Mjc1OTUwMTc3Nzg3NV8xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

LangGraph的代码实现如下：

```Python
from LangGraph.graph import StateGraph, START, END
from LangChain_ollama import ChatOllama
from LangGraph.types import Send
from typing_extensions import TypedDict
from typing import Annotated
from pydantic import BaseModel,Field
import operator

class Section(BaseModel):
    num: int = Field(description="章节序号")
    name:str=Field(description="章节标题，采用“【第三章】 迷雾重现”的形式")
    description:str=Field(description="章节描述，最前面是章节标题，后面是章节内容。章节标题采用“【第三章】 迷雾重现”的形式，单独一行")

class Sections(BaseModel):
    sections: list[Section] = Field(description="文章的各个子章节")

class State(TypedDict):
    storyLine:str
    sections:list[Section]
    completedSections:Annotated[list,operator.add]
    novel:str

class WorkerState(TypedDict):
    section:Section
    completedSections:Annotated[list,operator.add]

llm = ChatOllama(model="qwen2.5:7b")

def getWholeStory(state):
    prompt = "你是一位著名小说家，正在创作一部精彩的侦探小说，首先给出故事梗概，1000字左右。"
    state["storyLine"] = llm.invoke(prompt).content
    print("storyLine  " + "*" * 80)
    print(state["storyLine"])
    return state

def orchestrate(state):
    planner = llm.with_structured_output(Sections)
    result = planner.invoke("""你是一位著名小说家，正在创作一部精彩的侦探小说，根据下面的【故事梗概】，将小说分成10个章节，并给出章节的剧情发展。1000字左右。
                            【故事梗概】
                            """+state["storyLine"])
    state["sections"] = result.sections
    print("sections  " + "*" * 80)
    for section in state["sections"]:
        print(str(section.name+'        '+section.description))
    return state

def work(state:WorkerState):
    prompt = """你是一位著名小说家，正在创作一部精彩的侦探小说，根据下面提供的【章节标题】和【章节概述】，完成其中的一个章节，最前面是章节标题，后面是章节内容。章节标题采用“【第三章】 迷雾重现”的形式，单独一行。章节的序号为"""+str(state["section"].num)+""",本章节长度1500字左右
    
    【章节标题】
    """+state["section"].name+"""
    
    【章节概述】
    """+state["section"].description
    result = llm.invoke(prompt)
    return {"num":state["section"].num,"name":state["section"].name,"description":state["section"].description,"completedSections":[{"num":state["section"].num,"content":result.content}]}

def synthesizer(state):
    completedSections = sorted(state["completedSections"],key=lambda completeSection:completeSection["num"])
    novel = "\n\n".join([completeSection["content"] for completeSection in completedSections])
    state["novel"] = novel
    return state

def assignWorkers(state:State):
    return [Send("work",{"section":s}) for s in state["sections"]]

def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("getWholeStory", getWholeStory)
    graphBuilder.add_node("orchestrate", orchestrate)
    graphBuilder.add_node("work", work)
    graphBuilder.add_node("synthesizer", synthesizer)

    graphBuilder.add_edge(START, "getWholeStory")
    graphBuilder.add_edge("getWholeStory", "orchestrate")
    graphBuilder.add_conditional_edges("orchestrate",assignWorkers,["work"])
    graphBuilder.add_edge("work", "synthesizer")

    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph()

    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")

    state: State = {}
    result = graph.invoke(state)
    print("final  " + "*" * 80)
    print(result["novel"])
```

产出的侦探小说：<cite doc-id="Pq9jd4vljopmQbx89FVcwuXqn7f" file-type="docx" title="侦探小说" token="Pq9jd4vljopmQbx89FVcwuXqn7f" type="doc"></cite>

> 问题：
> 
>        1 计划-执行工作流的思路是什么？
> 
>        2 计划-执行工作流适用于哪些场景？
> 
>        3 计划-执行工作流是怎样分发任务的？
> 
> 实操：
> 
>        1 练习计划-执行工作流

#### v. 工作流：生成-评估（Evaluator-Optimizer）

有些情况下大模型生成的结果存在某些方面的不足，需要做针对性优化，可以采用生成-评估模式。

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTUwYzg0YmFkZGY5ODU0NDQ2YmY1NjZhMGFlYjZiODhfOGVkMjAzZDM3MTI2ODM0YmM1OThjZDU3MGE5MWViMjZfSUQ6NzU5Mzk0Mjc2MDk3ODMwNDE5NF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

LangGraph的代码实现如下：

```Python
from LangGraph.graph import StateGraph, START, END
from LangChain_ollama import ChatOllama
from typing_extensions import TypedDict
import json

class State(TypedDict):
    topic:str
    article:str
    feedback:str
    qualified:str
    count:int


llm = ChatOllama(model="qwen2.5:7b")

def generate(state):
    if state.get("feedback"):
        prompt = """根据提供的主题写一篇论证文章。确保文章逻辑严密、有说服力。
        主题为"""+state["topic"]+"""
        同时你需要考虑如下的修改建议："""+state["feedback"]
    else:
        prompt = """根据提供的主题写一篇论证文章。确保文章逻辑严密、有说服力。
                主题为""" + state["topic"]
        prompt = """你是一位小学生，完全不会写作文，现在需要你写一篇论证文章。
                 主题为""" + state["topic"]
    result = llm.invoke(prompt)
    state["count"] += 1
    state["article"] = result.content
    print("generate  " + "*" * 80)
    print(state["article"])
    return state

def evaluate(state):
    prompt = """判断【论证文章】是否很好地论证了【主题】，是否逻辑严密，有说服力。如果不合格，给出具体的修改意见，并按照【指定格式】输出，【指定格式】中的“是否合格”只允许输出“是”或者“否”。只允许输出【指定格式】规定的字符，不允许输出任何其他字符。
    
    【指定格式】
    {"是否合格":"", "修改意见":""}
    
    【主题】
    """+state["topic"]+"""
    
    【论证文章】
    """+state["article"]

    result = llm.invoke(prompt)
    print("evaluate  " + "*" * 80)
    print(result.content)
    resultJson = json.loads(result.content)

    state["qualified"] = resultJson["是否合格"]
    state["feedback"] = resultJson["修改意见"]
    return state

def judgement(state):
    if state["count"] >= 2:
        return "accept"
    else:
        if state["qualified"] == "合格":
            return "accept"
        else:
            return "reject"

def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("generate", generate)
    graphBuilder.add_node("evaluate", evaluate)

    graphBuilder.add_edge(START, "generate")
    graphBuilder.add_edge("generate", "evaluate")
    graphBuilder.add_conditional_edges("evaluate",judgement, {"accept":END,"reject":"generate"})

    graph = graphBuilder.compile()
    return graph

if __name__ == "__main__":
    graph = buildGraph()

    from tools import showGraph

    showGraph.showGraphInCode(graph, "graph.jpg")

    state: State = {"topic":"日本经济会在未来再次崛起","count":0}
    result = graph.invoke(state)
    print("final  " + "*" * 80)
    print(result)
```

输出结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YjFhYTQ2YzcxOGQ2N2M3NmMzMzI1MDNlYTYxOTE1MDFfYjViM2IyMjllZGJjMDZjZmM0OGEzZmYwMjhmYmEzNTJfSUQ6NzU5Mzk0Mjc2MDYyMTczOTIzM18xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTA2NWU4YmZkZGZhOTgzMzdmNTRhZDk5ZDk3M2QwZjlfYjExNmVjOWEzNTlmNGM2YjczMjFiOTE3NzJmNDA3OGNfSUQ6NzU5Mzk0Mjc2MjE3MzU0OTc1OV8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YmM2MGYyZmQ2YTIxOTZlOTkyYTdmNjI5MWZhMmExMzJfMmYyYmYxNzdjYThmZTk4MjkxOTM5NjBhMzRjNzc5YzFfSUQ6NzU5Mzk0Mjc2MjQ1NDY0OTgxOF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)



这种工作流稍加改动甚至可以让大模型左右互博，搞辩论赛

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YzI3Njc4NjIxZThiNDhlMTBiODcxMjUzMGZhYjUwODVfY2FjY2ZlYWE1NTZiNjM2ZmFhYjkwZTNkZTZkMzg5ZmNfSUQ6NzU5Mzk0Mjc2MDM2NTkwMzA0OF8xNzc5MDE4MTk4OjE3NzkwMjE3OThfVjM)

演示代码如下：

```Python
from LangGraph.graph import StateGraph, START, END
from LangChain_ollama import ChatOllama
from typing_extensions import TypedDict


class State(TypedDict):
    topic: str
    pos: str
    neg: str
    count: int

llm = ChatOllama(model="qwen2.5:7b")

def poser(state):
    if state.get("neg"):
        prompt = """你是一位辩论高手，现在在辩论中担任正方，根据【论题】和【反方发言】，用口语化的风格说出你的观点，驳斥【反方发言】，证明【论题】的正确性。500字以内。
        【论题】
        """ + state["topic"] + """
        【反方发言】
        """ + state["neg"]
    else:
        prompt = """你是一位辩论高手，现在在辩论中担任正方，用口语化的风格说出你的观点，证明【论题】的正确性。
        【论题】
        """ + state["topic"]
    result = llm.invoke(prompt)
    state["count"] += 1
    state["pos"] = result.content
    print("正方发言  " + "*" * 80)
    print(state["pos"])
    return state


def neger(state):
    prompt = """你是一位辩论高手，现在在辩论中担任反方，根据【论题】和【正方发言】，用口语化的风格说出你的观点，驳斥【正方发言】，证明【论题】的正确性。500字以内。
        【论题】
        """ + state["topic"] + """
        【正方发言】
        """ + state["pos"]
    result = llm.invoke(prompt)
    state["neg"] = result.content
    print("反方发言  " + "*" * 80)
    print(state["neg"])
    return state


def judgement(state):
    if state["count"] >= 10:
        return "finish"
    else:
        return "proceed"

def buildGraph():
    graphBuilder = StateGraph(State)

    graphBuilder.add_node("poser", poser)
    graphBuilder.add_node("neger", neger)

    graphBuilder.add_edge(START, "poser")
    graphBuilder.add_edge("poser", "neger")
    graphBuilder.add_conditional_edges("neger", judgement, {"finish": END, "proceed": "poser"})

    graph = graphBuilder.compile()
    return graph


if __name__ == "__main__":
    graph = buildGraph()

    from tools import showGraph
    showGraph.showGraphInCode(graph, "graph.jpg")

    state: State = {"topic": "高彩礼是造成结婚率下降的主要原因", "count": 0}
    result = graph.invoke(state)
    print("final  " + "*" * 80)
    print(result)
```

辩论赛节选:<cite doc-id="O914dKv0io3ur4xI54dcU4JOnJf" file-type="docx" title="辩论赛" token="O914dKv0io3ur4xI54dcU4JOnJf" type="doc"></cite>

> 问题：
> 
>       1 生成-评估工作流的思路是什么？
> 
>       2 生成-评估工作流适用于哪些场景？
> 
> 实操：
> 
>        1 练习生成-评估工作流

#### vi. 智能体（agent）

工作流是任务定制和特化加强的，不具备普适性，真正的智能体是我们的终极目标，大模型+工具集的方式已经显示了很大的潜力。演示代码如下：

```Python
from LangChain_ollama import ChatOllama
from LangGraph.prebuilt import create_react_agent

def getTrainSchedule(queryDate,start,end):
    """根据指定的日期、起点城市名称和终点城市名称，查询列车班次"""
    print("获取列车时刻表")
    result = [["D81","12:24","14:30","北京西站","540"],["K4427","15:38","21:30","北京站","220"]]
    resultStr = "您查询的在 "+queryDate+" 这一天从 "+start+" 到 "+end+" 的列车共有 "+str(len(result))+"班：\n"
    for res in result:
        resultStr+=res[0]+" 次列车：发车时间为: "+res[1]+" 到站时间为： "+res[2]+" 发车站为： "+res[3]+" 票价为： "+res[4]+"\n"
    return resultStr

def getAvailableHotel(queryDate,location):
    """根据指定的日期和城市名称，查询可用的旅店"""
    print("获取目的地旅馆的情况")
    result = [["丽晶酒店", "五星级", "大床房", "1200"], ["丽晶大宾馆", "二星级", "标准间", "300"]]
    resultStr = "您查询的 " + queryDate + " 这一天可以预定的酒店有" + str(len(result)) + "家：\n"
    for res in result:
        resultStr += res[0] + " 等级为 " + res[1] + " 房间是 " + res[2] + " 价格是： " + res[3] + "\n"
    return resultStr

toolList = [getTrainSchedule,getAvailableHotel]

agent = create_react_agent(
            model=ChatOllama(model="qwen3:8b"),
            tools=toolList,
            prompt=""
        )

if __name__ == '__main__':
    prompt = "你是一位可靠的个人AI助理，我要在6月15日从北京到青岛旅游，请帮我安排一下车次和旅店。这次旅行要求尽可能便宜。"
    result = agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
    print(result["messages"][-1].content)
```

运行结果：

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YmQ5MDVjNGU2ODIxOTk4ZTkzZWRhMjM2YTAwZWZmNjJfNTZiNDRlODlkOTdiOGE2Njk1ZjMxYzM5ZTg0ZTU3Y2ZfSUQ6NzU5Mzk0Mjc2MjQwMDA1ODMyM18xNzc5MDE4MTk5OjE3NzkwMjE3OTlfVjM)

> 问题：
> 
>        1 智能体构建块适用于什么场景？
> 
> 实操：
> 
>        1 练习智能体构建块

### f. 小结

> 问题：
> 
>         1 构建智能体的两种思路是什么？有哪些优缺点？
> 
>         1  提示链模式工作流的优势是什么？
> 
>         2  为什么引入计划执行工作流？
> 
> 实操：
> 
>         1  练习提示链工作流
> 
>         2  练习分支工作流
> 
>         3  练习并行工作流
> 
>         4  练习计划执行工作流
> 
>         5  练习生成评估工作流
> 
>         6  尝试创建智能体构建块
