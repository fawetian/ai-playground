"""
Case 05: Custom Tools - 自定义工具 (@tool 装饰器)
=========================================

学习目标:
  - 使用 @tool 装饰器定义自定义工具
  - 使用 create_sdk_mcp_server() 创建 MCP 服务器
  - 让 agent 调用你的自定义函数

这是 Agent SDK 最强大的特性之一：
  你可以把任意 Python 函数暴露给 agent，让它自主决定何时调用。

运行: python case05_custom_tools.py
"""

import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
)
from claude_agent_sdk import tool
from claude_agent_sdk import create_sdk_mcp_server
from claude_agent_sdk.types import AssistantMessage


# ===== 定义自定义工具 =====

@tool("get_weather", "获取指定城市的天气信息", {"city": str})
async def get_weather(args):
    """获取城市天气（模拟数据）"""
    city = args["city"]
    weather_data = {
        "北京": "晴天，温度 22°C，AQI 45（优）",
        "上海": "多云，温度 25°C，AQI 62（良）",
        "深圳": "阵雨，温度 28°C，AQI 38（优）",
        "成都": "阴天，温度 18°C，AQI 78（良）",
    }
    result = weather_data.get(city, f"{city}：暂无天气数据")
    return {"content": [{"type": "text", "text": result}]}


@tool("calculator", "计算两个数的四则运算", {"a": float, "b": float, "operation": str})
async def calculator(args):
    """计算器工具"""
    a = args["a"]
    b = args["b"]
    operation = args.get("operation", "add")
    ops = {
        "add": lambda x, y: x + y,
        "sub": lambda x, y: x - y,
        "mul": lambda x, y: x * y,
        "div": lambda x, y: x / y if y != 0 else "Error: 除数不能为0",
    }
    result = ops.get(operation, lambda x, y: "未知运算")(a, b)
    return {"content": [{"type": "text", "text": f"{a} {operation} {b} = {result}"}]}


@tool("get_order", "查询用户的订单信息", {"order_id": str})
async def get_order(args):
    """根据订单号查询订单"""
    order_id = args["order_id"]
    orders = {
        "ORD001": "订单 ORD001: MacBook Pro 14寸, 状态: 已发货, 预计明天送达",
        "ORD002": "订单 ORD002: AirPods Pro, 状态: 待发货, 预计后天发出",
        "ORD003": "订单 ORD003: iPhone 16, 状态: 已签收, 2024-01-15 签收",
    }
    result = orders.get(order_id, f"未找到订单 {order_id}")
    return {"content": [{"type": "text", "text": result}]}


async def main():
    # 创建 MCP 服务器，注册自定义工具
    mcp_server = create_sdk_mcp_server(
        name="my_tools",
        tools=[get_weather, calculator, get_order],
    )

    # 将 MCP 服务器配置到 agent options（使用 dict 格式）
    options = ClaudeAgentOptions(
        system_prompt="你是一个智能助手，可以使用提供的工具来帮助用户。请用中文回答。",
        mcp_servers={"my_tools": mcp_server},
        allowed_tools=["get_weather", "calculator", "get_order"],
        permission_mode="bypassPermissions",
    )

    # 测试 1：天气查询
    print("===== 测试 1: 天气查询 =====")
    async for message in query(
        prompt="帮我查一下北京和上海的天气怎么样？",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)

    # 测试 2：计算器
    print("\n===== 测试 2: 计算器 =====")
    async for message in query(
        prompt="帮我算一下 1234 * 5678 等于多少？",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)

    # 测试 3：订单查询
    print("\n===== 测试 3: 订单查询 =====")
    async for message in query(
        prompt="我有一个订单号 ORD002，帮我看看状态。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)


if __name__ == "__main__":
    asyncio.run(main())
