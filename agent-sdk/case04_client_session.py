"""
Case 04: ClaudeSDKClient - 多轮连续对话
=========================================

学习目标:
  - 使用 ClaudeSDKClient 创建持续会话
  - 实现多轮对话（上下文保持）
  - 对比 query() 和 client 的区别

query() vs ClaudeSDKClient:
  - query(): 一次性会话，发一条消息拿结果，会话销毁
  - ClaudeSDKClient: 持续会话，支持多轮对话，上下文自动保持

运行: python case04_client_session.py
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, ResultMessage


async def main():
    # 创建 client 实例（使用 async with 管理生命周期）
    options = ClaudeAgentOptions(
        system_prompt="你是一个有帮助的编程助手，请用中文回答。",
        tools=[],
    )

    async with ClaudeSDKClient(options=options) as client:
        # ===== 第一轮对话 =====
        print("===== 第一轮 =====")
        await client.query("我想学 Rust，你能给我一个学习路线吗？简要列出 5 个阶段即可。")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        print(block.text)

        # ===== 第二轮对话（上下文延续） =====
        print("\n===== 第二轮 =====")
        # 注意：这里没有再重复上下文，agent 记得之前的对话
        await client.query(
            "针对你刚才提到的第 3 阶段，能详细说说应该做哪些练习项目吗？"
        )

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        print(block.text)

        # ===== 第三轮对话 =====
        print("\n===== 第三轮 =====")
        await client.query("把以上所有内容整理成一个学习计划表格。")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        print(block.text)
            elif isinstance(message, ResultMessage):
                print(f"\nsession_id: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
