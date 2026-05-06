# MCP（Model Context Protocol）

## 背景

使用 Function Call 时，每个工具都需要手动编写描述（Schema），每个 AI 平台都要重写一遍。如果有 N 个 AI 平台 × M 个工具，就是 N×M 倍的工作量。

MCP 解决的就是"统一插件接口"——工具提供一次，所有 AI 平台通用。

## 什么是 MCP

MCP（Model Context Protocol，模型上下文协议）由 Anthropic 于 2024 年提出，旨在实现 LLM 与外部数据源/工具的无缝集成。它是一种 C/S 架构的开放协议。

## 核心架构

```
MCP Host (LLM 应用)
  └── MCP Client (内部，用于连接 MCP Server)
         ↕ MCP 协议
MCP Server (工具提供者)
  ├── 工具 1: 查天气
  ├── 工具 2: 查数据库
  └── 工具 3: 发邮件
```

### MCP Server（工具提供者）

- 将本地函数包装为标准 MCP 接口
- 监听客户端请求，执行函数，返回结果

### MCP Client（工具消费者）

- 连接 MCP Server
- 自动发现可用工具列表（Tool Manifest）
- 按需调用工具

## 工具调用流程

1. **注册连接** — Client 连接 Server，获取工具描述列表
2. **LLM 决策** — 用户输入 → LLM 判断需要什么工具 → 生成调用指令
3. **Client 执行** — 匹配 Server，发送调用请求
4. **Server 执行** — 执行工具逻辑，返回结果
5. **回传 LLM** — 结果包装为 ToolMessage，LLM 生成最终回复

## 三种传输方式

| 特性 | stdio | SSE | Streamable HTTP |
|------|-------|-----|-----------------|
| 通信方向 | 双向 | 单向（Server→Client） | 双向 |
| 传输层 | 本地进程间通信（IPC） | HTTP 长连接 | HTTP |
| 适用场景 | 本地命令行工具 | 简单数据推送 | 复杂实时双向通信 |
| 网络开销 | 无 | 有 | 有 |
| 可靠性 | OS 保证 | TCP 保证 | TCP 保证 |

## 代码实现

### stdio 方式

**Server：**
```python
from mcp.server import FastMCP

mcp = FastMCP('stdio_server', log_level='ERROR')

@mcp.tool(name="get_weather", description="查询天气")
async def get_weather() -> str:
    return "北京的天气是多云"

if __name__ == '__main__':
    mcp.run(transport='stdio')
```

**Client：**
```python
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

server_parameters = StdioServerParameters(
    command="python",
    args=["./stdio_server.py"],
)

async with stdio_client(server_parameters) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        result = await session.call_tool("get_weather", {})
```

### SSE 方式

**Server（与 stdio 的不同）：**
```python
mcp = FastMCP('sse_server', log_level='ERROR', host="127.0.0.1", port=8001)
mcp.run(transport="sse")
```

**Client（连接改为 URL）：**
```python
from mcp.client.sse import sse_client

async with sse_client(url="http://localhost:8001/sse") as streams:
    async with ClientSession(*streams) as session:
        ...
```

### Streamable HTTP 方式

**Server：**
```python
mcp = FastMCP("my_server", log_level="ERROR", host="127.0.0.1", port=8001)
mcp.run(transport="streamable-http")
```

**Client：**
```python
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://127.0.0.1:8001/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        ...
```

## python_a2a 包的 MCP 使用

`python_a2a` 包提供了更简洁的 MCP 封装：

**Server：**
```python
from python_a2a.mcp import FastMCP, create_fastapi_app

mcp = FastMCP(name="MyMCPTools", description="...", version="1.0.0")

@mcp.tool(name="get_weather", description="查询天气")
async def get_weather(**kwargs) -> str:
    return '{"status": "success", "data": "北京的天气是多云"}'

app = create_fastapi_app(mcp)
uvicorn.run(app, host="0.0.0.0", port=8010)
```

**Client（Agent 调用）：**
```python
from python_a2a import MCPClient, to_langchain_tool

mcp_client = MCPClient(server_url="http://localhost:8010")
tools = await mcp_client.get_tools()

# 将 MCP 工具转为 LangChain 工具
get_weather_tool = to_langchain_tool(url, "get_weather")
tools = [get_weather_tool]

# 创建 Agent，正常使用
agent = create_tool_calling_agent(llm, tools, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

## langchain_mcp_adapters vs python_a2a

- `langchain_mcp_adapters` — 标准 MCP 客户端适配器，直接用 `load_mcp_tools(session)` 加载
- `python_a2a` — 额外封装了一层，`MCPClient` + `to_langchain_tool` 使用更简洁
