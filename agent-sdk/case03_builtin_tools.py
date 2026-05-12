"""
Case 03: Built-in Tools - 使用内置工具
=========================================

学习目标:
  - 了解 Agent SDK 的内置工具
  - 使用 allowed_tools 自动允许特定工具
  - 观察 agent 如何自动调用工具完成任务

内置工具列表:
  - Read      读取文件
  - Write     写入文件
  - Edit      编辑文件
  - Bash      执行 shell 命令
  - Glob      文件模式匹配搜索
  - Grep      内容搜索
  - WebSearch 网页搜索
  - WebFetch  抓取网页内容

运行: python case03_builtin_tools.py
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock


async def main():
    # allowed_tools 自动允许 Bash 和 Read 工具（不需要权限确认）
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read"],
        system_prompt="你是一个系统运维助手，帮助用户执行简单的系统操作。",
    )

    # agent 会自动判断是否需要调用工具
    async for message in query(
        prompt="帮我看看当前系统的 Python 版本和已安装的包数量。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for i, block in enumerate(message.content):
                print(f"\n--- Block {i}: {type(block).__name__} ---")

                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"  Tool: {block.name}")
                    print(f"  Input: {block.input}")
                elif isinstance(block, ToolResultBlock):
                    for c in block.content:
                        if isinstance(c, TextBlock):
                            print(f"  Result: {c.text[:300]}")


if __name__ == "__main__":
    asyncio.run(main())
