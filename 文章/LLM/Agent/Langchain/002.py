# ============================================================
# 1. 导包
# ============================================================
from mcp.server.fastmcp import FastMCP      # MCP Server 快速构建

# ============================================================
# 2. 配置
# ============================================================
mcp = FastMCP(
    name="DemoServer",
    instructions="演示 MCP Server，只返回固定数据",
    log_level="ERROR",
    host="127.0.0.1", port=8001
)

# ============================================================
# 3. 代码逻辑
# ============================================================

# 3.1 业务函数
def get_weather(city: str) -> str:
    """查天气，直接返回固定值"""
    return f"{city}: 多云，25°C"

# 3.2 注册工具
@mcp.tool(
    name="get_weather",
    description="查询指定城市的天气，输入城市名如 '北京'"
)
def query_weather(city: str) -> str:
    return get_weather(city)

# 3.3 启动
if __name__ == '__main__':
    mcp.run(transport="streamable-http")
