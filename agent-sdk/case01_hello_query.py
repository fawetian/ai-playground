"""
Case 01: Hello Query - 最基础的 SDK 调用
=========================================

学习目标:
  - 理解 query() 函数的基本用法（异步迭代器）
  - 了解返回的 Message 类型（AssistantMessage / ResultMessage）
  - 体验最简单的 agent 调用

运行: python case01_hello_query.py
"""

import asyncio
from claude_agent_sdk import query
from claude_agent_sdk.types import AssistantMessage, ResultMessage


async def main():
    async for message in query(
        prompt="用一句话介绍你自己，然后用 Python 写一个冒泡排序。",
    ):
        if isinstance(message, AssistantMessage):
            # AssistantMessage 包含 content 列表，其中有 TextBlock / ToolUseBlock 等
            print("\n=== 内容块 ===")
            for i, block in enumerate(message.content):
                print(f"[Block {i}] type={type(block).__name__}")
                if hasattr(block, "text"):
                    print(f"  text: {block.text[:200]}...")
                if hasattr(block, "thinking"):
                    print(f"  thinking: {block.thinking[:200]}...")

        elif isinstance(message, ResultMessage):
            print("\n=== 费用 ===")
            print(f"total_cost_usd: {message.total_cost_usd}")
            print(f"session_id: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
