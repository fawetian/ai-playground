"""
Case 06: Streaming - 流式输出
=========================================

学习目标:
  - 理解 query() 默认就是流式输出（AsyncIterator）
  - 处理不同类型的 Message 事件
  - 对比 streaming vs 非流式的区别

运行: python case06_streaming.py
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)


async def main():
    options = ClaudeAgentOptions(
        system_prompt="你是一个有帮助的助手，请用中文回答。",
        tools=[],
    )

    print("===== 流式输出 =====\n")

    # query() 返回 AsyncIterator，天然支持流式处理
    async for message in query(
        prompt="用 Python 写一个快速排序算法，并解释其原理。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[Tool Call] {block.name}({block.input})")
                elif isinstance(block, ToolResultBlock):
                    if hasattr(block, "content"):
                        for c in block.content:
                            if hasattr(c, "text"):
                                print(f"[Tool Result] {c.text[:200]}")

        elif isinstance(message, ResultMessage):
            print("\n\n===== 最终结果 =====")
            print(f"session_id: {message.session_id}")
            print(f"total_cost_usd: {message.total_cost_usd}")

    print("\n\n===== 对比：使用 include_partial_messages 实现逐字输出 =====")
    # 开启 include_partial_messages 可以获取部分消息（真正的逐 token 流式）
    options_streaming = ClaudeAgentOptions(
        system_prompt="你是一个有帮助的助手，请用中文回答。",
        tools=[],
        include_partial_messages=True,
    )

    async for message in query(
        prompt="一句话说明什么是快速排序。",
        options=options_streaming,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    # 部分消息时 text 可能是增量
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n[cost: {message.total_cost_usd}]")


if __name__ == "__main__":
    asyncio.run(main())
